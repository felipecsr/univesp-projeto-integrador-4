# Reprodutibilidade técnica

Este documento substitui a antiga exigência de execução manual no Google Colab como evidência de conclusão.

## Decisão

A execução manual dos notebooks continua **possível e útil para reprodução independente**, mas não é necessária apenas para gerar prints ou comprovar uma etapa que já foi validada tecnicamente.

O projeto considera como evidência técnica suficiente:

- código versionado no GitHub;
- notebooks versionados com as etapas analíticas;
- validação executada sobre os arquivos oficiais;
- QA consolidado na base de consumo;
- tabelas de resultados finais documentadas no repositório;
- Web App publicado consumindo a base final.

## Pipeline

O fluxo principal é:

`Censo Escolar/INEP → src/censo_pipeline.py → painel escola-ano → src/eda.py → src/build_consumption.py → Google Sheets → Apps Script/Web App`

### Etapas versionadas

| Etapa | Artefato principal | Função |
| --- | --- | --- |
| Ingestão e harmonização | `src/censo_pipeline.py` | Lê, filtra e harmoniza 2023–2025 |
| QA da base analítica | `src/validate_analytic_base.py` | Revalida chaves, domínios e contagens |
| EDA | `src/eda.py` | Agregações e análises descritivas |
| Base final | `src/build_consumption.py` | Produz as tabelas consumidas pelo Web App |
| Reprodução didática | `notebooks/*.ipynb` | Organiza as mesmas etapas em notebooks |
| Aplicação | `webapp/` | Consulta e visualiza a base final |

## Notebooks

Os notebooks permanecem no repositório:

1. `01_ingestao_e_qa_censo.ipynb`
2. `02_eda_guaratingueta.ipynb`
3. `03_comparaveis_sp.ipynb`
4. `04_rede_zona.ipynb`
5. `05_ponderacao_matriculas.ipynb`

Eles podem ser executados no Colab ou em outro ambiente compatível caso alguém queira reproduzir uma etapa. Não existe, porém, uma obrigação de salvar cópias executadas ou capturas de tela como parte do fechamento técnico do PI.

## QA já consolidado

| Checagem | Resultado |
| --- | ---: |
| Painel escola-ano | 92.143 linhas |
| Duplicidades na chave | 0 |
| Municípios paulistas por ano | 645 |
| Escolas ativas em SP — 2023 | 30.580 |
| Escolas ativas em SP — 2024 | 30.746 |
| Escolas ativas em SP — 2025 | 30.817 |
| Contagens negativas | 0 |
| Domínio dos indicadores binários | 0/1 validado |

A base final de consumo possui uma aba `QA` com os controles finais utilizados pela aplicação.

## Evidência para relatório e apresentação

Para o trabalho escrito, não é necessário substituir os resultados por prints de notebook. As tabelas consolidadas em [`RESULTADOS_TECNICOS.md`](RESULTADOS_TECNICOS.md) são a referência principal.

Para a etapa de apresentação, prints do Web App podem ser usados quando ajudarem a demonstrar a ferramenta. Nesse caso, o print serve para **comunicar o produto**, e não como prova de que um notebook foi executado.

## Regra de rastreabilidade

Se um número for utilizado no relatório, ele deve poder ser associado a uma regra de cálculo e a uma tabela final versionada/documentada. O objetivo da reprodutibilidade é permitir reconstrução e auditoria do processo, não acumular evidências manuais redundantes.
