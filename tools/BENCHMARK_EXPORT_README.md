# Benchmark Results Export & Reload

## Panoramica

Il sistema di benchmark salva **completamente** tutti i dati e i grafici in un unico file ZIP, permettendo di:
- ✅ Ricaricare i dati in futuro
- ✅ Rigenerare grafici e tabelle identici
- ✅ Condividere i risultati del benchmark

## Struttura del ZIP

Ogni file ZIP di benchmark contiene:

```
benchmark_results_YYYYMMDD_HHMMSS.zip
├── summary.csv              # Tabella riassuntiva (colonne standard)
├── results.json             # Dati completi (agent_configs, preset_raw, ecc.)
├── curves.json              # Curve cumulative per ogni preset
├── metadata.json            # Info run (seed, timestamp, bench_config)
├── plot_ticks.png           # Grafico: Tick per preset
├── plot_objects.png         # Grafico: Oggetti consegnati per preset
└── plot_curves.png          # Grafico: Curve cumulative (Top 10)
```

### Descrizione dei file

| File | Descrizione |
|---|---|
| **summary.csv** | CSV riassuntivo (leggibile, ideale per Excel/Pandas) |
| **results.json** | JSON con tutti i dettagli: `agent_configs`, `preset_raw`, `dominant_strategy`, ecc. |
| **curves.json** | Curve di delivery cumulativi per ogni preset (lista di valori per tick) |
| **metadata.json** | Metadata del run: `format_version`, `seed`, `generated_at`, `bench_max_ticks`, `bench_strategy_ids`, ecc. |
| **plot_*.png** | 3 grafici PNG (Tick, Oggetti, Curve) |

## Utilizzo

### 1. Esportare i risultati (in Streamlit)

Dopo un run di benchmark, nella sezione "📊 Risultati benchmark" vedrai:

```
💾 Scarica risultati completi (ZIP con dati, grafici e metadata)
```

Clicca il pulsante per scaricare l'intera archive.

### 2. Ricaricare e rigenerare i grafici

Una volta salvato il ZIP, puoi rigenerare i grafici esattamente come erano nel momento del run:

```bash
cd /path/to/Swarm_intelligence_projectWarehouse

# Rigenerare i grafici nella stessa directory dello ZIP
python tools/replot_from_results.py benchmark_results_20260321_120000.zip

# Oppure specificare una directory di output
python tools/replot_from_results.py benchmark_results_20260321_120000.zip ./output_dir
```

Lo script:
- ✓ Carica i dati dal ZIP
- ✓ Ricrea i 3 grafici (identici all'originale)
- ✓ Salva i grafici come PNG
- ✓ Genera anche un file `summary.txt` leggibile

### 3. Analizzare i dati programmaticamente

Puoi caricare i dati Python senza lo script:

```python
import json
import zipfile
import pandas as pd

zip_path = "benchmark_results_20260321_120000.zip"

with zipfile.ZipFile(zip_path, "r") as z:
    # Leggi il CSV riassuntivo
    df_summary = pd.read_csv(z.open("summary.csv"))
    
    # Leggi i dati completi
    with z.open("results.json") as f:
        all_results = json.load(f)
    
    # Leggi le curve
    with z.open("curves.json") as f:
        curves = json.load(f)
    
    # Leggi il metadata
    with z.open("metadata.json") as f:
        metadata = json.load(f)

# Usa i dati come preferisci
print(f"Presets eseguiti: {len(df_summary)}")
print(f"Seed: {metadata['seed']}")
print(f"Max ticks: {metadata['bench_max_ticks']}")
```

## Formato versione

Il file `metadata.json` contiene `format_version: "1.0"`. Se in futuro il formato cambia, questo numero aumenterà per garantire compatibilità.

Esempio di metadata.json:
```json
{
  "format_version": "1.0",
  "generated_at": 1711008000.123,
  "generated_at_iso": "2025-03-21 12:00:00",
  "seed": 12345,
  "instance_path": "instances/A.json",
  "bench_max_ticks": 500,
  "bench_strategy_ids": [1, 2, 3, 4, 5],
  "vis_values": [1, 2, 3],
  "comm_values": [2],
  "actual_presets_run": 20,
  "total_bench_time_seconds": 15.42
}
```

## Cosa viene salvato

✅ **Salvato nel ZIP:**
- Riassunto (CSV)
- Dati completi (agent_configs, preset_raw per ricostruzione)
- Curve cumulative (per rigenerare esattamente i grafici)
- Metadata (configurazione del run)
- 3 grafici PNG (Tick, Oggetti, Curve)

❌ **Non salvato:**
- History per-tick (sarebbe troppo grande)
- Stdout/stderr della simulazione

## Riproduttibilità

I grafici rigenerati da `replot_from_results.py` sono **identici** agli originali perché:
1. Usano gli stessi dati (curves.json contiene i valori esatti per ogni tick)
2. Usano la stessa configurazione grafica (colori, font, layout)
3. Le curve sono generate nello stesso ordine (Top 10 per delivery rapido)

## Troubleshooting

### "ModuleNotFoundError: No module named 'ui'"
Se il working directory non è nella root del progetto, il file `tools/replot_from_results.py` fallirà. Esegui da:
```bash
cd /path/to/Swarm_intelligence_projectWarehouse
python tools/replot_from_results.py ...
```

### I grafici sono diversi
Controlla che il file ZIP non sia corrotto:
```bash
unzip -t benchmark_results_*.zip
```

---

**Last Updated**: March 2026
