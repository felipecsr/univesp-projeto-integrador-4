# Base final de consumo do Web App

A base de consumo é produzida por `src/build_consumption.py` a partir do painel escola-ano validado.

Ela reduz processamento no Apps Script e mantém as regras analíticas explícitas antes da camada de visualização.

## Tabelas

- `CONFIG`: parâmetros estáveis do MVP, como ano padrão, município-foco e limite de base pequena.
- `CATALOGO`: indicadores finais, variáveis-fonte e regras de cálculo.
- `COMPARAVEIS`: Guaratinguetá + grupo final de 10 municípios comparáveis em 2025.
- `MUNICIPIO_ANO`: agregados municipais 2023–2025 para tendências e comparações.
- `MUNICIPIO_REDE_2025`: agregados municipais por dependência administrativa.
- `MUNICIPIO_ZONA_2025`: agregados municipais por localização urbana/rural.
- `ESCOLAS_2025`: base por escola para consulta individual.
- `QA`: controles de integridade e contagens finais.

## Regras finais

- 2025 é a fotografia padrão do MVP.
- Tendências usam 2023–2025 quando a variável é semanticamente comparável.
- Percentuais principais usam escolas válidas como denominador.
- A ponderação por matrículas é uma visão secundária e opcional.
- Recortes com menos de 5 escolas são sinalizados como base pequena.
- Infraestrutura não entra no critério de seleção dos municípios comparáveis.
- Índice composto e machine learning ficam fora do MVP.

## QA consolidado

| Checagem | Status | Valor |
| --- | --- | ---: |
| `ESCOLAS_2025` | PASS | 30.817 |
| Guaratinguetá — escolas 2025 | PASS | 92 |
| `MUNICIPIO_ANO` | PASS | 1.935 |
| Guaratinguetá — anos | PASS | 3 |
| `MUNICIPIO_REDE_2025` | PASS | 1.724 |
| Guaratinguetá — redes | PASS | 3 |
| `MUNICIPIO_ZONA_2025` | PASS | 924 |
| Guaratinguetá — zonas | PASS | 2 |
| `COMPARAVEIS` | PASS | 10 + foco |
| `CATALOGO` | PASS | 14 |

Os campos percentuais estão armazenados numericamente entre 0 e 1. A base final preserva a distinção entre valor ausente e valor zero.

## Rastreabilidade

A construção da base está versionada em `src/build_consumption.py` e deriva do painel escola-ano validado. A execução manual de notebooks não é requisito adicional para aceitar a base final: o QA acima é o checkpoint técnico utilizado pelo Web App publicado.

## Consumo pela aplicação

O Web App consulta a planilha final por meio do Apps Script. Para reduzir latência:

- a Visão Geral é priorizada no carregamento;
- outras áreas são carregadas sob demanda;
- a lista de escolas de Guaratinguetá é lida uma vez e filtrada no navegador;
- leituras do backend usam cache temporário;
- a consulta por escola evita carregar repetidamente a tabela completa de São Paulo.

Resultados derivados desta base estão consolidados em [`RESULTADOS_TECNICOS.md`](RESULTADOS_TECNICOS.md).
