# E.L.B.E.R.R. — Swarm Intelligence Warehouse Exploration

**Efficient Logistics by Exploration with Robotic Retrieval**

A real-time multi-agent simulation framework where autonomous agents explore warehouse environments, discover objects, and optimize retrieval through swarm intelligence principles. Built with Python (Streamlit) backend for interactive visualization and benchmarking.

---

## Features

### Exploration Strategies (5 Usable + 1 Prototype)

| Strategy      | Colour    | Approach                                                   |
| ------------- | --------- | ---------------------------------------------------------- |
| Frontier      | Blue      | Frontier-based systematic exploration with target lock     |
| Greedy        | Orange    | Warehouse-centric greedy search                            |
| Sector        | Green     | Grid-partitioning with assigned sectors per agent          |
| Repulsion     | Red       | Emergent dispersion based on inter-agent repulsion         |
| Smart Random  | Purple    | Information-gain guided random walk with stale avoidance   |
| Ant-Colony    | Teal      | Experimental prototype (currently not usable)              |

### Real-time interactive UI

- **Live grid visualization** with Pygame offscreen rendering — fog-of-war, agent vision radius, communication range
- **Three-column layout**: agent configuration | simulation grid | live metrics & battery bars
- **Preset system** — save/load agent configurations as JSON for reproducible runs
- **Battery monitoring** — real-time per-agent energy consumption tracking
- **Run history** — compare multiple simulation runs side-by-side
- **Full-screen benchmarking** — automated batch testing of strategy combinations

### Comprehensive benchmarking

- **Random preset generation** — vary usable strategies, vision radius, communication radius independently
- **Exhaustive or sampled search** — generate unique presets up to the full combinatorial space
- **Multi-run execution** with configurable random seeds
- **Delivery curves** — cumulative object retrieval over time (per preset)
- **CSV export** — download full results for external analysis
- **Top-10 rankings** — filters by tick count, completion rate, energy consumption
- **Ant-Colony excluded** — currently treated as a prototype and not used in benchmark runs

### Configurable environments

- Two provided warehouse instances (`A.json`, `B.json`) with identical structure:
  - Grid size: 25×25 cells
  - 4 warehouses with entrance/exit per warehouse
  - 10 objects to retrieve per instance
- Easy JSON format for custom scenarios

---

## Architecture

```text
├── 📄 README.md                    (this file)
├── 📄 requirements.txt             (Python dependencies)
├── 📄 app.py                       (Streamlit entry point)
├── 🐍 benchmark_strategies.py      (CLI benchmarking script)
│
├── 📁 assets/                      (Images: logo, icons)
│   ├── 2.png
│   ├── agent.png
│   └── package.png
│
├── 📁 ui/                          (Streamlit UI modules)
│   ├── 📄 __init__.py
│   └── (future: component split)
│
├── 📁 src/
│   ├── 📁 agents/
│   │   ├── 🐍 agent.py             (Core Agent class)
│   │   ├── 🐍 sensors.py           (Perception: visibility, communication)
│   │   └── 📁 strategies/
│   │       ├── 🐍 base.py          (Strategy interface)
│   │       ├── 🐍 frontier.py      (Frontier exploration)
│   │       ├── 🐍 greedy.py        (Warehouse-centric greedy)
│   │       ├── 🐍 sector.py        (Sector partitioning)
│   │       ├── 🐍 Repulsion.py     (Emergent repulsion)
│   │       ├── 🐍 random_walk.py   (Info-gain random walk)
│   │       └── 🐍 ant_colony_lite.py (Pheromone-based)
│   │
│   ├── 📁 environment/
│   │   ├── 🐍 environment.py       (Simulator state & logic)
│   │   ├── 🐍 grid.py              (Cell types, grid data)
│   │   └── 🐍 __init__.py
│   │
│   ├── 📁 simulation/
│   │   ├── 🐍 simulator.py         (Tick loop & step generator)
│   │   ├── 🐍 metrics.py           (Statistics collection)
│   │   └── 🐍 __init__.py
│   │
│   ├── 📁 pathfinding/
│   │   ├── 🐍 pathfinder.py        (A* navigation)
│   │   └── 🐍 __init__.py
│   │
│   ├── 📁 communication/
│   │   ├── 🐍 protocol.py          (Inter-agent messaging)
│   │   └── 🐍 __init__.py
│   │
│   ├── 📁 visualization/
│   │   ├── 🐍 base.py              (Abstract visualizer)
│   │   ├── 🐍 matplotlib_viz.py    (Matplotlib rendering)
│   │   ├── 🐍 pygame_viz.py        (Pygame rendering)
│   │   └── 🐍 __init__.py
│   │
│   └── 📄 __init__.py
│
└── 📁 __pycache__/                 (Python cache)
```

---

## Local Development

### Prerequisites

- **Python 3.9+**
- **pip** or **uv** (recommended: `uv` for speed)
- **Streamlit** (installed via `requirements.txt`)

### 1 — Clone and Setup Environment

```bash
git clone <repo-url>
cd Swarm_intelligence_projectWarehouse
python -m venv .venv
```

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
source .venv/bin/activate
```

### 2 — Install Dependencies

```bash
pip install -r requirements.txt
```

Or using `uv` (faster):

```bash
uv sync
```

### 3 — Run the Interactive UI

```bash
streamlit run app.py
```

This launches a web-based dashboard at `http://localhost:8501` where you can:

- Configure agents (strategy, vision radius, communication radius)
- Run single simulations with live visualization
- Save/load presets
- Execute benchmarks with pre-generated configurations
- Download results as CSV

### 4 — Run CLI Benchmarks (Optional)

For headless benchmarking:

```bash
python benchmark_strategies.py \
    --runs 10 \
    --agents 5 \
    --visibility 2 \
    --seed 42 \
    --max-ticks 500 \
    --save-results results.json
```

Use `--help` for all available options.

---

## Configuration & Parameters

### Agent Capabilities

| Parameter              | Min | Max | Default | Notes                                                |
| ---------------------- | --- | --- | ------- | ---------------------------------------------------- |
| **Vision radius**      | 1   | 3   | 2       | Cells visible in Manhattan distance (orthogonal)     |
| **Comm radius**        | 1   | 2   | 2       | Max distance for inter-agent message exchange        |
| **Initial battery**    | —   | —   | 500     | Energy units; −1 per step; agent stops at 0         |
| **Grid size**          | —   | —   | 25×25   | Environment dimensions (fixed per instance)          |
| **Num agents**         | 1   | 10  | 5       | Team size; configurable per run                      |
| **Max ticks**          | 100 | 750 | 500     | Simulation duration limit                            |

### Warehouse Geometry

Both instances (`A.json`, `B.json`) contain:

- **4 warehouses** — rectangular regions marked `WAREHOUSE` (value 2)
- **4 entrances** — one per warehouse, marked `ENTRANCE` (value 3)
- **4 exits** — one per warehouse, marked `EXIT` (value 4)
- **Corridors** — `EMPTY` cells (value 0) connecting warehouses
- **Obstacles** — `WALL` cells (value 1) representing shelves
- **10 objects** — coordinates in separate `objects` array (not grid-embedded)

**Cell type values:**

| Value | Type      | Walkable | Role                         |
| ----- | --------- | -------- | ---------------------------- |
| 0     | EMPTY     | ✓        | Corridor, general space      |
| 1     | WALL      | ✗        | Obstacle, shelf              |
| 2     | WAREHOUSE | ✓        | Interior; delivery target    |
| 3     | ENTRANCE  | ✓        | Gateway into warehouse       |
| 4     | EXIT      | ✓        | Gateway out of warehouse     |

---

## Simulation Flow

1. **Initialization**
   - Load environment from JSON
   - Create N agents with assigned strategies
   - Reset batteries, local maps, object tracking

2. **Per-tick loop** (up to `max_ticks`)
   - Each agent perceives surroundings (vision + communication)
   - Each agent executes strategy logic (navigation, exploration)
   - Local maps (agent knowledge) are updated
   - Metrics are collected (ticks, objects delivered, energy)
   - Stop if all objects are delivered

3. **Metrics & reporting**
   - **Total ticks**: simulation duration
   - **Objects delivered**: count of objects successfully carried to warehouse
   - **Completion rate**: delivered / total objects (0–1)
   - **Average energy consumed**: sum of energy spent / num agents
   - **First pickup tick**: when first object was picked up
   - **First delivery tick**: when first object was delivered

---

## Benchmarking Modes

### Interactive Benchmarking (UI)

Run from the **🔬 Benchmark** tab in Streamlit:

1. Select parametrization mode:
   - **Random**: vary each parameter independently across a range
   - **Fixed**: lock each parameter to a single value

2. Configure ranges:
  - Strategy pool (subset of usable strategies; Ant-Colony excluded)
   - Vision radius range (1–5, or fixed)
   - Communication radius range (1–2, or fixed)

3. Generate presets:
   - Displayed: max unique combinations
   - Input: number of presets to test (sampled or exhaustive)

4. Execute & analyze:
   - Run all presets with progress bar
   - Download CSV with all results
   - View delivery curves (cumulative objects/tick)
   - Rank by efficiency (ticks, energy, completion)

### CLI Benchmarking

```bash
python benchmark_strategies.py \
    --runs 5 \
    --agents 5 \
    --visibility 2 \
    --seed 42 \
    --max-ticks 500
```

Outputs a formatted table with average metrics across runs per strategy.

---

## Exploration Strategies

### Frontier

Explores based on "frontier" cells — boundaries between known and unknown areas. Prioritizes distant frontiers and locks on selected targets to avoid oscillation. Weights frontier distance sub-linearly to prefer nearby exploration while still reaching far areas.

### Greedy

Performs warehouse-centric search: prioritizes cells closest to known warehouse locations, exploring warehouse interiors first. Simpler but may miss distributed objects.

### Sector

Divides the grid into equal sectors and assigns each agent a sector. Agents explore only their assigned area to minimize overlap and ensure uniform coverage.

### Repulsion

Agents repel each other based on proximity, creating emergent separation. No explicit coordination; behavior emerges from local repulsion forces.

### Smart Random

Enhances random walk with:
- **Information gain** — prefers cells that reveal more unknown area
- **Stale avoidance** — deprioritizes recently visited cells
- **Separation** — avoids crowding with nearby agents

### Ant-Colony

**Prototype**: Pheromone-inspired strategy where agents should lay virtual pheromones and bias motion toward low-pheromone cells. This strategy is not fully implemented yet, so it is documented for completeness only. Do not use in production runs or benchmark comparisons.

---

## File Format

### Warehouse Instance (JSON)

```json
{
  "metadata": {
    "grid_size": 25,
    "num_warehouses": 4,
    "num_objects": 10
  },
  "grid": [
    [0, 0, 1, ..., 0],
    [0, 2, 3, ..., 4],
    ...
  ],
  "warehouses": [
    {
      "entrance": [r1, c1],
      "exit": [r2, c2],
      "bounds": [[r_min, c_min], [r_max, c_max]]
    },
    ...
  ],
  "objects": [
    [r1, c1],
    [r2, c2],
    ...
  ]
}
```

### Agent Configuration Preset (JSON)

```json
{
  "name": "preset",
  "num_agents": 5,
  "agents": [
    {
      "agent_id": 0,
      "strategy_id": 0,
      "radius": 2,
      "comm_radius": 2
    },
    ...
  ]
}
```

Save/load presets via the UI or manually create custom configurations.

---

## Performance Tips

- **Reduce max_ticks** for faster iteration during development
- **Use fixed seeds** (same seed across runs) to eliminate variance
- **Lower vision_radius** to constrain agent perception (faster computation)
- **Limit num_agents** for smaller benchmark spaces
- **CSV export** enables post-simulation analysis in Excel/Python

---

## Troubleshooting

| Issue                         | Solution                                           |
| ----------------------------- | -------------------------------------------------- |
| Module import errors          | Ensure `.venv` is activated; `pip install -r requirements.txt` |
| Streamlit port conflict       | Run `streamlit run app.py --server.port 8502`     |
| Pygame offscreen rendering    | Ensure X11/display server available; works headless with `DISPLAY=:99` |
| Large benchmark hangs         | Reduce preset count or lower max_ticks              |
| Preset download fails         | Check browser permissions; try incognito mode      |

---

## Build & Code Quality (Optional)

For all-round polish:

```bash
# Format with Black
black .

# Lint with Ruff
ruff check --fix .

# Run tests (if added)
pytest
```

---

## License

Course project — developed for Multi-Agent Systems curriculum. See individual files for authorship details.

---

## Quick Links

- **Main app**: `app.py`
- **CLI benchmark**: `benchmark_strategies.py`
- **Core source**: `src/`
