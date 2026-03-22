"""Tests for the Boltzmann Wealth Model."""

import pytest

from model import WealthAgent, WealthModel


class TestWealthAgent:
    """Unit tests for WealthAgent."""

    def test_initial_wealth(self):
        """Each agent starts with exactly 1 unit of wealth."""
        model = WealthModel(n_agents=5, seed=42)
        for agent in model.agents:
            assert agent.wealth == 1

    def test_step_transfers_wealth(self):
        """A step keeps total wealth constant and may change distribution."""
        model = WealthModel(n_agents=5, seed=42)
        initial_total = model.total_wealth()
        model.step()
        assert model.total_wealth() == initial_total

    def test_agent_with_zero_wealth_skips(self):
        """An agent with 0 wealth does nothing in its step."""
        model = WealthModel(n_agents=5, seed=0)
        poor_agent = next(iter(model.agents))
        poor_agent.wealth = 0
        wealth_before = {a.unique_id: a.wealth for a in model.agents}
        poor_agent.step()
        for agent in model.agents:
            if agent is not poor_agent:
                # Other agents' wealth should be unchanged by the poor agent's step
                assert agent.wealth == wealth_before[agent.unique_id]


class TestWealthModel:
    """Integration tests for WealthModel."""

    def test_agent_count(self):
        """Model creates the requested number of agents."""
        for n in [1, 5, 20]:
            model = WealthModel(n_agents=n, seed=0)
            assert len(model.agents) == n

    def test_total_wealth_conserved_over_many_steps(self):
        """Total wealth is conserved across many steps."""
        model = WealthModel(n_agents=10, seed=7)
        expected = model.total_wealth()
        for _ in range(100):
            model.step()
        assert model.total_wealth() == expected

    def test_wealth_non_negative(self):
        """No agent should ever have negative wealth."""
        model = WealthModel(n_agents=10, seed=13)
        for _ in range(50):
            model.step()
            for agent in model.agents:
                assert agent.wealth >= 0

    def test_gini_zero_when_equal(self):
        """Gini coefficient is 0 when all agents have equal wealth."""
        model = WealthModel(n_agents=5, seed=0)
        # All agents start with 1 unit — perfect equality.
        assert model.gini() == pytest.approx(0.0, abs=1e-9)

    def test_gini_increases_over_time(self):
        """Gini coefficient should increase (inequality grows) over many steps."""
        model = WealthModel(n_agents=50, seed=99)
        initial_gini = model.gini()
        for _ in range(200):
            model.step()
        assert model.gini() > initial_gini

    def test_reproducible_with_seed(self):
        """Two models with the same seed produce identical results."""
        model_a = WealthModel(n_agents=10, seed=42)
        model_b = WealthModel(n_agents=10, seed=42)
        for _ in range(10):
            model_a.step()
            model_b.step()
        wealth_a = sorted(a.wealth for a in model_a.agents)
        wealth_b = sorted(b.wealth for b in model_b.agents)
        assert wealth_a == wealth_b

    def test_step_counter_increments(self):
        """Model.steps increments by 1 after each call to step()."""
        model = WealthModel(n_agents=5, seed=0)
        assert model.steps == 0
        model.step()
        assert model.steps == 1
        model.step()
        assert model.steps == 2

    def test_single_agent_model(self):
        """A model with a single agent should not crash and conserve wealth."""
        model = WealthModel(n_agents=1, seed=0)
        initial = model.total_wealth()
        model.step()
        assert model.total_wealth() == initial
