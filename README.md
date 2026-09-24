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

A base final usada pelo Web App será disponibilizada em Google Sheets. Exports leves em CSV poderão ser publicados aqui quando forem úteis para transparência e reprodutibilidade.

## Papel deste repositório

Este repositório é a vitrine técnica pública do projeto e o histórico de checkpoints reproduzíveis.

Entram aqui, quando consolidados:

- notebooks e scripts;
- artefatos de dados leves;
- informações necessárias para compreender ou reproduzir os resultados;
- código do Web App;
- links e resultados finais do projeto.

A organização operacional do grupo, o Kanban e os arquivos vivos de trabalho permanecem no Google Drive compartilhado.

## Próxima etapa

Construir e validar a base analítica que alimentará a EDA de Guaratinguetá e a seleção objetiva de municípios paulistas comparáveis.

## Equipe

Projeto desenvolvido no âmbito do Projeto Integrador 4 da UNIVESP.
