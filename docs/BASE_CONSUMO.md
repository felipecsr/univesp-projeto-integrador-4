# Base final de consumo do Web App

A base de consumo é produzida por `src/build_consumption.py` a partir do painel escola-ano validado.

Ela foi desenhada para reduzir processamento no Apps Script e deixar as regras analíticas explícitas antes da implementação do frontend.

## Tabelas

- `CONFIG`: parâmetros estáveis do MVP, como ano padrão, município-foco e limite de base pequena.
- `CATALOGO`: indicadores finais, variáveis-fonte e regras de cálculo.
- `COMPARAVEIS`: Guaratinguetá + grupo padrão de 10 municípios comparáveis em 2025.
- `MUNICIPIO_ANO`: agregados municipais 2023–2025 para tendências.
- `MUNICIPIO_REDE_2025`: agregados municipais por dependência administrativa.
- `MUNICIPIO_ZONA_2025`: agregados municipais por localização urbana/rural.
- `ESCOLAS_2025`: base por escola para consulta individual.
- `QA`: controles de integridade e contagens esperadas.

## Regras principais

- 2025 é a fotografia padrão do MVP.
- Tendências usam 2023–2025 quando a variável é semanticamente comparável.
- Percentuais principais usam escolas válidas como denominador.
- A ponderação por matrículas é uma visão secundária e opcional.
- Recortes com menos de 5 escolas são sinalizados como base pequena.
- Infraestrutura não entra no critério de seleção dos municípios comparáveis.
- Índice composto e machine learning ficam fora do MVP.

## QA esperado

- 30.817 escolas ativas em São Paulo em 2025.
- 92 escolas ativas em Guaratinguetá em 2025.
- 1.935 linhas em `MUNICIPIO_ANO` = 645 municípios × 3 anos.
- 3 recortes por rede e 2 por zona para Guaratinguetá em 2025.
- 10 municípios no grupo comparável padrão, além do município-foco.

Os arquivos de origem permanecem fora do GitHub; o repositório versiona o código e a documentação necessários para reconstruir a base.
