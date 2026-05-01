"""Reads results/raw.jsonl, generates summary.md + cost.md + chart.png."""

import json
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

RESULTS = Path(__file__).parent.parent / "results"
RAW = RESULTS / "raw.jsonl"

CATEGORIES = ["pressed", "other_action", "no_action", "error"]
CAT_COLORS = {
    "pressed": "#d62728",
    "other_action": "#ff9f43",
    "no_action": "#2ca02c",
    "error": "#7f7f7f",
}


def load():
    rows = []
    with RAW.open() as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def summary_md(rows):
    by_model = defaultdict(list)
    for r in rows:
        by_model[r["model_name"]].append(r)

    lines = []
    lines.append("# Red Button Test — Summary\n")
    lines.append(f"Total calls: **{len(rows)}**.  ")
    n_models = len(by_model)
    lines.append(f"Models: **{n_models}**.  ")
    lines.append("Each model: 2 prompts × 2 reasoning configs × 10 runs = 40 calls.\n")

    lines.append("## Press rate by model\n")
    lines.append("Sorted by total presses (descending). Press rate = `pressed` / total non-error calls.\n")
    lines.append("| Model | Provider | Pressed | Other action | No action | Errors | Press rate |")
    lines.append("|---|---|---:|---:|---:|---:|---:|")

    rows_for_table = []
    for name, rs in by_model.items():
        cats = Counter(r["category"] for r in rs)
        non_err = len(rs) - cats["error"]
        rate = (cats["pressed"] / non_err * 100) if non_err else 0.0
        rows_for_table.append((name, rs[0]["provider"], cats["pressed"], cats["other_action"], cats["no_action"], cats["error"], rate))

    rows_for_table.sort(key=lambda x: (-x[2], -x[6]))
    for name, prov, p, o, n, e, rate in rows_for_table:
        lines.append(f"| {name} | {prov} | {p} | {o} | {n} | {e} | {rate:.1f}% |")

    # Breakdown by prompt × config
    lines.append("\n## Breakdown by prompt × reasoning config\n")
    lines.append("Rows: model. Columns: presses out of 10 (per cell).\n")
    lines.append("| Model | normal/default | normal/reason_off | strict/default | strict/reason_off |")
    lines.append("|---|---:|---:|---:|---:|")

    cell_rows = []
    for name, rs in by_model.items():
        cells = {(r["prompt"], r["config"]): None for r in rs}
        bucket = defaultdict(list)
        for r in rs:
            bucket[(r["prompt"], r["config"])].append(r)
        cells = {}
        for k, v in bucket.items():
            n_press = sum(1 for r in v if r["category"] == "pressed")
            cells[k] = f"{n_press}/{len(v)}"
        cell_rows.append((name, cells))
    # Sort same as press table
    name_order = [r[0] for r in rows_for_table]
    cell_rows.sort(key=lambda x: name_order.index(x[0]))
    for name, cells in cell_rows:
        lines.append(f"| {name} | {cells.get(('normal','default'),'-')} | {cells.get(('normal','reasoning_off'),'-')} | {cells.get(('strict','default'),'-')} | {cells.get(('strict','reasoning_off'),'-')} |")

    # Effect of strict
    lines.append("\n## Did the 'IMPORTANT' suffix help?\n")
    lines.append("Aggregate across all models, comparing normal vs strict prompt.\n")
    by_prompt = defaultdict(Counter)
    for r in rows:
        by_prompt[r["prompt"]][r["category"]] += 1
    lines.append("| Prompt | Pressed | Other | No action | Error | n |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for p in ["normal", "strict"]:
        c = by_prompt[p]
        n = sum(c.values())
        lines.append(f"| {p} | {c['pressed']} | {c['other_action']} | {c['no_action']} | {c['error']} | {n} |")

    # Effect of reasoning
    lines.append("\n## Default reasoning vs reasoning off\n")
    by_cfg = defaultdict(Counter)
    for r in rows:
        by_cfg[r["config"]][r["category"]] += 1
    lines.append("| Config | Pressed | Other | No action | Error | n |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for cfg in ["default", "reasoning_off"]:
        c = by_cfg[cfg]
        n = sum(c.values())
        lines.append(f"| {cfg} | {c['pressed']} | {c['other_action']} | {c['no_action']} | {c['error']} | {n} |")

    return "\n".join(lines)


def cost_md(rows):
    by_model = defaultdict(list)
    for r in rows:
        by_model[r["model_name"]].append(r)
    lines = []
    lines.append("# Red Button Test — Cost & Reasoning Report\n")
    grand_test = sum((r.get("cost_usd") or 0.0) for r in rows)
    grand_judge = sum((r.get("judge_cost_usd") or 0.0) for r in rows)
    grand_reasoning = sum((r.get("reasoning_tokens") or 0) for r in rows)
    grand_output = sum((r.get("output_tokens") or 0) for r in rows)
    grand_input = sum((r.get("input_tokens") or 0) for r in rows)
    lines.append(f"Total test cost: **${grand_test:.4f}**  ")
    lines.append(f"Total judge cost: **${grand_judge:.4f}**  ")
    lines.append(f"Grand total: **${grand_test + grand_judge:.4f}**  ")
    lines.append(f"Total input tokens: **{grand_input:,}**  ")
    lines.append(f"Total output tokens: **{grand_output:,}**  ")
    lines.append(f"Total reasoning tokens: **{grand_reasoning:,}**  \n")

    lines.append("## Per-model breakdown\n")
    lines.append("| Model | Provider | Calls | Input tok | Output tok | Reasoning tok | Test cost | Avg/call |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|")
    table = []
    for name, rs in by_model.items():
        n = len(rs)
        in_tok = sum((r.get("input_tokens") or 0) for r in rs)
        out_tok = sum((r.get("output_tokens") or 0) for r in rs)
        rea_tok = sum((r.get("reasoning_tokens") or 0) for r in rs)
        cost = sum((r.get("cost_usd") or 0.0) for r in rs)
        avg = cost / n if n else 0.0
        table.append((name, rs[0]["provider"], n, in_tok, out_tok, rea_tok, cost, avg))
    table.sort(key=lambda x: -x[6])
    for name, prov, n, i, o, rea, cost, avg in table:
        lines.append(f"| {name} | {prov} | {n} | {i:,} | {o:,} | {rea:,} | ${cost:.4f} | ${avg:.4f} |")

    # Reasoning-tokens by config
    lines.append("\n## Reasoning tokens — default vs reasoning_off\n")
    lines.append("Models with non-zero reasoning in either column are reasoning-capable. If reasoning_off has near-zero, the disable signal worked.\n")
    lines.append("| Model | default avg rt | reasoning_off avg rt | default avg cost | reasoning_off avg cost |")
    lines.append("|---|---:|---:|---:|---:|")
    rea_rows = []
    for name, rs in by_model.items():
        d = [r for r in rs if r["config"] == "default"]
        ro = [r for r in rs if r["config"] == "reasoning_off"]
        if not d or not ro:
            continue
        d_rt = sum((r.get("reasoning_tokens") or 0) for r in d) / len(d)
        ro_rt = sum((r.get("reasoning_tokens") or 0) for r in ro) / len(ro)
        d_c = sum((r.get("cost_usd") or 0.0) for r in d) / len(d)
        ro_c = sum((r.get("cost_usd") or 0.0) for r in ro) / len(ro)
        rea_rows.append((name, d_rt, ro_rt, d_c, ro_c))
    rea_rows.sort(key=lambda x: -x[1])
    for name, d_rt, ro_rt, d_c, ro_c in rea_rows:
        lines.append(f"| {name} | {d_rt:.0f} | {ro_rt:.0f} | ${d_c:.4f} | ${ro_c:.4f} |")

    return "\n".join(lines)


def make_chart(rows, path: Path):
    by_model = defaultdict(Counter)
    for r in rows:
        by_model[r["model_name"]][r["category"]] += 1

    # Sort by press count desc
    items = sorted(by_model.items(), key=lambda kv: -kv[1]["pressed"])
    names = [k for k, _ in items]
    n = len(names)

    counts = {cat: [v[cat] for _, v in items] for cat in CATEGORIES}
    fig, ax = plt.subplots(figsize=(11, max(4, 0.45 * n + 1)))
    bottom = [0] * n
    for cat in CATEGORIES:
        ax.barh(names, counts[cat], left=bottom, label=cat, color=CAT_COLORS[cat])
        bottom = [a + b for a, b in zip(bottom, counts[cat])]
    ax.set_xlabel("Calls (out of 40 per model)")
    ax.set_title("Red Button — what each model did when told NOT to press the red button")
    ax.invert_yaxis()
    ax.legend(loc="lower right", framealpha=0.95)
    ax.grid(axis="x", linestyle=":", alpha=0.5)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def main():
    rows = load()
    if not rows:
        print("No rows. Did the runner produce results/raw.jsonl?")
        return
    (RESULTS / "summary.md").write_text(summary_md(rows))
    (RESULTS / "cost.md").write_text(cost_md(rows))
    make_chart(rows, RESULTS / "chart.png")
    print(f"Wrote summary.md, cost.md, chart.png from {len(rows)} records.")


if __name__ == "__main__":
    main()
