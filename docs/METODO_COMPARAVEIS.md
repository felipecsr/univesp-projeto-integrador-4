# Método exploratório para municípios comparáveis

A comparação de Guaratinguetá com outros municípios deve evitar escolher pares com base nos próprios indicadores de infraestrutura que depois serão comparados.

## Primeira etapa

O pool inicial usa o Censo Escolar de 2025 e considera características estruturais do sistema escolar:

- número de escolas ativas;
- total de matrículas;
- mediana de matrículas por escola;
- composição das escolas por dependência administrativa;
- participação de escolas rurais.

Os indicadores de infraestrutura não entram no cálculo de semelhança.

## Filtro de porte

O notebook testa janelas de ±50%, ±40% e ±30% em torno de Guaratinguetá para:

- número de escolas;
- total de matrículas.

A janela padrão inicial é ±40%, somente para inspeção exploratória.

## Ordenação exploratória

Dentro do pool, a coluna `distancia_estrutural` combina diferenças relativas de porte e diferenças médias na composição por rede/zona.

Essa ordenação:

- ajuda a inspecionar os candidatos;
- não é um modelo de machine learning;
- não define automaticamente o grupo final;
- não deve ser interpretada como qualidade ou ranking dos municípios.

## Decisão final

O grupo comparável será congelado apenas após a EDA.

Se a distribuição mostrar que o Censo Escolar não captura bem o porte municipal, poderemos acrescentar população ou outro indicador externo oficial. Isso será uma decisão explícita, e não uma exigência prévia do pipeline.
