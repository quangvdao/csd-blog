#!/usr/bin/env python3
"""Generate diagrams for the sum-check blog post.

Design concepts:
  Fig 1 (Linear-time): Timeline with shrinking work bars
  Fig 2 (Streaming):   Same data, different weight "lenses" per round
  Fig 3 (Batching):    1D slit vs 2D window over data
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.colors import to_rgba
import numpy as np
import os

# ── Style ─────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 12,
    "axes.linewidth": 0,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
    # Use tight cropping but with padding so it doesn't feel cramped.
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.35,
    "savefig.dpi": 220,
    "text.usetex": False,
    "mathtext.fontset": "cm",
})

# Palette
C_BLUE_4 = "#1E40AF"
C_BLUE_3 = "#2563EB"
C_BLUE_2 = "#60A5FA"
C_BLUE_1 = "#93C5FD"
C_BLUE_0 = "#DBEAFE"

C_TEAL   = "#0D9488"
C_TEAL_L = "#CCFBF1"
C_AMBER  = "#D97706"
C_AMBER_L = "#FEF3C7"
C_ROSE   = "#E11D48"
C_ROSE_L = "#FFE4E6"
C_VIOLET = "#7C3AED"
C_VIOLET_L = "#EDE9FE"
C_GREEN  = "#059669"
C_GREEN_L = "#D1FAE5"

C_DARK   = "#111827"
C_GRAY   = "#6B7280"
C_GRAY_L = "#F3F4F6"
C_GRAY_M = "#D1D5DB"

OUTDIR = os.path.dirname(os.path.abspath(__file__))


# ── Helpers ───────────────────────────────────────────────────────────────

def _rbox(ax, x, y, w, h, fc, ec=None, lw=1.5, zorder=2, radius=0.05):
    """Draw a rounded rectangle and return it."""
    if ec is None:
        ec = fc
    box = FancyBboxPatch((x, y), w, h,
                         boxstyle=f"round,pad={radius}",
                         facecolor=fc, edgecolor=ec, linewidth=lw, zorder=zorder)
    ax.add_patch(box)
    return box


def _arrow(ax, x0, y0, x1, y1, color=C_GRAY, lw=1.5, style="-|>", zorder=3):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw), zorder=zorder)


# ══════════════════════════════════════════════════════════════════════════
#  FIGURE 1 — Linear-time: timeline with shrinking bars
# ══════════════════════════════════════════════════════════════════════════

def fig_linear_time():
    # Slightly taller aspect so the header and labels aren't cramped.
    fig, ax = plt.subplots(figsize=(10.8, 6.0))
    ax.set_xlim(-2.5, 12.5)
    ax.set_ylim(-2.7, 20.2)
    ax.axis("off")

    # (No title/caption; those live in the markdown.)

    # Bars
    n = 4
    work = [16, 8, 4, 2]
    bar_colors = [C_BLUE_1, C_BLUE_2, C_BLUE_3, C_BLUE_4]
    bar_edge   = [C_BLUE_3, C_BLUE_3, C_BLUE_4, C_BLUE_4]
    bar_w = 1.8
    gap = 0.65
    max_h = 14.0
    base_y = 0.5
    scale = max_h / max(work)

    xs = []
    for i in range(4):
        x = i * (bar_w + gap)
        xs.append(x)
        h = work[i] * scale
        _rbox(ax, x, base_y, bar_w, h, bar_colors[i], ec=bar_edge[i], lw=2, radius=0.08)

        # Work label inside bar
        ax.text(x + bar_w / 2, base_y + h / 2 + 0.2,
                f"${work[i]}$", ha="center", va="center",
                fontsize=16, fontweight="bold", color="white" if i >= 2 else C_BLUE_4)
        ax.text(x + bar_w / 2, base_y + h / 2 - 0.7,
                r"compute $s_i$", ha="center", va="center",
                fontsize=9, color="white" if i >= 2 else C_BLUE_3, alpha=0.8)

        # Round label below bar
        ax.text(x + bar_w / 2, base_y - 0.5,
                f"Round {i+1}", ha="center", va="top",
                fontsize=11, fontweight="bold", color=C_DARK)

        # Detail below round label
        ax.text(x + bar_w / 2, base_y - 1.2,
                f"read $2^{{{n-i}}}$ entries",
                ha="center", va="top", fontsize=9, color=C_GRAY)

    # Halving arrows between bars (make them long enough for the label)
    for i in range(3):
        # Extend into adjacent bars so the arrow spans the "bind r_i" label.
        x0 = xs[i] + 0.55 * bar_w
        x1 = xs[i+1] + 0.45 * bar_w
        mid_y = base_y + max(work[i], work[i + 1]) * scale + 0.55
        _arrow(ax, x0, mid_y, x1, mid_y, color=C_AMBER, lw=1.5, style="->")
        ax.text((x0 + x1) / 2, mid_y + 0.28, rf"bind $r_{{{i+1}}}$",
                ha="center", va="bottom", fontsize=9, color=C_AMBER, fontweight="bold")

    # Total work bracket on the right
    bx = xs[-1] + bar_w + 0.5
    total_h = sum(work) * scale
    # vertical line
    ax.plot([bx, bx], [base_y, base_y + work[0] * scale], color=C_DARK, lw=1.5, zorder=4)
    # top tick
    ax.plot([bx - 0.15, bx + 0.15], [base_y + work[0] * scale]*2, color=C_DARK, lw=1.5, zorder=4)
    # bottom tick
    ax.plot([bx - 0.15, bx + 0.15], [base_y]*2, color=C_DARK, lw=1.5, zorder=4)
    # label
    ax.text(bx + 0.35, base_y + work[0] * scale / 2,
            "Total:\n$16{+}8{+}4{+}2$\n$= 30 \\approx 2N$\n$= O(N)$",
            ha="left", va="center", fontsize=10, color=C_DARK,
            linespacing=1.4,
            bbox=dict(boxstyle="round,pad=0.3", fc=C_AMBER_L, ec=C_AMBER, lw=1.2))

    # RAM indicator at bottom
    ram_y = -2.2
    ax.text(-1.5, ram_y + 0.15, "RAM:", ha="right", va="center",
            fontsize=10, fontweight="bold", color=C_ROSE)
    for i in range(4):
        ram_w = bar_w * (work[i] / work[0])
        rx = xs[i] + (bar_w - ram_w) / 2
        _rbox(ax, rx, ram_y - 0.15, ram_w, 0.35, C_ROSE_L, ec=C_ROSE, lw=1.2, radius=0.04)
        ax.text(xs[i] + bar_w / 2, ram_y + 0.55, f"${work[i]}$",
                ha="center", va="center", fontsize=8, color=C_ROSE)

    fig.savefig(os.path.join(OUTDIR, "fig-linear-time.png"))
    plt.close(fig)
    print("  + fig-linear-time.png")


# ══════════════════════════════════════════════════════════════════════════
#  FIGURE 2 — Streaming: same data, different weight lenses
# ══════════════════════════════════════════════════════════════════════════

def fig_streaming():
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.set_xlim(-2.0, 13.0)
    # Less top whitespace now that we removed the title.
    ax.set_ylim(-1.0, 11.4)
    ax.axis("off")
    # (No title/caption; those live in the markdown.)

    N = 8   # 2^3
    n = 3
    cell_w = 1.15
    cell_h = 0.85
    x0 = 0.0  # left edge of cell row

    labels_bin = ["000", "001", "010", "011", "100", "101", "110", "111"]

    # ── Original data row ──
    data_y = 10.0
    ax.text(-1.5, data_y + cell_h / 2, "Data\n(on disk)",
            ha="center", va="center", fontsize=10, fontweight="bold", color=C_DARK,
            linespacing=1.3)
    for j in range(N):
        x = x0 + j * cell_w
        _rbox(ax, x, data_y, cell_w - 0.06, cell_h, C_GRAY_L, ec=C_GRAY_M, lw=1.5, radius=0.04)
        ax.text(x + (cell_w - 0.06) / 2, data_y + cell_h / 2 + 0.12,
                f"$p({labels_bin[j]})$", ha="center", va="center", fontsize=8, color=C_DARK)
        ax.text(x + (cell_w - 0.06) / 2, data_y + cell_h / 2 - 0.18,
                f"$q({labels_bin[j]})$", ha="center", va="center", fontsize=8, color=C_GRAY)

    # Grouping labels for x1
    mid_left = x0 + (4 * cell_w - 0.06) / 2
    mid_right = x0 + 4 * cell_w + (4 * cell_w - 0.06) / 2
    ax.text(mid_left, data_y - 0.25, "$x_1{=}0$",
            ha="center", va="top", fontsize=9, color=C_GRAY)
    ax.text(mid_right, data_y - 0.25, "$x_1{=}1$",
            ha="center", va="top", fontsize=9, color=C_GRAY)

    # ── Weight lens rows ──
    # r1=0.7, r2=0.4
    r1, r2 = 0.7, 0.4

    round_configs = [
        {
            "label": "Round 1",
            "sublabel": "Weights: uniform",
            "weights": [1.0] * 8,
            "groups": [8],                # one group of 8
            "group_labels": [],
            "color": C_TEAL,
            "color_l": C_TEAL_L,
            "result": "$s_1(X)$",
        },
        {
            "label": "Round 2",
            "sublabel": f"Weights via $\\widetilde{{eq}}(r_1, x_1)$",
            "weights": [1 - r1]*4 + [r1]*4,
            "groups": [4, 4],
            "group_labels": ["$1{-}r_1$", "$r_1$"],
            "color": C_VIOLET,
            "color_l": C_VIOLET_L,
            "result": "$s_2(X)$",
        },
        {
            "label": "Round 3",
            "sublabel": f"Weights via $\\widetilde{{eq}}((r_1,r_2),(x_1,x_2))$",
            "weights": [(1-r1)*(1-r2)]*2 + [(1-r1)*r2]*2 + [r1*(1-r2)]*2 + [r1*r2]*2,
            "groups": [2, 2, 2, 2],
            "group_labels": [
                "$(1{-}r_1)(1{-}r_2)$",
                "$(1{-}r_1)r_2$",
                "$r_1(1{-}r_2)$",
                "$r_1 r_2$",
            ],
            "color": C_AMBER,
            "color_l": C_AMBER_L,
            "result": "$s_3(X)$",
        },
    ]

    row_gap = 2.85
    for ri, cfg in enumerate(round_configs):
        y = data_y - (ri + 1) * row_gap
        col = cfg["color"]
        col_l = cfg["color_l"]
        weights = cfg["weights"]
        max_w = max(weights)

        # Row label
        ax.text(-1.5, y + cell_h / 2 + 0.15, cfg["label"],
                ha="center", va="center", fontsize=11, fontweight="bold", color=col)
        ax.text(-1.5, y + cell_h / 2 - 0.2, cfg["sublabel"],
                ha="center", va="center", fontsize=7.5, color=C_GRAY)

        # "Lens" arrows: bottom border of data row → top border of round row.
        # data_y is the bottom edge of the data box (drawn upward with height cell_h).
        # y + cell_h is the top edge of the round row box.
        # Draw arrows behind the boxes (zorder=1) so they don't cover content.
        for j in [0, N - 1]:
            ax_src = x0 + j * cell_w + cell_w / 2
            _arrow(ax, ax_src, data_y, ax_src, y + cell_h + 0.08,
                   color=to_rgba(C_GRAY_M, 0.35), lw=1, style="-|>", zorder=1)
        if ri == 0:
            ax.text(x0 + (N/2) * cell_w, data_y - 0.75, "full read each round",
                    ha="center", va="top", fontsize=8, color=C_GRAY_M, fontstyle="italic")

        # Draw cells with weight-based opacity
        for j in range(N):
            x = x0 + j * cell_w
            alpha = 0.15 + 0.85 * (weights[j] / max_w)
            fc = to_rgba(col, alpha)
            _rbox(ax, x, y, cell_w - 0.06, cell_h, fc, ec=col, lw=1.5, radius=0.04)
            # weight number — white text on dark cells, dark text on light cells
            txt_color = "white" if alpha > 0.55 else C_DARK
            ax.text(x + (cell_w - 0.06) / 2, y + cell_h / 2,
                    f"{weights[j]:.2f}", ha="center", va="center",
                    fontsize=8.5, color=txt_color, fontweight="bold")

        # Group separators and labels
        offset = 0
        for gi, gsz in enumerate(cfg["groups"]):
            gx = x0 + offset * cell_w
            gw = gsz * cell_w - 0.06
            # bracket below cells
            by = y - 0.15
            if len(cfg["group_labels"]) > gi:
                ax.plot([gx + 0.1, gx + gw - 0.1], [by, by], color=col, lw=1.2)
                ax.text(gx + gw / 2, by - 0.15, cfg["group_labels"][gi],
                        ha="center", va="top", fontsize=7.5, color=col)
            offset += gsz

        # Result arrow on right
        # Start the output arrow at the right edge of the bar.
        bar_right = x0 + (N - 1) * cell_w + (cell_w - 0.06)
        rx = bar_right + 0.25
        _arrow(ax, bar_right, y + cell_h / 2, rx + 0.55, y + cell_h / 2,
               color=col, lw=2, style="-|>")
        ax.text(rx + 0.75, y + cell_h / 2, cfg["result"],
                ha="left", va="center", fontsize=12, fontweight="bold", color=col)

    fig.savefig(os.path.join(OUTDIR, "fig-streaming.png"))
    plt.close(fig)
    print("  + fig-streaming.png")


# ══════════════════════════════════════════════════════════════════════════
#  FIGURE 3 — Round batching: 1D slit vs 2D window
# ══════════════════════════════════════════════════════════════════════════

def fig_round_batching():
    fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(12, 6.5))
    # Panels much closer together (halved spacing).
    fig.subplots_adjust(wspace=0.06)
    for ax in (ax_l, ax_r):
        ax.axis("off")
        ax.set_aspect("equal")

    # ── Left panel: round-by-round (1D slit) ─────────────────────────
    ax = ax_l
    ax.set_xlim(-1.5, 7.0)
    ax.set_ylim(-1.5, 9.5)

    # Data block
    dw, dh = 4.5, 1.2
    dx = 0.5
    dy_1 = 7.8
    cell = 0.85
    slit_y = 5.6
    _rbox(ax, dx, dy_1, dw, dh, C_BLUE_0, ec=C_BLUE_3, lw=2, radius=0.06)
    ax.text(dx + dw / 2, dy_1 + dh / 2, "Data  ($N$ entries)",
            ha="center", va="center", fontsize=11, fontweight="bold", color=C_BLUE_3)

    # Pass 1 arrow (bottom of data box → top of slit)
    slit_top = slit_y + cell - 0.06
    _arrow(ax, dx + dw / 2, dy_1, dx + dw / 2, slit_top + 0.05,
           color=C_TEAL, lw=2, style="-|>")
    ax.text(dx + dw / 2 + 0.25, (dy_1 + slit_top) / 2, "Pass 1", ha="left", va="center",
            fontsize=9, color=C_TEAL, fontweight="bold")

    # Slit output: 1x3 strip
    slit_x0 = dx + dw / 2 - 1.5 * cell
    for j, v in enumerate([0, 1, 2]):
        sx = slit_x0 + j * cell
        _rbox(ax, sx, slit_y, cell - 0.06, cell - 0.06,
              C_TEAL_L, ec=C_TEAL, lw=2, radius=0.04)
        ax.text(sx + (cell - 0.06) / 2, slit_y + (cell - 0.06) / 2,
                f"${v}$", ha="center", va="center", fontsize=13,
                fontweight="bold", color=C_TEAL)
    ax.text(slit_x0 + 3 * cell + 0.15, slit_y + (cell - 0.06) / 2,
            "$s_1(X)$", ha="left", va="center", fontsize=11,
            fontweight="bold", color=C_TEAL)
    ax.text(slit_x0 + 1.5 * cell, slit_y - 0.35,
            "3 points  (1D slit)", ha="center", va="top",
            fontsize=9, color=C_GRAY, fontstyle="italic")

    # Bind r1: long vertical arrow from bottom of slit to top of bound-table,
    # with label on the side (like Pass 1 / Pass 2).
    dy_2 = slit_y - 2.6
    dw2 = dw * 0.65
    dx2 = dx + (dw - dw2) / 2
    bind_arrow_top = slit_y
    bind_arrow_bot = dy_2 + dh * 0.9
    _arrow(ax, dx + dw / 2, bind_arrow_top, dx + dw / 2, bind_arrow_bot,
           color=C_AMBER, lw=1.5, style="-|>")
    ax.text(dx + dw / 2 + 0.25, (bind_arrow_top + bind_arrow_bot) / 2,
            "bind $r_1$", ha="left", va="center",
            fontsize=10, color=C_AMBER, fontweight="bold")

    # Pass 2 data block (smaller)
    _rbox(ax, dx2, dy_2, dw2, dh * 0.9, C_BLUE_0, ec=C_BLUE_3, lw=2, radius=0.06)
    ax.text(dx2 + dw2 / 2, dy_2 + dh * 0.9 / 2, "Bound table  ($N/2$)",
            ha="center", va="center", fontsize=10, fontweight="bold", color=C_BLUE_3)

    slit2_y = dy_2 - 1.55
    slit2_top = slit2_y + cell - 0.06
    # Pass 2 arrow (bottom of bound-table → top of slit2)
    _arrow(ax, dx2 + dw2 / 2, dy_2, dx2 + dw2 / 2, slit2_top + 0.05,
           color=C_VIOLET, lw=2, style="-|>")
    ax.text(dx2 + dw2 / 2 + 0.25, (dy_2 + slit2_top) / 2, "Pass 2", ha="left", va="center",
            fontsize=9, color=C_VIOLET, fontweight="bold")

    slit2_x0 = dx + dw / 2 - 1.5 * cell
    for j, v in enumerate([0, 1, 2]):
        sx = slit2_x0 + j * cell
        _rbox(ax, sx, slit2_y, cell - 0.06, cell - 0.06,
              C_VIOLET_L, ec=C_VIOLET, lw=2, radius=0.04)
        ax.text(sx + (cell - 0.06) / 2, slit2_y + (cell - 0.06) / 2,
                f"${v}$", ha="center", va="center", fontsize=13,
                fontweight="bold", color=C_VIOLET)
    ax.text(slit2_x0 + 3 * cell + 0.15, slit2_y + (cell - 0.06) / 2,
            "$s_2(X)$", ha="left", va="center", fontsize=11,
            fontweight="bold", color=C_VIOLET)
    ax.text(slit2_x0 + 1.5 * cell, slit2_y - 0.35,
            "3 points  (1D slit)", ha="center", va="top",
            fontsize=9, color=C_GRAY, fontstyle="italic")

    # Cost box (middle ground spacing)
    ax.text(2.75, slit2_y - 1.4, "2 passes,  6 evaluation points",
            ha="center", va="center", fontsize=10.5, fontweight="bold", color=C_ROSE,
            bbox=dict(boxstyle="round,pad=0.35", fc=C_ROSE_L, ec=C_ROSE, lw=1.5))

    # ── Right panel: round batching (2D window) ──────────────────────
    ax = ax_r
    ax.set_xlim(-1.5, 7.0)
    ax.set_ylim(-1.5, 9.5)

    # Data block
    _rbox(ax, dx, dy_1, dw, dh, C_BLUE_0, ec=C_BLUE_3, lw=2, radius=0.06)
    ax.text(dx + dw / 2, dy_1 + dh / 2, "Data  ($N$ entries)",
            ha="center", va="center", fontsize=11, fontweight="bold", color=C_BLUE_3)

    # Push grid down so column labels (X_2=0,1,2) have room below the arrow.
    grid_y0 = 3.0
    grid_top = grid_y0 + 3 * cell
    # Single pass arrow (bottom of data box → well above grid column labels)
    _arrow(ax, dx + dw / 2, dy_1, dx + dw / 2, grid_top + 0.55,
           color=C_GREEN, lw=2.5, style="-|>")
    ax.text(dx + dw / 2 + 0.25, (dy_1 + grid_top + 0.55) / 2,
            "Single pass", ha="left", va="center",
            fontsize=9, color=C_GREEN, fontweight="bold")

    # 3x3 grid output (2D window)
    grid_x0 = dx + dw / 2 - 1.5 * cell
    for row in range(3):
        for col in range(3):
            gx = grid_x0 + col * cell
            gy = grid_y0 + (2 - row) * cell
            _rbox(ax, gx, gy, cell - 0.06, cell - 0.06,
                  C_GREEN_L, ec=C_GREEN, lw=2, radius=0.04)
            ax.text(gx + (cell - 0.06) / 2, gy + (cell - 0.06) / 2,
                    f"${row},{col}$", ha="center", va="center",
                    fontsize=11, fontweight="bold", color=C_GREEN)

    # Column labels above grid (with extra gap so the arrow doesn't cover them)
    for col, v in enumerate([0, 1, 2]):
        gx = grid_x0 + col * cell + (cell - 0.06) / 2
        ax.text(gx, grid_top + 0.2, "$X_2{=}" + str(v) + "$",
                ha="center", va="bottom", fontsize=8, color=C_GRAY)
    for row, v in enumerate([0, 1, 2]):
        gy = grid_y0 + (2 - row) * cell + (cell - 0.06) / 2
        ax.text(grid_x0 - 0.2, gy, "$X_1{=}" + str(v) + "$",
                ha="right", va="center", fontsize=8, color=C_GRAY)

    ax.text(grid_x0 + 3 * cell + 0.25, grid_y0 + 1.5 * cell,
            "$s(X_1, X_2)$\n2D window\n$3^2 = 9$ points",
            ha="left", va="center", fontsize=10, fontweight="bold",
            color=C_GREEN, linespacing=1.4)

    # Extraction arrows below grid
    ext_y = grid_y0 - 0.55
    ax.text(dx + dw / 2, ext_y,
            "Extract round polynomials cheaply:",
            ha="center", va="center", fontsize=9, color=C_GRAY)

    ext_y2 = ext_y - 0.65
    ax.text(dx + dw / 2, ext_y2,
            r"$s_1(X) = \sum_{x_2 \in \{0,1\}} s(X, x_2)$"
            ",      "
            "$s_2(X) = s(r_1, X)$",
            ha="center", va="center", fontsize=9, color=C_DARK, fontstyle="italic")

    # Cost box (middle ground spacing)
    ax.text(2.75, ext_y2 - 1.0, "1 pass,  9 evaluation points",
            ha="center", va="center", fontsize=10.5, fontweight="bold", color=C_GREEN,
            bbox=dict(boxstyle="round,pad=0.35", fc=C_GREEN_L, ec=C_GREEN, lw=1.5))

    fig.savefig(os.path.join(OUTDIR, "fig-round-batching.png"))
    plt.close(fig)
    print("  + fig-round-batching.png")


# ══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Generating figures...")
    fig_linear_time()
    fig_streaming()
    fig_round_batching()
    print("Done.")
