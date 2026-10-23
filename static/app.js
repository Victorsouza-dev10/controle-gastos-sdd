// Formata valor para moeda brasileira
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
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

// Inicializa o dashboard
async function init() {
    await Promise.all([
        fetchSaldo(),
        fetchResumo()
    ]);
}

// Executar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', init);