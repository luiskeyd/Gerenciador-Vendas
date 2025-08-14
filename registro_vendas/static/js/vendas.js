// JavaScript para funcionalidade completa de venda
document.addEventListener('DOMContentLoaded', function() {
    // Obter dados dos produtos do Django
    const produtosData = document.getElementById('produtos-data');
    const produtos = produtosData ? JSON.parse(produtosData.textContent) : [];
    
    // Elementos da interface
    const campoPesquisa = document.getElementById('pesquisar-produto');
    const resultadosPesquisa = document.getElementById('resultados-pesquisa');
    const produtoSelecionadoInput = document.getElementById('produto-selecionado');
    const quantidadeInput = document.getElementById('quantidade');
    const subtotalInput = document.getElementById('subtotal');
    const adicionarBtn = document.getElementById('adicionar-produto');
    const listaVenda = document.getElementById('lista-produtos-venda');
    const totalVenda = document.getElementById('total-venda');
    const limparBtn = document.getElementById('limpar-venda');
    
    // Produto selecionado temporariamente
    let produtoAtual = null;
    
    // Lista de produtos na venda
    let itensVenda = [];
    
    // Pesquisa de produtos com resultados visíveis
    campoPesquisa.addEventListener('input', function(e) {
        const termo = e.target.value.toLowerCase().trim();
        
        if (termo.length === 0) {
            resultadosPesquisa.classList.add('hidden');
            return;
        }
        
        // Filtrar produtos que correspondem ao termo de pesquisa
        const produtosFiltrados = produtos.filter(produto => 
            produto.nome.toLowerCase().includes(termo)
        );
        
        // Mostrar resultados
        mostrarResultados(produtosFiltrados, termo);
    });
    
    // Função para mostrar os resultados da pesquisa
    function mostrarResultados(produtosFiltrados, termo) {
        resultadosPesquisa.innerHTML = '';
        
        if (produtosFiltrados.length === 0) {
            resultadosPesquisa.innerHTML = `
                <div class="p-3 text-center text-gray-500">
                    <svg class="h-8 w-8 mx-auto mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 15c-2.485 0-4.751.952-6.414 2.514l-.828-.828A8.928 8.928 0 0112 14a8.928 8.928 0 016.414 2.514l-.828.828A7.962 7.962 0 0112 15z"></path>
                    </svg>
                    Produto "${termo}" não encontrado
                </div>
            `;
        } else {
            produtosFiltrados.forEach(produto => {
                const item = document.createElement('div');
                item.className = 'p-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-b-0';
                item.innerHTML = `
                    <div class="flex justify-between items-center">
                        <div>
                            <div class="font-medium text-gray-900">${produto.nome}</div>
                            <div class="text-sm text-gray-500">R$ ${produto.preco.toFixed(2)} - Estoque: ${produto.estoque}</div>
                        </div>
                        <button class="text-blue-600 hover:text-blue-800 font-medium">
                            Selecionar
                        </button>
                    </div>
                `;
                
                item.addEventListener('click', function() {
                    selecionarProduto(produto);
                });
                
                resultadosPesquisa.appendChild(item);
            });
        }
        
        resultadosPesquisa.classList.remove('hidden');
    }
    
    // Função para selecionar um produto
    function selecionarProduto(produto) {
        produtoAtual = produto;
        produtoSelecionadoInput.value = produto.nome;
        campoPesquisa.value = produto.nome;
        resultadosPesquisa.classList.add('hidden');
        
        // Limpar quantidade e subtotal
        quantidadeInput.value = '';
        subtotalInput.value = '';
        
        // Focar no campo de quantidade
        quantidadeInput.focus();
        
        // Habilitar/desabilitar botão adicionar
        verificarBotaoAdicionar();
    }
    
    // Calcular subtotal quando quantidade mudar
    quantidadeInput.addEventListener('input', function() {
        if (produtoAtual) {
            const quantidade = parseInt(this.value) || 0;
            const subtotal = quantidade * produtoAtual.preco;
            subtotalInput.value = quantidade > 0 ? `R$ ${subtotal.toFixed(2)}` : '';
            
            verificarBotaoAdicionar();
        }
    });
    
    // Verificar se deve habilitar botão adicionar
    function verificarBotaoAdicionar() {
        const quantidade = parseInt(quantidadeInput.value) || 0;
        adicionarBtn.disabled = !(produtoAtual && quantidade > 0);
    }
    
    // Adicionar produto à venda
    adicionarBtn.addEventListener('click', function() {
        if (!produtoAtual || !quantidadeInput.value) return;
        
        const quantidade = parseInt(quantidadeInput.value);
        const subtotal = quantidade * produtoAtual.preco;
        
        // Verificar se produto já está na venda
        const itemExistente = itensVenda.find(item => item.produto.id === produtoAtual.id);
        
        if (itemExistente) {
            // Atualizar quantidade do item existente
            itemExistente.quantidade += quantidade;
            itemExistente.subtotal = itemExistente.quantidade * itemExistente.produto.preco;
        } else {
            // Adicionar novo item
            itensVenda.push({
                produto: produtoAtual,
                quantidade: quantidade,
                subtotal: subtotal
            });
        }
        
        // Atualizar interface
        atualizarListaVenda();
        limparSelecao();
        calcularTotal();
        
        // Mostrar animação de sucesso
        mostrarAnimacaoSucesso();
    });
    
    // Atualizar lista de produtos na venda
    function atualizarListaVenda() {
        listaVenda.innerHTML = '';
        
        if (itensVenda.length === 0) {
            listaVenda.innerHTML = `
                <div class="flex-1 flex items-center justify-center text-center text-gray-500 py-12 min-h-[200px]">
                    <div>
                        <svg class="h-16 w-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"></path>
                        </svg>
                        <p class="text-lg font-medium text-gray-400 mb-2">Nenhum produto adicionado à venda</p>
                        <p class="text-sm text-gray-400">Pesquise e adicione produtos acima</p>
                    </div>
                </div>
            `;
            return;
        }
        
        itensVenda.forEach((item, index) => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'bg-white p-4 rounded-lg border border-gray-200 shadow-sm transition-all duration-300 hover:shadow-md';
            itemDiv.innerHTML = `
                <div class="flex items-center justify-between">
                    <div class="flex-1">
                        <h3 class="font-medium text-gray-900">${item.produto.nome}</h3>
                        <p class="text-sm text-gray-600">
                            ${item.quantidade}x R$ ${item.produto.preco.toFixed(2)} = 
                            <span class="font-semibold">R$ ${item.subtotal.toFixed(2)}</span>
                        </p>
                    </div>
                    <div class="flex items-center space-x-2">
                        <button onclick="editarQuantidade(${index})" class="text-blue-600 hover:text-blue-800 p-1 rounded hover:bg-blue-50 transition-colors" title="Editar quantidade">
                            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                            </svg>
                        </button>
                        <button onclick="removerItem(${index})" class="text-red-600 hover:text-red-800 p-1 rounded hover:bg-red-50 transition-colors" title="Remover item">
                            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                            </svg>
                        </button>
                    </div>
                </div>
            `;
            
            listaVenda.appendChild(itemDiv);
        });
    }
    
    // Função global para remover item
    window.removerItem = function(index) {
        // Confirmação antes de remover
        if (confirm(`Deseja remover "${itensVenda[index].produto.nome}" da venda?`)) {
            itensVenda.splice(index, 1);
            atualizarListaVenda();
            calcularTotal();
            mostrarNotificacao('Item removido da venda', 'warning');
        }
    };
    
    // Função global para editar quantidade
    window.editarQuantidade = function(index) {
        const item = itensVenda[index];
        const novaQuantidade = prompt(`Nova quantidade para "${item.produto.nome}":`, item.quantidade);
        
        if (novaQuantidade !== null) {
            const quantidade = parseInt(novaQuantidade);
            
            if (quantidade > 0) {
                item.quantidade = quantidade;
                item.subtotal = item.quantidade * item.produto.preco;
                atualizarListaVenda();
                calcularTotal();
                mostrarNotificacao('Quantidade atualizada', 'success');
            } else if (quantidade === 0) {
                // Se quantidade for 0, remover o item
                if (confirm(`Quantidade 0 informada. Deseja remover "${item.produto.nome}" da venda?`)) {
                    itensVenda.splice(index, 1);
                    atualizarListaVenda();
                    calcularTotal();
                    mostrarNotificacao('Item removido da venda', 'warning');
                }
            } else {
                alert('Quantidade deve ser um número válido maior que 0');
            }
        }
    };
    
    // Calcular total da venda
    function calcularTotal() {
        const total = itensVenda.reduce((sum, item) => sum + item.subtotal, 0);
        totalVenda.textContent = `R$ ${total.toFixed(2)}`;
    }
    
    // Limpar seleção atual
    function limparSelecao() {
        produtoAtual = null;
        campoPesquisa.value = '';
        produtoSelecionadoInput.value = '';
        quantidadeInput.value = '';
        subtotalInput.value = '';
        adicionarBtn.disabled = true;
        resultadosPesquisa.classList.add('hidden');
    }
    
    // Função para limpar toda a venda
    function limparVenda() {
        if (itensVenda.length === 0) {
            mostrarNotificacao('Não há itens para remover', 'info');
            return;
        }
        
        // Modal de confirmação personalizado
        if (confirm(`Deseja limpar toda a venda?\n\nItens: ${itensVenda.length}\nTotal: R$ ${itensVenda.reduce((sum, item) => sum + item.subtotal, 0).toFixed(2)}\n\nEsta ação não pode ser desfeita.`)) {
            itensVenda = [];
            atualizarListaVenda();
            calcularTotal();
            limparSelecao();
            mostrarNotificacao('Venda limpa com sucesso', 'success');
            
            // Focar no campo de pesquisa
            campoPesquisa.focus();
        }
    }
    
    // Event listener para o botão limpar
    if (limparBtn) {
        limparBtn.addEventListener('click', limparVenda);
    }
    
    // Função para mostrar notificações
    function mostrarNotificacao(mensagem, tipo = 'info') {
        // Remover notificação existente se houver
        const notificacaoExistente = document.getElementById('notificacao-venda');
        if (notificacaoExistente) {
            notificacaoExistente.remove();
        }
        
        // Cores baseadas no tipo
        const cores = {
            success: 'bg-green-100 border-green-400 text-green-700',
            warning: 'bg-yellow-100 border-yellow-400 text-yellow-700',
            error: 'bg-red-100 border-red-400 text-red-700',
            info: 'bg-blue-100 border-blue-400 text-blue-700'
        };
        
        const notificacao = document.createElement('div');
        notificacao.id = 'notificacao-venda';
        notificacao.className = `fixed top-4 right-4 z-50 p-4 border-l-4 rounded-md shadow-lg transition-all duration-300 ${cores[tipo] || cores.info}`;
        notificacao.innerHTML = `
            <div class="flex items-center">
                <span class="mr-2">${mensagem}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-2 hover:opacity-70">
                    <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
        `;
        
        document.body.appendChild(notificacao);
        
        // Remover automaticamente após 3 segundos
        setTimeout(() => {
            if (notificacao.parentNode) {
                notificacao.remove();
            }
        }, 3000);
    }
    
    // Função para mostrar animação de sucesso ao adicionar produto
    function mostrarAnimacaoSucesso() {
        const btn = adicionarBtn;
        const textoOriginal = btn.innerHTML;
        
        btn.innerHTML = `
            <svg class="h-5 w-5 mr-2 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
            Produto Adicionado!
        `;
        
        btn.className = btn.className.replace('bg-green-600 hover:bg-green-700', 'bg-green-700');
        
        setTimeout(() => {
            btn.innerHTML = textoOriginal;
            btn.className = btn.className.replace('bg-green-700', 'bg-green-600 hover:bg-green-700');
        }, 1500);
    }
    
    // Fechar resultados ao clicar fora
    document.addEventListener('click', function(e) {
        if (!campoPesquisa.contains(e.target) && !resultadosPesquisa.contains(e.target)) {
            resultadosPesquisa.classList.add('hidden');
        }
    });
    
    // Atalhos de teclado
    document.addEventListener('keydown', function(e) {
        // ESC para limpar seleção
        if (e.key === 'Escape') {
            limparSelecao();
        }
        
        // Enter no campo de quantidade para adicionar produto
        if (e.target === quantidadeInput && e.key === 'Enter' && !adicionarBtn.disabled) {
            adicionarBtn.click();
        }
        
        // F2 para focar no campo de pesquisa
        if (e.key === 'F2') {
            e.preventDefault();
            campoPesquisa.focus();
        }
    });
    
    // Inicializar
    atualizarListaVenda();
    calcularTotal();
    
    // Focar no campo de pesquisa ao carregar
    campoPesquisa.focus();
});