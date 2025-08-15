// JavaScript para funcionalidades de relatórios
document.addEventListener('DOMContentLoaded', function() {
    // Elementos da interface
    const anoSelect = document.getElementById('ano-select');
    const mesSelect = document.getElementById('mes-select');
    const buscarBtn = document.getElementById('buscar-relatorios');
    const loading = document.getElementById('loading');
    const relatoriosContainer = document.getElementById('relatorios-container');
    const modal = document.getElementById('modal-preview');
    const modalTitulo = document.getElementById('modal-titulo');
    const modalConteudo = document.getElementById('modal-conteudo');
    const fecharModalBtn = document.getElementById('fechar-modal');
    const cancelarModalBtn = document.getElementById('cancelar-modal');
    const downloadModalBtn = document.getElementById('download-modal');
    
    // Dados para modal
    let modalData = null;
    
    // Carregar estatísticas rápidas
    carregarEstatisticasRapidas();
    
    // Carregar relatórios do mês atual
    buscarRelatorios();
    
    // Event Listeners
    buscarBtn.addEventListener('click', buscarRelatorios);
    
    // Buscar ao pressionar Enter
    anoSelect.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') buscarRelatorios();
    });
    mesSelect.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') buscarRelatorios();
    });
    
    // Modal
    fecharModalBtn.addEventListener('click', fecharModal);
    cancelarModalBtn.addEventListener('click', fecharModal);
    downloadModalBtn.addEventListener('click', downloadDoModal);
    
    // Fechar modal ao clicar fora
    modal.addEventListener('click', function(e) {
        if (e.target === modal) fecharModal();
    });
    
    // Fechar modal com ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
            fecharModal();
        }
    });
    
    function carregarEstatisticasRapidas() {
        fetch('/vendas/estatisticas-rapidas/')
            .then(response => response.json())
            .then(data => {
                if (data.erro) {
                    console.error('Erro ao carregar estatísticas:', data.erro);
                    return;
                }
                
                // Atualizar elementos
                document.getElementById('vendas-hoje').textContent = `R$ ${data.hoje.total.toFixed(2)}`;
                document.getElementById('vendas-mes').textContent = `R$ ${data.mes_atual.total.toFixed(2)}`;
                
                // Comparativo
                const comparativo = data.comparativo.diferenca;
                const comparativoEl = document.getElementById('comparativo');
                
                if (comparativo > 0) {
                    comparativoEl.textContent = `+R$ ${comparativo.toFixed(2)}`;
                    comparativoEl.className = comparativoEl.className.replace('text-purple-900', 'text-green-900');
                    comparativoEl.parentElement.parentElement.className = 
                        comparativoEl.parentElement.parentElement.className.replace('bg-purple-50 border-purple-200', 'bg-green-50 border-green-200');
                } else if (comparativo < 0) {
                    comparativoEl.textContent = `R$ ${comparativo.toFixed(2)}`;
                    comparativoEl.className = comparativoEl.className.replace('text-purple-900', 'text-red-900');
                    comparativoEl.parentElement.parentElement.className = 
                        comparativoEl.parentElement.parentElement.className.replace('bg-purple-50 border-purple-200', 'bg-red-50 border-red-200');
                } else {
                    comparativoEl.textContent = 'R$ 0,00';
                }
            })
            .catch(error => {
                console.error('Erro ao carregar estatísticas:', error);
            });
    }
    
    function buscarRelatorios() {
        const ano = anoSelect.value;
        const mes = mesSelect.value;
        
        // Mostrar loading
        loading.classList.remove('hidden');
        relatoriosContainer.innerHTML = '';
        
        // Fazer requisição
        fetch(`/vendas/buscar-relatorios-mes/?ano=${ano}&mes=${mes}`)
            .then(response => response.json())
            .then(data => {
                loading.classList.add('hidden');
                
                if (data.erro) {
                    mostrarErro(data.erro);
                    return;
                }
                
                renderizarRelatorios(data);
            })
            .catch(error => {
                loading.classList.add('hidden');
                mostrarErro('Erro ao carregar relatórios');
                console.error('Erro:', error);
            });
    }
    
    function renderizarRelatorios(data) {
        relatoriosContainer.innerHTML = '';
        
        // Container principal do mês
        const mesContainer = document.createElement('div');
        mesContainer.className = 'bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden';
        
        // Cabeçalho do mês
        const cabecalho = document.createElement('div');
        cabecalho.className = 'bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6';
        cabecalho.innerHTML = `
            <div class="flex justify-between items-center">
                <div>
                    <h2 class="text-2xl font-bold">${data.mes_nome} ${data.ano}</h2>
                    <p class="text-blue-100 mt-1">${data.dias_com_vendas} dias com vendas</p>
                </div>
                <div class="text-right">
                    <div class="text-3xl font-bold">R$ ${data.total_mensal.toFixed(2)}</div>
                    <button 
                        onclick="downloadRelatorioMensal(${data.ano}, ${getMesNumero(data.mes_nome)})"
                        class="mt-2 bg-white bg-opacity-20 hover:bg-opacity-30 text-white px-4 py-2 rounded-md transition-colors flex items-center"
                    >
                        <svg class="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                        </svg>
                        Download Mensal
                    </button>
                </div>
            </div>
        `;
        
        mesContainer.appendChild(cabecalho);
        
        // Lista de dias
        const listaDias = document.createElement('div');
        listaDias.className = 'p-6';
        
        if (data.relatorios_diarios.filter(r => r.tem_vendas).length === 0) {
            listaDias.innerHTML = `
                <div class="text-center py-12 text-gray-500">
                    <svg class="h-16 w-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                    <p class="text-lg font-medium text-gray-400">Nenhuma venda registrada neste mês</p>
                    <p class="text-sm text-gray-400">Relatórios aparecerão aqui conforme as vendas forem realizadas</p>
                </div>
            `;
        } else {
            // Criar grid de dias
            const grid = document.createElement('div');
            grid.className = 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4';
            
            data.relatorios_diarios.forEach(relatorio => {
                if (relatorio.tem_vendas) {
                    const diaCard = criarCardDia(relatorio, data.ano);
                    grid.appendChild(diaCard);
                }
            });
            
            listaDias.appendChild(grid);
        }
        
        mesContainer.appendChild(listaDias);
        relatoriosContainer.appendChild(mesContainer);
    }
    
    function criarCardDia(relatorio, ano) {
        const card = document.createElement('div');
        card.className = 'bg-gray-50 border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer';
        
        // Calcular cor baseada no valor
        let corClasse = 'text-gray-600';
        let bgClasse = 'bg-gray-50';
        
        if (relatorio.total > 100) {
            corClasse = 'text-green-700';
            bgClasse = 'bg-green-50';
        } else if (relatorio.total > 50) {
            corClasse = 'text-blue-700';
            bgClasse = 'bg-blue-50';
        } else if (relatorio.total > 20) {
            corClasse = 'text-yellow-700';
            bgClasse = 'bg-yellow-50';
        }
        
        card.className = `${bgClasse} border border-gray-200 rounded-lg p-4 hover:shadow-md transition-all cursor-pointer hover:scale-105`;
        
        // Extrair dia da data
        const partesData = relatorio.data.split('/');
        const dia = partesData[0];
        const mes = partesData[1];
        
        card.innerHTML = `
            <div class="flex justify-between items-start mb-3">
                <div class="text-2xl font-bold ${corClasse}">${dia}</div>
                <div class="text-xs text-gray-500">${relatorio.data}</div>
            </div>
            <div class="space-y-2">
                <div class="text-lg font-semibold ${corClasse}">R$ ${relatorio.total.toFixed(2)}</div>
                <div class="text-sm text-gray-600">${relatorio.numero_vendas} venda${relatorio.numero_vendas !== 1 ? 's' : ''}</div>
                
                <!-- Produtos mais vendidos -->
                <div class="text-xs text-gray-500 max-h-12 overflow-hidden">
                    ${Object.keys(relatorio.produtos_resumo).slice(0, 2).map(produto => 
                        `${relatorio.produtos_resumo[produto].quantidade}x ${produto}`
                    ).join(', ')}
                    ${Object.keys(relatorio.produtos_resumo).length > 2 ? '...' : ''}
                </div>
            </div>
            <div class="mt-3 flex space-x-2">
                <button 
                    onclick="previewRelatorio(${ano}, ${mes}, ${dia})"
                    class="flex-1 text-xs bg-white border border-gray-300 text-gray-700 px-2 py-1 rounded hover:bg-gray-50 transition-colors"
                >
                    👁️ Ver
                </button>
                <button 
                    onclick="downloadRelatorio(${ano}, ${mes}, ${dia})"
                    class="flex-1 text-xs bg-blue-600 text-white px-2 py-1 rounded hover:bg-blue-700 transition-colors"
                >
                    📄 PDF
                </button>
            </div>
        `;
        
        return card;
    }
    
    // Funções globais para os botões
    window.previewRelatorio = function(ano, mes, dia) {
        fetch(`/vendas/preview-relatorio-diario/${ano}/${mes}/${dia}/`)
            .then(response => response.json())
            .then(data => {
                if (data.erro) {
                    mostrarErro(data.erro);
                    return;
                }
                
                modalData = { ano, mes, dia };
                modalTitulo.textContent = `Relatório de ${data.data}`;
                modalConteudo.textContent = data.texto_formatado;
                modal.classList.remove('hidden');
            })
            .catch(error => {
                mostrarErro('Erro ao carregar preview');
                console.error('Erro:', error);
            });
    };
    
    window.downloadRelatorio = function(ano, mes, dia) {
        mostrarNotificacao('Gerando PDF...', 'info');
        
        // Criar link temporário para download
        const link = document.createElement('a');
        link.href = `/vendas/download-relatorio-diario/${ano}/${mes}/${dia}/`;
        link.download = `relatorio_${dia}_${mes}_${ano}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        setTimeout(() => {
            mostrarNotificacao('PDF baixado com sucesso!', 'success');
        }, 1000);
    };
    
    window.downloadRelatorioMensal = function(ano, mes) {
        mostrarNotificacao('Gerando relatório mensal...', 'info');
        
        const link = document.createElement('a');
        link.href = `/vendas/download-relatorio-mensal/${ano}/${mes}/`;
        const meses = ['', 'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
                     'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'];
        link.download = `relatorio_mensal_${meses[mes]}_${ano}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        setTimeout(() => {
            mostrarNotificacao('Relatório mensal baixado!', 'success');
        }, 1000);
    };
    
    function downloadDoModal() {
        if (modalData) {
            downloadRelatorio(modalData.ano, modalData.mes, modalData.dia);
            fecharModal();
        }
    }
    
    function fecharModal() {
        modal.classList.add('hidden');
        modalData = null;
    }
    
    function getMesNumero(nomeMs) {
        const meses = {
            'Janeiro': 1, 'Fevereiro': 2, 'Março': 3, 'Abril': 4,
            'Maio': 5, 'Junho': 6, 'Julho': 7, 'Agosto': 8,
            'Setembro': 9, 'Outubro': 10, 'Novembro': 11, 'Dezembro': 12
        };
        return meses[nomeMs] || 1;
    }
    
    function mostrarErro(mensagem) {
        relatoriosContainer.innerHTML = `
            <div class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
                <svg class="h-12 w-12 text-red-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <h3 class="text-lg font-semibold text-red-800 mb-2">Erro ao carregar relatórios</h3>
                <p class="text-red-600">${mensagem}</p>
                <button 
                    onclick="location.reload()" 
                    class="mt-4 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md transition-colors"
                >
                    Tentar novamente
                </button>
            </div>
        `;
    }
    
    function mostrarNotificacao(mensagem, tipo = 'info') {
        // Remover notificação existente
        const existente = document.getElementById('notificacao-relatorios');
        if (existente) existente.remove();
        
        const cores = {
            success: 'bg-green-100 border-green-400 text-green-700',
            warning: 'bg-yellow-100 border-yellow-400 text-yellow-700',
            error: 'bg-red-100 border-red-400 text-red-700',
            info: 'bg-blue-100 border-blue-400 text-blue-700'
        };
        
        const icones = {
            success: '✅',
            warning: '⚠️',
            error: '❌',
            info: 'ℹ️'
        };
        
        const notificacao = document.createElement('div');
        notificacao.id = 'notificacao-relatorios';
        notificacao.className = `fixed top-4 right-4 z-50 p-4 border-l-4 rounded-md shadow-lg transition-all duration-300 ${cores[tipo]}`;
        notificacao.innerHTML = `
            <div class="flex items-center">
                <span class="text-lg mr-2">${icones[tipo]}</span>
                <span>${mensagem}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-4 hover:opacity-70">
                    <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
        `;
        
        document.body.appendChild(notificacao);
        
        // Remover automaticamente
        setTimeout(() => {
            if (notificacao.parentNode) {
                notificacao.remove();
            }
        }, 4000);
    }
    
    // Atualizar estatísticas a cada 5 minutos
    setInterval(carregarEstatisticasRapidas, 300000);
});
