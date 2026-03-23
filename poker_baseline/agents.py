"""Agents for the poker baseline example."""

import mesa


RANKS = "23456789TJQKA"


def card_value(card: str) -> int:
    return RANKS.index(card[0])


def hand_strength(card_1: str, card_2: str) -> int:
    # Simple pre-flop heuristic: high card + pair bonus.
    score = max(card_value(card_1), card_value(card_2))
    if card_1[0] == card_2[0]:
        score += 5
    return score


class PokerPlayer(mesa.Agent):
    def __init__(self, model: mesa.Model, name: str, stack: int = 100) -> None:
        super().__init__(model)
        self.name = name
        self.stack = stack
        self.cards: list[str] = []
        self.folded = False
        self.current_bet = 0

    def reset_for_hand(self) -> None:
        self.cards = []
        self.folded = False
        self.current_bet = 0

    def decide_action(self, to_call: int) -> tuple[str, int]:
        if self.folded or self.stack <= 0:
            return ("fold", 0)

        score = hand_strength(self.cards[0], self.cards[1])

        if to_call == 0:
            if score >= 10 and self.stack >= 4:
                return ("raise", 4)
            return ("check", 0)

        if score >= 11 and self.stack >= to_call + 4:
            return ("raise", to_call + 4)
        if score >= 8 and self.stack >= to_call:
            return ("call", to_call)
        return ("fold", 0)
