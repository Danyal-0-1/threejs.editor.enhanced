#!/usr/bin/env python3
"""Generate Experiment 01 summary plots from the archived result files.

The script uses only Python's standard library for SVG and CSV output. If
ImageMagick's ``convert`` command is available, it also renders PNG copies.
No raw experiment artifact is modified.
"""

from __future__ import annotations

import csv
import html
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Iterable, Sequence


SUMMARY_DIR = Path(__file__).resolve().parent
EXPERIMENT_DIR = SUMMARY_DIR.parent
RESULTS_DIR = EXPERIMENT_DIR / "results"
FERTILITY_PATH = RESULTS_DIR / "fertility-tokenizers.md"
PROXY_PATH = RESULTS_DIR / "fertility-structural-proxy.md"
COLLISION_DETAIL_PATH = RESULTS_DIR / "collisions-check-g-gamma.txt"

WIDTH = 1280
HEIGHT = 760

COLORS = {
    "ink": "#172033",
    "muted": "#5b6475",
    "grid": "#d9dee8",
    "qwen": "#2563eb",
    "deepseek": "#7c3aed",
    "proxy": "#64748b",
    "alpha": "#d97706",
    "beta": "#2563eb",
    "gamma": "#7c3aed",
    "pass_fill": "#dcfce7",
    "pass_text": "#166534",
    "fail_fill": "#fee2e2",
    "fail_text": "#991b1b",
    "pending_fill": "#e5e7eb",
    "pending_text": "#374151",
    "decision_fill": "#ffedd5",
    "decision_text": "#9a3412",
    "g1": "#dc2626",
    "g2": "#f97316",
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def text_element(
    x: float,
    y: float,
    value: object,
    css_class: str = "body",
    anchor: str = "start",
    extra: str = "",
) -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" class="{css_class}" '
        f'text-anchor="{anchor}" {extra}>{esc(value)}</text>'
    )


def multiline_text(
    x: float,
    y: float,
    lines: Sequence[str],
    css_class: str = "body",
    anchor: str = "middle",
    line_height: int = 18,
) -> str:
    tspans = []
    for index, line in enumerate(lines):
        dy = 0 if index == 0 else line_height
        tspans.append(f'<tspan x="{x:.1f}" dy="{dy}">{esc(line)}</tspan>')
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" class="{css_class}" '
        f'text-anchor="{anchor}">' + "".join(tspans) + "</text>"
    )


def svg_start(title: str, description: str) -> list[str]:
    return [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" '
            f'height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" '
            f'aria-labelledby="plot-title plot-description">'
        ),
        f'<title id="plot-title">{esc(title)}</title>',
        f'<desc id="plot-description">{esc(description)}</desc>',
        """<style>
            text { font-family: 'DejaVu Sans', Arial, sans-serif; fill: #172033; }
            .title { font-size: 30px; font-weight: 700; }
            .subtitle { font-size: 16px; fill: #5b6475; }
            .axis { font-size: 14px; fill: #374151; }
            .axis-label { font-size: 16px; font-weight: 600; fill: #374151; }
            .body { font-size: 15px; }
            .value { font-size: 14px; font-weight: 700; }
            .legend { font-size: 14px; font-weight: 600; }
            .panel-title { font-size: 18px; font-weight: 700; }
            .cell { font-size: 15px; font-weight: 700; }
            .row-label { font-size: 15px; font-weight: 600; }
            .footnote { font-size: 13px; fill: #5b6475; }
        </style>""",
        f'<rect x="0" y="0" width="{WIDTH}" height="{HEIGHT}" fill="white"/>',
    ]


def finish_svg(parts: list[str], target: Path) -> None:
    parts.append("</svg>")
    target.write_text("\n".join(parts) + "\n", encoding="utf-8")


def write_csv(target: Path, header: Sequence[str], rows: Iterable[Sequence[object]]) -> None:
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def load_provenance() -> dict:
    source = FERTILITY_PATH.read_text(encoding="utf-8")
    match = re.search(
        r"### Provenance\s*```json\s*(\{.*?\})\s*```",
        source,
        flags=re.DOTALL,
    )
    if match is None:
        raise RuntimeError(f"No provenance JSON found in {FERTILITY_PATH}")
    return json.loads(match.group(1))


def tokenizer_entries(provenance: dict) -> tuple[list[dict], dict]:
    entries = provenance["tokenizers"]
    qwen = [
        item
        for item in entries
        if item["tokenizer"]["repo"].startswith("Qwen/Qwen2.5-Coder-")
    ]
    deepseek = [
        item for item in entries if item["tokenizer"]["repo"] == "deepseek-ai/DeepSeek-V3"
    ]
    if len(qwen) != 4 or len(deepseek) != 1:
        raise RuntimeError("Expected four Qwen repositories and one DeepSeek repository")

    # The experiment reports these as repeated configurations of one tokenizer.
    for candidate in ("identity", "alpha", "beta", "gamma"):
        reference = qwen[0]["rows"][candidate]
        for item in qwen[1:]:
            if item["rows"][candidate] != reference:
                raise RuntimeError("Qwen repository rows are no longer byte-identical")
    return qwen, deepseek[0]


def relative_metric(entry: dict, candidate: str, metric: str) -> float:
    rows = entry["rows"]
    return rows[candidate][metric] / rows["identity"][metric]


def structural_character_data(provenance: dict) -> tuple[dict[str, int], dict[str, float]]:
    source = PROXY_PATH.read_text(encoding="utf-8")
    line = next(
        (candidate for candidate in source.splitlines() if candidate.startswith("| chars/program |")),
        None,
    )
    if line is None:
        raise RuntimeError(f"No chars/program row found in {PROXY_PATH}")
    cells = [cell.strip() for cell in line.strip("|").split("|")]
    means = dict(zip(("identity", "alpha", "beta", "gamma"), map(float, cells[1:5])))
    programs = provenance["corpus"]["programs_per_lexicon"]["identity"]
    totals = {candidate: round(mean * programs) for candidate, mean in means.items()}
    ratios = {
        candidate: total / totals["identity"] for candidate, total in totals.items()
    }
    for candidate, mean in means.items():
        if abs(totals[candidate] / programs - mean) > 0.00051:
            raise RuntimeError(f"Could not recover exact character total for {candidate}")
    return totals, ratios


def collision_counts() -> dict[str, tuple[int, int]]:
    source = COLLISION_DETAIL_PATH.read_text(encoding="utf-8")
    pattern = re.compile(
        r"^=== (alpha|beta|gamma): \d+ finding\(s\)  \(g1=(\d+), g2=(\d+)\) ===$",
        flags=re.MULTILINE,
    )
    counts = {name: (int(g1), int(g2)) for name, g1, g2 in pattern.findall(source)}
    if counts != {"alpha": (0, 0), "beta": (0, 0), "gamma": (22, 2)}:
        raise RuntimeError(f"Unexpected check-(g) counts: {counts}")
    return counts


def grouped_bar_chart(
    target: Path,
    *,
    title: str,
    subtitle: str,
    categories: Sequence[str],
    series: Sequence[tuple[str, str, Sequence[float]]],
    y_max: float,
    y_ticks: Sequence[float],
    y_label: str,
    footer_lines: Sequence[str],
    value_digits: int = 3,
    acceptance_band: tuple[float, float] | None = None,
    band_label: str | None = None,
) -> None:
    parts = svg_start(title, subtitle)
    parts.append(text_element(55, 44, title, "title"))
    parts.append(text_element(55, 73, subtitle, "subtitle"))

    legend_x = 55
    for name, color, _ in series:
        parts.append(
            f'<rect x="{legend_x}" y="91" width="18" height="18" rx="3" fill="{color}"/>'
        )
        parts.append(text_element(legend_x + 26, 105, name, "legend"))
        legend_x += 26 + max(145, len(name) * 8)

    left, right, top, bottom = 105, 1235, 135, 625
    plot_width = right - left
    plot_height = bottom - top

    def y(value: float) -> float:
        return bottom - (value / y_max) * plot_height

    if acceptance_band is not None:
        low, high = acceptance_band
        band_top, band_bottom = y(high), y(low)
        parts.append(
            f'<rect x="{left}" y="{band_top:.1f}" width="{plot_width}" '
            f'height="{band_bottom - band_top:.1f}" fill="{COLORS["pass_fill"]}"/>'
        )
        parts.append(
            f'<line x1="{left}" y1="{y(high):.1f}" x2="{right}" y2="{y(high):.1f}" '
            f'stroke="{COLORS["pass_text"]}" stroke-width="2" stroke-dasharray="7 5"/>'
        )
        parts.append(
            text_element(
                right - 4,
                y(high) - 7,
                band_label or f"upper limit {high:.2f}",
                "axis",
                "end",
            )
        )

    for tick in y_ticks:
        tick_y = y(tick)
        parts.append(
            f'<line x1="{left}" y1="{tick_y:.1f}" x2="{right}" y2="{tick_y:.1f}" '
            f'stroke="{COLORS["grid"]}" stroke-width="1"/>'
        )
        parts.append(text_element(left - 12, tick_y + 5, f"{tick:g}", "axis", "end"))

    parts.append(
        f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" '
        f'stroke="{COLORS["ink"]}" stroke-width="1.5"/>'
    )
    parts.append(
        text_element(
            0,
            0,
            y_label,
            "axis-label",
            "middle",
            f'transform="translate(30 {(top + bottom) / 2:.1f}) rotate(-90)"',
        )
    )

    group_width = plot_width / len(categories)
    usable_group = group_width * 0.72
    bar_width = min(72.0, usable_group / len(series))
    for category_index, category in enumerate(categories):
        center = left + group_width * (category_index + 0.5)
        total_width = bar_width * len(series)
        start_x = center - total_width / 2
        for series_index, (_, color, values) in enumerate(series):
            value = values[category_index]
            bar_x = start_x + series_index * bar_width + 2
            bar_top = y(value)
            height = bottom - bar_top
            parts.append(
                f'<rect x="{bar_x:.1f}" y="{bar_top:.1f}" width="{bar_width - 4:.1f}" '
                f'height="{height:.1f}" rx="3" fill="{color}"/>'
            )
            parts.append(
                text_element(
                    bar_x + (bar_width - 4) / 2,
                    max(top + 15, bar_top - 8),
                    f"{value:.{value_digits}f}",
                    "value",
                    "middle",
                )
            )
        parts.append(text_element(center, bottom + 28, category, "axis-label", "middle"))

    for index, line in enumerate(footer_lines):
        parts.append(text_element(55, 684 + index * 21, line, "footnote"))
    finish_svg(parts, target)


def two_panel_token_chart(
    target: Path,
    categories: Sequence[str],
    qwen: dict[str, dict[str, float]],
    deepseek: dict[str, dict[str, float]],
) -> None:
    title = "Token cost and byte fallback are different signals"
    subtitle = "β costs many tokens with 0% byte fallback; γ is costly and also triggers byte fallback"
    parts = svg_start(title, subtitle)
    parts.append(text_element(55, 44, title, "title"))
    parts.append(text_element(55, 73, subtitle, "subtitle"))
    parts.append(f'<rect x="55" y="91" width="18" height="18" rx="3" fill="{COLORS["qwen"]}"/>')
    parts.append(text_element(81, 105, "Qwen2 shared tokenizer", "legend"))
    parts.append(f'<rect x="300" y="91" width="18" height="18" rx="3" fill="{COLORS["deepseek"]}"/>')
    parts.append(text_element(326, 105, "DeepSeek-V3 tokenizer", "legend"))

    def panel(
        left: float,
        right: float,
        panel_title: str,
        metric: str,
        y_max: float,
        ticks: Sequence[float],
        digits: int,
    ) -> None:
        top, bottom = 155, 610
        parts.append(text_element((left + right) / 2, 135, panel_title, "panel-title", "middle"))

        def y(value: float) -> float:
            return bottom - (value / y_max) * (bottom - top)

        for tick in ticks:
            tick_y = y(tick)
            parts.append(
                f'<line x1="{left}" y1="{tick_y:.1f}" x2="{right}" y2="{tick_y:.1f}" '
                f'stroke="{COLORS["grid"]}" stroke-width="1"/>'
            )
            parts.append(text_element(left - 9, tick_y + 5, f"{tick:g}", "axis", "end"))
        parts.append(
            f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" '
            f'stroke="{COLORS["ink"]}" stroke-width="1.5"/>'
        )

        group_width = (right - left) / len(categories)
        bar_width = min(48.0, group_width * 0.34)
        for index, category in enumerate(categories):
            center = left + group_width * (index + 0.5)
            for offset, data, color in (
                (-bar_width, qwen, COLORS["qwen"]),
                (0, deepseek, COLORS["deepseek"]),
            ):
                value = data[category][metric]
                bar_x = center + offset
                bar_top = y(value)
                height = max(0, bottom - bar_top)
                if value > 0:
                    parts.append(
                        f'<rect x="{bar_x:.1f}" y="{bar_top:.1f}" width="{bar_width - 3:.1f}" '
                        f'height="{height:.1f}" rx="3" fill="{color}"/>'
                    )
                parts.append(
                    text_element(
                        bar_x + (bar_width - 3) / 2,
                        max(top + 14, bar_top - 7) if value else bottom - 7,
                        f"{value:.{digits}f}",
                        "value",
                        "middle",
                    )
                )
            parts.append(text_element(center, bottom + 27, category, "axis", "middle"))

    panel(75, 610, "Mean tokenizer tokens per program", "tokens/program", 35, range(0, 36, 5), 1)
    panel(715, 1220, "Byte-fallback signal (fragmented %)", "fragmented %", 60, range(0, 61, 10), 1)
    parts.append(
        text_element(
            55,
            690,
            "The fragmented-% metric detects partial-character byte fallback, not ordinary subword splitting.",
            "footnote",
        )
    )
    parts.append(
        text_element(
            55,
            712,
            "Source: results/fertility-tokenizers.md provenance; 62 paired programs; no model forward pass.",
            "footnote",
        )
    )
    finish_svg(parts, target)


def collision_chart(target: Path, counts: dict[str, tuple[int, int]]) -> None:
    title = "γ alone fails the proposed lexical-equivalence diagnostic"
    subtitle = "Check (g) is additional evidence; original collision Constraint 2 checks (a)–(f) passed for all candidates"
    parts = svg_start(title, subtitle)
    parts.append(text_element(55, 44, title, "title"))
    parts.append(text_element(55, 73, subtitle, "subtitle"))
    parts.append(f'<rect x="55" y="91" width="18" height="18" rx="3" fill="{COLORS["g1"]}"/>')
    parts.append(text_element(81, 105, "g1: lexical-class mismatch", "legend"))
    parts.append(f'<rect x="330" y="91" width="18" height="18" rx="3" fill="{COLORS["g2"]}"/>')
    parts.append(text_element(356, 105, "g2: reachability mismatch", "legend"))

    left, right, top, bottom = 110, 1225, 140, 610
    y_max = 26

    def y(value: float) -> float:
        return bottom - value / y_max * (bottom - top)

    for tick in range(0, 26, 5):
        tick_y = y(tick)
        parts.append(
            f'<line x1="{left}" y1="{tick_y:.1f}" x2="{right}" y2="{tick_y:.1f}" '
            f'stroke="{COLORS["grid"]}" stroke-width="1"/>'
        )
        parts.append(text_element(left - 12, tick_y + 5, tick, "axis", "end"))
    parts.append(
        f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" '
        f'stroke="{COLORS["ink"]}" stroke-width="1.5"/>'
    )
    parts.append(
        text_element(
            0,
            0,
            "Number of findings",
            "axis-label",
            "middle",
            f'transform="translate(30 {(top + bottom) / 2:.1f}) rotate(-90)"',
        )
    )

    categories = ("alpha", "beta", "gamma")
    group_width = (right - left) / len(categories)
    bar_width = 150
    for index, category in enumerate(categories):
        center = left + group_width * (index + 0.5)
        g1, g2 = counts[category]
        if g1:
            parts.append(
                f'<rect x="{center - bar_width / 2:.1f}" y="{y(g1):.1f}" '
                f'width="{bar_width}" height="{bottom - y(g1):.1f}" rx="3" fill="{COLORS["g1"]}"/>'
            )
            parts.append(text_element(center, y(g1 / 2) + 5, g1, "cell", "middle", 'fill="white"'))
        if g2:
            parts.append(
                f'<rect x="{center - bar_width / 2:.1f}" y="{y(g1 + g2):.1f}" '
                f'width="{bar_width}" height="{y(g1) - y(g1 + g2):.1f}" rx="3" fill="{COLORS["g2"]}"/>'
            )
            parts.append(text_element(center, y(g1 + g2 / 2) + 5, g2, "cell", "middle"))
        total = g1 + g2
        label_y = y(total) - 10 if total else bottom - 10
        parts.append(text_element(center, label_y, f"total {total}", "value", "middle"))
        parts.append(text_element(center, bottom + 30, category, "axis-label", "middle"))

    parts.append(
        text_element(
            55,
            683,
            "γ: 22 word-class spellings became symbols; 2 adjacent-token cases became reachable only in γ.",
            "footnote",
        )
    )
    parts.append(
        text_element(
            55,
            705,
            "Source: results/collisions-check-g-gamma.txt. This diagnostic was proposed after the original rule.",
            "footnote",
        )
    )
    finish_svg(parts, target)


def decision_matrix(target: Path, worst: dict[str, float], counts: dict[str, tuple[int, int]]) -> None:
    title = "Why Experiment 01 has no eligible winner"
    subtitle = "Specified finite gates passed; every candidate failed binding fertility; ΔNLL was not run"
    parts = svg_start(title, subtitle)
    parts.append(text_element(55, 44, title, "title"))
    parts.append(text_element(55, 73, subtitle, "subtitle"))

    columns = ("alpha", "beta", "gamma")
    rows = [
        (
            ("Specified finite gates", "grammar, corpus and DFA candidate checks"),
            [("PASS", "pass")] * 3,
        ),
        (("Original collision checks", "Constraint 2: checks (a)–(f)"), [("PASS", "pass")] * 3),
        (
            ("Tokenizer fertility", "binding band [0.95, 1.05]"),
            [(f"FAIL {worst[name]:.3f}", "fail") for name in columns],
        ),
        (
            ("Proposed diagnostic (g)", "not original Constraint 2"),
            [
                (
                    f"PASS {sum(counts[name])}" if sum(counts[name]) == 0 else f"FAIL {sum(counts[name])}",
                    "pass" if sum(counts[name]) == 0 else "fail",
                )
                for name in columns
            ],
        ),
        (("Base-model ΔNLL", "primary ranking objective"), [("NOT RUN", "pending")] * 3),
        (("Eligible winner", "final Experiment 01 decision"), [("NO", "decision")] * 3),
    ]

    styles = {
        "pass": (COLORS["pass_fill"], COLORS["pass_text"]),
        "fail": (COLORS["fail_fill"], COLORS["fail_text"]),
        "pending": (COLORS["pending_fill"], COLORS["pending_text"]),
        "decision": (COLORS["decision_fill"], COLORS["decision_text"]),
    }
    label_left = 55
    grid_left = 435
    cell_width = 250
    cell_height = 79
    top = 135

    for index, column in enumerate(columns):
        center = grid_left + cell_width * (index + 0.5)
        parts.append(text_element(center, top - 18, column, "panel-title", "middle"))

    for row_index, (labels, values) in enumerate(rows):
        row_top = top + row_index * cell_height
        label, detail = labels
        parts.append(text_element(label_left, row_top + 30, label, "row-label"))
        parts.append(text_element(label_left, row_top + 53, detail, "footnote"))
        for column_index, (value, style) in enumerate(values):
            fill, color = styles[style]
            x = grid_left + column_index * cell_width + 4
            y = row_top + 4
            parts.append(
                f'<rect x="{x}" y="{y}" width="{cell_width - 8}" height="{cell_height - 8}" '
                f'rx="7" fill="{fill}" stroke="white" stroke-width="2"/>'
            )
            parts.append(
                text_element(
                    x + (cell_width - 8) / 2,
                    y + 43,
                    value,
                    "cell",
                    "middle",
                    f'fill="{color}"',
                )
            )

    parts.append(
        text_element(
            55,
            688,
            "Candidate-specific finite gates passed; repository-wide test suites totaled 149/149.",
            "footnote",
        )
    )
    parts.append(
        text_element(
            55,
            710,
            "Sources: RESULTS.md §§1–3; constraint1-fertility-decision.md; collisions-check-g-gamma.txt.",
            "footnote",
        )
    )
    finish_svg(parts, target)


def render_png(svg_path: Path) -> None:
    executable = shutil.which("convert")
    if executable is None:
        return
    png_path = svg_path.with_suffix(".png")
    completed = subprocess.run(
        [
            executable,
            "-background",
            "white",
            "-density",
            "144",
            str(svg_path),
            "-resize",
            f"{WIDTH}x{HEIGHT}",
            "-strip",
            "-define",
            "png:exclude-chunks=date,time",
            str(png_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        print(f"warning: PNG render failed for {svg_path}: {completed.stderr.strip()}")


def main() -> int:
    provenance = load_provenance()
    qwen_entries, deepseek_entry = tokenizer_entries(provenance)
    qwen_entry = qwen_entries[0]
    candidates = ("alpha", "beta", "gamma")
    all_lexicons = ("identity",) + candidates

    qwen_ratios = {
        candidate: relative_metric(qwen_entry, candidate, "fertility (tok/char)")
        for candidate in candidates
    }
    deepseek_ratios = {
        candidate: relative_metric(deepseek_entry, candidate, "fertility (tok/char)")
        for candidate in candidates
    }
    worst = {
        candidate: max(qwen_ratios[candidate], deepseek_ratios[candidate])
        for candidate in candidates
    }
    character_totals, character_ratios = structural_character_data(provenance)
    counts = collision_counts()

    plot1 = SUMMARY_DIR / "01_constraint1_fertility"
    plot1.mkdir(parents=True, exist_ok=True)
    write_csv(
        plot1 / "data.csv",
        (
            "candidate",
            "qwen_relative_fertility",
            "deepseek_relative_fertility",
            "worst_relative_fertility",
            "pass_min",
            "pass_max",
        ),
        (
            (
                candidate,
                f"{qwen_ratios[candidate]:.12f}",
                f"{deepseek_ratios[candidate]:.12f}",
                f"{worst[candidate]:.12f}",
                "0.95",
                "1.05",
            )
            for candidate in candidates
        ),
    )
    grouped_bar_chart(
        plot1 / "fertility_ratio.svg",
        title="Constraint 1: every candidate exceeds the fertility limit",
        subtitle="Relative token density on the same 62 programs; a candidate had to pass every tokenizer",
        categories=candidates,
        series=(
            ("Qwen2 shared tokenizer (4 repos)", COLORS["qwen"], [qwen_ratios[x] for x in candidates]),
            ("DeepSeek-V3 tokenizer", COLORS["deepseek"], [deepseek_ratios[x] for x in candidates]),
        ),
        y_max=2.5,
        y_ticks=(0, 0.5, 1.0, 1.5, 2.0, 2.5),
        y_label="Relative fertility (alien tok/char ÷ 3DOM tok/char)",
        footer_lines=(
            "Allowed band: 0.95–1.05. Labels use exact provenance ratios rounded to three decimals.",
            "Source: results/fertility-tokenizers.md and results/constraint1-fertility-decision.md.",
        ),
        acceptance_band=(0.95, 1.05),
        band_label="upper limit 1.05",
    )

    plot2 = SUMMARY_DIR / "02_proxy_vs_actual"
    plot2.mkdir(parents=True, exist_ok=True)
    write_csv(
        plot2 / "data.csv",
        (
            "candidate",
            "character_total",
            "identity_character_total",
            "character_length_ratio",
            "qwen_relative_fertility",
            "deepseek_relative_fertility",
        ),
        (
            (
                candidate,
                character_totals[candidate],
                character_totals["identity"],
                f"{character_ratios[candidate]:.12f}",
                f"{qwen_ratios[candidate]:.12f}",
                f"{deepseek_ratios[candidate]:.12f}",
            )
            for candidate in candidates
        ),
    )
    grouped_bar_chart(
        plot2 / "proxy_vs_actual.svg",
        title="Character length did not predict tokenizer cost",
        subtitle="The structural character proxy is compared with the binding tok/char fertility measurement",
        categories=candidates,
        series=(
            ("Character-length ratio (proxy)", COLORS["proxy"], [character_ratios[x] for x in candidates]),
            ("Qwen2 fertility ratio", COLORS["qwen"], [qwen_ratios[x] for x in candidates]),
            ("DeepSeek fertility ratio", COLORS["deepseek"], [deepseek_ratios[x] for x in candidates]),
        ),
        y_max=2.5,
        y_ticks=(0, 0.5, 1.0, 1.5, 2.0, 2.5),
        y_label="Ratio relative to 3DOM",
        footer_lines=(
            "The green band is the fertility gate only; the gray character proxy was not gated against it.",
            "β: 1.000 proxy vs 1.401–1.448 fertility. γ: 0.716 proxy vs 1.937–2.285 fertility.",
        ),
        acceptance_band=(0.95, 1.05),
        band_label="limit 1.05",
    )

    qwen_rows = qwen_entry["rows"]
    deepseek_rows = deepseek_entry["rows"]
    plot3 = SUMMARY_DIR / "03_token_cost_and_fragmentation"
    plot3.mkdir(parents=True, exist_ok=True)
    write_csv(
        plot3 / "data.csv",
        (
            "lexicon",
            "qwen_tokens_per_program",
            "deepseek_tokens_per_program",
            "qwen_fragmented_percent",
            "deepseek_fragmented_percent",
        ),
        (
            (
                candidate,
                f'{qwen_rows[candidate]["tokens/program"]:.12f}',
                f'{deepseek_rows[candidate]["tokens/program"]:.12f}',
                f'{qwen_rows[candidate]["fragmented %"]:.12f}',
                f'{deepseek_rows[candidate]["fragmented %"]:.12f}',
            )
            for candidate in all_lexicons
        ),
    )
    two_panel_token_chart(
        plot3 / "token_cost_and_fragmentation.svg",
        all_lexicons,
        qwen_rows,
        deepseek_rows,
    )

    plot4 = SUMMARY_DIR / "04_gamma_lexical_diagnostic"
    plot4.mkdir(parents=True, exist_ok=True)
    write_csv(
        plot4 / "data.csv",
        ("candidate", "g1_lexical_class_findings", "g2_reachability_findings", "total"),
        (
            (candidate, counts[candidate][0], counts[candidate][1], sum(counts[candidate]))
            for candidate in candidates
        ),
    )
    collision_chart(plot4 / "gamma_lexical_diagnostic.svg", counts)

    plot5 = SUMMARY_DIR / "05_decision_matrix"
    plot5.mkdir(parents=True, exist_ok=True)
    matrix_rows = (
        ("specified_finite_structural_gates", "PASS", "PASS", "PASS"),
        ("original_collision_checks_a_to_f", "PASS", "PASS", "PASS"),
        (
            "binding_fertility_constraint",
            f"FAIL {worst['alpha']:.3f}",
            f"FAIL {worst['beta']:.3f}",
            f"FAIL {worst['gamma']:.3f}",
        ),
        (
            "proposed_diagnostic_g",
            f"PASS {sum(counts['alpha'])}",
            f"PASS {sum(counts['beta'])}",
            f"FAIL {sum(counts['gamma'])}",
        ),
        ("base_model_delta_nll", "NOT RUN", "NOT RUN", "NOT RUN"),
        ("eligible_winner", "NO", "NO", "NO"),
    )
    write_csv(plot5 / "data.csv", ("criterion", "alpha", "beta", "gamma"), matrix_rows)
    decision_matrix(plot5 / "decision_matrix.svg", worst, counts)

    svg_paths = sorted(SUMMARY_DIR.glob("*/**/*.svg"))
    for svg_path in svg_paths:
        render_png(svg_path)
        print(svg_path.relative_to(SUMMARY_DIR))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
