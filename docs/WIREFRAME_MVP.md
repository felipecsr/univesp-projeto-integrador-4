# Wireframe funcional do Web App — MVP

## Objetivo

Disponibilizar uma leitura simples da infraestrutura escolar de Guaratinguetá, com visão atual, tendência temporal, comparações com municípios estruturalmente semelhantes e consulta por escola.

O MVP final possui **quatro telas**. A navegação principal fica em uma **barra lateral à esquerda** no desktop e se adapta para navegação horizontal em telas pequenas. Rede, zona, série temporal e ponderação são controles dentro das telas; não viram páginas próprias.

## Navegação

Menu principal:

1. **Visão Geral**
2. **Comparações**
3. **Escolas**
4. **Sobre os dados**

A aplicação publicada abre em **Visão Geral**.

---

## 1. Visão Geral — Guaratinguetá

### Objetivo
Responder rapidamente: como está a infraestrutura escolar do município e como ela mudou no período disponível?

### Controles
- Ano: 2023, 2024, 2025; padrão = 2025.
- Não há filtro de rede ou zona no topo da Visão Geral.
- A leitura principal nessa tela é percentual de escolas.

### Regra importante
- A Visão Geral é sempre municipal e mostra somente Guaratinguetá.
- O ano selecionado altera KPIs e o perfil horizontal dos 11 indicadores.
- A série 2023–2025 permanece municipal.
- Rede e zona aparecem como **gráficos de detalhamento de 2025**, não como filtros da visão principal.
- Bases com menos de 5 escolas devem ser sinalizadas.

### KPIs
- Escolas ativas.
- Matrículas.
- Salas utilizadas.

### Conteúdo principal
- KPIs de escolas, matrículas e salas.
- Gráfico horizontal com os 11 indicadores do ano selecionado, ordenados do maior para o menor percentual.
- Gráfico de tendência 2023–2025 para o indicador selecionado.
- Gráficos de detalhamento por rede administrativa e por zona em 2025 para o mesmo indicador.
- Informação de denominador válido quando houver nulos.

### Interação
Clicar em qualquer barra do gráfico horizontal seleciona o indicador. A seleção destaca a barra, atualiza imediatamente a evolução 2023–2025 e atualiza os dois gráficos inferiores de rede e zona. Os cards individuais de indicadores foram removidos por redundância.

---

## 2. Comparações

### Objetivo
Responder: como Guaratinguetá se compara a municípios paulistas com estrutura escolar semelhante?

### Grupo padrão
Guaratinguetá + 10 municípios comparáveis definidos pela análise estrutural de 2025.

### Controles
- Indicador.
- Anos exibidos: 2023, 2024 e 2025 selecionados independentemente; padrão = os três juntos.
- Município comparável individual ou grupo completo.
- Ponderação por matrículas disponível apenas em **Opções de leitura**.

### Conteúdo principal
- Gráfico comparativo do indicador selecionado com os anos escolhidos lado a lado e valores visíveis nas barras.
- Destaque visual para Guaratinguetá.
- Gráfico de perfil geral: Guaratinguetá versus média simples dos 10 comparáveis nos 11 indicadores.
- Gráfico de dispersão/bolhas: indicador no eixo X, matrículas no eixo Y e número de escolas no tamanho da bolha; Guaratinguetá destacada.
- Tabela curta com município, valor e denominador.
- Contexto estrutural dos comparáveis: escolas e matrículas.

### Regra
A ordenação é apenas uma forma de visualização do indicador escolhido. O Web App não cria índice geral de qualidade nem ranking composto.

---

## 3. Escolas

### Objetivo
Permitir consulta direta de uma escola de Guaratinguetá.

### Controles
- Busca por nome da escola.
- Rede.
- Zona.

### Conteúdo da ficha
- Nome.
- Rede.
- Zona.
- Matrículas.
- Salas utilizadas.
- Situação de cada um dos 11 indicadores de infraestrutura.

### Comparação contextual
Para cada indicador binário, mostrar o percentual correspondente do município em 2025 como referência, sem transformar a escola em ranking. A ficha inclui um gráfico horizontal escola × Guaratinguetá e uma opção para acrescentar a média dos 10 municípios comparáveis.

### Regra
A consulta por escola usa a fotografia de 2025, que é a base final por escola do MVP.

---

## 4. Sobre os dados

### Conteúdo
- Fonte: Censo Escolar / INEP.
- Anos: 2023, 2024 e 2025.
- Unidade de análise: escola ativa em cada ano.
- Definição resumida dos indicadores.
- Regra de valores ausentes.
- Critério de municípios comparáveis.
- Explicação do percentual simples e da ponderação por matrículas.
- Alerta para bases pequenas.
- Nota de que a análise é descritiva e não estabelece causalidade.
- Observação específica de que QT_MAT_MED não é usado automaticamente como série temporal no MVP devido à mudança de descrição em 2025.

---

## Regras de interface

- Desktop e celular devem usar a mesma estrutura funcional.
- Filtros ficam visíveis no início da tela.
- Evitar excesso de gráficos simultâneos.
- Mostrar sempre unidade e denominador do percentual.
- Sinalizar base pequena junto ao resultado, não apenas em nota metodológica.
- Estado inicial deve ser utilizável sem qualquer configuração: Guaratinguetá, 2025, percentual por escolas.
- Não implementar índice composto ou machine learning no MVP.

## Relação com a base de consumo

| Tela | Abas principais |
| --- | --- |
| Visão Geral | CONFIG, CATALOGO, MUNICIPIO_ANO, MUNICIPIO_REDE_2025, MUNICIPIO_ZONA_2025 |
| Comparações | COMPARAVEIS, MUNICIPIO_ANO, MUNICIPIO_REDE_2025, MUNICIPIO_ZONA_2025 |
| Escolas | ESCOLAS_2025, MUNICIPIO_ANO |
| Sobre os dados | CONFIG, CATALOGO |

## Desempenho de carregamento

- A aplicação carrega primeiro apenas a Visão Geral.
- Comparações, Escolas e Sobre os dados são carregadas sob demanda quando o usuário abre a seção.
- A lista de escolas de Guaratinguetá é carregada uma única vez e filtrada no navegador.
- O backend evita ler repetidamente a tabela completa de escolas de SP: localiza e lê somente o bloco do município-foco, com cache temporário.
- A configuração inicial pode ser reaproveitada no navegador por curto período para reduzir roundtrips sem alterar a fonte oficial.

## Convenções visuais da versão final

- Valores percentuais aparecem diretamente nas barras e nos pontos da série temporal; tooltip permanece como detalhe adicional.
- Guaratinguetá usa destaque amarelo nas comparações.
- A barra de filtros muda discretamente de tonalidade quando fica presa ao topo durante a rolagem.
- A interface mostra estado de **Atualizando dados…** e **Dados carregados** durante chamadas ao backend.
- Com apenas três anos e necessidade de combinações não contíguas (por exemplo, 2023 + 2025), seletores independentes de ano são mais adequados do que um slider contínuo.

## Estado final

O Web App foi concluído e publicado em 24/09/2026.

**URL pública:**  
https://script.google.com/macros/s/AKfycbwN7KphXDuU-Yhjjv_C9GdCNlhHKb1IeP50xz_Thw_Q6HAXT4woKL-AKjYW26Tm-cvhOQ/exec

As decisões documentadas acima correspondem à arquitetura efetivamente implementada. Alterações posteriores devem ser tratadas como evolução do produto, não como pendência do MVP acadêmico.
