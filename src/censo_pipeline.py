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


def _header(zf: zipfile.ZipFile, member: str) -> list[str]:
    with zf.open(member) as fh:
        return list(
            pd.read_csv(
                fh,
                sep=";",
                encoding="latin1",
                nrows=0,
            ).columns
        )


def _read_filtered(
    zf: zipfile.ZipFile,
    member: str,
    wanted: list[str],
    *,
    uf: str | None = None,
    active_only: bool = False,
    school_ids: set[str] | None = None,
    chunksize: int = 50_000,
) -> pd.DataFrame:
    available = _header(zf, member)
    selected = [column for column in wanted if column in available]
    if not selected:
        raise KeyError(f"Nenhuma coluna solicitada existe em {member}")

    if uf is not None and "SG_UF" not in selected and "SG_UF" in available:
        selected.append("SG_UF")
    if active_only and "TP_SITUACAO_FUNCIONAMENTO" not in selected:
        selected.append("TP_SITUACAO_FUNCIONAMENTO")
    if school_ids is not None and "CO_ENTIDADE" not in selected:
        selected.append("CO_ENTIDADE")

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
            if uf is not None:
                chunk = chunk[chunk["SG_UF"] == uf]
            if active_only:
                chunk = chunk[chunk["TP_SITUACAO_FUNCIONAMENTO"] == "1"]
            if school_ids is not None:
                chunk = chunk[chunk["CO_ENTIDADE"].isin(school_ids)]
            if not chunk.empty:
                frames.append(chunk)

    if not frames:
        return pd.DataFrame(columns=selected)
    return pd.concat(frames, ignore_index=True)


def _validate_school_columns(df: pd.DataFrame, year: int) -> None:
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
        df = _read_filtered(
            zf,
            member,
            CANONICAL_COLUMNS,
            uf=uf,
            active_only=True,
        )

    _validate_school_columns(df, year)
    return df.reindex(columns=CANONICAL_COLUMNS)


def load_2025(zip_path: str | Path, uf: str = UF_DEFAULT) -> pd.DataFrame:
    with zipfile.ZipFile(zip_path) as zf:
        school_member = _find_member(
            zf,
            [r"/Tabela_Escola_2025(?:_V\d+)?\.csv$"],
        )
        school = _read_filtered(
            zf,
            school_member,
            ID_COLUMNS + INFRA_COLUMNS,
            uf=uf,
            active_only=True,
        )
        _validate_school_columns(school, 2025)

        matricula_member = _find_member(
            zf,
            [r"/Tabela_Matricula_2025(?:_V\d+)?\.csv$"],
        )
        ids = set(school["CO_ENTIDADE"].dropna())
        matricula = _read_filtered(
            zf,
            matricula_member,
            ["CO_ENTIDADE"] + MATRICULA_COLUMNS,
            school_ids=ids,
        )

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


def load_year(zip_path: str | Path, year: int, uf: str = UF_DEFAULT) -> pd.DataFrame:
    if year in (2023, 2024):
        return load_legacy_year(zip_path, year, uf=uf)
    if year == 2025:
        return load_2025(zip_path, uf=uf)
    raise ValueError(f"Ano fora do escopo atual: {year}")


def canonicalize_types(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for column in ID_COLUMNS:
        if column in out.columns:
            out[column] = out[column].astype("string")

    numeric = [
        column
        for column in INFRA_COLUMNS + MATRICULA_COLUMNS
        if column in out.columns
    ]
    for column in numeric:
        out[column] = pd.to_numeric(out[column], errors="coerce").astype("Int64")
    return out


def build_panel(
    zip_by_year: dict[int, str | Path],
    *,
    uf: str = UF_DEFAULT,
) -> pd.DataFrame:
    missing_years = sorted(set(YEARS) - set(zip_by_year))
    if missing_years:
        raise ValueError(f"ZIPs não informados para os anos: {missing_years}")

    frames = [
        canonicalize_types(load_year(zip_by_year[year], year, uf=uf))
        for year in YEARS
    ]
    panel = pd.concat(frames, ignore_index=True)

    duplicated = panel.duplicated(["NU_ANO_CENSO", "CO_ENTIDADE"])
    if duplicated.any():
        sample = panel.loc[
            duplicated, ["NU_ANO_CENSO", "CO_ENTIDADE"]
        ].head().to_dict("records")
        raise ValueError(f"Chave escola-ano duplicada: {sample}")

    return panel.sort_values(["NU_ANO_CENSO", "CO_ENTIDADE"]).reset_index(drop=True)


def qa_summary(panel: pd.DataFrame) -> pd.DataFrame:
    return (
        panel.groupby("NU_ANO_CENSO", dropna=False)
        .agg(
            escolas=("CO_ENTIDADE", "nunique"),
            municipios=("CO_MUNICIPIO", "nunique"),
            pct_sem_matricula=(
                "QT_MAT_BAS",
                lambda s: round(float(s.isna().mean() * 100), 2),
            ),
        )
        .reset_index()
    )


def save_outputs(
    panel: pd.DataFrame,
    output_dir: str | Path,
    *,
    municipio_foco: str = GUARATINGUETA,
) -> tuple[Path, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    panel_path = output / "censo_escolar_sp_escola_ano_2023_2025.parquet"
    foco_path = output / "censo_escolar_guaratingueta_2023_2025.csv"

    panel.to_parquet(panel_path, index=False)
    panel.loc[panel["CO_MUNICIPIO"] == municipio_foco].to_csv(
        foco_path,
        index=False,
        encoding="utf-8",
    )
    return panel_path, foco_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Constrói painel escola-ano do Censo Escolar 2023–2025."
    )
    parser.add_argument("--zip-2023", required=True)
    parser.add_argument("--zip-2024", required=True)
    parser.add_argument("--zip-2025", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--uf", default=UF_DEFAULT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    panel = build_panel(
        {
            2023: args.zip_2023,
            2024: args.zip_2024,
            2025: args.zip_2025,
        },
        uf=args.uf,
    )
    print(qa_summary(panel).to_string(index=False))
    panel_path, foco_path = save_outputs(panel, args.output_dir)
    print(f"Painel: {panel_path}")
    print(f"Guaratinguetá: {foco_path}")


if __name__ == "__main__":
    main()
