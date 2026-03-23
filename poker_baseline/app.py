import solara

from model import PokerTable
from mesa.visualization import (
    SolaraViz,
    make_plot_component,
)


def get_table_info(model):
    if model.hand_number == 0:
        return solara.Markdown("**Waiting for first hand...**")

    players_info = ""
    for p in model.players:
        if p.stack <= 0:
            players_info += f"- ~~{p.name}~~ (out)\n"
        else:
            action = p.last_action if p.last_action else "-"
            cards = " ".join(p.cards) if p.cards and not p.folded else "XX XX"
            players_info += f"- **{p.name}** [{p.style}] : ${p.stack} | {cards} | {action}\n"

    txt = f"""
**Hand #{model.hand_number}** | Pot: ${model.last_pot} | Winner: {model.last_winner}

Community: {' '.join(model.community_cards) if model.community_cards else 'none'}

{players_info}
"""
    return solara.Markdown(txt)


def get_stats(model):
    if model.hand_number == 0:
        return solara.Markdown("")
    txt = "### Win counts\n"
    for p in sorted(model.players, key=lambda x: x.wins, reverse=True):
        txt += f"- {p.name}: {p.wins} wins\n"
    return solara.Markdown(txt)


model_params = {
    "rng": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "num_players": {
        "type": "SliderInt",
        "value": 4,
        "label": "Number of players",
        "min": 2,
        "max": 6,
        "step": 1,
    },
    "starting_stack": {
        "type": "SliderInt",
        "value": 100,
        "label": "Starting stack",
        "min": 50,
        "max": 500,
        "step": 50,
    },
    "small_blind": {
        "type": "SliderInt",
        "value": 1,
        "label": "Small blind",
        "min": 1,
        "max": 10,
        "step": 1,
    },
}


model = PokerTable(num_players=4, starting_stack=100, rng=42)

StackPlot = make_plot_component("Biggest Stack")
AlivePlot = make_plot_component("Players Alive")

page = SolaraViz(
    model,
    components=[get_table_info, StackPlot, AlivePlot, get_stats],
    model_params=model_params,
    name="Poker Table",
)
page
