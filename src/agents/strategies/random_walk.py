"""
Strategia 1 — Smart Random Walk con priorità oggetti noti.

L'agente mantiene una componente casuale, ma preferisce:
- celle che aprono nuova visibilità
- celle meno recenti / meno battute
- celle lontane dagli altri agenti noti
Se ha un oggetto noto nel campo visivo si dirige subito verso di esso.
Se sta trasportando un oggetto, si dirige all'ingresso del magazzino più vicino.
"""

from __future__ import annotations

import random
from typing import Optional, Set, Tuple, TYPE_CHECKING

from src.agents.strategies.base import ExplorationStrategy
from src.environment.grid import CellType

if TYPE_CHECKING:
    from src.agents.agent import Agent
    from src.environment.environment import Environment
    from src.pathfinding.pathfinder import Pathfinder


class RandomWalkStrategy(ExplorationStrategy):
    """
    Smart random walk:
    - mantiene casualità
    - evita mosse miopi
    - favorisce copertura utile e dispersione
    """

    def __init__(
        self,
        info_weight: float = 1.2,
        stale_weight: float = 0.8,
        sep_weight: float = 0.5,
        revisit_penalty: float = 1.0,
        noise: float = 0.3,
    ) -> None:
        super().__init__()
        self.info_weight = info_weight
        self.stale_weight = stale_weight
        self.sep_weight = sep_weight
        self.revisit_penalty = revisit_penalty
        self.noise = noise

    def next_move(
        self,
        agent: "Agent",
        env: "Environment",
        pathfinder: "Pathfinder",
        occupied: Set[Tuple[int, int]],
    ) -> Optional[Tuple[int, int]]:

        # --- Priorità universale: trasporto + oggetti noti ---
        move = self._priority_move(agent, env, pathfinder, occupied)
        if move:
            return move

        neighbors = env.grid.walkable_neighbors(agent.row, agent.col)
        if not neighbors:
            return None

        free = [n for n in neighbors if n not in occupied]
        candidates = free if free else neighbors

        scored = [(pos, self._score_neighbor(pos, agent, env)) for pos in candidates]
        max_score = max(score for _, score in scored)

        # Tiene un po' di casualità: sceglie tra le mosse quasi migliori
        threshold = max_score - self.noise
        pool = [pos for pos, score in scored if score >= threshold]

        return random.choice(pool) if pool else random.choice(candidates)

    def _score_neighbor(
        self,
        pos: Tuple[int, int],
        agent: "Agent",
        env: "Environment",
    ) -> float:
        score = 0.0

        # 1. Premia celle che aprono nuova visibilità
        info_gain = self._local_information_gain(pos, agent, env)
        score += self.info_weight * info_gain

        # 2. Premia celle non viste di recente
        if pos in agent.seen_cells:
            score -= self.revisit_penalty
        else:
            score += self.stale_weight

        # 3. Premia dispersione rispetto agli altri agenti noti
        score += self.sep_weight * self._separation_term(pos, agent)

        # 4. Piccolo rumore per non diventare deterministico
        score += random.uniform(-0.15, 0.15)

        return score

    def _local_information_gain(
        self,
        target: Tuple[int, int],
        agent: "Agent",
        env: "Environment",
    ) -> int:
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
                if (nr, nc) not in agent.seen_cells:
                    gain += 1

        return gain

    def _separation_term(
        self,
        target: Tuple[int, int],
        agent: "Agent",
    ) -> float:
        other_positions = []

        for _other_id, (pos, _tick) in agent.known_agents.items():
            if pos is None or pos == agent.pos:
                continue
            other_positions.append(pos)

        if not other_positions:
            return 0.0

        min_dist = min(abs(target[0] - r) + abs(target[1] - c) for r, c in other_positions)
        return min_dist / (min_dist + 2.0)