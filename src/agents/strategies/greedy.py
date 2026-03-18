from src.agents.strategies.base import ExplorationStrategy
from src.environment.grid import CellType
import random
from typing import Optional, Set, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from src.agents.agent import Agent
    from src.environment.environment import Environment
    from src.pathfinding.pathfinder import Pathfinder


class GreedyStrategy(ExplorationStrategy):
    def __init__(self) -> None:
        super().__init__()

    def next_move(self, agent: 'Agent', env: 'Environment', pathfinder: 'Pathfinder', occupied: Set[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        move = self._priority_move(agent, env, pathfinder, occupied)
        if move:
            return move

        nearest_wh = self._nearest_known_warehouse(agent)
        targets = self._coverage_targets(agent, env)

        if targets:
            best = min(targets, key=lambda p: (abs(p[0] - agent.row) + abs(p[1] - agent.col) + (abs(p[0] - nearest_wh[0]) + abs(p[1] - nearest_wh[1]) if nearest_wh else 0) - self._information_gain(p, agent)))
            step = pathfinder.next_step(agent.pos, best, occupied - {agent.pos})
            if step:
                return step

        if agent.known_agents:
            nearest_agent_pos = min((pos for pos, _tick in agent.known_agents.values()), key=lambda p: abs(p[0] - agent.row) + abs(p[1] - agent.col))
            if abs(nearest_agent_pos[0] - agent.row) + abs(nearest_agent_pos[1] - agent.col) > agent.comm_radius:
                step = pathfinder.next_step(agent.pos, nearest_agent_pos, occupied - {agent.pos})
                if step:
                    return step

        neighbors = env.grid.walkable_neighbors(agent.row, agent.col)
        free = [n for n in neighbors if n not in occupied]
        return random.choice(free) if free else (random.choice(neighbors) if neighbors else None)

    def _nearest_known_warehouse(self, agent: 'Agent') -> Optional[Tuple[int, int]]:
        nearest = None
        best_dist = float('inf')
        for (r, c), cell_type in agent.local_map.items():
            if cell_type in (CellType.ENTRANCE, CellType.EXIT, CellType.WAREHOUSE):
                dist = abs(r - agent.row) + abs(c - agent.col)
                if dist < best_dist:
                    best_dist = dist
                    nearest = (r, c)
        return nearest

    def _information_gain(self, target: Tuple[int, int], agent: 'Agent') -> int:
        radius = agent.visibility_radius
        tr, tc = target
        gain = 0
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                if abs(dr) + abs(dc) > radius:
                    continue
                nr, nc = tr + dr, tc + dc
                if (nr, nc) not in agent.seen_cells:
                    gain += 1
        return gain
