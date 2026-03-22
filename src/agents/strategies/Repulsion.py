from src.agents.strategies.base import ExplorationStrategy
from src.environment.grid import CellType
import random
from typing import List, Optional, Set, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from src.agents.agent import Agent
    from src.environment.environment import Environment
    from src.pathfinding.pathfinder import Pathfinder


class RepulsionStrategy(ExplorationStrategy):
    def __init__(self) -> None:
        super().__init__()

    def next_move(self, agent: 'Agent', env: 'Environment', pathfinder: 'Pathfinder', occupied: Set[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        move = self._priority_move(agent, env, pathfinder, occupied)
        if move:
            return move

        known_positions: List[Tuple[int, int]] = [pos for pos, _tick in agent.known_agents.values()]

        targets = self._coverage_targets(agent, env)
        if not targets:
            neighbors = env.grid.walkable_neighbors(agent.row, agent.col)
            free = [n for n in neighbors if n not in occupied]
            return random.choice(free) if free else (random.choice(neighbors) if neighbors else None)

        best = max(targets, key=lambda p: self._score(p, agent, known_positions))
        return pathfinder.next_step(agent.pos, best, occupied - {agent.pos})

    def _score(self, frontier: Tuple[int, int], agent: 'Agent', known_positions: List[Tuple[int, int]]) -> float:
        if known_positions:
            isolation = sum(abs(frontier[0] - p[0]) + abs(frontier[1] - p[1]) for p in known_positions) / len(known_positions)
        else:
            isolation = 0.0

        travel = abs(frontier[0] - agent.row) + abs(frontier[1] - agent.col)
        return isolation - travel
