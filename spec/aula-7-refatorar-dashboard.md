# Spec — Aula 7: Refatorar o dashboard (separar HTML, CSS e JS)

**Projeto:** Controle de Gastos Pessoais
**Stack:** Python 3.11+ · FastAPI · SQLite · Pydantic

## Convenções gerais do projeto
(mesmo bloco das outras specs)

---

**Objetivo (por quê):** organizar o front-end para facilitar manutenção, sem mudar o comportamento.

**Contexto:** o dashboard da Aula 6 funciona, mas está num único arquivo, com `<style>` e `<script>` inline.

**Requisitos funcionais:**
1. Mover o CSS para `static/style.css`.
2. Mover o JavaScript para `static/app.js`.
3. Deixar o `static/index.html` apenas com a estrutura, referenciando os dois arquivos.
4. Expor a pasta `static/` no FastAPI e manter a rota `GET /` servindo o dashboard.

**Critérios de aceite:**
- O dashboard abre em `GET /` e é visualmente idêntico ao anterior.
- Cards de entradas, saídas e saldo e o gráfico por categoria continuam funcionando.
- O `index.html` não contém `<style>` nem código dentro de `<script>` (a tag `<script src>` do Chart.js por CDN é permitida).
- Os testes da Aula 5 continuam passando.

**Fora de escopo:** mudar o visual, adicionar funcionalidades, alterar endpoints ou o back-end além de servir os arquivos estáticos.

**Restrições técnicas:** não alterar nomes de IDs e classes usados pelo JS; nenhuma lógica nova, apenas mover o código existente.