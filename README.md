# UNIVESP — Projeto Integrador 4

Projeto acadêmico do curso de Ciência de Dados da UNIVESP voltado à análise da infraestrutura escolar de Guaratinguetá (SP), utilizando dados públicos do Censo Escolar/INEP.

## Objetivo

Transformar dados públicos de infraestrutura escolar em informações simples de consultar e comparar, com foco em Guaratinguetá e em recortes que façam sentido após a análise exploratória.

## Recorte atual

A análise trabalha com os Censos Escolares de **2023, 2024 e 2025**.

- 2025 é a fotografia mais recente.
- A unidade longitudinal é escola-ano, identificada por `CO_ENTIDADE` + `NU_ANO_CENSO`.
- O universo principal mantém somente escolas em funcionamento em cada edição.
- O primeiro recorte territorial é o estado de São Paulo, com Guaratinguetá como município-foco.
- Séries temporais usam somente variáveis cuja presença e semântica sejam compatíveis entre os três anos.

Em 2025 o INEP mudou o formato de distribuição: infraestrutura permanece na tabela de escolas, enquanto contagens de matrículas passam a uma tabela própria. O pipeline trata essa diferença por junção em `CO_ENTIDADE`.

## Pipeline reproduzível

O primeiro pipeline está em `src/censo_pipeline.py`.

Ele:

1. lê os arquivos oficiais sem edição manual;
2. seleciona apenas as colunas necessárias;
3. filtra escolas ativas de São Paulo;
4. harmoniza o formato de 2023, 2024 e 2025;
5. valida chaves, domínios binários e contagens;
6. gera o painel escola-ano e artefatos de QA.

O notebook `notebooks/01_ingestao_e_qa_censo.ipynb` reproduz o processo no Google Colab usando os arquivos preservados no Google Drive do projeto. O roteiro de execução humana e das evidências esperadas está em [`docs/EXECUCAO_COLAB.md`](docs/EXECUCAO_COLAB.md).

## QA do primeiro pipeline

A validação executada sobre os arquivos oficiais reais resultou em:

| Ano | Escolas ativas em SP | Municípios | Escolas sem `QT_MAT_BAS` |
| ---: | ---: | ---: | ---: |
| 2023 | 30.580 | 645 | 367 |
| 2024 | 30.746 | 645 | 345 |
| 2025 | 30.817 | 645 | 378 |

Também foram verificados:

- ausência de duplicidades na chave escola-ano;
- domínio 0/1 nos indicadores binários selecionados;
- ausência de contagens negativas;
- presença dos 645 municípios paulistas nos três anos;
- junção one-to-one válida entre Escola e Matrícula em 2025.

Os arquivos sem matrícula não são automaticamente convertidos para zero; a ausência é preservada para tratamento analítico explícito.

## Organização dos dados

Os arquivos oficiais de origem e os dados de trabalho permanecem no Google Drive compartilhado e não são versionados integralmente neste repositório.

Não adotamos uma arquitetura obrigatória de camadas como bronze/silver/gold. Etapas intermediárias existem somente quando cumprem uma função técnica clara.

A estrutura atual distingue:

- fonte original, preservada sem edição;
- tratamentos e base analítica para EDA;
- base final de consumo do Web App.

A base final de consumo do Web App já foi materializada em Google Sheets no Drive do projeto. Sua construção é reproduzível por `src/build_consumption.py`; a estrutura está documentada em [`docs/BASE_CONSUMO.md`](docs/BASE_CONSUMO.md).

## Papel deste repositório

Este repositório é a vitrine técnica pública do projeto e o histórico de checkpoints reproduzíveis.

Entram aqui, quando consolidados:

- notebooks e scripts;
- artefatos de dados leves;
- informações necessárias para compreender ou reproduzir os resultados;
- código do Web App;
- links e resultados finais do projeto.

A organização operacional do grupo, o Kanban e os arquivos vivos de trabalho permanecem no Google Drive compartilhado.

## EDA e base de consumo

A camada analítica e a preparação da base de consumo estão consolidadas no repositório:

- `notebooks/02_eda_guaratingueta.ipynb`: perfil descritivo de Guaratinguetá, infraestrutura, rede, zona e permanência das escolas;
- `notebooks/03_comparaveis_sp.ipynb`: perfil dos 645 municípios paulistas e construção de um pool exploratório de comparáveis;
- `notebooks/04_rede_zona.ipynb`: diferenças de infraestrutura por rede administrativa e localização urbana/rural;
- `notebooks/05_ponderacao_matriculas.ipynb`: teste de percentual simples de escolas versus ponderação por matrículas;
- `src/eda.py`: funções reutilizáveis dessas análises;
- [`docs/METODO_COMPARAVEIS.md`](docs/METODO_COMPARAVEIS.md): critérios e limites do método de comparabilidade;
- [`docs/PONDERACAO_MATRICULAS.md`](docs/PONDERACAO_MATRICULAS.md): regra e interpretação do teste de ponderação.

A validação técnica de P04 e a EDA foram executadas sobre os arquivos oficiais. As execuções manuais no Colab permanecem como trilha adicional de reprodução e evidência do grupo.

## Base de consumo

`src/build_consumption.py` produz as tabelas finais por escola e agregadas usadas pelo Web App. O escopo inclui 2025 como fotografia principal, tendências 2023–2025, comparações por rede/zona, consulta por escola e grupo padrão de 10 municípios comparáveis.

## Web App — MVP

A arquitetura funcional do MVP está documentada em [`docs/WIREFRAME_MVP.md`](docs/WIREFRAME_MVP.md). O código inicial do Web App está em `webapp/`, com backend em Apps Script e frontend HTML/CSS/JavaScript apontando para a base final de consumo.

O MVP foi organizado em quatro telas: Visão Geral, Comparações, Escolas e Sobre os dados.

## Próxima etapa

Validar a execução do Web App no Apps Script e completar os testes das consultas e visualizações.

## Equipe

Projeto desenvolvido no âmbito do Projeto Integrador 4 da UNIVESP.
