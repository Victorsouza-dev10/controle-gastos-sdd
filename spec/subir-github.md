# Spec: Subir o projeto para um NOVO repositório no GitHub

## Objetivo
Gerar a lista de comandos para publicar a pasta aula1 num repositório
novo e separado no GitHub (conta Victorsouza-dev10), sem mexer em
nenhum repositório que já exista.

## Regra principal
NÃO executar nenhum comando. Apenas mostrar os comandos, na ordem,
com uma explicação curta de cada um, espere minha ordem para executar.

## Antes de escrever os comandos, verificar
1. Rodar `git rev-parse --show-toplevel` para saber se a aula1 já está
   dentro de algum repositório Git.
   - Se a raiz do Git for a própria aula1, usar o repositório atual.
   - Se for uma pasta acima da aula1, AVISAR e propor comandos que não
     criem um repositório dentro de outro nem misturem a aula1 com
     outros projetos.
2. Rodar `git remote -v` e avisar se já existir um remote `origin`
   apontando para outro repositório. Nesse caso, NÃO sobrescrever:
   propor remover o remote antigo só da aula1, ou usar outro nome.
3. Confirmar que existe `.gitignore` na raiz da aula1 ignorando
   `__pycache__/`, `*.pyc`, `.pytest_cache/`, `*.db` e `.env`.
4. Procurar chaves, senhas ou tokens em arquivos que seriam versionados
   e avisar se achar algum.

## Comandos que devem ser listados, nesta ordem
1. Criar o repositório novo no GitHub (https://github.com/new):
   - nome sugerido: controle-gastos-sdd
   - visibilidade pública
   - SEM marcar README, .gitignore ou licença (o repositório precisa
     nascer vazio)
2. `git init` (só se a aula1 ainda não for um repositório)
3. `git branch -M main`
4. `git rm -r --cached` para tirar do Git o que já estava rastreado e
   deve ser ignorado (`__pycache__`, `.pytest_cache`, `transacoes.db`),
   sem apagar do disco
5. `git status` para eu conferir o que vai subir
6. `git add .`
7. `git commit -m "Primeira versão: controle de gastos com API e dashboard"`
8. `git remote add origin https://github.com/Victorsouza-dev10/controle-gastos-sdd.git`
9. `git push -u origin main`

## Critérios de aceite
- O repositório é novo, com o nome controle-gastos-sdd.
- Nenhum repositório existente (como o carteira-banco) é alterado.
- Nenhum `.pyc`, `__pycache__`, `.pytest_cache`, `.db` ou `.env` sobe.
- Nenhum comando usa `--force` ou `-f`.
- Cada comando vem com uma linha dizendo o que faz.

## Fora do escopo
- Executar os comandos.
- Alterar código, specs ou README.
- Criar o repositório pelo terminal.