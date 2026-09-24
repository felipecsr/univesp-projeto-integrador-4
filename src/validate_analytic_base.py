from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.censo_pipeline import (
    CANONICAL_COLUMNS,
    GUARATINGUETA,
    canonicalize_types,
    qa_summary,
    validate_panel,
    variable_qa,
)

EXPECTED_SCHOOLS = {
    "2023": 30580,
    "2024": 30746,
    "2025": 30817,
}

EXPECTED_MUNICIPALITIES = {
    "2023": 645,
    "2024": 645,
    "2025": 645,
}

EXPECTED_GUARA_SCHOOLS = {
    "2023": 91,
    "2024": 93,
    "2025": 92,
}

REQUIRED_FILES = (
    "censo_escolar_sp_escola_ano_2023_2025.csv.gz",
    "censo_escolar_guaratingueta_2023_2025.csv",
    "qa_resumo_2023_2025.csv",
    "qa_variaveis_2023_2025.csv",
    "fontes_execucao.csv",
    "resumo_guaratingueta.csv",
    "manifesto_execucao.csv",
)


def _record(rows: list[dict[str, object]], check: str, passed: bool, detail: str) -> None:
    rows.append(
        {
            "checagem": check,
            "status": "PASS" if passed else "FAIL",
            "detalhe": detail,
        }
    )


def validate_execution(execution_dir: str | Path) -> pd.DataFrame:
    execution_dir = Path(execution_dir)
    rows: list[dict[str, object]] = []

    if not execution_dir.exists():
        raise FileNotFoundError(f"Pasta de execução não encontrada: {execution_dir}")

    missing = [name for name in REQUIRED_FILES if not (execution_dir / name).exists()]
    _record(
        rows,
        "Arquivos obrigatórios",
        not missing,
        "Todos presentes" if not missing else f"Ausentes: {', '.join(missing)}",
    )
    if missing:
        return pd.DataFrame(rows)

    panel_path = execution_dir / "censo_escolar_sp_escola_ano_2023_2025.csv.gz"
    panel = pd.read_csv(panel_path, dtype=str)
    panel = panel.reindex(columns=CANONICAL_COLUMNS)
    panel = canonicalize_types(panel)

    try:
        validate_panel(panel)
        _record(rows, "Validação estrutural do painel", True, "validate_panel executado sem erro")
    except Exception as exc:  # pragma: no cover - audit trail
        _record(rows, "Validação estrutural do painel", False, str(exc))
        return pd.DataFrame(rows)

    summary = qa_summary(panel)
    summary["NU_ANO_CENSO"] = summary["NU_ANO_CENSO"].astype(str)
    indexed = summary.set_index("NU_ANO_CENSO")

    for year in ("2023", "2024", "2025"):
        schools = int(indexed.loc[year, "escolas"])
        municipalities = int(indexed.loc[year, "municipios"])
        _record(
            rows,
            f"Escolas ativas SP {year}",
            schools == EXPECTED_SCHOOLS[year],
            f"observado={schools}; esperado={EXPECTED_SCHOOLS[year]}",
        )
        _record(
            rows,
            f"Municípios SP {year}",
            municipalities == EXPECTED_MUNICIPALITIES[year],
            f"observado={municipalities}; esperado={EXPECTED_MUNICIPALITIES[year]}",
        )

    guara = panel[panel["CO_MUNICIPIO"] == GUARATINGUETA]
    guara_counts = (
        guara.groupby("NU_ANO_CENSO")["CO_ENTIDADE"]
        .nunique()
        .astype(int)
        .to_dict()
    )
    for year in ("2023", "2024", "2025"):
        observed = int(guara_counts.get(year, 0))
        _record(
            rows,
            f"Escolas Guaratinguetá {year}",
            observed == EXPECTED_GUARA_SCHOOLS[year],
            f"observado={observed}; esperado={EXPECTED_GUARA_SCHOOLS[year]}",
        )

    saved_summary = pd.read_csv(execution_dir / "qa_resumo_2023_2025.csv", dtype=str)
    current_summary = qa_summary(panel).astype(str)
    same_summary = saved_summary.equals(current_summary)
    _record(
        rows,
        "QA resumo salvo × recalculado",
        same_summary,
        "CSV salvo coincide com o QA recalculado" if same_summary else "Há divergência no QA resumo",
    )

    saved_vars = pd.read_csv(execution_dir / "qa_variaveis_2023_2025.csv", dtype=str)
    current_vars = variable_qa(panel).astype(str)
    same_vars = saved_vars.equals(current_vars)
    _record(
        rows,
        "QA variáveis salvo × recalculado",
        same_vars,
        "CSV salvo coincide com o QA recalculado" if same_vars else "Há divergência no QA de variáveis",
    )

    guara_saved = pd.read_csv(
        execution_dir / "censo_escolar_guaratingueta_2023_2025.csv",
        dtype=str,
    )
    expected_guara_keys = (
        guara[["NU_ANO_CENSO", "CO_ENTIDADE"]]
        .astype(str)
        .sort_values(["NU_ANO_CENSO", "CO_ENTIDADE"])
        .reset_index(drop=True)
    )
    saved_guara_keys = (
        guara_saved[["NU_ANO_CENSO", "CO_ENTIDADE"]]
        .astype(str)
        .sort_values(["NU_ANO_CENSO", "CO_ENTIDADE"])
        .reset_index(drop=True)
    )
    same_guara = expected_guara_keys.equals(saved_guara_keys)
    _record(
        rows,
        "Recorte Guaratinguetá × painel",
        same_guara,
        "Chaves escola-ano coincidem" if same_guara else "Recorte salvo diverge do painel",
    )

    manifest = pd.read_csv(execution_dir / "manifesto_execucao.csv", dtype=str)
    commit = manifest.loc[0, "repo_commit"] if "repo_commit" in manifest.columns and not manifest.empty else ""
    _record(
        rows,
        "Manifesto da execução",
        len(commit) == 40,
        f"repo_commit={commit or 'ausente'}",
    )

    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reconcilia a base analítica materializada pela execução humana do Colab."
    )
    parser.add_argument("--execution-dir", required=True)
    parser.add_argument(
        "--output",
        default=None,
        help="CSV de reconciliação. Padrão: reconciliacao_p04.csv dentro da pasta de execução.",
    )
    args = parser.parse_args()

    result = validate_execution(args.execution_dir)
    output = Path(args.output) if args.output else Path(args.execution_dir) / "reconciliacao_p04.csv"
    result.to_csv(output, index=False, encoding="utf-8")

    print(result.to_string(index=False))
    print(f"\nReconciliação salva em: {output}")

    if (result["status"] == "FAIL").any():
        raise SystemExit("P04 falhou: há checagens com status FAIL.")


if __name__ == "__main__":
    main()
