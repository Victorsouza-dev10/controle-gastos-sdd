# Spec: Gerar o README do projeto

## Objetivo
Criar um README.md na raiz da aula1 que explique o projeto para quem
abrir o repositório no GitHub, com base no que realmente existe no código.

## Antes de escrever
1. Ler as pastas database, models, routes, static e spec, além do
   arquivo principal (main.py) e do app.js.
2. Listar as rotas da API e as telas do dashboard que existem de fato.
3. Não descrever nenhuma funcionalidade que não esteja no código.
   Se tiver dúvida, deixar de fora.

## Conteúdo do README
1. Título e descrição curta: um controle de gastos pessoais com API
   e dashboard (entradas, saídas, saldo e gastos por categoria).
2. Funcionalidades: só as que existem hoje.
3. Tecnologias: linguagem, framework da API, banco de dados e
   biblioteca do gráfico, conforme o código.
4. Estrutura de pastas: o que cada pasta faz, em uma linha.
5. Como rodar: instalar dependências, subir o servidor e a URL
   do dashboard e do /docs. Os comandos devem estar corretos para Windows.
6. Como rodar os testes (pytest), se existirem.
7. Seção "Como este projeto foi feito":
   - Projeto criado como exercício do curso de Spec Driven Development
     (SDD) com Claude Code.
   - A maior parte do código foi gerada por IA (Claude Code) a partir
     de specs escritas por mim, que estão na pasta spec.
   - Meu papel: escrever as specs, revisar, testar e ajustar.
   - Escrever de forma honesta e direta, sem exagerar nem diminuir.
8. Autor: Victor Souza, com link do GitHub.

## Critérios de aceite
- Todo comando do README funciona se copiado e colado.
- Todo item de "Funcionalidades" existe no código.
- A seção sobre IA está clara para quem ler.
- O README tem menos de 150 linhas e está em português.

## Fora do escopo
- Alterar código, specs ou arquivos que não sejam o README.md.