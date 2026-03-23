from model import PokerTable


def main():
    model = PokerTable(num_players=4, starting_stack=100, rng=42)

    for _ in range(20):
        model.step()
        if not model.running:
            break

    print(f"\nAfter {model.hand_number} hands:")
    for p in model.players:
        status = "OUT" if p.stack <= 0 else f"${p.stack}"
        print(f"  {p.name} ({p.style}): {status} - {p.wins} wins")

    print(f"\nLast hand won by: {model.last_winner}")


if __name__ == "__main__":
    main()
