"""
apps/obsidia_api/os_adapters/svg.py — P65 readonly adapter.

Adapted from engine/os3/svg.py (SAFE_READONLY_ADAPTER_CANDIDATE P62).
DRY_RUN_ONLY = True — returns SVG string, never writes to disk.
Original write-to-file behaviour is disabled.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

DRY_RUN_ONLY: bool = True

Point = Tuple[float, float]

_BOUNDARY = {
    "readonly": True,
    "dry_run_only": True,
    "emits_act": False,
    "memory_write": False,
    "graphiti_write": False,
    "neo4j_write": False,
    "kernel_mutation": False,
    "decision_authority": "KX108_ONLY",
}


def _svg_circle(x: float, y: float, r: float, label: str) -> str:
    return (
        f'<circle cx="{x}" cy="{y}" r="{r}" />'
        f'<text x="{x}" y="{y - 10}" font-size="12" text-anchor="middle">{label}</text>'
    )


def _svg_line(a: Point, b: Point, w: float) -> str:
    return (
        f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" '
        f'stroke-width="{max(1.0, w)}" />'
    )


def render_core_svg(
    labels: Dict[int, str],
    positions: Dict[int, Point],
    edges: List[Tuple[int, int, float]],
    width: int = 1000,
    height: int = 800,
    padding: int = 60,
    out_path: str = "",
) -> str:
    """Render a core graph as SVG and return the SVG string (DRY_RUN_ONLY).

    In DRY_RUN_ONLY mode, the SVG is never written to disk regardless of out_path.
    Returns the SVG markup string.
    """
    if not DRY_RUN_ONLY:
        raise ValueError("DRY_RUN_ONLY mode is active — file writes are permanently disabled")

    xs = [p[0] for p in positions.values()] or [0.0]
    ys = [p[1] for p in positions.values()] or [0.0]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    sx = (width - 2 * padding) / max(1e-9, maxx - minx)
    sy = (height - 2 * padding) / max(1e-9, maxy - miny)
    s = min(sx, sy)

    def map_pt(p: Point) -> Point:
        return (padding + (p[0] - minx) * s, padding + (p[1] - miny) * s)

    mapped = {k: map_pt(v) for k, v in positions.items()}

    svg: List[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        "<style>circle{fill:white;stroke:black;stroke-width:2} "
        "line{stroke:black} text{fill:black;font-family:Arial}</style>",
    ]
    for i, j, w in edges:
        svg.append(_svg_line(mapped[i], mapped[j], w))
    for n, (x, y) in mapped.items():
        svg.append(_svg_circle(x, y, 16, labels.get(n, str(n))))
    svg.append("</svg>")
    return "\n".join(svg)
