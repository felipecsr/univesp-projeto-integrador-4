from __future__ import annotations

import argparse
import re
import zipfile
from pathlib import Path

import pandas as pd

YEARS = (2023, 2024, 2025)
UF_DEFAULT = "SP"
GUARATINGUETA = "3518404"

ID_COLUMNS = [
    "NU_ANO_CENSO",
    "CO_ENTIDADE",
    "NO_ENTIDADE",
    "CO_MUNICIPIO",
    "NO_MUNICIPIO",
    "SG_UF",
    "TP_SITUACAO_FUNCIONAMENTO",
    "TP_DEPENDENCIA",
    "TP_LOCALIZACAO",
]

INFRA_COLUMNS = [
    "IN_AGUA_POTAVEL",
    "IN_ENERGIA_REDE_PUBLICA",
    "IN_ESGOTO_REDE_PUBLICA",
    "IN_ACESSIBILIDADE_RAMPAS",
    "IN_INTERNET",
    "IN_BANDA_LARGA",
    "IN_BIBLIOTECA",
    "IN_LABORATORIO_INFORMATICA",
    "IN_LABORATORIO_CIENCIAS",
    "IN_QUADRA_ESPORTES",
    "IN_REFEITORIO",
    "QT_SALAS_UTILIZADAS",
]

MATRICULA_COLUMNS = [
    "QT_MAT_BAS",
    "QT_MAT_INF",
    "QT_MAT_FUND",
    "QT_MAT_MED",
    "QT_MAT_EJA",
    "QT_MAT_PROF",
]

CANONICAL_COLUMNS = ID_COLUMNS + INFRA_COLUMNS + MATRICULA_COLUMNS
BINARY_COLUMNS = [column for column in INFRA_COLUMNS if column.startswith("IN_")]
COUNT_COLUMNS = ["QT_SALAS_UTILIZADAS", *MATRICULA_COLUMNS]

REQUIRED_SCHOOL_COLUMNS = {
    "NU_ANO_CENSO",
    "CO_ENTIDADE",
    "CO_MUNICIPIO",
    "SG_UF",
    "TP_SITUACAO_FUNCIONAMENTO",
    "TP_DEPENDENCIA",
    "TP_LOCALIZACAO",
}


def _find_member(zf: zipfile.ZipFile, patterns: list[str]) -> str:
    candidates = [
        name
        for name in zf.namelist()
        if any(re.search(pattern, name, flags=re.IGNORECASE) for pattern in patterns)
    ]
    if not candidates:
        raise FileNotFoundError(
            "Nenhum arquivo compatível encontrado no ZIP. "
            f"Padrões: {patterns}"
        )
    return max(candidates, key=lambda name: zf.getinfo(name).file_size)


def _csv_header(path_or_handle) -> list[str]:
    return list(
        pd.read_csv(
            path_or_handle,
            sep=";",
            encoding="latin1",
            nrows=0,
        ).columns
    )


def _selected_columns(available: list[str], wanted: list[str]) -> list[str]:
    selected = [column for column in wanted if column in available]
    if not selected:
        raise KeyError("Nenhuma coluna solicitada existe na fonte")
    return selected


def _filter_chunk(
    chunk: pd.DataFrame,
    *,
    uf: str | None = None,
    active_only: bool = False,
    school_ids: set[str] | None = None,
) -> pd.DataFrame:
    if uf is not None:
        chunk = chunk[chunk["SG_UF"] == uf]
    if active_only:
        chunk = chunk[chunk["TP_SITUACAO_FUNCIONAMENTO"] == "1"]
    if school_ids is not None:
        chunk = chunk[chunk["CO_ENTIDADE"].isin(school_ids)]
    return chunk


def _read_filtered_csv(
    csv_path: str | Path,
    wanted: list[str],
    *,
    uf: str | None = None,
    active_only: bool = False,
    school_ids: set[str] | None = None,
    chunksize: int = 50_000,
) -> pd.DataFrame:
    available = _csv_header(csv_path)
    selected = _selected_columns(available, wanted)

    for required in (
        "SG_UF" if uf is not None else None,
        "TP_SITUACAO_FUNCIONAMENTO" if active_only else None,
        "CO_ENTIDADE" if school_ids is not None else None,
    ):
        if required and required not in selected:
            if required not in available:
                raise KeyError(f"Coluna necessária ao filtro ausente: {required}")
            selected.append(required)

    frames: list[pd.DataFrame] = []
    reader = pd.read_csv(
        csv_path,
        sep=";",
        encoding="latin1",
        usecols=selected,
        dtype=str,
        chunksize=chunksize,
        low_memory=False,
    )
    for chunk in reader:
        chunk = _filter_chunk(
            chunk,
            uf=uf,
            active_only=active_only,
            school_ids=school_ids,
        )
        if not chunk.empty:
            frames.append(chunk)

    if not frames:
        return pd.DataFrame(columns=selected)
    return pd.concat(frames, ignore_index=True)


def _read_filtered_zip_member(
    zf: zipfile.ZipFile,
    member: str,
    wanted: list[str],
    *,
    uf: str | None = None,
    active_only: bool = False,
    school_ids: set[str] | None = None,
    chunksize: int = 50_000,
) -> pd.DataFrame:
    with zf.open(member) as fh:
        available = _csv_header(fh)
    selected = _selected_columns(available, wanted)

    for required in (
        "SG_UF" if uf is not None else None,
        "TP_SITUACAO_FUNCIONAMENTO" if active_only else None,
        "CO_ENTIDADE" if school_ids is not None else None,
    ):
        if required and required not in selected:
            if required not in available:
                raise KeyError(f"Coluna necessária ao filtro ausente: {required}")
            selected.append(required)

    frames: list[pd.DataFrame] = []
    with zf.open(member) as fh:
        reader = pd.read_csv(
            fh,
            sep=";",
            encoding="latin1",
            usecols=selected,
            dtype=str,
            chunksize=chunksize,
            low_memory=False,
        )
        for chunk in reader:
            chunk = _filter_chunk(
                chunk,
                uf=uf,
                active_only=active_only,
                school_ids=school_ids,
            )
            if not chunk.empty:
                frames.append(chunk)

    if not frames:
        return pd.DataFrame(columns=selected)
    return pd.concat(frames, ignore_index=True)


def _validate_school_table(df: pd.DataFrame, year: int) -> None:
    missing = sorted(REQUIRED_SCHOOL_COLUMNS - set(df.columns))
    if missing:
        raise KeyError(f"{year}: colunas escolares obrigatórias ausentes: {missing}")
    if df["CO_ENTIDADE"].isna().any():
        raise ValueError(f"{year}: CO_ENTIDADE contém nulos")
    if df["CO_ENTIDADE"].duplicated().any():
        sample = df.loc[df["CO_ENTIDADE"].duplicated(), "CO_ENTIDADE"].head().tolist()
        raise ValueError(f"{year}: CO_ENTIDADE duplicado na tabela de escolas: {sample}")


def load_legacy_year(zip_path: str | Path, year: int, uf: str = UF_DEFAULT) -> pd.DataFrame:
    with zipfile.ZipFile(zip_path) as zf:
        member = _find_member(
            zf,
            [rf"/microdados_ed_basica_{year}\.csv$"],
        )
        df = _read_filtered_zip_member(
            zf,
            member,
            CANONICAL_COLUMNS,
            uf=uf,
            active_only=True,
        )

    _validate_school_table(df, year)
    return df.reindex(columns=CANONICAL_COLUMNS)


def _join_2025(school: pd.DataFrame, matricula: pd.DataFrame) -> pd.DataFrame:
    _validate_school_table(school, 2025)

    if matricula["CO_ENTIDADE"].duplicated().any():
        sample = (
            matricula.loc[matricula["CO_ENTIDADE"].duplicated(), "CO_ENTIDADE"]
            .head()
            .tolist()
        )
        raise ValueError(
            "2025: Tabela_Matricula contém mais de uma linha por escola. "
            f"Rever regra de agregação antes de continuar. Exemplos: {sample}"
        )

    merged = school.merge(
        matricula,
        on="CO_ENTIDADE",
        how="left",
        validate="one_to_one",
    )
    return merged.reindex(columns=CANONICAL_COLUMNS)


def load_2025_from_csvs(
    school_csv: str | Path,
    matricula_csv: str | Path,
    uf: str = UF_DEFAULT,
) -> pd.DataFrame:
    school = _read_filtered_csv(
        school_csv,
        ID_COLUMNS + INFRA_COLUMNS,
        uf=uf,
        active_only=True,
    )
    ids = set(school["CO_ENTIDADE"].dropna())
    matricula = _read_filtered_csv(
        matricula_csv,
        ["CO_ENTIDADE", *MATRICULA_COLUMNS],
        school_ids=ids,
    )
    return _join_2025(school, matricula)


def load_2025_from_zip(zip_path: str | Path, uf: str = UF_DEFAULT) -> pd.DataFrame:
    with zipfile.ZipFile(zip_path) as zf:
        school_member = _find_member(
            zf,
            [r"/Tabela_Escola_2025(?:_V\d+)?\.csv$"],
        )
        school = _read_filtered_zip_member(
            zf,
            school_member,
            ID_COLUMNS + INFRA_COLUMNS,
            uf=uf,
            active_only=True,
        )
        ids = set(school["CO_ENTIDADE"].dropna())

        matricula_member = _find_member(
            zf,
            [r"/Tabela_Matricula_2025(?:_V\d+)?\.csv$"],
        )
        matricula = _read_filtered_zip_member(
            zf,
            matricula_member,
            ["CO_ENTIDADE", *MATRICULA_COLUMNS],
            school_ids=ids,
        )

    return _join_2025(school, matricula)


def canonicalize_types(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for column in ID_COLUMNS:
        if column in out.columns:
            out[column] = out[column].astype("string")

    for column in COUNT_COLUMNS + BINARY_COLUMNS:
        if column in out.columns:
            out[column] = pd.to_numeric(out[column], errors="coerce").astype("Int64")
    return out


def build_panel(
    zip_2023: str | Path,
    zip_2024: str | Path,
    *,
    school_2025: str | Path | None = None,
    matricula_2025: str | Path | None = None,
    zip_2025: str | Path | None = None,
    uf: str = UF_DEFAULT,
) -> pd.DataFrame:
    frames = [
        canonicalize_types(load_legacy_year(zip_2023, 2023, uf=uf)),
        canonicalize_types(load_legacy_year(zip_2024, 2024, uf=uf)),
    ]

    if school_2025 is not None and matricula_2025 is not None:
        year_2025 = load_2025_from_csvs(school_2025, matricula_2025, uf=uf)
    elif zip_2025 is not None:
        year_2025 = load_2025_from_zip(zip_2025, uf=uf)
    else:
        raise ValueError(
            "Informe school_2025 + matricula_2025 ou zip_2025 para carregar 2025."
        )
    frames.append(canonicalize_types(year_2025))

    panel = pd.concat(frames, ignore_index=True)
    duplicated = panel.duplicated(["NU_ANO_CENSO", "CO_ENTIDADE"])
    if duplicated.any():
        sample = panel.loc[
            duplicated, ["NU_ANO_CENSO", "CO_ENTIDADE"]
        ].head().to_dict("records")
        raise ValueError(f"Chave escola-ano duplicada: {sample}")

    return panel.sort_values(["NU_ANO_CENSO", "CO_ENTIDADE"]).reset_index(drop=True)


def validate_panel(panel: pd.DataFrame) -> None:
    if panel.empty:
        raise ValueError("Painel vazio")

    years = set(panel["NU_ANO_CENSO"].dropna().astype(str))
    expected_years = {str(year) for year in YEARS}
    if years != expected_years:
        raise ValueError(f"Anos inesperados no painel: {sorted(years)}")

    duplicated = panel.duplicated(["NU_ANO_CENSO", "CO_ENTIDADE"])
    if duplicated.any():
        raise ValueError("Painel contém chave escola-ano duplicada")

    for column in BINARY_COLUMNS:
        observed = set(panel[column].dropna().astype(int).unique())
        if not observed.issubset({0, 1}):
            raise ValueError(f"{column}: domínio binário inválido: {sorted(observed)}")

    for column in COUNT_COLUMNS:
        numeric = pd.to_numeric(panel[column], errors="coerce")
        if (numeric.dropna() < 0).any():
            raise ValueError(f"{column}: contagem negativa encontrada")

    if not (panel["CO_MUNICIPIO"] == GUARATINGUETA).any():
        raise ValueError("Guaratinguetá não apareceu no painel")


def qa_summary(panel: pd.DataFrame) -> pd.DataFrame:
    return (
        panel.groupby("NU_ANO_CENSO", dropna=False)
        .agg(
            escolas=("CO_ENTIDADE", "nunique"),
            municipios=("CO_MUNICIPIO", "nunique"),
            escolas_sem_matricula=("QT_MAT_BAS", lambda s: int(s.isna().sum())),
            pct_sem_matricula=(
                "QT_MAT_BAS",
                lambda s: round(float(s.isna().mean() * 100), 2),
            ),
        )
        .reset_index()
    )


def variable_qa(panel: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for year, group in panel.groupby("NU_ANO_CENSO", dropna=False):
        for column in INFRA_COLUMNS + MATRICULA_COLUMNS:
            series = pd.to_numeric(group[column], errors="coerce")
            row: dict[str, object] = {
                "ano": str(year),
                "variavel": column,
                "pct_nulo": round(float(series.isna().mean() * 100), 2),
                "n_validos": int(series.notna().sum()),
            }
            row["minimo"] = int(series.min()) if series.notna().any() else None
            row["maximo"] = int(series.max()) if series.notna().any() else None
            row["n_distintos"] = int(series.nunique(dropna=True))
            rows.append(row)
    return pd.DataFrame(rows)


def save_outputs(
    panel: pd.DataFrame,
    output_dir: str | Path,
    *,
    municipio_foco: str = GUARATINGUETA,
) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    paths = {
        "panel": output / "censo_escolar_sp_escola_ano_2023_2025.csv.gz",
        "guaratingueta": output / "censo_escolar_guaratingueta_2023_2025.csv",
        "qa_resumo": output / "qa_resumo_2023_2025.csv",
        "qa_variaveis": output / "qa_variaveis_2023_2025.csv",
    }
    panel.to_csv(paths["panel"], index=False, encoding="utf-8", compression="gzip")
    panel.loc[panel["CO_MUNICIPIO"] == municipio_foco].to_csv(
        paths["guaratingueta"], index=False, encoding="utf-8"
    )
    qa_summary(panel).to_csv(paths["qa_resumo"], index=False, encoding="utf-8")
    variable_qa(panel).to_csv(paths["qa_variaveis"], index=False, encoding="utf-8")
    return paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Constrói painel escola-ano do Censo Escolar 2023–2025."
    )
    parser.add_argument("--zip-2023", required=True)
    parser.add_argument("--zip-2024", required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--zip-2025")
    group.add_argument("--escola-2025")
    parser.add_argument("--matricula-2025")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--uf", default=UF_DEFAULT)
    args = parser.parse_args()

    if args.escola_2025 and not args.matricula_2025:
        parser.error("--escola-2025 exige --matricula-2025")
    if args.matricula_2025 and not args.escola_2025:
        parser.error("--matricula-2025 exige --escola-2025")
    return args


def main() -> None:
    args = parse_args()
    panel = build_panel(
        args.zip_2023,
        args.zip_2024,
        school_2025=args.escola_2025,
        matricula_2025=args.matricula_2025,
        zip_2025=args.zip_2025,
        uf=args.uf,
    )
    validate_panel(panel)
    print(qa_summary(panel).to_string(index=False))
    paths = save_outputs(panel, args.output_dir)
    for name, path in paths.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
