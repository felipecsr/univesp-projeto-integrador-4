# Ponderação por matrículas

A análise pode responder duas perguntas diferentes:

1. **Percentual de escolas com o item**: cada escola tem o mesmo peso.
2. **Percentual aproximado de estudantes matriculados em escolas com o item**: cada escola é ponderada por `QT_MAT_BAS`.

As duas leituras são válidas, mas respondem perguntas diferentes.

## Regra do teste

Para cada indicador binário de infraestrutura e ano:

- cálculo simples: média do indicador entre escolas com valor válido;
- cálculo ponderado: soma de `indicador × QT_MAT_BAS` dividida pela soma de `QT_MAT_BAS` das escolas válidas.

Escolas sem matrícula informada não entram no denominador ponderado e são contabilizadas separadamente.

## Uso no projeto

O notebook `05_ponderacao_matriculas.ipynb` compara os dois resultados e mede a diferença em pontos percentuais.

A decisão final sobre qual leitura usar no Web App será tomada somente após a revisão da EDA. É possível manter as duas: uma visão por escola e outra visão aproximada por estudantes, desde que a interface deixe o denominador explícito.
