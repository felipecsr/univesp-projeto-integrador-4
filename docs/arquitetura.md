# Arquitetura do Projeto

## Fluxo geral

INEP/Censo Escolar → extração → tratamento → base analítica → Google Sheets → Google Apps Script → Web App.

## Componentes previstos

- **Python / Google Colab:** extração, tratamento, validação e análise dos dados.
- **Google Drive:** armazenamento de arquivos de trabalho e dados que não devem ser versionados no GitHub.
- **Google Sheets:** camada de dados curada para consumo pelo Web App.
- **Google Apps Script:** backend e publicação da aplicação web.
- **HTML, CSS e JavaScript:** interface e interações do dashboard.
- **GitHub:** versionamento de código, notebooks e documentação.

Esta arquitetura poderá ser refinada conforme os dados e requisitos do produto forem validados.
