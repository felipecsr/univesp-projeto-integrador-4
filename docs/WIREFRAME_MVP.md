# Wireframe funcional do Web App — MVP

## Objetivo

Disponibilizar uma leitura simples da infraestrutura escolar de Guaratinguetá, com visão atual, tendência temporal, comparações com municípios estruturalmente semelhantes e consulta por escola.

O MVP terá **quatro telas**. Rede, zona, série temporal e ponderação são controles dentro das telas; não viram páginas próprias.

## Navegação

Menu principal:

1. **Visão Geral**
2. **Comparações**
3. **Escolas**
4. **Sobre os dados**

A aplicação abre em **Visão Geral**.

---

## 1. Visão Geral — Guaratinguetá

### Objetivo
Responder rapidamente: como está a infraestrutura escolar do município e como ela mudou no período disponível?

### Controles
- Ano: 2023, 2024, 2025; padrão = 2025.
- Rede administrativa: Estadual, Municipal, Privada e Federal quando aplicável.
- Zona: Urbana / Rural.
- Alternância de leitura: percentual de escolas / percentual ponderado por matrículas.

### Regra importante
- Rede e zona são filtros da fotografia de **2025**.
- A série 2023–2025 é apresentada no agregado municipal para evitar misturar recortes que ainda não fazem parte da base final histórica por rede/zona.
- Ponderação por matrículas é secundária; a leitura padrão é percentual de escolas.
- Bases com menos de 5 escolas devem ser sinalizadas.

### KPIs
- Escolas ativas.
- Matrículas.
- Salas utilizadas.

### Conteúdo principal
- Cards dos 11 indicadores de infraestrutura.
- Gráfico de tendência 2023–2025 para o indicador selecionado.
- Informação de denominador válido quando houver nulos.

### Interação
Selecionar um indicador nos cards atualiza o gráfico temporal e os detalhes daquele indicador.

---

## 2. Comparações

### Objetivo
Responder: como Guaratinguetá se compara a municípios paulistas com estrutura escolar semelhante?

### Grupo padrão
Guaratinguetá + 10 municípios comparáveis definidos pela análise estrutural de 2025.

### Controles
- Indicador.
- Ano.
- Município comparável individual ou grupo completo.
- Alternância percentual de escolas / percentual ponderado por matrículas, quando aplicável.

### Conteúdo principal
- Gráfico comparativo do indicador selecionado.
- Destaque visual para Guaratinguetá.
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
Para cada indicador binário, mostrar o percentual correspondente do município em 2025 como referência, sem transformar a escola em ranking.

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

## Critério de fechamento de A01

A01 está concluída quando estas quatro telas, seus controles e suas regras de interação forem aceitos como arquitetura funcional do MVP. Ajustes visuais finos permanecem para A03/A04.