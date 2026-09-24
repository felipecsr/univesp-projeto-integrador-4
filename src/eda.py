from __future__ import annotations

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

INFRA_DIMENSIONS = {
    "IN_AGUA_POTAVEL": "Saneamento",
    "IN_ENERGIA_REDE_PUBLICA": "Saneamento",
    "IN_ESGOTO_REDE_PUBLICA": "Saneamento",
    "IN_ACESSIBILIDADE_RAMPAS": "Acessibilidade",
    "IN_INTERNET": "Tecnologia",
    "IN_BANDA_LARGA": "Tecnologia",
    "IN_LABORATORIO_INFORMATICA": "Tecnologia",
    "IN_BIBLIOTECA": "Espaços pedagógicos",
    "IN_LABORATORIO_CIENCIAS": "Espaços pedagógicos",
    "IN_QUADRA_ESPORTES": "Esporte / convivência",
    "IN_REFEITORIO": "Alimentação / convivência",
}


def latest_execution_dir(base_analitica: str | Path) -> Path:
    base_analitica = Path(base_analitica)
    candidates = sorted(
        path
        for path in base_analitica.glob("execucao_colab_*")
        if path.is_dir()
    )
    if not candidates:
        raise FileNotFoundError(
            "Nenhuma execução humana do Colab encontrada em base_analitica. "
            "Conclua a pendência P03M antes de executar a análise oficial."
        )
    return candidates[-1]


def load_materialized_panel(execution_dir: str | Path) -> pd.DataFrame:
    execution_dir = Path(execution_dir)
    path = execution_dir / "censo_escolar_sp_escola_ano_2023_2025.csv.gz"
    if not path.exists():
        raise FileNotFoundError(f"Painel materializado não encontrado: {path}")

    panel = pd.read_csv(path, dtype=str).reindex(columns=CANONICAL_COLUMNS)
    panel = canonicalize_types(panel)
    validate_panel(panel)
    return panel


def _municipality(panel: pd.DataFrame, code: str = GUARATINGUETA) -> pd.DataFrame:
    subset = panel[panel["CO_MUNICIPIO"].astype(str) == str(code)].copy()
    if subset.empty:
        raise ValueError(f"Município {code} não encontrado no painel.")
    return subset


def guaratingueta_overview(
    panel: pd.DataFrame,
    municipality_code: str = GUARATINGUETA,
) -> pd.DataFrame:
    df = _municipality(panel, municipality_code)
    rows: list[dict[str, object]] = []

    for year, group in df.groupby("NU_ANO_CENSO", sort=True):
        enrollment = pd.to_numeric(group["QT_MAT_BAS"], errors="coerce")
        rooms = pd.to_numeric(group["QT_SALAS_UTILIZADAS"], errors="coerce")
        rows.append(
            {
                "ano": str(year),
                "escolas_ativas": int(group["CO_ENTIDADE"].nunique()),
                "escolas_sem_matricula": int(enrollment.isna().sum()),
                "matriculas": (
                    int(enrollment.sum(min_count=1))
                    if enrollment.notna().any()
                    else pd.NA
                ),
                "mediana_matriculas_escola": (
                    float(enrollment.median())
                    if enrollment.notna().any()
                    else pd.NA
                ),
                "salas_utilizadas": (
                    int(rooms.sum(min_count=1))
                    if rooms.notna().any()
                    else pd.NA
                ),
            }
        )

    return pd.DataFrame(rows)


def infrastructure_by_year(
    panel: pd.DataFrame,
    municipality_code: str = GUARATINGUETA,
) -> pd.DataFrame:
    df = _municipality(panel, municipality_code)
    rows: list[dict[str, object]] = []

    for year, group in df.groupby("NU_ANO_CENSO", sort=True):
        for indicator in BINARY_COLUMNS:
            values = pd.to_numeric(group[indicator], errors="coerce")
            valid = values.dropna()
            rows.append(
                {
                    "ano": str(year),
                    "dimensao": INFRA_DIMENSIONS.get(indicator, "Outro"),
                    "indicador": indicator,
                    "escolas_validas": int(valid.shape[0]),
                    "escolas_com_item": int((valid == 1).sum()),
                    "pct_escolas_com_item": (
                        float(valid.mean()) if len(valid) else np.nan
                    ),
                    "pct_nulo": float(values.isna().mean()),
                }
            )

    result = (
        pd.DataFrame(rows)
        .sort_values(["indicador", "ano"])
        .reset_index(drop=True)
    )
    result["variacao_pp_vs_ano_anterior"] = (
        result.groupby("indicador")["pct_escolas_com_item"].diff() * 100
    )
    return result


def network_summary(
    panel: pd.DataFrame,
    municipality_code: str = GUARATINGUETA,
) -> pd.DataFrame:
    df = _municipality(panel, municipality_code)
    rows: list[dict[str, object]] = []

    for (year, dependency), group in df.groupby(
        ["NU_ANO_CENSO", "TP_DEPENDENCIA"],
        dropna=False,
        sort=True,
    ):
        enrollment = pd.to_numeric(group["QT_MAT_BAS"], errors="coerce")
        rows.append(
            {
                "ano": str(year),
                "tp_dependencia": str(dependency),
                "rede": DEPENDENCY_LABELS.get(
                    str(dependency), f"Código {dependency}"
                ),
                "escolas": int(group["CO_ENTIDADE"].nunique()),
                "matriculas": (
                    int(enrollment.sum(min_count=1))
                    if enrollment.notna().any()
                    else pd.NA
                ),
            }
        )

    return pd.DataFrame(rows)


def localization_summary(
    panel: pd.DataFrame,
    municipality_code: str = GUARATINGUETA,
) -> pd.DataFrame:
    df = _municipality(panel, municipality_code)
    rows: list[dict[str, object]] = []

    for (year, localization), group in df.groupby(
        ["NU_ANO_CENSO", "TP_LOCALIZACAO"],
        dropna=False,
        sort=True,
    ):
        enrollment = pd.to_numeric(group["QT_MAT_BAS"], errors="coerce")
        rows.append(
            {
                "ano": str(year),
                "tp_localizacao": str(localization),
                "localizacao": LOCALIZATION_LABELS.get(
                    str(localization), f"Código {localization}"
                ),
                "escolas": int(group["CO_ENTIDADE"].nunique()),
                "matriculas": (
                    int(enrollment.sum(min_count=1))
                    if enrollment.notna().any()
                    else pd.NA
                ),
            }
        )

    return pd.DataFrame(rows)


def school_presence(
    panel: pd.DataFrame,
    municipality_code: str = GUARATINGUETA,
) -> pd.DataFrame:
    df = _municipality(panel, municipality_code)
    years = sorted(df["NU_ANO_CENSO"].astype(str).unique())

    presence = (
        df.assign(presente=1)
        .pivot_table(
            index=["CO_ENTIDADE", "NO_ENTIDADE"],
            columns="NU_ANO_CENSO",
            values="presente",
            aggfunc="max",
            fill_value=0,
        )
        .reset_index()
    )
    for year in years:
        if year not in presence.columns:
            presence[year] = 0

    presence["n_anos_presente"] = presence[years].sum(axis=1)
    return presence[
        ["CO_ENTIDADE", "NO_ENTIDADE", *years, "n_anos_presente"]
    ]


def municipality_profiles(
    panel: pd.DataFrame,
    year: str = "2025",
) -> pd.DataFrame:
    df = panel[panel["NU_ANO_CENSO"].astype(str) == str(year)].copy()
    if df.empty:
        raise ValueError(f"Ano {year} não encontrado.")

    df["QT_MAT_BAS"] = pd.to_numeric(df["QT_MAT_BAS"], errors="coerce")

    base = (
        df.groupby(["CO_MUNICIPIO", "NO_MUNICIPIO"], as_index=False)
        .agg(
            escolas=("CO_ENTIDADE", "nunique"),
            matriculas=(
                "QT_MAT_BAS",
                lambda s: s.sum(min_count=1),
            ),
            mediana_matriculas_escola=("QT_MAT_BAS", "median"),
        )
    )

    dep = (
        df.assign(value=1)
        .pivot_table(
            index=["CO_MUNICIPIO", "NO_MUNICIPIO"],
            columns="TP_DEPENDENCIA",
            values="value",
            aggfunc="sum",
            fill_value=0,
        )
        .reset_index()
    )
    dep_codes = list(DEPENDENCY_LABELS)
    for code, label in DEPENDENCY_LABELS.items():
        if code not in dep.columns:
            dep[code] = 0
        denominator = dep[[c for c in dep_codes if c in dep.columns]].sum(axis=1)
        dep[f"pct_rede_{label.lower()}"] = np.where(
            denominator > 0,
            dep[code] / denominator,
            np.nan,
        )

    loc = (
        df.assign(value=1)
        .pivot_table(
            index=["CO_MUNICIPIO", "NO_MUNICIPIO"],
            columns="TP_LOCALIZACAO",
            values="value",
            aggfunc="sum",
            fill_value=0,
        )
        .reset_index()
    )
    for code in LOCALIZATION_LABELS:
        if code not in loc.columns:
            loc[code] = 0
    total_loc = loc[list(LOCALIZATION_LABELS)].sum(axis=1)
    loc["pct_escolas_rurais"] = np.where(
        total_loc > 0,
        loc["2"] / total_loc,
        np.nan,
    )

    dep_cols = ["CO_MUNICIPIO", "NO_MUNICIPIO"] + [
        f"pct_rede_{label.lower()}"
        for label in DEPENDENCY_LABELS.values()
    ]
    loc_cols = [
        "CO_MUNICIPIO",
        "NO_MUNICIPIO",
        "pct_escolas_rurais",
    ]

    return (
        base.merge(
            dep[dep_cols],
            on=["CO_MUNICIPIO", "NO_MUNICIPIO"],
            how="left",
        )
        .merge(
            loc[loc_cols],
            on=["CO_MUNICIPIO", "NO_MUNICIPIO"],
            how="left",
        )
        .sort_values("matriculas", ascending=False)
        .reset_index(drop=True)
    )


def comparable_pool(
    panel: pd.DataFrame,
    target_code: str = GUARATINGUETA,
    year: str = "2025",
    school_ratio: tuple[float, float] = (0.6, 1.4),
    enrollment_ratio: tuple[float, float] = (0.6, 1.4),
) -> pd.DataFrame:
    """
    Gera um pool exploratório de municípios estruturalmente semelhantes.

    O filtro NÃO usa indicadores de infraestrutura como critério de semelhança,
    porque esses indicadores são justamente o objeto que queremos comparar.
    A comparação usa porte do sistema escolar e composição por rede/zona.
    """
    profiles = municipality_profiles(panel, year=year)

    target_rows = profiles[
        profiles["CO_MUNICIPIO"].astype(str) == str(target_code)
    ]
    if target_rows.empty:
        raise ValueError(
            f"Município-alvo {target_code} não encontrado em {year}."
        )
    target = target_rows.iloc[0]

    candidates = profiles[
        profiles["CO_MUNICIPIO"].astype(str) != str(target_code)
    ].copy()

    school_low = target["escolas"] * school_ratio[0]
    school_high = target["escolas"] * school_ratio[1]
    enrollment_low = target["matriculas"] * enrollment_ratio[0]
    enrollment_high = target["matriculas"] * enrollment_ratio[1]

    candidates = candidates[
        candidates["escolas"].between(school_low, school_high)
        & candidates["matriculas"].between(
            enrollment_low, enrollment_high
        )
    ].copy()

    candidates["dif_escolas_pct"] = (
        (candidates["escolas"] - target["escolas"]).abs()
        / target["escolas"]
    )
    candidates["dif_matriculas_pct"] = (
        (candidates["matriculas"] - target["matriculas"]).abs()
        / target["matriculas"]
    )

    mix_columns = [
        "pct_rede_federal",
        "pct_rede_estadual",
        "pct_rede_municipal",
        "pct_rede_privada",
        "pct_escolas_rurais",
    ]
    available = [column for column in mix_columns if column in candidates]

    if available:
        candidates["dif_mix_pp_media"] = (
            candidates[available]
            .sub(target[available], axis=1)
            .abs()
            .astype(float)
            .mean(axis=1)
        )
    else:
        candidates["dif_mix_pp_media"] = np.nan

    candidates["distancia_estrutural"] = (
        candidates["dif_escolas_pct"].astype(float)
        + candidates["dif_matriculas_pct"].astype(float)
        + candidates["dif_mix_pp_media"].astype(float).fillna(0.0)
    )

    columns = [
        "CO_MUNICIPIO",
        "NO_MUNICIPIO",
        "escolas",
        "matriculas",
        "mediana_matriculas_escola",
        "pct_rede_federal",
        "pct_rede_estadual",
        "pct_rede_municipal",
        "pct_rede_privada",
        "pct_escolas_rurais",
        "dif_escolas_pct",
        "dif_matriculas_pct",
        "dif_mix_pp_media",
        "distancia_estrutural",
    ]
    return (
        candidates[[column for column in columns if column in candidates]]
        .sort_values(
            [
                "distancia_estrutural",
                "dif_matriculas_pct",
                "dif_escolas_pct",
            ]
        )
        .reset_index(drop=True)
    )


def infrastructure_by_cut(
    panel: pd.DataFrame,
    cut_column: str,
    municipality_code: str = GUARATINGUETA,
) -> pd.DataFrame:
    """
    Compara indicadores de infraestrutura por rede ou zona dentro do município.

    Bases com menos de 5 escolas válidas são marcadas como `base_pequena`
    para evitar leitura excessiva de percentuais instáveis.
    """
    if cut_column not in {"TP_DEPENDENCIA", "TP_LOCALIZACAO"}:
        raise ValueError(
            "cut_column deve ser TP_DEPENDENCIA ou TP_LOCALIZACAO."
        )

    df = _municipality(panel, municipality_code)
    labels = (
        DEPENDENCY_LABELS
        if cut_column == "TP_DEPENDENCIA"
        else LOCALIZATION_LABELS
    )
    rows: list[dict[str, object]] = []

    for (year, cut), group in df.groupby(
        ["NU_ANO_CENSO", cut_column],
        dropna=False,
        sort=True,
    ):
        for indicator in BINARY_COLUMNS:
            values = pd.to_numeric(group[indicator], errors="coerce")
            valid = values.dropna()
            rows.append(
                {
                    "ano": str(year),
                    "corte": cut_column,
                    "codigo_corte": str(cut),
                    "grupo": labels.get(str(cut), f"Código {cut}"),
                    "indicador": indicator,
                    "escolas_validas": int(valid.shape[0]),
                    "escolas_com_item": int((valid == 1).sum()),
                    "pct_escolas_com_item": (
                        float(valid.mean()) if len(valid) else np.nan
                    ),
                    "pct_nulo": float(values.isna().mean()),
                    "base_pequena": bool(len(valid) < 5),
                }
            )

    return pd.DataFrame(rows)


def enrollment_weighted_infrastructure(
    panel: pd.DataFrame,
    municipality_code: str = GUARATINGUETA,
) -> pd.DataFrame:
    """
    Compara percentual simples de escolas com o item e percentual ponderado
    pelas matrículas da escola.

    O ponderado aproxima a parcela de estudantes matriculados em escolas que
    possuem cada item de infraestrutura. Escolas sem matrícula informada não
    entram no denominador ponderado e são contabilizadas separadamente.
    """
    df = _municipality(panel, municipality_code)
    rows: list[dict[str, object]] = []

    for year, group in df.groupby("NU_ANO_CENSO", sort=True):
        weights = pd.to_numeric(group["QT_MAT_BAS"], errors="coerce")

        for indicator in BINARY_COLUMNS:
            values = pd.to_numeric(group[indicator], errors="coerce")
            unweighted_valid = values.dropna()
            mask = values.notna() & weights.notna() & (weights >= 0)

            pct_schools = (
                float(unweighted_valid.mean())
                if len(unweighted_valid)
                else np.nan
            )

            if mask.any() and float(weights[mask].sum()) > 0:
                pct_enrollments = float(
                    (values[mask] * weights[mask]).sum()
                    / weights[mask].sum()
                )
                covered_enrollment = int(weights[mask].sum())
            else:
                pct_enrollments = np.nan
                covered_enrollment = 0

            rows.append(
                {
                    "ano": str(year),
                    "indicador": indicator,
                    "pct_escolas_com_item": pct_schools,
                    "pct_matriculas_em_escolas_com_item": pct_enrollments,
                    "dif_ponderado_vs_escolas_pp": (
                        (pct_enrollments - pct_schools) * 100
                        if pd.notna(pct_enrollments)
                        and pd.notna(pct_schools)
                        else np.nan
                    ),
                    "escolas_validas_simples": int(
                        unweighted_valid.shape[0]
                    ),
                    "escolas_validas_ponderacao": int(mask.sum()),
                    "matriculas_cobertas_ponderacao": covered_enrollment,
                    "escolas_sem_matricula": int(weights.isna().sum()),
                }
            )

    return pd.DataFrame(rows)
