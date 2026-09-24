# Método para municípios comparáveis

A comparação de Guaratinguetá com outros municípios evita escolher pares com base nos próprios indicadores de infraestrutura que depois serão analisados.

## Critério estrutural

O método usa o Censo Escolar de 2025 e considera características do sistema escolar:

- número de escolas ativas;
- total de matrículas;
- mediana de matrículas por escola;
- composição das escolas por dependência administrativa;
- participação de escolas rurais.

Os indicadores de infraestrutura **não entram no cálculo de semelhança**.

## Filtro de porte

A análise testou janelas de ±50%, ±40% e ±30% em torno de Guaratinguetá para:

- número de escolas;
- total de matrículas.

A janela padrão adotada foi **±40%**, que produziu 47 municípios candidatos antes da ordenação estrutural.

## Ordenação estrutural

Dentro do pool, a coluna `distancia_estrutural` combina diferenças relativas de porte e diferenças na composição por rede/zona.

Essa distância:

- serve para ordenar candidatos estruturalmente semelhantes;
- não é um modelo de machine learning;
- não mede qualidade;
- não é um ranking de desempenho educacional.

## Grupo final congelado — 2025

Referência de Guaratinguetá: **92 escolas, 25.168 matrículas, mediana de 208 matrículas por escola, 17,4% estadual, 50,0% municipal, 32,6% privada e 4,3% rural**.

| Ordem | Município | Escolas | Matrículas | Distância estrutural |
| ---: | --- | ---: | ---: | ---: |
| 1 | Valinhos | 88 | 25.334 | 0,100 |
| 2 | Itatiba | 94 | 24.711 | 0,112 |
| 3 | Votorantim | 91 | 24.129 | 0,117 |
| 4 | Cubatão | 87 | 25.982 | 0,148 |
| 5 | Poá | 85 | 25.800 | 0,151 |
| 6 | Araras | 91 | 28.649 | 0,167 |
| 7 | Barretos | 98 | 27.496 | 0,171 |
| 8 | Catanduva | 81 | 24.108 | 0,188 |
| 9 | Jandira | 78 | 24.470 | 0,209 |
| 10 | Paulínia | 101 | 26.655 | 0,211 |

Este é o grupo utilizado no Web App final.

## Interpretação

A comparação responde a uma pergunta específica: **como Guaratinguetá se posiciona em indicadores de infraestrutura quando colocada ao lado de municípios com estrutura escolar semelhante?**

Ela não pretende afirmar que os municípios sejam equivalentes em renda, população total, políticas públicas ou demais características socioeconômicas.

## Limite metodológico

O método privilegia uma comparação coerente com a própria base do Censo Escolar. Variáveis externas poderiam refinar a comparabilidade, mas não foram necessárias para o escopo do MVP e não foram incorporadas ao grupo final.
