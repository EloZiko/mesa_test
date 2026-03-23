"""Run a tiny demo of the poker baseline model."""

from mesa.examples.basic.poker_baseline.model import PokerTable


def main() -> None:
    model = PokerTable(seed=42, starting_stack=100)

    for hand_idx in range(1, 6):
        winner = model.play_one_hand()
        stacks = {player.name: player.stack for player in model.players}
        print(f"Hand {hand_idx}: winner={winner.name}, pot={model.pot}, stacks={stacks}")


if __name__ == "__main__":
    main()
