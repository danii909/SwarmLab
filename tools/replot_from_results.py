"""
Script per ricaricare i risultati di un benchmark da ZIP e rigenerare i grafici.

Utilizzo:
    python tools/replot_from_results.py path/to/benchmark_results_YYYYMMDD_HHMMSS.zip [output_dir]

Se output_dir non è specificato, i grafici vengono salvati nella stessa directory dello ZIP.
"""

import json
import sys
import zipfile
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Importa lo stile da ui
try:
    from ui.constants import STRATEGY_COLORS
    from ui.helpers import style_dark_chart
except ImportError:
    # Fallback se il modulo non è disponibile
    STRATEGY_COLORS = {}
    def style_dark_chart(ax):
        ax.set_facecolor("#1a1a2e")
        ax.grid(True, alpha=0.15, color="white")


def load_benchmark_zip(zip_path):
    """Carica i dati da un ZIP di benchmark."""
    with zipfile.ZipFile(zip_path, "r") as z:
        data = {}
        
        # Leggi CSV
        if "summary.csv" in z.namelist():
            data["summary"] = pd.read_csv(z.open("summary.csv"))
        
        # Leggi JSON files
        for json_file in ["results.json", "curves.json", "metadata.json"]:
            if json_file in z.namelist():
                with z.open(json_file) as f:
                    data[json_file[:-5]] = json.load(f)
        
        return data


def replot_benchmark(data, output_dir=None):
    """Ricrea i grafici dai dati caricati."""
    if output_dir is None:
        output_dir = Path.cwd()
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    df = data.get("summary")
    all_results = data.get("results", [])
    curves = data.get("curves", {})
    metadata = data.get("metadata", {})
    
    if df is None or df.empty:
        print("⚠ Dati di summary non trovati nel ZIP.")
        return
    
    print(f"📊 Rigenerazione grafici da {len(df)} preset...")
    
    # Ordina come nell'originale
    df_rank = df.sort_values(
        by=["total_ticks", "delivery_rate", "average_energy"],
        ascending=[True, False, True]
    ).reset_index(drop=True)
    
    bench_max_ticks = int(metadata.get("bench_max_ticks", 500))
    
    # Estrai la strategia dominante per ogni preset (da all_results)
    dominant_strategy = {}
    for result in all_results:
        preset_name = result.get("preset_name", "")
        dom_strat = result.get("dominant_strategy", "Unknown")
        dominant_strategy[preset_name] = dom_strat
    
    # Grafico 1: Tick
    print("  - Generando plot_ticks.png...")
    fig_ticks, ax_ticks = plt.subplots(
        figsize=(min(max(10, len(df_rank) * 0.35), 38), 4.6),
        facecolor="#0e1117"
    )
    style_dark_chart(ax_ticks)
    ax_ticks.bar(
        range(len(df_rank)),
        df_rank["total_ticks"].values,
        color=[STRATEGY_COLORS.get(dominant_strategy.get(pn, "Unknown"), "#888")
               for pn in df_rank["preset_name"]],
        edgecolor="#444",
        linewidth=0.5,
    )
    mean_ticks = float(np.mean(df_rank["total_ticks"].values))
    ax_ticks.axhline(y=mean_ticks, color="#FFD700", linestyle="--", linewidth=1.5,
                    label=f"Media: {mean_ticks:.1f}")
    ax_ticks.set_title("Tick per preset", color="white")
    ax_ticks.set_xlabel("Preset", color="white")
    ax_ticks.set_ylabel("Tick", color="white")
    if len(df_rank) <= 60:
        ax_ticks.set_xticks(range(len(df_rank)))
        ax_ticks.set_xticklabels(df_rank["preset_name"].tolist(), rotation=35, ha="right",
                                color="white", fontsize=7)
    ax_ticks.legend(fontsize=8, facecolor="#1a1a2e", edgecolor="#555", labelcolor="white")
    fig_ticks.tight_layout()
    fig_ticks.savefig(output_dir / "plot_ticks.png", dpi=100, facecolor="#0e1117")
    print(f"    ✓ Salvato in {output_dir / 'plot_ticks.png'}")
    plt.close(fig_ticks)
    
    # Grafico 2: Oggetti
    print("  - Generando plot_objects.png...")
    fig_obj, ax_obj = plt.subplots(
        figsize=(min(max(10, len(df_rank) * 0.35), 38), 4.6),
        facecolor="#0e1117"
    )
    style_dark_chart(ax_obj)
    total_obj = int(df["total_objects"].iloc[0]) if len(df) > 0 else 10
    y_objects = df_rank["objects_delivered"].values
    ax_obj.bar(
        range(len(df_rank)),
        y_objects,
        color=["#55A868" if d >= total_obj else "#DD8452" if d >= total_obj * 0.5 else "#C44E52"
               for d in y_objects],
        edgecolor="#444",
        linewidth=0.5,
    )
    ax_obj.axhline(y=total_obj, color="#FFD700", linestyle=":", linewidth=1.2,
                  label=f"Totale oggetti: {total_obj}")
    ax_obj.set_title("Oggetti consegnati per preset", color="white")
    ax_obj.set_xlabel("Preset", color="white")
    ax_obj.set_ylabel("Oggetti consegnati", color="white")
    if len(df_rank) <= 60:
        ax_obj.set_xticks(range(len(df_rank)))
        ax_obj.set_xticklabels(df_rank["preset_name"].tolist(), rotation=35, ha="right",
                              color="white", fontsize=7)
    ax_obj.legend(fontsize=8, facecolor="#1a1a2e", edgecolor="#555", labelcolor="white")
    fig_obj.tight_layout()
    fig_obj.savefig(output_dir / "plot_objects.png", dpi=100, facecolor="#0e1117")
    print(f"    ✓ Salvato in {output_dir / 'plot_objects.png'}")
    plt.close(fig_obj)
    
    # Grafico 3: Curve cumulative
    print("  - Generando plot_curves.png...")
    fig_curves, ax_curves = plt.subplots(figsize=(10, 5), facecolor="#0e1117")
    style_dark_chart(ax_curves)
    x_ticks = np.arange(1, bench_max_ticks + 1)
    curves_to_show = min(10, len(df_rank))
    preset_names = df_rank.head(curves_to_show)["preset_name"].tolist()
    palette = plt.get_cmap("tab20")
    
    for i, preset_name in enumerate(preset_names):
        curve = curves.get(preset_name)
        if curve is None:
            continue
        curve_arr = np.array(curve, dtype=float)
        if curve_arr.ndim > 1:
            curve_arr = curve_arr[0]
        ax_curves.plot(x_ticks, curve_arr, linewidth=2, color=palette(i % 20),
                      label=preset_name)
    
    ax_curves.set_title("Curve cumulative deliveries (Top 10)", color="white")
    ax_curves.set_xlabel("Tick", color="white")
    ax_curves.set_ylabel("Oggetti consegnati", color="white")
    ax_curves.set_ylim(bottom=0)
    if curves_to_show <= 20:
        ax_curves.legend(fontsize=8, facecolor="#1a1a2e", edgecolor="#555",
                        labelcolor="white")
    fig_curves.tight_layout()
    fig_curves.savefig(output_dir / "plot_curves.png", dpi=100, facecolor="#0e1117")
    print(f"    ✓ Salvato in {output_dir / 'plot_curves.png'}")
    plt.close(fig_curves)
    
    # Salva anche il summary in formato leggibile
    summary_txt = output_dir / "summary.txt"
    with open(summary_txt, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("BENCHMARK RESULTS SUMMARY\n")
        f.write("=" * 70 + "\n\n")
        
        if metadata:
            f.write("METADATA:\n")
            f.write(f"  Generated: {metadata.get('generated_at_iso', 'N/A')}\n")
            f.write(f"  Format Version: {metadata.get('format_version', 'N/A')}\n")
            f.write(f"  Seed: {metadata.get('seed', 'N/A')}\n")
            f.write(f"  Presets Run: {metadata.get('actual_presets_run', 'N/A')}\n")
            f.write(f"  Total Bench Time: {metadata.get('total_bench_time_seconds', 0):.2f}s\n")
            f.write(f"  Max Ticks: {metadata.get('bench_max_ticks', 'N/A')}\n\n")
        
        f.write("TOP 10 PRESETS:\n")
        f.write("-" * 70 + "\n")
        for idx, row in df_rank.head(10).iterrows():
            f.write(f"{idx + 1}. {row['preset_name']}\n")
            f.write(f"   Team: {row['team_desc']}\n")
            f.write(f"   Ticks: {row['total_ticks']:.0f} | Objects: {row['objects_delivered']}/{row['total_objects']} | ")
            f.write(f"Completion: {row['delivery_rate'] * 100:.1f}% | Energy: {row['average_energy']:.1f}\n")
            f.write(f"   Config: {row['config_str']}\n\n")
    
    print(f"    ✓ Salvato summary in {summary_txt}")
    print(f"\n✅ Grafici rigenerati con successo in: {output_dir}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    zip_path = Path(sys.argv[1])
    if not zip_path.exists():
        print(f"❌ File non trovato: {zip_path}")
        sys.exit(1)
    
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else zip_path.parent
    
    print(f"📂 Caricando dati da: {zip_path}")
    data = load_benchmark_zip(zip_path)
    
    print(f"✓ Dati caricati (summary con {len(data.get('summary', []))} preset)")
    replot_benchmark(data, output_dir)


if __name__ == "__main__":
    main()
