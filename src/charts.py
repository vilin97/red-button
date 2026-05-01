"""Generate the 5 charts used in FINDINGS.md.

Reads results/raw.jsonl and results/claude_followup.jsonl. Writes:
  results/chart_press_by_model.png       — main bar chart (existing, refreshed)
  results/chart_strict_vs_normal.png     — side-by-side press counts per model
  results/chart_opus_system_prompt.png   — the headline follow-up finding
  results/chart_press_heatmap.png        — model × (prompt × config) cells
  results/chart_reasoning_vs_press.png   — reasoning tokens vs press rate
"""

import json
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linestyle": "--",
    "axes.titleweight": "bold",
    "axes.titlesize": 13,
    "figure.dpi": 140,
    "savefig.dpi": 160,
    "savefig.bbox": "tight",
})

RESULTS = Path(__file__).parent.parent / "results"
RAW = RESULTS / "raw.jsonl"
FOLLOWUP = RESULTS / "claude_followup.jsonl"

CAT_COLORS = {
    "pressed": "#d62728",
    "other_action": "#f0a04b",
    "no_action": "#3a9b50",
    "error": "#9aa0a6",
}


def load(path):
    return [json.loads(l) for l in open(path) if l.strip()]


# ---------- Chart 1: press rate by model (horizontal stacked) ----------

def chart_press_by_model(rows, out):
    by_model = defaultdict(Counter)
    provider_of = {}
    for r in rows:
        by_model[r["model_name"]][r["category"]] += 1
        provider_of[r["model_name"]] = r["provider"]

    items = sorted(by_model.items(), key=lambda kv: (-kv[1]["pressed"], -kv[1]["other_action"]))
    names = [k for k, _ in items]
    n = len(names)

    cats = ["pressed", "other_action", "no_action", "error"]
    counts = {c: [v[c] for _, v in items] for c in cats}

    fig, ax = plt.subplots(figsize=(11.5, max(4.5, 0.42 * n + 1.2)))
    bottom = np.zeros(n)
    for c in cats:
        ax.barh(names, counts[c], left=bottom, label=c.replace("_", " "), color=CAT_COLORS[c], edgecolor="white", linewidth=0.5)
        bottom += np.array(counts[c])

    # Annotate press counts
    for i, name in enumerate(names):
        p = counts["pressed"][i]
        if p > 0:
            ax.text(p + 0.5, i, f"{p}", va="center", ha="left", fontsize=9, color="#a31818", fontweight="bold")

    ax.set_xlim(0, 41)
    ax.set_xlabel("Calls (out of 40 per model)")
    ax.set_title("How each model responded to “do not press the red button”\n(40 calls = 2 prompts × 2 reasoning configs × 10 runs)", loc="left")
    ax.invert_yaxis()
    ax.legend(loc="lower right", framealpha=0.95, ncol=4, fontsize=9)
    ax.set_axisbelow(True)
    fig.savefig(out)
    plt.close(fig)


# ---------- Chart 2: strict vs normal per model ----------

def chart_strict_vs_normal(rows, out):
    by_model_prompt = defaultdict(lambda: Counter())
    for r in rows:
        by_model_prompt[(r["model_name"], r["prompt"])][r["category"]] += 1

    # Sort by total presses desc; only show models with >=1 press
    presses_by_model = defaultdict(int)
    for (m, p), c in by_model_prompt.items():
        presses_by_model[m] += c["pressed"]

    models = sorted([m for m, p in presses_by_model.items() if p > 0], key=lambda m: -presses_by_model[m])
    if not models:
        return

    normal = [by_model_prompt[(m, "normal")]["pressed"] for m in models]
    strict = [by_model_prompt[(m, "strict")]["pressed"] for m in models]

    x = np.arange(len(models))
    w = 0.38
    fig, ax = plt.subplots(figsize=(10, max(3.5, 0.55 * len(models) + 2)))
    b1 = ax.barh(x - w/2, normal, w, color="#d62728", label="normal prompt")
    b2 = ax.barh(x + w/2, strict, w, color="#666666", label="strict (“IMPORTANT”) prompt")

    for bars, vals in [(b1, normal), (b2, strict)]:
        for bar, v in zip(bars, vals):
            if v > 0:
                ax.text(v + 0.1, bar.get_y() + bar.get_height()/2, str(v), va="center", fontsize=9)

    ax.set_yticks(x)
    ax.set_yticklabels(models)
    ax.invert_yaxis()
    ax.set_xlabel("Presses (out of 20 calls per prompt variant)")
    ax.set_title("Strict prompt eliminates pressing — every model that pressed did so only on the normal prompt", loc="left")
    ax.legend(loc="lower right")
    ax.set_xlim(0, max(max(normal + strict), 1) + 1.5)
    fig.savefig(out)
    plt.close(fig)


# ---------- Chart 3: Opus 4.7 system prompt headline ----------

def chart_opus_system_prompt(followup, out):
    # Aggregate: for Opus 4.7, count presses in each of the 4 cells × 2 prompts
    rows = [r for r in followup if r["model_name"] == "Claude Opus 4.7"]
    cfgs = [
        ("no_sys_no_think", "No system prompt\nNo thinking"),
        ("no_sys_think",    "No system prompt\nThinking on"),
        ("sys_no_think",    "claude.ai sys prompt\nNo thinking"),
        ("sys_think",       "claude.ai sys prompt\nThinking on"),
    ]
    normal = []
    strict = []
    for cfg_id, _ in cfgs:
        n = sum(1 for r in rows if r["config"] == cfg_id and r["prompt"] == "normal" and r["category"] == "pressed")
        s = sum(1 for r in rows if r["config"] == cfg_id and r["prompt"] == "strict" and r["category"] == "pressed")
        normal.append(n)
        strict.append(s)

    x = np.arange(len(cfgs))
    w = 0.4
    fig, ax = plt.subplots(figsize=(11, 5.5))
    b1 = ax.bar(x - w/2, normal, w, color="#d62728", label="normal prompt")
    b2 = ax.bar(x + w/2, strict, w, color="#666666", label="strict prompt")

    for bars, vals in [(b1, normal), (b2, strict)]:
        for bar, v in zip(bars, vals):
            if v > 0:
                ax.text(bar.get_x() + bar.get_width()/2, v + 0.15, str(v), ha="center", fontsize=11, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels([lbl for _, lbl in cfgs])
    ax.set_ylabel("Presses (out of 10 runs per cell)")
    ax.set_ylim(0, 10.5)
    ax.set_title("Claude Opus 4.7 — adding claude.ai’s system prompt drives the press rate from 0/10 to 7/10\n(strict prompt still mostly stops it, even with the system prompt)", loc="left")
    ax.legend(loc="upper left")
    ax.set_axisbelow(True)
    fig.savefig(out)
    plt.close(fig)


# ---------- Chart 4: heatmap of press counts per (model, cell) ----------

def chart_press_heatmap(rows, out):
    cells = [
        ("normal", "default"),
        ("normal", "reasoning_off"),
        ("strict", "default"),
        ("strict", "reasoning_off"),
    ]
    by = defaultdict(Counter)
    for r in rows:
        by[(r["model_name"], r["prompt"], r["config"])][r["category"]] += 1

    presses_by_model = {m: sum(by[(m, p, c)]["pressed"] for p, c in cells) for m, _, _ in by.keys()}
    models = sorted(set(m for (m, _, _) in by.keys()), key=lambda m: -presses_by_model[m])

    matrix = np.zeros((len(models), len(cells)), dtype=int)
    for i, m in enumerate(models):
        for j, (p, c) in enumerate(cells):
            matrix[i, j] = by[(m, p, c)]["pressed"]

    fig, ax = plt.subplots(figsize=(10, max(6, 0.45 * len(models) + 1.2)))
    im = ax.imshow(matrix, cmap="Reds", vmin=0, vmax=max(5, matrix.max()), aspect="auto")
    ax.set_xticks(range(len(cells)))
    ax.set_xticklabels([f"{p}\n{c.replace('_', ' ')}" for p, c in cells], fontsize=10)
    ax.set_yticks(range(len(models)))
    ax.set_yticklabels(models, fontsize=10)
    for i in range(len(models)):
        for j in range(len(cells)):
            v = matrix[i, j]
            ax.text(j, i, str(v), ha="center", va="center", fontsize=10,
                    color="white" if v >= 3 else "#222", fontweight="bold")
    ax.set_title("Where the presses happened — model × (prompt × reasoning config)\n(cell value = presses out of 10 runs)", loc="left")
    cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
    cbar.set_label("Presses / 10")
    ax.grid(False)
    fig.savefig(out)
    plt.close(fig)


# ---------- Chart 5: reasoning tokens vs press rate ----------

def chart_reasoning_vs_press(rows, out):
    by_model = defaultdict(list)
    for r in rows:
        by_model[r["model_name"]].append(r)

    xs, ys, labels, colors = [], [], [], []
    for m, rs in by_model.items():
        non_err = [r for r in rs if r["category"] != "error"]
        if not non_err:
            continue
        press_rate = sum(1 for r in non_err if r["category"] == "pressed") / len(non_err) * 100
        # Default-config reasoning tokens average (a proxy for "thinking spend on this prompt")
        d = [r for r in rs if r["config"] == "default"]
        avg_rt = (sum(r.get("reasoning_tokens", 0) or 0 for r in d) / len(d)) if d else 0
        xs.append(avg_rt)
        ys.append(press_rate)
        labels.append(m)
        colors.append("#d62728" if press_rate > 0 else "#3a9b50")

    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax.scatter(xs, ys, s=80, c=colors, edgecolor="black", linewidth=0.6, alpha=0.85, zorder=3)
    # Resolve label collisions by alternating offsets when two points are very close
    pts = list(zip(xs, ys, labels))
    pts_sorted = sorted(range(len(pts)), key=lambda i: (xs[i], ys[i]))
    used = []
    for i in pts_sorted:
        x, y, lbl = pts[i]
        if not (y > 0 or x > 800):
            continue
        # If a previous point is within (Δlog x < 0.15, Δy < 0.5), shift this label down
        dy_offset = 5
        for ux, uy in used:
            if abs((np.log10(max(x, 1)) - np.log10(max(ux, 1)))) < 0.2 and abs(y - uy) < 0.6:
                dy_offset = -14
                break
        ax.annotate(lbl, (x, y), xytext=(8, dy_offset), textcoords="offset points", fontsize=9)
        used.append((x, y))
    ax.set_xlabel("Avg reasoning tokens per call (default config)")
    ax.set_ylabel("Press rate, % (non-error)")
    ax.set_title("Reasoning effort and press rate are not correlated\n(some heavy thinkers refuse, some non-thinkers press)", loc="left")
    ax.set_axisbelow(True)
    ax.set_xscale("symlog", linthresh=10)
    ax.set_xlim(-5, max(xs) * 1.1 if xs else 1)
    ax.set_ylim(-1, max(ys) * 1.15 + 1 if ys else 1)
    fig.savefig(out)
    plt.close(fig)


def main():
    rows = load(RAW)
    followup = load(FOLLOWUP)
    chart_press_by_model(rows, RESULTS / "chart_press_by_model.png")
    chart_strict_vs_normal(rows, RESULTS / "chart_strict_vs_normal.png")
    chart_opus_system_prompt(followup, RESULTS / "chart_opus_system_prompt.png")
    chart_press_heatmap(rows, RESULTS / "chart_press_heatmap.png")
    chart_reasoning_vs_press(rows, RESULTS / "chart_reasoning_vs_press.png")
    print("Wrote 5 charts to results/.")


if __name__ == "__main__":
    main()
