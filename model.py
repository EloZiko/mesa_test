"""Boltzmann Wealth Model — a simple Agent-Based Model built with Mesa.

Each agent starts with 1 unit of wealth.  On every step, each agent with
at least 1 unit of wealth picks a random neighbour and gives that neighbour
1 unit.  Over time the wealth distribution converges toward an exponential
(Boltzmann) distribution.
"""

import mesa


class WealthAgent(mesa.Agent):
    """An agent with some initial wealth."""

    def __init__(self, model: mesa.Model) -> None:
        super().__init__(model)
        self.wealth: int = 1

    def step(self) -> None:
        """Give 1 unit of wealth to a randomly chosen other agent."""
        if self.wealth == 0:
            return
        others = self.model.agents.select(lambda a: a is not self).to_list()
        if not others:
            return
        other = self.random.choice(others)
        other.wealth += 1
        self.wealth -= 1


class WealthModel(mesa.Model):
    """A simple model of wealth exchange between N agents."""

    def __init__(self, n_agents: int = 10, seed: int | None = None) -> None:
        super().__init__(rng=seed)
        self.n_agents = n_agents
        for _ in range(n_agents):
            WealthAgent(self)

    def step(self) -> None:
        """Advance the model by one step."""
        self.agents.shuffle_do("step")

    def total_wealth(self) -> int:
        """Return the sum of wealth across all agents."""
        return sum(agent.wealth for agent in self.agents)

    def gini(self) -> float:
        """Return the Gini coefficient of the current wealth distribution.

        A value of 0 means perfect equality; 1 means perfect inequality.
        """
        wealth_values = sorted(agent.wealth for agent in self.agents)
        n = len(wealth_values)
        if n == 0 or sum(wealth_values) == 0:
            return 0.0
        cumulative = sum((2 * i - n - 1) * w for i, w in enumerate(wealth_values, start=1))
        return cumulative / (n * sum(wealth_values))
