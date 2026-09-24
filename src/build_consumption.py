from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from src.censo_pipeline import (
    BINARY_COLUMNS,
    CANONICAL_COLUMNS,
    GUARATINGUETA,
    canonicalize_types,
    validate_panel,
)
from src.eda import comparable_pool

DEPENDENCY_LABELS = {
    "1": "Federal",
    "2": "Estadual",
    "3": "Municipal",
    "4": "Privada",
}
LOCALIZATION_LABELS = {
    "1": "Urbana",
    "2": "Rural",
}

INDICATOR_META = {
    "IN_AGUA_POTAVEL": ("agua_potavel", "Água potável", "Saneamento"),
    "IN_ENERGIA_REDE_PUBLICA": ("energia_rede_publica", "Energia da rede pública", "Saneamento"),
    "IN_ESGOTO_REDE_PUBLICA": ("esgoto_rede_publica", "Esgoto da rede pública", "Saneamento"),
    "IN_ACESSIBILIDADE_RAMPAS": ("acessibilidade_rampas", "Rampas de acessibilidade", "Acessibilidade"),
    "IN_INTERNET": ("internet", "Internet", "Tecnologia"),
    "IN_BANDA_LARGA": ("banda_larga", "Banda larga", "Tecnologia"),
    "IN_BIBLIOTECA": ("biblioteca", "Biblioteca", "Espaços pedagógicos"),
    "IN_LABORATORIO_INFORMATICA": ("lab_informatica", "Laboratório de informática", "Espaços pedagógicos"),
    "IN_LABORATORIO_CIENCIAS": ("lab_ciencias", "Laboratório de ciências", "Espaços pedagógicos"),
    "IN_QUADRA_ESPORTES": ("quadra_esportes", "Quadra de esportes", "Esporte / convivência"),
    "IN_REFEITORIO": ("refeitorio", "Refeitório", "Alimentação / convivência"),
}

CORE_SCHOOL_COLUMNS = [
    "NU_ANO_CENSO",
    "CO_ENTIDADE",
    "NO_ENTIDADE",
    "CO_MUNICIPIO",
    "NO_MUNICIPIO",
    "TP_DEPENDENCIA",
    "TP_LOCALIZACAO",
    *BINARY_COLUMNS,
    "QT_SALAS_UTILIZADAS",
    "QT_MAT_BAS",
    "QT_MAT_INF",
    "QT_MAT_FUND",
    "QT_MAT_MED",
    "QT_MAT_EJA",
    "QT_MAT_PROF",
]


def load_panel(path: str | Path) -> pd.DataFrame:
    panel = pd.read_csv(path, dtype=str).reindex(columns=CANONICAL_COLUMNS)
    panel = canonicalize_types(panel)
    validate_panel(panel)
    return panel


def school_base_2025(panel: pd.DataFrame) -> pd.DataFrame:
    df = panel[panel["NU_ANO_CENSO"].astype(str) == "2025"].copy()
    df = df[CORE_SCHOOL_COLUMNS]
    df.insert(
        df.columns.get_loc("TP_DEPENDENCIA") + 1,
        "REDE",
        df["TP_DEPENDENCIA"].astype(str).map(DEPENDENCY_LABELS),
    )
    df.insert(
        df.columns.get_loc("TP_LOCALIZACAO") + 1,
        "ZONA",
        df["TP_LOCALIZACAO"].astype(str).map(LOCALIZATION_LABELS),
    )
    return df.sort_values(["NO_MUNICIPIO", "NO_ENTIDADE"]).reset_index(drop=True)


def _aggregate_one(group: pd.DataFrame) -> pd.Series:
    out: dict[str, object] = {
        "N_ESCOLAS": int(group["CO_ENTIDADE"].nunique()),
        "QT_MAT_BAS": group["QT_MAT_BAS"].sum(min_count=1),
        "QT_SALAS_UTILIZADAS": group["QT_SALAS_UTILIZADAS"].sum(min_count=1),
    }
    weights = pd.to_numeric(group["QT_MAT_BAS"], errors="coerce")

    for source, (indicator_id, _, _) in INDICATOR_META.items():
        values = pd.to_numeric(group[source], errors="coerce")
        valid = values.notna()
        out[f"N_VALIDOS_{indicator_id}"] = int(valid.sum())
        out[f"PCT_{indicator_id}"] = float(values[valid].mean()) if valid.any() else np.nan

        weighted_mask = values.notna() & weights.notna()
        denominator = weights[weighted_mask].sum(min_count=1)
        out[f"N_VALIDOS_POND_{indicator_id}"] = int(weighted_mask.sum())
        out[f"PCTPOND_{indicator_id}"] = (
            float((values[weighted_mask] * weights[weighted_mask]).sum() / denominator)
            if pd.notna(denominator) and denominator > 0
            else np.nan
        )

    return pd.Series(out)


def _aggregate_table(df: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for key_values, group in df.groupby(keys, dropna=False, sort=True):
        if not isinstance(key_values, tuple):
            key_values = (key_values,)
        row = dict(zip(keys, key_values))
        row.update(_aggregate_one(group).to_dict())
        rows.append(row)
    return pd.DataFrame(rows)


def municipality_year(panel: pd.DataFrame) -> pd.DataFrame:
    return _aggregate_table(
        panel,
        ["NU_ANO_CENSO", "CO_MUNICIPIO", "NO_MUNICIPIO"],
    )


def municipality_network_2025(panel: pd.DataFrame) -> pd.DataFrame:
    df = panel[panel["NU_ANO_CENSO"].astype(str) == "2025"].copy()
    result = _aggregate_table(
        df,
        ["CO_MUNICIPIO", "NO_MUNICIPIO", "TP_DEPENDENCIA"],
    )
    result.insert(
        3,
        "REDE",
        result["TP_DEPENDENCIA"].astype(str).map(DEPENDENCY_LABELS),
    )
    result["BASE_PEQUENA"] = result["N_ESCOLAS"] < 5
    return result


def municipality_zone_2025(panel: pd.DataFrame) -> pd.DataFrame:
    df = panel[panel["NU_ANO_CENSO"].astype(str) == "2025"].copy()
    result = _aggregate_table(
        df,
        ["CO_MUNICIPIO", "NO_MUNICIPIO", "TP_LOCALIZACAO"],
    )
    result.insert(
        3,
        "ZONA",
        result["TP_LOCALIZACAO"].astype(str).map(LOCALIZATION_LABELS),
    )
    result["BASE_PEQUENA"] = result["N_ESCOLAS"] < 5
    return result


def comparables(panel: pd.DataFrame) -> pd.DataFrame:
    pool = comparable_pool(
        panel,
        target_code=GUARATINGUETA,
        year="2025",
        school_ratio=(0.6, 1.4),
        enrollment_ratio=(0.6, 1.4),
    )
    top = pool.head(10).copy()
    top.insert(0, "ORDEM", range(1, len(top) + 1))
    top.insert(1, "TIPO", "Comparável")

    target = (
        panel[
            (panel["NU_ANO_CENSO"].astype(str) == "2025")
            & (panel["CO_MUNICIPIO"].astype(str) == GUARATINGUETA)
        ]
        .groupby(["CO_MUNICIPIO", "NO_MUNICIPIO"], as_index=False)
        .agg(
            escolas=("CO_ENTIDADE", "nunique"),
            matriculas=("QT_MAT_BAS", lambda s: s.sum(min_count=1)),
        )
    )
    target.insert(0, "ORDEM", 0)
    target.insert(1, "TIPO", "Município-foco")

    for col in top.columns:
        if col not in target.columns:
            target[col] = np.nan
    target = target[top.columns]

    return pd.concat([target, top], ignore_index=True)


def indicator_catalog() -> pd.DataFrame:
    rows = [
        {
            "ID": "n_escolas",
            "INDICADOR": "Escolas ativas",
            "DIMENSAO": "Contexto",
            "VARIAVEL_FONTE": "CO_ENTIDADE",
            "TIPO": "Contagem",
            "REGRA": "COUNT DISTINCT CO_ENTIDADE",
            "TENDENCIA": "Sim",
            "PONDERACAO": "Não",
        },
        {
            "ID": "matriculas",
            "INDICADOR": "Matrículas",
            "DIMENSAO": "Contexto",
            "VARIAVEL_FONTE": "QT_MAT_BAS",
            "TIPO": "Contagem",
            "REGRA": "SUM(QT_MAT_BAS)",
            "TENDENCIA": "Sim",
            "PONDERACAO": "Não",
        },
        {
            "ID": "salas_utilizadas",
            "INDICADOR": "Salas utilizadas",
            "DIMENSAO": "Capacidade física",
            "VARIAVEL_FONTE": "QT_SALAS_UTILIZADAS",
            "TIPO": "Contagem",
            "REGRA": "SUM(QT_SALAS_UTILIZADAS)",
            "TENDENCIA": "Sim",
            "PONDERACAO": "Não",
        },
    ]

    for source, (indicator_id, label, dimension) in INDICATOR_META.items():
        rows.append(
            {
                "ID": indicator_id,
                "INDICADOR": label,
                "DIMENSAO": dimension,
                "VARIAVEL_FONTE": source,
                "TIPO": "Percentual",
                "REGRA": "SUM(valor=1) / COUNT(valor não nulo)",
                "TENDENCIA": "Sim, com cautela" if source == "IN_ACESSIBILIDADE_RAMPAS" else "Sim",
                "PONDERACAO": "Opcional",
            }
        )

    return pd.DataFrame(rows)


def config_table() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["ANO_PADRAO", "2025", "Fotografia principal do MVP"],
            ["MUNICIPIO_FOCO", GUARATINGUETA, "Guaratinguetá"],
            ["PCT_PADRAO", "escolas", "Percentual simples de escolas"],
            ["PCT_SECUNDARIO", "matriculas", "Ponderação opcional por QT_MAT_BAS"],
            ["BASE_PEQUENA_LIMITE", "5", "Sinalizar cortes com menos de 5 escolas"],
            ["COMPARAVEIS_N", "10", "Top 10 do pool estrutural ±40%"],
            ["INDICE_COMPOSTO", "fora_mvp", "Não implementar no MVP"],
            ["ML", "fora_mvp", "Não implementar no MVP"],
        ],
        columns=["CHAVE", "VALOR", "DESCRICAO"],
    )


def build_all(panel: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {
        "ESCOLAS_2025": school_base_2025(panel),
        "MUNICIPIO_ANO": municipality_year(panel),
        "MUNICIPIO_REDE_2025": municipality_network_2025(panel),
        "MUNICIPIO_ZONA_2025": municipality_zone_2025(panel),
        "COMPARAVEIS": comparables(panel),
        "CATALOGO": indicator_catalog(),
        "CONFIG": config_table(),
    }


def save_all(tables: dict[str, pd.DataFrame], output_dir: str | Path) -> None:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    for name, table in tables.items():
        table.to_csv(output / f"{name.lower()}.csv", index=False, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Constrói as tabelas finais de consumo do Web App."
    )
    parser.add_argument("--panel", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    panel = load_panel(args.panel)
    tables = build_all(panel)
    save_all(tables, args.output_dir)

    for name, table in tables.items():
        print(f"{name}: {len(table):,} linhas × {len(table.columns)} colunas")


if __name__ == "__main__":
    main()
