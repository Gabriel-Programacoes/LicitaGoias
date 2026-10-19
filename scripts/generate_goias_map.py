"""Build the login illustration from the official local municipal GeoJSON."""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "public" / "geojson" / "geojs-52-mun.json"
OUTPUT = ROOT / "src" / "licitagoias" / "api" / "static" / "goias-map.svg"
MUNICIPALITIES_OUTPUT = ROOT / "src" / "licitagoias" / "api" / "static" / "municipalities-go.json"
SIZE = 240
PADDING = 14


def polygon_rings(geometry: dict) -> list[list[list[float]]]:
    if geometry["type"] == "Polygon":
        return geometry["coordinates"]
    if geometry["type"] == "MultiPolygon":
        return [ring for polygon in geometry["coordinates"] for ring in polygon]
    return []


def simplify(points: list[tuple[float, float]], tolerance: float) -> list[tuple[float, float]]:
    """Ramer-Douglas-Peucker simplification without third-party packages."""
    if len(points) <= 3:
        return points
    keep = {0, len(points) - 1}
    stack = [(0, len(points) - 1)]
    while stack:
        start, end = stack.pop()
        ax, ay = points[start]
        bx, by = points[end]
        dx, dy = bx - ax, by - ay
        length_sq = dx * dx + dy * dy
        farthest, max_distance = -1, tolerance
        for index in range(start + 1, end):
            px, py = points[index]
            if length_sq:
                ratio = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / length_sq))
                distance = math.hypot(px - (ax + ratio * dx), py - (ay + ratio * dy))
            else:
                distance = math.hypot(px - ax, py - ay)
            if distance > max_distance:
                farthest, max_distance = index, distance
        if farthest >= 0:
            keep.add(farthest)
            stack.extend(((start, farthest), (farthest, end)))
    return [point for index, point in enumerate(points) if index in keep]


def loops_from_geojson(data: dict) -> list[list[tuple[float, float]]]:
    edge_counts: Counter[tuple[tuple[float, float], tuple[float, float]]] = Counter()
    for feature in data["features"]:
        for ring in polygon_rings(feature["geometry"]):
            for first, second in zip(ring, ring[1:]):
                a = (round(first[0], 9), round(first[1], 9))
                b = (round(second[0], 9), round(second[1], 9))
                edge_counts[tuple(sorted((a, b)))] += 1

    boundary_edges = {edge for edge, count in edge_counts.items() if count == 1}
    adjacency: dict[tuple[float, float], set[tuple[float, float]]] = defaultdict(set)
    for a, b in boundary_edges:
        adjacency[a].add(b)
        adjacency[b].add(a)
    if any(len(neighbors) != 2 for neighbors in adjacency.values()):
        raise ValueError("O GeoJSON não formou anéis de contorno fechados.")

    loops = []
    while boundary_edges:
        start = next(iter(boundary_edges))[0]
        previous = None
        current = start
        loop = [start]
        while True:
            following = next(point for point in adjacency[current] if point != previous)
            edge = tuple(sorted((current, following)))
            if edge not in boundary_edges:
                break
            boundary_edges.remove(edge)
            previous, current = current, following
            if current == start:
                break
            loop.append(current)
        if current != start:
            raise ValueError("O GeoJSON contém um contorno aberto.")
        loops.append(loop)
    return loops


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    municipalities = [
        {"id": str(feature["properties"]["id"]), "name": feature["properties"]["name"]}
        for feature in data["features"]
    ]
    municipalities.sort(key=lambda item: item["name"].casefold())
    MUNICIPALITIES_OUTPUT.write_text(
        json.dumps(municipalities, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    loops = loops_from_geojson(data)
    # The largest exterior loop represents the state; smaller loops are holes/islands.
    outline = max(loops, key=len)
    center_lat = sum(lat for _, lat in outline) / len(outline)
    longitude_scale = math.cos(math.radians(center_lat))
    projected = [(lon * longitude_scale, lat) for lon, lat in outline]
    min_x = min(x for x, _ in projected)
    max_x = max(x for x, _ in projected)
    min_y = min(y for _, y in projected)
    max_y = max(y for _, y in projected)
    scale = (SIZE - 2 * PADDING) / max(max_x - min_x, max_y - min_y)
    offset_x = (SIZE - (max_x - min_x) * scale) / 2
    offset_y = (SIZE - (max_y - min_y) * scale) / 2

    def to_svg(lon: float, lat: float) -> tuple[float, float]:
        x = lon * longitude_scale
        return offset_x + (x - min_x) * scale, offset_y + (max_y - lat) * scale

    simple = simplify(projected, tolerance=0.008)
    path_points = []
    for x, y in simple:
        path_points.append((offset_x + (x - min_x) * scale, offset_y + (max_y - y) * scale))
    commands = " ".join(
        ("M" if index == 0 else "L") + f"{x:.2f},{y:.2f}"
        for index, (x, y) in enumerate(path_points)
    ) + " Z"
    goiania_x, goiania_y = to_svg(-49.253, -16.686)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}" role="img" aria-labelledby="title desc">
  <title id="title">Estado de Goiás</title>
  <desc id="desc">Contorno derivado dos polígonos municipais do GeoJSON local, com marcador aproximado de Goiânia.</desc>
  <path d="{commands}" fill="#2e8b57" fill-opacity=".045" stroke="#2e8b57" stroke-opacity=".48" stroke-width="1.25" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>
  <circle cx="{goiania_x:.2f}" cy="{goiania_y:.2f}" r="7" fill="none" stroke="#2e8b57" stroke-opacity=".3" stroke-width="1"/>
  <circle cx="{goiania_x:.2f}" cy="{goiania_y:.2f}" r="3" fill="#2e8b57" stroke="#fff" stroke-width="1"/>
  <text x="{goiania_x + 9:.2f}" y="{goiania_y + 2.5:.2f}" fill="#1a1a1a" font-family="ui-monospace,monospace" font-size="6" letter-spacing=".4">GOIÂNIA</text>
</svg>
'''
    OUTPUT.write_text(svg, encoding="utf-8")
    print(f"Gerado {OUTPUT.relative_to(ROOT)} ({len(path_points)} pontos simplificados)")
    print(f"Gerado {MUNICIPALITIES_OUTPUT.relative_to(ROOT)} ({len(municipalities)} municípios)")


if __name__ == "__main__":
    main()
