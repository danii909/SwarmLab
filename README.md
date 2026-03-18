# Sistema Multi-Agente per il Recupero di Oggetti in una Rete di Magazzini

Simulazione swarm intelligence su griglia 25x25 dove 5 agenti autonomi cercano
oggetti e li consegnano ai magazzini.

Assunzione operativa aggiornata:
- la mappa statica e' nota a priori (muri, corridoi, porte, magazzini)
- la posizione degli oggetti resta ignota e viene scoperta via sensori

## Struttura del progetto

```
Progetto_swarm_intelligence/
├── Consegna/                  # Specifiche e istanze originali
│   ├── 20260226-progetto.pdf
│   ├── A.json / B.json        # Istanze dell'ambiente
│   ├── A.png / B.png          # Render delle mappe
│   ├── README.md
│   └── visualize_environment.py
├── src/
│   ├── environment/
│   │   ├── grid.py            # Costanti celle, walkability
│   │   └── environment.py     # Stato dell'ambiente, gestione oggetti
│   ├── agents/
│   │   ├── agent.py           # Classe agente (posizione, batteria, mappa locale)
│   │   ├── sensors.py         # Visibilità, rilevamento, comunicazione
│   │   └── strategies/
│   │       ├── base.py        # Strategia astratta
│   │       ├── random_walk.py # Esplorazione casuale
│   │       ├── frontier.py    # Frontier-based (BFS verso celle inesplorate)
│   │       ├── spiral.py      # Esplorazione sistematica a spirale
│   │       ├── sector.py      # Copertura per settori
│   │       └── greedy.py      # Greedy verso oggetto noto più vicino
│   ├── communication/
│   │   └── protocol.py        # Scambio mappa locale + oggetti tra agenti vicini
│   ├── pathfinding/
│   │   └── pathfinder.py      # BFS / A* per navigazione
│   └── simulation/
│       ├── simulator.py       # Loop principale della simulazione
│       └── metrics.py         # Raccolta e calcolo metriche
├── tests/
│   ├── test_environment.py
│   ├── test_agents.py
│   └── test_simulation.py
├── results/                   # Output JSON e PNG delle simulazioni
├── run_simulation.py          # Entry point
└── requirements.txt
```

## Installazione

```bash
pip install -r requirements.txt
```

## Utilizzo

```bash
# Istanza A, strategia di default, senza visualizzazione
python run_simulation.py --instance Consegna/A.json

# Istanza B, con visualizzazione live
python run_simulation.py --instance Consegna/B.json --visualize

# Imposta seed per riproducibilità
python run_simulation.py --instance Consegna/A.json --seed 42

# Imposta numero massimo di tick
python run_simulation.py --instance Consegna/A.json --max-ticks 750
```

## Parametri agenti

| Parametro | Valore |
|---|---|
| Numero agenti | 5 |
| Posizione iniziale | [0, 0] |
| Batteria iniziale | 500 unità |
| Consumo per mossa | 1 unità |
| Raggio visibilità | 1-3 celle (Manhattan + occlusione) |
| Raggio comunicazione | 1-2 celle |

Le strategie di esplorazione sono ottimizzate per questo scenario:
- obiettivo primario: coprire rapidamente le celle candidate ai pacchi
- fallback: revisita periodica di celle non osservate da tempo (stale)
- coordinamento: scambio via comunicazione di celle gia' scansionate

## Metriche di valutazione

1. Oggetti consegnati correttamente al magazzino
2. Tempo totale (tick)
3. Energia media consumata dagli agenti
