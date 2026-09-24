# Resultados técnicos consolidados

Este documento reúne resultados já produzidos e validados pelo pipeline e pela base final de consumo do Web App. Ele existe para que relatório, apresentação e vídeo possam reutilizar números técnicos sem exigir uma nova execução manual apenas para gerar evidências.

## 1. QA estrutural

| Checagem | Resultado |
| --- | ---: |
| Escolas ativas em SP — 2023 | 30.580 |
| Escolas ativas em SP — 2024 | 30.746 |
| Escolas ativas em SP — 2025 | 30.817 |
| Municípios paulistas por ano | 645 |
| Linhas escola-ano no painel validado | 92.143 |
| Duplicidades escola-ano | 0 |
| Contagens negativas | 0 |
| Escolas ativas em Guaratinguetá — 2025 | 92 |
| Linhas em `MUNICIPIO_ANO` | 1.935 |
| Municípios comparáveis padrão | 10 + Guaratinguetá |

A base final também passou nos controles de domínio dos indicadores binários, consistência de agregações e rastreabilidade até o pipeline versionado.

## 2. Perfil anual de Guaratinguetá

| Ano | Escolas ativas | Matrículas | Salas utilizadas |
| ---: | ---: | ---: | ---: |
| 2023 | 91 | 26.502 | 1.029 |
| 2024 | 93 | 26.213 | 1.051 |
| 2025 | 92 | 25.168 | 1.015 |

## 3. Infraestrutura em Guaratinguetá — percentual de escolas

| Indicador | 2023 | 2024 | 2025 |
| --- | ---: | ---: | ---: |
| Água potável | 98,9% | 98,9% | 98,9% |
| Energia da rede pública | 100,0% | 100,0% | 100,0% |
| Esgoto da rede pública | 95,6% | 95,7% | 94,6% |
| Rampas de acessibilidade | 22,0% | 51,6% | 68,5% |
| Internet | 97,8% | 97,8% | 98,9% |
| Banda larga | 95,5% | 95,6% | 95,6% |
| Biblioteca | 28,6% | 35,5% | 35,9% |
| Laboratório de informática | 46,2% | 49,5% | 40,2% |
| Laboratório de ciências | 7,7% | 10,8% | 12,0% |
| Quadra de esportes | 51,6% | 53,8% | 54,3% |
| Refeitório | 75,8% | 77,4% | 78,3% |

Os percentuais acima usam como denominador as escolas com valor válido para cada indicador. Valores ausentes não são automaticamente convertidos para zero.

### Visualização gerada a partir dos resultados consolidados

![Evolução de indicadores selecionados em Guaratinguetá](assets/guaratingueta_evolucao.svg)

O arquivo é gerado por `src/generate_report_assets.py`, permitindo recriar a figura sem depender de edição manual.

## 4. Grupo final de municípios comparáveis — 2025

| Ordem estrutural | Município | Escolas | Matrículas |
| ---: | --- | ---: | ---: |
| 1 | Valinhos | 88 | 25.334 |
| 2 | Itatiba | 94 | 24.711 |
| 3 | Votorantim | 91 | 24.129 |
| 4 | Cubatão | 87 | 25.982 |
| 5 | Poá | 85 | 25.800 |
| 6 | Araras | 91 | 28.649 |
| 7 | Barretos | 98 | 27.496 |
| 8 | Catanduva | 81 | 24.108 |
| 9 | Jandira | 78 | 24.470 |
| 10 | Paulínia | 101 | 26.655 |

Referência do município-foco em 2025: **Guaratinguetá — 92 escolas e 25.168 matrículas**.

A infraestrutura não entra na escolha dos comparáveis. O grupo é selecionado a partir da estrutura escolar, para que os próprios resultados de infraestrutura permaneçam livres para comparação posterior.

## 5. Percentual simples × ponderação por matrículas — exemplos de 2025

| Indicador | % de escolas | % ponderado por matrículas | Diferença |
| --- | ---: | ---: | ---: |
| Quadra de esportes | 54,3% | 79,8% | +25,4 p.p. |
| Laboratório de informática | 40,2% | 61,3% | +21,1 p.p. |
| Biblioteca | 35,9% | 50,7% | +14,8 p.p. |
| Refeitório | 78,3% | 72,8% | -5,5 p.p. |

A diferença mostra por que as duas leituras não são equivalentes. O Web App usa **percentual de escolas** como padrão e oferece a ponderação por matrículas apenas como visão complementar.

## 6. Limitações e cautelas

- A análise é descritiva; não atribui causas às diferenças observadas.
- Recortes com menos de 5 escolas são sinalizados como base pequena. Em Guaratinguetá, a zona rural em 2025 tem apenas 4 escolas.
- Comparabilidade estrutural não significa equivalência socioeconômica completa entre municípios.
- Algumas variáveis podem sofrer alteração semântica entre edições do Censo. Por isso, tendências só são apresentadas quando a comparação temporal é considerada segura.
- `QT_MAT_MED` recebeu descrição diferente no dicionário de 2025 e não é usado automaticamente como série longitudinal no MVP.

## 7. Uso no relatório

Estas tabelas podem ser copiadas diretamente para o trabalho escrito, com adaptação apenas de estilo e numeração. A interpretação crítica, seleção de prints do Web App e discussão do que a ferramenta ajuda a enxergar permanecem como etapa humana final do grupo.
