# UNIVESP — Projeto Integrador 4

Projeto acadêmico do curso de Ciência de Dados da UNIVESP voltado à análise da infraestrutura escolar de Guaratinguetá (SP), utilizando dados públicos do Censo Escolar/INEP.

## Objetivo

Transformar dados públicos de infraestrutura escolar em informações simples de consultar, comparar e discutir, com foco em Guaratinguetá e em municípios paulistas de estrutura escolar semelhante.

## Recorte analítico

A análise trabalha com os Censos Escolares de **2023, 2024 e 2025**.

- 2025 é a fotografia mais recente.
- A unidade longitudinal é escola-ano, identificada por `CO_ENTIDADE` + `NU_ANO_CENSO`.
- O universo mantém somente escolas em funcionamento em cada edição.
- O primeiro recorte territorial é o estado de São Paulo, com Guaratinguetá como município-foco.
- Séries temporais usam somente variáveis cuja presença e semântica sejam compatíveis entre os anos.
- Em 2025, infraestrutura e matrículas passaram a vir de tabelas distintas; o pipeline recompõe a base por `CO_ENTIDADE`.

## Pipeline reproduzível

O pipeline principal está em `src/censo_pipeline.py`.

Ele:

1. lê os arquivos oficiais sem edição manual;
2. seleciona apenas as colunas necessárias;
3. filtra escolas ativas de São Paulo;
4. harmoniza 2023, 2024 e 2025;
5. valida chaves, domínios binários e contagens;
6. gera o painel escola-ano e artefatos de QA.

Os notebooks em `notebooks/` registram as etapas de ingestão, EDA, comparáveis, rede/zona e ponderação por matrículas. **A execução manual no Colab não é requisito de conclusão do projeto**: a validação técnica já foi executada sobre os arquivos oficiais e os resultados consolidados estão documentados no repositório.

Detalhes: [`docs/REPRODUTIBILIDADE.md`](docs/REPRODUTIBILIDADE.md).

## QA técnico consolidado

| Checagem | Resultado |
| --- | ---: |
| Escolas ativas em SP — 2023 | 30.580 |
| Escolas ativas em SP — 2024 | 30.746 |
| Escolas ativas em SP — 2025 | 30.817 |
| Municípios paulistas por ano | 645 |
| Linhas escola-ano no painel validado | 92.143 |
| Duplicidades na chave escola-ano | 0 |
| Escolas ativas em Guaratinguetá — 2025 | 92 |

Também foram verificados domínios 0/1 dos indicadores binários, ausência de contagens negativas e consistência entre o QA salvo e o QA recalculado.

## Resultados técnicos consolidados

Os principais resultados descritivos já estão registrados em tabelas prontas para uso no relatório:

- perfil anual de Guaratinguetá;
- evolução dos 11 indicadores de infraestrutura;
- grupo final de 10 municípios comparáveis;
- diferença entre percentual simples de escolas e ponderação por matrículas;
- regras de interpretação e limitações.

Ver [`docs/RESULTADOS_TECNICOS.md`](docs/RESULTADOS_TECNICOS.md).

## Base final de consumo

`src/build_consumption.py` produz as tabelas finais usadas pelo Web App.

A base inclui:

- `CONFIG`;
- `CATALOGO`;
- `COMPARAVEIS`;
- `MUNICIPIO_ANO`;
- `MUNICIPIO_REDE_2025`;
- `MUNICIPIO_ZONA_2025`;
- `ESCOLAS_2025`;
- `QA`.

Estrutura e controles: [`docs/BASE_CONSUMO.md`](docs/BASE_CONSUMO.md).

## Municípios comparáveis

A seleção não usa os próprios indicadores de infraestrutura. O método considera porte e estrutura escolar, incluindo número de escolas, matrículas, mediana de matrículas por escola, composição por rede e participação rural.

O grupo final de 2025 está documentado em [`docs/METODO_COMPARAVEIS.md`](docs/METODO_COMPARAVEIS.md).

## Ponderação por matrículas

A leitura principal do projeto é **percentual de escolas com o item**. A ponderação por matrículas foi mantida como visão complementar, porque responde a uma pergunta diferente: em que medida os estudantes estão concentrados em escolas que possuem determinada infraestrutura.

Detalhes e diferenças observadas: [`docs/PONDERACAO_MATRICULAS.md`](docs/PONDERACAO_MATRICULAS.md).

## Web App

A aplicação final foi construída com Google Apps Script + HTML/CSS/JavaScript e consome a base final em Google Sheets.

As quatro áreas principais são:

1. **Visão Geral**
2. **Comparações**
3. **Escolas**
4. **Sobre os dados**

**Aplicação publicada:**  
https://script.google.com/macros/s/AKfycbwN7KphXDuU-Yhjjv_C9GdCNlhHKb1IeP50xz_Thw_Q6HAXT4woKL-AKjYW26Tm-cvhOQ/exec

A arquitetura e as decisões de interface estão em [`docs/WIREFRAME_MVP.md`](docs/WIREFRAME_MVP.md).

## Fechamento do projeto

O projeto está concluído em sua camada técnica e analítica.

O repositório já reúne:

- pipeline reproduzível e notebooks versionados;
- QA consolidado;
- resultados técnicos em tabelas reutilizáveis;
- método de comparáveis;
- regras de ponderação por matrículas;
- base final de consumo;
- Web App publicado;
- documentação suficiente para sustentar relatório, análise crítica e apresentação.

A leitura final do produto parte diretamente do Web App e dos resultados consolidados em [`docs/RESULTADOS_TECNICOS.md`](docs/RESULTADOS_TECNICOS.md). Não há dependência de novas execuções técnicas ou de evidências manuais para considerar o trabalho concluído.

## Papel deste repositório

Este repositório funciona como vitrine técnica pública e histórico de checkpoints reproduzíveis.

Entram aqui:

- scripts e notebooks;
- documentação metodológica;
- resultados técnicos consolidados;
- código do Web App;
- link público da aplicação;
- material-base para relatório e apresentação.

Arquivos oficiais de origem, bases de trabalho e organização operacional do grupo permanecem no Google Drive compartilhado.

## Equipe

Projeto desenvolvido no âmbito do Projeto Integrador 4 da UNIVESP.
