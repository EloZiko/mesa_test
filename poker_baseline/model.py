import mesa
from mesa.datacollection import DataCollector

from agents import PokerPlayer, RANKS, hand_strength

SUITS = "CDHS"


def avg_stack(model):
    stacks = [p.stack for p in model.players if p.stack > 0]
    if not stacks:
        return 0
    return sum(stacks) / len(stacks)


def players_alive(model):
    return sum(1 for p in model.players if p.stack > 0)


def biggest_stack(model):
    return max(p.stack for p in model.players)


class PokerTable(mesa.Model):
    def __init__(self, num_players=4, starting_stack=100, small_blind=1, rng=None):
        super().__init__(rng=rng)
        self.starting_stack = starting_stack
        self.small_blind = small_blind
        self.big_blind = small_blind * 2
        self.num_players = num_players

        styles = ["normal", "tight", "loose"]
        names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank"]

        self.players = []
        for i in range(num_players):
            style = styles[i % len(styles)]
            p = PokerPlayer(self, names[i], stack=starting_stack, style=style)
            self.players.append(p)

        self.pot = 0
        self.current_bet = 0
        self.community_cards = []
        self.deck = []
        self.hand_number = 0
        self.dealer_idx = 0
        self.last_winner = ""
        self.last_pot = 0
        self.hand_log = []

        self.datacollector = DataCollector(
            model_reporters={
                "Avg Stack": avg_stack,
                "Players Alive": players_alive,
                "Biggest Stack": biggest_stack,
                "Pot": "last_pot",
            },
            agent_reporters={"Stack": "stack", "Wins": "wins"},
        )
        self.datacollector.collect(self)

    def build_deck(self):
        self.deck = [r + s for r in RANKS for s in SUITS]
        self.random.shuffle(self.deck)

    def active_players(self):
        return [p for p in self.players if not p.folded and p.stack > 0]

    def deal_cards(self):
        for p in self.players:
            p.reset_hand()
            if p.stack > 0:
                p.cards = [self.deck.pop(), self.deck.pop()]
                p.hands_played += 1
            else:
                p.folded = True

    def post_blinds(self):
        alive = [p for p in self.players if p.stack > 0]
        if len(alive) < 2:
            return

        sb_idx = (self.dealer_idx + 1) % len(self.players)
        bb_idx = (self.dealer_idx + 2) % len(self.players)

        while self.players[sb_idx].stack <= 0:
            sb_idx = (sb_idx + 1) % len(self.players)
        while self.players[bb_idx].stack <= 0 or bb_idx == sb_idx:
            bb_idx = (bb_idx + 1) % len(self.players)

        sb_player = self.players[sb_idx]
        bb_player = self.players[bb_idx]

        sb_amt = min(sb_player.stack, self.small_blind)
        sb_player.stack -= sb_amt
        sb_player.current_bet = sb_amt
        self.pot += sb_amt

        bb_amt = min(bb_player.stack, self.big_blind)
        bb_player.stack -= bb_amt
        bb_player.current_bet = bb_amt
        self.pot += bb_amt

        self.current_bet = self.big_blind

    def betting_round(self):
        active = self.active_players()
        if len(active) <= 1:
            return

        last_raiser = None
        players_acted = set()

        for _ in range(len(active) * 3):
            for p in active:
                if p.folded or p.is_all_in:
                    continue
                if p == last_raiser and p.unique_id in players_acted:
                    return

                to_call = self.current_bet - p.current_bet
                action, amount = p.decide(to_call)

                if action == "fold":
                    p.folded = True
                    p.last_action = "fold"
                elif action == "check":
                    p.last_action = "check"
                elif action == "call":
                    paid = min(p.stack, to_call)
                    p.stack -= paid
                    p.current_bet += paid
                    self.pot += paid
                    if p.stack == 0:
                        p.is_all_in = True
                    p.last_action = "call"
                elif action == "raise":
                    paid = min(p.stack, amount)
                    p.stack -= paid
                    p.current_bet += paid
                    self.current_bet = max(self.current_bet, p.current_bet)
                    self.pot += paid
                    last_raiser = p
                    if p.stack == 0:
                        p.is_all_in = True
                    p.last_action = "raise"

                players_acted.add(p.unique_id)

            if len(self.active_players()) <= 1:
                return

            all_matched = all(
                p.current_bet >= self.current_bet or p.is_all_in
                for p in self.active_players()
            )
            if all_matched and len(players_acted) >= len(self.active_players()):
                return

    def deal_community(self, count):
        self.deck.pop()
        for _ in range(count):
            self.community_cards.append(self.deck.pop())

    def eval_hand(self, player):
        all_cards = player.cards + self.community_cards
        score = hand_strength(player.cards)

        for c in self.community_cards:
            if c[0] == player.cards[0][0] or c[0] == player.cards[1][0]:
                score += 3

        ranks_in_hand = [c[0] for c in all_cards]
        for r in RANKS:
            cnt = ranks_in_hand.count(r)
            if cnt >= 3:
                score += 8
            if cnt >= 4:
                score += 15

        suits_in_hand = [c[1] for c in all_cards]
        for s in SUITS:
            if suits_in_hand.count(s) >= 5:
                score += 10

        return score

    def showdown(self):
        active = self.active_players()
        if len(active) == 0:
            return None

        if len(active) == 1:
            winner = active[0]
            winner.stack += self.pot
            winner.wins += 1
            return winner

        best_score = -1
        winner = active[0]
        for p in active:
            s = self.eval_hand(p)
            if s > best_score:
                best_score = s
                winner = p

        winner.stack += self.pot
        winner.wins += 1
        return winner

    def step(self):
        alive = [p for p in self.players if p.stack > 0]
        if len(alive) < 2:
            self.running = False
            self.datacollector.collect(self)
            return

        self.hand_number += 1
        self.pot = 0
        self.current_bet = 0
        self.community_cards = []

        self.build_deck()
        self.deal_cards()
        self.post_blinds()

        self.betting_round()

        if len(self.active_players()) > 1:
            self.deal_community(3)
            self.current_bet = 0
            for p in self.active_players():
                p.current_bet = 0
            self.betting_round()

        if len(self.active_players()) > 1:
            self.deal_community(1)
            self.current_bet = 0
            for p in self.active_players():
                p.current_bet = 0
            self.betting_round()

        if len(self.active_players()) > 1:
            self.deal_community(1)
            self.current_bet = 0
            for p in self.active_players():
                p.current_bet = 0
            self.betting_round()

        winner = self.showdown()
        if winner:
            self.last_winner = winner.name
            self.last_pot = self.pot
            self.hand_log.append({
                "hand": self.hand_number,
                "winner": winner.name,
                "pot": self.pot,
            })

        self.dealer_idx = (self.dealer_idx + 1) % len(self.players)
        self.datacollector.collect(self)
