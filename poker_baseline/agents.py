import mesa


RANKS = "23456789TJQKA"
SUITS = "CDHS"


def card_value(card):
    return RANKS.index(card[0])


def hand_strength(cards):
    if len(cards) < 2:
        return 0
    v1 = card_value(cards[0])
    v2 = card_value(cards[1])
    score = max(v1, v2)
    if cards[0][0] == cards[1][0]:
        score += 6
    if cards[0][1] == cards[1][1]:
        score += 2
    if abs(v1 - v2) <= 2:
        score += 1
    return score


class PokerPlayer(mesa.Agent):
    def __init__(self, model, name, stack=100, style="normal"):
        super().__init__(model)
        self.name = name
        self.stack = stack
        self.style = style
        self.cards = []
        self.folded = False
        self.current_bet = 0
        self.wins = 0
        self.hands_played = 0
        self.is_all_in = False
        self.last_action = ""

    def reset_hand(self):
        self.cards = []
        self.folded = False
        self.current_bet = 0
        self.is_all_in = False
        self.last_action = ""

    def decide(self, to_call):
        if self.folded or self.stack <= 0:
            return ("fold", 0)

        strength = hand_strength(self.cards)

        if self.style == "tight":
            return self._tight_strategy(strength, to_call)
        elif self.style == "loose":
            return self._loose_strategy(strength, to_call)
        else:
            return self._normal_strategy(strength, to_call)

    def _normal_strategy(self, strength, to_call):
        if to_call == 0:
            if strength >= 10 and self.stack >= 4:
                return ("raise", 4)
            return ("check", 0)
        if strength >= 11 and self.stack >= to_call + 4:
            return ("raise", to_call + 4)
        if strength >= 7 and self.stack >= to_call:
            return ("call", to_call)
        return ("fold", 0)

    def _tight_strategy(self, strength, to_call):
        if to_call == 0:
            if strength >= 12:
                return ("raise", 6)
            return ("check", 0)
        if strength >= 12 and self.stack >= to_call + 6:
            return ("raise", to_call + 6)
        if strength >= 9 and self.stack >= to_call:
            return ("call", to_call)
        return ("fold", 0)

    def _loose_strategy(self, strength, to_call):
        bluff = self.model.random.random() < 0.15
        if to_call == 0:
            if strength >= 8 or bluff:
                bet = min(self.stack, 4)
                return ("raise", bet)
            return ("check", 0)
        if strength >= 5 or bluff:
            if strength >= 10 and self.stack >= to_call + 4:
                return ("raise", to_call + 4)
            if self.stack >= to_call:
                return ("call", to_call)
        return ("fold", 0)
