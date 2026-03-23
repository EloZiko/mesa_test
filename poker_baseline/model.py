"""Simple two-player poker table model (step 1 baseline)."""

import mesa

from mesa.examples.basic.poker_baseline.agents import PokerPlayer, RANKS, hand_strength

SUITS = "CDHS"


class PokerTable(mesa.Model):
    def __init__(self, seed: int | None = 42, starting_stack: int = 100) -> None:
        super().__init__(rng=seed)
        self.starting_stack = starting_stack

        self.players = [
            PokerPlayer(self, "Novice", stack=starting_stack),
            PokerPlayer(self, "Expert", stack=starting_stack),
        ]

        self.pot = 0
        self.current_bet = 0
        self.deck: list[str] = []
        self.hand_over = False

    def build_deck(self) -> None:
        self.deck = [rank + suit for rank in RANKS for suit in SUITS]
        self.random.shuffle(self.deck)

    def deal_private_cards(self) -> None:
        for player in self.players:
            player.reset_for_hand()
            player.cards = [self.deck.pop(), self.deck.pop()]

    def post_blinds(self) -> None:
        small_blind, big_blind = 1, 2
        sb, bb = self.players[0], self.players[1]

        for player, blind in ((sb, small_blind), (bb, big_blind)):
            paid = min(player.stack, blind)
            player.stack -= paid
            player.current_bet += paid
            self.pot += paid

        self.current_bet = big_blind

    def apply_action(self, player: PokerPlayer, action_kind: str, amount: int = 0) -> None:
        to_call = self.current_bet - player.current_bet

        if action_kind == "fold":
            player.folded = True
            return

        if action_kind == "check":
            return

        if action_kind == "call":
            paid = min(player.stack, to_call)
            player.stack -= paid
            player.current_bet += paid
            self.pot += paid
            return

        if action_kind == "raise":
            paid = min(player.stack, amount)
            player.stack -= paid
            player.current_bet += paid
            self.current_bet = max(self.current_bet, player.current_bet)
            self.pot += paid

    def betting_round(self) -> None:
        for player in self.players:
            if player.folded:
                continue
            to_call = self.current_bet - player.current_bet
            action_kind, amount = player.decide_action(to_call)
            self.apply_action(player, action_kind, amount)

    def payout_to_winner(self, winner: PokerPlayer) -> None:
        winner.stack += self.pot

    def showdown_or_fold_win(self) -> PokerPlayer:
        active = [player for player in self.players if not player.folded]

        if len(active) == 1:
            winner = active[0]
            self.payout_to_winner(winner)
            return winner

        p0, p1 = active
        s0 = hand_strength(p0.cards[0], p0.cards[1])
        s1 = hand_strength(p1.cards[0], p1.cards[1])

        if s0 > s1:
            winner = p0
            self.payout_to_winner(winner)
            return winner

        if s1 > s0:
            winner = p1
            self.payout_to_winner(winner)
            return winner

        # Tie: split pot, odd chip goes to first player.
        split = self.pot // 2
        p0.stack += split + (self.pot % 2)
        p1.stack += split
        return p0

    def play_one_hand(self) -> PokerPlayer:
        self.pot = 0
        self.current_bet = 0
        self.hand_over = False

        self.build_deck()
        self.deal_private_cards()
        self.post_blinds()
        self.betting_round()

        winner = self.showdown_or_fold_win()
        self.hand_over = True
        return winner
