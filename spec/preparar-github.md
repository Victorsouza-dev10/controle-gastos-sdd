# Spec: Preparar o projeto para o GitHub

## Objetivo
Deixar o repositório limpo, versionando só código e documentação.

## Requisitos
1. Existir um `.gitignore` na raiz da `aula1` ignorando:
   `__pycache__/`, `*.pyc`, `.pytest_cache/`, `*.db`, `.env`
2. Arquivos já rastreados que se encaixem nessas regras devem sair do
   Git (`git rm --cached`), sem serem apagados do disco.
3. Não pode haver chaves, senhas ou tokens em nenhum arquivo versionado.
4. O README deve explicar o que o projeto faz e como rodar
   (instalar dependências e subir o servidor).

## Critérios de aceite
- `git status` não lista `.pyc`, `__pycache__`, `.pytest_cache` nem `transacoes.db`.
- O projeto continua rodando normalmente depois da limpeza.
- Um `git clone` do repositório mais as instruções do README sobem o app do zero.

## Fora do escopo
- Alterar a lógica da API ou do dashboard