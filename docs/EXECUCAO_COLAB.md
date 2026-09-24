# Execução humana no Google Colab — P03

Este roteiro registra a execução reproduzível do pipeline do Censo Escolar 2023–2025 antes da EDA.

## Objetivo

A execução deve produzir uma base analítica materializada no Google Drive e evidências suficientes para confirmar que o pipeline versionado no GitHub funciona no ambiente adotado pelo grupo.

## Notebook

Abra no Colab:

https://colab.research.google.com/github/felipecsr/univesp-projeto-integrador-4/blob/main/notebooks/01_ingestao_e_qa_censo.ipynb

Antes de executar, use **Arquivo → Salvar uma cópia no Drive**. A cópia executada deve permanecer com os outputs salvos.

Se a pasta compartilhada do PI4 não aparecer em `Meu Drive`, adicione um atalho dela ao Meu Drive antes de rodar o notebook.

## Execução

Execute as células em ordem, de cima para baixo. Não altere nenhum arquivo de `01_Dados/1_fonte_original`.

A execução deve:

1. montar o Google Drive;
2. registrar versão de Python/Pandas e commit da `main`;
3. conferir os quatro arquivos-fonte;
4. construir o painel escola-ano 2023–2025;
5. reproduzir os números estruturais já validados;
6. produzir o QA das variáveis;
7. mostrar o resumo de Guaratinguetá;
8. gravar uma pasta `execucao_colab_YYYYMMDD_HHMMSS` em `01_Dados/2_tratamentos_dados/base_analitica`.

## Evidências esperadas

Guardar:

- notebook executado com outputs;
- CSVs gerados automaticamente na pasta da execução;
- Print 1: conferência dos arquivos-fonte;
- Print 2: QA estrutural e mensagem de checkpoint reproduzido;
- Print 3: resumo de Guaratinguetá;
- Print 4: manifesto e lista dos arquivos gerados.

Não editar os CSVs produzidos manualmente.

## Critério para fechar P03

P03 pode ser concluído quando:

- o notebook terminar sem erro;
- os três anos reproduzirem os volumes esperados;
- os arquivos estiverem materializados em `base_analitica`;
- a cópia do notebook executado e os quatro prints estiverem preservados.

Depois disso, P04 reconcilia os artefatos dessa execução com a fonte e libera a base para EDA.
