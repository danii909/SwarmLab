from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Optional, Set, Tuple, TYPE_CHECKING

from src.environment.grid import CellType, DIRECTIONS

if TYPE_CHECKING:
    from src.agents.agent import Agent
    from src.environment.environment import Environment
    from src.pathfinding.pathfinder import Pathfinder


class ExplorationStrategy(ABC):
    """
    Ogni strategia implementa `next_move`, che restituisce la prossima
    cella (row, col) verso cui l'agente deve muoversi, oppure None se
    l'agente deve restare fermo per questo tick.

    La strategia può usare:
      - agent.local_map     — celle esplorate finora dall'agente
      - agent.known_objects — oggetti noti non ancora raccolti
      - agent.known_agents  — posizioni note di altri agenti
      - agent.pos           — posizione corrente
      - agent.carrying_object
      - env.grid            — mappa globale (solo per walkability)
      - pathfinder          — per calcolare percorsi
      - occupied            — posizioni occupate da altri agenti (anti-collisione)
    """

    def __init__(self) -> None:
        # Cache frontiere: {agent_id: (frontier_set, map_size_al_calcolo)}
        self._frontier_cache: Dict[int, Tuple[Set, int]] = {}

    @abstractmethod
    def next_move(
        self,
        agent: "Agent",
        env: "Environment",
        pathfinder: "Pathfinder",
        occupied: Set[Tuple[int, int]],
    ) -> Optional[Tuple[int, int]]:
        """Restituisce la prossima cella verso cui spostarsi, oppure None."""
        ...

    # ------------------------------------------------------------------
    # Metodi condivisi tra le strategie
    # ------------------------------------------------------------------

    def _priority_move(
        self,
        agent: "Agent",
        env: "Environment",
        pathfinder: "Pathfinder",
        occupied: Set[Tuple[int, int]],
    ) -> Optional[Tuple[int, int]]:
        """
        Priorità universale applicata da tutte le strategie:
          1. Se l'agente trasporta un oggetto → vai all'ingresso più vicino.
          2. Se conosce oggetti → vai al più vicino.
        Restituisce None se nessuna delle due condizioni è attiva,
        delegando alla logica di esplorazione specifica.
        """
        if agent.carrying_object:
            target = env.nearest_warehouse_entrance(*agent.pos)
            if target:
                step = pathfinder.next_step(agent.pos, target, occupied - {agent.pos})
                if step:
                    return step

        if agent.known_objects:
            nearest = min(
                agent.known_objects,
                key=lambda p: abs(p[0] - agent.row) + abs(p[1] - agent.col),
            )
            step = pathfinder.next_step(agent.pos, nearest, occupied - {agent.pos})
            if step:
                return step

        return None

    def _find_frontiers(
        self,
        agent: "Agent",
        env: "Environment",
    ) -> Set[Tuple[int, int]]:
        """
        Celle EMPTY già esplorate nella mappa locale che hanno almeno
        un vicino non ancora esplorato. Cached per agent_id finché
        local_map non cresce (ricalcolo solo quando si esplora).
        """
        map_size = len(agent.local_map)
        cached = self._frontier_cache.get(agent.id)
        if cached is not None and cached[1] == map_size:
            return cached[0]

        frontiers: Set[Tuple[int, int]] = set()
        local_map = agent.local_map
        in_bounds = env.grid.in_bounds
        for (r, c), cell_type in local_map.items():
            if cell_type != CellType.EMPTY:
                continue
            for dr, dc in DIRECTIONS:
                nr, nc = r + dr, c + dc
                if (nr, nc) not in local_map and in_bounds(nr, nc):
                    frontiers.add((r, c))
                    break

        self._frontier_cache[agent.id] = (frontiers, map_size)
        return frontiers

    def _unexplored_empty(
        self,
        agent: "Agent",
        env: "Environment",
    ) -> Set[Tuple[int, int]]:
        """
        Compat helper: restituisce le frontiere locali non ancora coperte.

        Nota: non usa conoscenza globale della mappa per evitare leakage
        informativo fuori dal raggio di visione/comunicazione.
        """
        return self._find_frontiers(agent, env)

    @property
    def name(self) -> str:
        return self.__class__.__name__
