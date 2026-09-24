# Ponderação por matrículas

A análise pode responder duas perguntas diferentes:

1. **Percentual de escolas com o item**: cada escola tem o mesmo peso.
2. **Percentual aproximado de estudantes matriculados em escolas com o item**: cada escola é ponderada por `QT_MAT_BAS`.

As duas leituras são válidas, mas não são intercambiáveis.

## Regra de cálculo

Para cada indicador binário de infraestrutura:

- cálculo simples: média do indicador entre escolas com valor válido;
- cálculo ponderado: soma de `indicador × QT_MAT_BAS` dividida pela soma de `QT_MAT_BAS` das escolas válidas.

Escolas sem matrícula informada não entram no denominador ponderado.

## Resultado do teste em Guaratinguetá — 2025

| Indicador | % de escolas | % ponderado por matrículas | Diferença |
| --- | ---: | ---: | ---: |
| Quadra de esportes | 54,3% | 79,8% | +25,4 p.p. |
| Laboratório de informática | 40,2% | 61,3% | +21,1 p.p. |
| Biblioteca | 35,9% | 50,7% | +14,8 p.p. |
| Refeitório | 78,3% | 72,8% | -5,5 p.p. |

As diferenças mostram que a localização dos estudantes entre escolas altera a leitura. Por exemplo, um item pode estar presente em pouco mais da metade das escolas, mas concentrado em escolas de maior porte.

## Decisão final do projeto

A leitura **padrão** do Web App e do relatório é **percentual de escolas com o item**.

A ponderação por matrículas permanece disponível como **visão complementar**, escondida em opções de leitura da interface. Essa escolha mantém a interpretação principal mais simples e direta para o público, sem perder a possibilidade de investigar a distribuição dos estudantes.

## Como interpretar

- percentual simples responde: *em quantas escolas o item está presente?*
- ponderação responde aproximadamente: *qual proporção das matrículas está em escolas que possuem o item?*

A segunda leitura não mede uso efetivo da infraestrutura por cada estudante e não deve ser apresentada dessa forma.

## Uso no relatório

Não é necessário apresentar os dois cálculos para todos os indicadores. A tabela acima pode ser usada para justificar metodologicamente por que a ponderação foi mantida como recurso secundário no produto final.
