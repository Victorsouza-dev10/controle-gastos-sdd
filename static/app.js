// Formata valor para moeda brasileira
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

// Mostra mensagem no formulário
function showFormMessage(message, isError = false) {
    const messageDiv = document.getElementById('form-message');
    messageDiv.textContent = message;
    messageDiv.className = 'form-message ' + (isError ? 'error' : 'success');
    messageDiv.style.display = 'block';

    // Esconder após 5 segundos se for sucesso
    if (!isError) {
        setTimeout(() => {
            messageDiv.style.display = 'none';
        }, 5000);
    }
}

// Mostra mensagem de zerar histórico
function showZerarMessage(message, isError = false) {
    const messageDiv = document.getElementById('zerar-message');
    messageDiv.textContent = message;
    messageDiv.className = 'form-message ' + (isError ? 'error' : 'success');
    messageDiv.style.display = 'block';

    // Esconder após 5 segundos se for sucesso
    if (!isError) {
        setTimeout(() => {
            messageDiv.style.display = 'none';
        }, 5000);
    }
}

// Define data padrão para hoje
function setDefaultDate() {
    const hoje = new Date();
    const dataFormatada = hoje.toISOString().split('T')[0];
    document.getElementById('data').value = dataFormatada;
}

// Busca categorias para preencher o select
async function fetchCategorias() {
    try {
        const response = await fetch('/categorias');
        if (!response.ok) throw new Error('Erro ao buscar categorias');
        const categorias = await response.json();

        const select = document.getElementById('categoria');
        categorias.forEach(cat => {
            const option = document.createElement('option');
            option.value = cat.id;
            option.textContent = cat.nome;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Erro ao buscar categorias:', error);
    }
}

// Atualiza cards de saldo
function updateSaldoCards(data) {
    document.getElementById('entradas').textContent = formatCurrency(parseFloat(data.entradas));
    document.getElementById('saidas').textContent = formatCurrency(parseFloat(data.saidas));
    const saldo = parseFloat(data.saldo);
    document.getElementById('saldo').textContent = formatCurrency(saldo);

    const saldoCard = document.getElementById('saldo-card');
    if (saldo < 0) {
        saldoCard.classList.add('negativo');
    } else {
        saldoCard.classList.remove('negativo');
    }
}

// Renderiza gráfico de gastos por categoria
function renderChart(categorias) {
    const ctx = document.getElementById('gastosChart').getContext('2d');
    const loading = document.getElementById('chart-loading');
    const errorDiv = document.getElementById('chart-error');

    loading.style.display = 'none';
    errorDiv.style.display = 'none';

    if (!categorias || categorias.length === 0) {
        errorDiv.textContent = 'Nenhum gasto cadastrado para o mês atual.';
        errorDiv.style.display = 'block';
        return;
    }

    const labels = categorias.map(c => c.categoria);
    const data = categorias.map(c => parseFloat(c.total));

    // Cores para o gráfico
    const colors = [
        'rgba(239, 68, 68, 0.8)',   // vermelho
        'rgba(249, 115, 22, 0.8)',  // laranja
        'rgba(234, 179, 8, 0.8)',   // amarelo
        'rgba(34, 197, 94, 0.8)',   // verde
        'rgba(59, 130, 246, 0.8)',  // azul
        'rgba(168, 85, 247, 0.8)',  // roxo
        'rgba(236, 72, 153, 0.8)',  // rosa
        'rgba(20, 184, 166, 0.8)',  // teal
    ];
    const borderColors = colors.map(c => c.replace('0.8', '1'));

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                label: 'Gastos por Categoria',
                data: data,
                backgroundColor: colors.slice(0, labels.length),
                borderColor: borderColors.slice(0, labels.length),
                borderWidth: 2,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        font: {
                            size: 13
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.raw;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${context.label}: ${formatCurrency(value)} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Busca saldo total
async function fetchSaldo() {
    try {
        const response = await fetch('/saldo');
        if (!response.ok) throw new Error('Erro ao buscar saldo');
        const data = await response.json();
        updateSaldoCards(data);
    } catch (error) {
        console.error('Erro ao buscar saldo:', error);
    }
}

// Busca resumo do mês atual
async function fetchResumo() {
    const hoje = new Date();
    const mesAtual = hoje.getFullYear() + '-' + String(hoje.getMonth() + 1).padStart(2, '0');

    try {
        const response = await fetch(`/resumo?mes=${mesAtual}`);
        if (!response.ok) throw new Error('Erro ao buscar resumo');
        const data = await response.json();
        renderChart(data.por_categoria);
    } catch (error) {
        console.error('Erro ao buscar resumo:', error);
        const errorDiv = document.getElementById('chart-error');
        errorDiv.textContent = 'Erro ao carregar gráfico: ' + error.message;
        errorDiv.style.display = 'block';
        document.getElementById('chart-loading').style.display = 'none';
    }
}

// Busca todas as transações
async function fetchAllTransacoes() {
    try {
        const response = await fetch('/transacoes');
        if (!response.ok) throw new Error('Erro ao buscar transações');
        return await response.json();
    } catch (error) {
        console.error('Erro ao buscar transações:', error);
        throw error;
    }
}

// Deleta transações por tipo
async function zerarHistorico(tipo) {
    // tipo: 'entrada', 'saida', ou 'tudo'
    const btnId = tipo === 'entrada' ? 'btn-zerar-entradas' :
                  tipo === 'saida' ? 'btn-zerar-saidas' : 'btn-zerar-saldo';
    const btn = document.getElementById(btnId);

    const confirmMsg = tipo === 'entrada'
        ? 'Tem certeza que deseja apagar TODAS as entradas? Esta ação não pode ser desfeita.'
        : tipo === 'saida'
        ? 'Tem certeza que deseja apagar TODAS as saídas? Esta ação não pode ser desfeita.'
        : 'Tem certeza que deseja apagar TODO o histórico (todas as transações)? Esta ação não pode ser desfeita.';

    if (!confirm(confirmMsg)) {
        return;
    }

    btn.disabled = true;
    btn.textContent = '⏳';

    try {
        const transacoes = await fetchAllTransacoes();

        let transacoesParaDeletar;
        if (tipo === 'tudo') {
            transacoesParaDeletar = transacoes;
        } else {
            transacoesParaDeletar = transacoes.filter(t => t.tipo === tipo);
        }

        if (transacoesParaDeletar.length === 0) {
            showZerarMessage(`Nenhuma ${tipo === 'entrada' ? 'entrada' : tipo === 'saida' ? 'saída' : 'transação'} encontrada para apagar.`);
            return;
        }

        showZerarMessage(`Apagando ${transacoesParaDeletar.length} transação(ões)...`);

        // Deletar em paralelo (com limite de concorrência para não sobrecarregar)
        const batchSize = 5;
        let deleted = 0;

        for (let i = 0; i < transacoesParaDeletar.length; i += batchSize) {
            const batch = transacoesParaDeletar.slice(i, i + batchSize);
            await Promise.all(batch.map(t =>
                fetch(`/transacoes/${t.id}`, { method: 'DELETE' })
            ));
            deleted += batch.length;
            showZerarMessage(`Apagando... ${deleted}/${transacoesParaDeletar.length}`);
        }

        showZerarMessage(`${transacoesParaDeletar.length} ${tipo === 'entrada' ? 'entrada(s)' : tipo === 'saida' ? 'saída(s)' : 'transação(ões)'} apagada(s) com sucesso!`);

        // Atualizar dashboard
        await Promise.all([
            fetchSaldo(),
            fetchResumo()
        ]);

    } catch (error) {
        console.error('Erro ao zerar histórico:', error);
        showZerarMessage('Erro ao apagar: ' + error.message, true);
    } finally {
        btn.disabled = false;
        btn.textContent = '🗑️';
    }
}

// Configura handlers dos botões de zerar
function setupZerarHandlers() {
    document.getElementById('btn-zerar-entradas').addEventListener('click', () => zerarHistorico('entrada'));
    document.getElementById('btn-zerar-saidas').addEventListener('click', () => zerarHistorico('saida'));
    document.getElementById('btn-zerar-saldo').addEventListener('click', () => zerarHistorico('tudo'));
}

// Inicializa o dashboard
async function init() {
    await Promise.all([
        fetchSaldo(),
        fetchResumo(),
        fetchCategorias()
    ]);
    setDefaultDate();
    setupFormHandler();
    setupZerarHandlers();
}

// Configura handler do formulário
function setupFormHandler() {
    const form = document.getElementById('transacao-form');
    const submitBtn = document.getElementById('btn-submit');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(form);
        const data = {
            descricao: formData.get('descricao'),
            valor: parseFloat(formData.get('valor')),
            tipo: formData.get('tipo'),
            data: formData.get('data')
        };

        const categoriaId = formData.get('categoria');
        if (categoriaId) {
            data.categoria_id = parseInt(categoriaId);
        }

        // Validação básica
        if (!data.descricao || !data.valor || !data.tipo || !data.data) {
            showFormMessage('Preencha todos os campos obrigatórios.', true);
            return;
        }

        if (data.valor <= 0) {
            showFormMessage('O valor deve ser maior que zero.', true);
            return;
        }

        // Desabilitar botão durante envio
        submitBtn.disabled = true;
        submitBtn.textContent = 'Adicionando...';

        try {
            const response = await fetch('/transacoes', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail?.[0]?.msg || 'Erro ao criar transação');
            }

            const result = await response.json();
            showFormMessage(`Transação "${result.descricao}" adicionada com sucesso!`);

            // Limpar formulário
            form.reset();
            setDefaultDate();

            // Atualizar dashboard
            await Promise.all([
                fetchSaldo(),
                fetchResumo()
            ]);

        } catch (error) {
            console.error('Erro ao criar transação:', error);
            showFormMessage('Erro: ' + error.message, true);
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Adicionar Transação';
        }
    });
}

// Executar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', init);