from __future__ import annotations

import random
from typing import ClassVar, Dict, Optional, Set, Tuple, TYPE_CHECKING

from src.agents.strategies.base import ExplorationStrategy
from src.environment.grid import CellType

if TYPE_CHECKING:
    from src.agents.agent import Agent
    from src.environment.environment import Environment
    from src.pathfinding.pathfinder import Pathfinder


class AntColonyLiteStrategy(ExplorationStrategy):
    """
    Ant-Colony Lite per esplorazione:
    - parte dai target di copertura (celle non viste/stale)
    - preferisce celle informative e poco "tracciate"
    - aggiunge una lieve repulsione dagli altri agenti noti per evitare clustering
    - la pheromone map e' condivisa tra tutti gli agenti con questa strategia
    """

    _pheromone: ClassVar[Dict[Tuple[int, int], float]] = {}
    _last_evap_tick: ClassVar[int] = -1

    def __init__(
        self,
        alpha_info: float = 2.0,
        beta_trail: float = 1.0,
        gamma_sep: float = 0.35,
        evaporation: float = 0.06,
        deposit: float = 1.2,
        noise: float = 0.02,
    ) -> None:
        super().__init__()
        self.alpha_info = alpha_info
        self.beta_trail = beta_trail
        self.gamma_sep = gamma_sep
        self.evaporation = evaporation
        self.deposit = deposit
        self.noise = noise

    def next_move(
        self,
        agent: "Agent",
        env: "Environment",
        pathfinder: "Pathfinder",
        occupied: Set[Tuple[int, int]],
    ) -> Optional[Tuple[int, int]]:
        move = self._priority_move(agent, env, pathfinder, occupied)
        if move:
            return move

        self._evaporate_once_per_tick(env.tick)

        targets = self._coverage_targets(agent, env)
        if not targets:
            neighbors = env.grid.walkable_neighbors(agent.row, agent.col)
            free = [n for n in neighbors if n not in occupied]
            return random.choice(free) if free else (random.choice(neighbors) if neighbors else None)

        best = max(targets, key=lambda p: self._score(p, agent, env))
        step = pathfinder.next_step(agent.pos, best, occupied - {agent.pos})

        if step:
            self._deposit(best, amount=self.deposit)
            self._deposit(agent.pos, amount=self.deposit * 0.35)
            return step

        neighbors = env.grid.walkable_neighbors(agent.row, agent.col)
        free = [n for n in neighbors if n not in occupied]
        return random.choice(free) if free else (random.choice(neighbors) if neighbors else None)

    def _score(self, target: Tuple[int, int], agent: "Agent", env: "Environment") -> float:
        dist = abs(target[0] - agent.row) + abs(target[1] - agent.col)
        info = self._information_gain(target, agent, env)
        pher = self._pheromone.get(target, 0.0)
        sep = self._separation_term(target, agent)

        info_term = self.alpha_info * (info / (dist + 1.0))
        trail_term = -self.beta_trail * pher
        sep_term = self.gamma_sep * sep
        jitter = random.uniform(-self.noise, self.noise)

        return info_term + trail_term + sep_term + jitter

    def _information_gain(
        self,
        target: Tuple[int, int],
        agent: "Agent",
        env: "Environment",
    ) -> int:
        # Conoscenza condivisa: local_map viene fusa via protocollo di comunicazione.
        shared_seen_cells = self._shared_seen_cells(agent)
        tr, tc = target
        radius = agent.visibility_radius
        gain = 0

        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                if abs(dr) + abs(dc) > radius:
                    continue
                nr, nc = tr + dr, tc + dc
                if not env.grid.in_bounds(nr, nc):
                    continue
                if env.grid.cell(nr, nc) != CellType.EMPTY:
                    continue
                if (nr, nc) not in shared_seen_cells:
                    gain += 1

        return gain

    def _shared_seen_cells(self, agent: "Agent") -> Set[Tuple[int, int]]:
        """Miglior conoscenza disponibile: visione locale + mappe ricevute via comunicazione."""
        return set(agent.local_map.keys()) | agent.seen_cells

    def _separation_term(self, target: Tuple[int, int], agent: "Agent") -> float:
        """
        Premia target lontani dagli altri agenti noti.
        Usa la distanza minima: efficace contro clustering locale.
        """
        other_positions = []

        for other_id, info in agent.known_agents.items():
            # `known_agents` historically stores values as tuples
            # `(pos, tick)`; some code might use dicts with a "pos" key.
            if isinstance(info, (tuple, list)):
                pos = info[0] if info else None
            elif isinstance(info, dict):
                pos = info.get("pos")
            else:
                pos = None

            if pos is None:
                continue
            if pos == agent.pos:
                continue
            other_positions.append(pos)

        if not other_positions:
            return 0.0

        min_dist = min(abs(target[0] - r) + abs(target[1] - c) for r, c in other_positions)

        # Normalizzazione morbida: evita che il termine esploda troppo
        return min_dist / (min_dist + 2.0)

    def _evaporate_once_per_tick(self, tick: int) -> None:
        if self.__class__._last_evap_tick == tick:
            return
        self.__class__._last_evap_tick = tick

        if not self.__class__._pheromone:
            return

        to_delete = []
        for pos, value in list(self.__class__._pheromone.items()):
            new_value = value * (1.0 - self.evaporation)
            if new_value < 0.01:
                to_delete.append(pos)
            else:
                self.__class__._pheromone[pos] = new_value

        for pos in to_delete:
            del self.__class__._pheromone[pos]

    @classmethod
    def _deposit(cls, pos: Tuple[int, int], amount: float) -> None:
        cls._pheromone[pos] = cls._pheromone.get(pos, 0.0) + amount