from __future__ import annotations
from typing import Dict, Tuple, List

Point = Tuple[float,float]

def _svg_circle(x,y,r, label):
    return f'<circle cx="{x}" cy="{y}" r="{r}" />' + \
           f'<text x="{x}" y="{y-10}" font-size="12" text-anchor="middle">{label}</text>'

def _svg_line(a:Point,b:Point, w:float):
    return f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke-width="{max(1.0, w)}" />'

def render_core_svg(
    out_path: str,
    labels: Dict[int,str],
    positions: Dict[int,Point],
    edges: List[Tuple[int,int,float]],
    width: int = 1000,
    height: int = 800,
    padding: int = 60
) -> None:
    xs=[p[0] for p in positions.values()]
    ys=[p[1] for p in positions.values()]
    minx,maxx=min(xs),max(xs)
    miny,maxy=min(ys),max(ys)
    sx=(width-2*padding)/max(1e-9,(maxx-minx))
    sy=(height-2*padding)/max(1e-9,(maxy-miny))
    s=min(sx,sy)

    def map_pt(p:Point)->Point:
        x = padding + (p[0]-minx)*s
        y = padding + (p[1]-miny)*s
        return (x,y)

    mapped={k: map_pt(v) for k,v in positions.items()}

    svg=[]
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">')
    svg.append('<style>circle{fill:white;stroke:black;stroke-width:2} line{stroke:black} text{fill:black;font-family:Arial}</style>')

    for i,j,w in edges:
        svg.append(_svg_line(mapped[i], mapped[j], w))

    for n,(x,y) in mapped.items():
        svg.append(_svg_circle(x,y,16, labels.get(n, str(n))))

    svg.append('</svg>')

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
