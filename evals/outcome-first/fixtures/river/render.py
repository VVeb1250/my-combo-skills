"""Fixed SVG view of the generated grid. No external dependencies."""
import json
import sys
from pathlib import Path

def render(data, output):
    n = data["size"]
    wet = {tuple(p) for p in data["water"]}
    banks = {(x+dx,y+dy) for x,y in wet for dx,dy in
             ((-1,0),(1,0),(0,-1),(0,1))
             if 0 <= x+dx < n and 0 <= y+dy < n} - wet
    def cells(points, color):
        path = "".join(f"M{x} {y}h1v1h-1z" for x,y in sorted(points))
        return f'<path d="{path}" fill="{color}"/>'
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n} {n}" '
           f'width="768" height="768" shape-rendering="crispEdges">'
           f'<rect width="{n}" height="{n}" fill="#86966e"/>'
           f'<rect width="6" height="{n}" fill="#b9a77d"/>'
           + cells(banks, "#d1bd91") + cells(wet, "#4d91b2") + '</svg>')
    Path(output).write_text(svg, encoding="utf-8")

if __name__ == "__main__":
    render(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")), sys.argv[2])
