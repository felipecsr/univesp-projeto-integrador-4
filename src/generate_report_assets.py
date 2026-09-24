from pathlib import Path

YEARS = [2023, 2024, 2025]
SERIES = {
    "Rampas de acessibilidade": [22.0, 51.6, 68.5],
    "Biblioteca": [28.6, 35.5, 35.9],
    "Laboratório de informática": [46.2, 49.5, 40.2],
    "Laboratório de ciências": [7.7, 10.8, 12.0],
}
DASHES = ["", "6 4", "2 3", "10 4 2 4"]


def esc(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def main():
    width, height = 860, 470
    left, right, top, bottom = 90, 210, 55, 70
    plot_w = width - left - right
    plot_h = height - top - bottom
    y_max = 80.0

    def x(year):
        return left + (year - YEARS[0]) / (YEARS[-1] - YEARS[0]) * plot_w

    def y(value):
        return top + (y_max - value) / y_max * plot_h

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Guaratinguetá — evolução de indicadores selecionados</title>',
        '<desc id="desc">Percentual de escolas com rampas, biblioteca, laboratório de informática e laboratório de ciências entre 2023 e 2025.</desc>',
        '<g font-family="system-ui, sans-serif" font-size="12" fill="currentColor" stroke="currentColor">',
        '<text x="90" y="28" font-size="18" font-weight="700" stroke="none">Guaratinguetá — evolução de indicadores selecionados</text>',
    ]

    for tick in range(0, 81, 20):
        yy = y(tick)
        parts.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{left+plot_w}" y2="{yy:.1f}" stroke-opacity=".18"/>')
        parts.append(f'<text x="{left-12}" y="{yy+4:.1f}" text-anchor="end" stroke="none">{tick}%</text>')

    for year in YEARS:
        xx = x(year)
        parts.append(f'<line x1="{xx:.1f}" y1="{top}" x2="{xx:.1f}" y2="{top+plot_h}" stroke-opacity=".08"/>')
        parts.append(f'<text x="{xx:.1f}" y="{top+plot_h+28}" text-anchor="middle" stroke="none">{year}</text>')

    parts.append(f'<line x1="{left}" y1="{top+plot_h}" x2="{left+plot_w}" y2="{top+plot_h}"/>')
    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top+plot_h}"/>')

    legend_x = left + plot_w + 28
    legend_y = top + 22

    for idx, (label, values) in enumerate(SERIES.items()):
        pts = " ".join(f"{x(year):.1f},{y(value):.1f}" for year, value in zip(YEARS, values))
        dash = f' stroke-dasharray="{DASHES[idx]}"' if DASHES[idx] else ""
        parts.append(f'<polyline points="{pts}" fill="none" stroke-width="2.4"{dash}/>')
        for year, value in zip(YEARS, values):
            xx, yy = x(year), y(value)
            parts.append(f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="4" fill="currentColor" stroke="none"/>')
            parts.append(f'<text x="{xx:.1f}" y="{yy-9:.1f}" text-anchor="middle" font-size="10" stroke="none">{value:.1f}%</text>')
        ly = legend_y + idx * 54
        parts.append(f'<line x1="{legend_x}" y1="{ly}" x2="{legend_x+34}" y2="{ly}" stroke-width="2.4"{dash}/>')
        parts.append(f'<circle cx="{legend_x+17}" cy="{ly}" r="3.5" fill="currentColor" stroke="none"/>')
        parts.append(f'<text x="{legend_x+44}" y="{ly+4}" font-size="11" stroke="none">{esc(label)}</text>')

    parts.append(f'<text x="{left + plot_w/2:.1f}" y="{height-18}" text-anchor="middle" stroke="none">Ano</text>')
    parts.append('</g></svg>')

    out = Path(__file__).resolve().parents[1] / "docs" / "assets" / "guaratingueta_evolucao.svg"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(parts), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
