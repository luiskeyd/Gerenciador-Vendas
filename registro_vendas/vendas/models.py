from django.db import models
from django.utils import timezone
from datetime import date


class Produto(models.Model):
  nome = models.CharField(max_length=100)
  preco = models.DecimalField(max_digits=100, decimal_places=2)
  quantidade_estoque = models.PositiveIntegerField()
  quantidade_vendidos = models.PositiveIntegerField(default=0)
  data_cadastro = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.nome

class Venda(models.Model):
  """Modelo principal de vendas"""
  data_venda = models.DateTimeField(default=timezone.now)
  total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
  finalizada = models.BooleanField(default=False)
  created_at = models.DateTimeField(default=timezone.now)
  
  class Meta:
      ordering = ['-data_venda']
  
  def __str__(self):
      return f"Venda {self.id} - {self.data_venda.strftime('%d/%m/%Y')}"


class ItemVenda(models.Model):
  """Itens de cada venda"""
  venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name='itens')
  produto = models.ForeignKey('Produto', on_delete=models.CASCADE)
  quantidade = models.IntegerField()
  preco_unitario = models.DecimalField(max_digits=8, decimal_places=2)
  subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
  
  def save(self, *args, **kwargs):
      self.subtotal = self.quantidade * self.preco_unitario
      super().save(*args, **kwargs)
  
  def __str__(self):
      return f"{self.quantidade:02d} {self.produto.nome} - R$ {self.subtotal:.2f}"

class RelatorioDiario(models.Model):
  """Consolidação diária das vendas - formato caderno do seu pai"""
  data = models.DateField(unique=True)
  vendas_do_dia = models.ManyToManyField(Venda, related_name='relatorio_diario')
  total_vendido = models.DecimalField(max_digits=10, decimal_places=2, default=0)
  total_itens = models.IntegerField(default=0)
  numero_vendas = models.IntegerField(default=0)
  
  # JSON com dados estruturados no formato do caderno
  resumo_produtos = models.JSONField(default=dict, blank=True)
  # Exemplo: {"parafuso": {"quantidade": 15, "total": 2.25}, "porca": {"quantidade": 8, "total": 1.60}}
  
  gerado_em = models.DateTimeField(auto_now=True)
  
  class Meta:
      ordering = ['-data']
      verbose_name = "Relatório Diário"
      verbose_name_plural = "Relatórios Diários"
  
  def __str__(self):
      return f"Relatório {self.data.strftime('%d/%m/%Y')} - R$ {self.total_vendido}"
  
  def gerar_resumo(self):
      """Gera resumo no formato do caderno"""
      vendas = self.vendas_do_dia.filter(finalizada=True)
      produtos_resumo = {}
      
      for venda in vendas:
          for item in venda.itens.all():
              nome_produto = item.produto.nome
              
              if nome_produto not in produtos_resumo:
                  produtos_resumo[nome_produto] = {
                      'quantidade': 0,
                      'total': 0.0
                  }
              
              produtos_resumo[nome_produto]['quantidade'] += item.quantidade
              produtos_resumo[nome_produto]['total'] += float(item.subtotal)
      
      # Atualizar campos
      self.resumo_produtos = produtos_resumo
      self.total_vendido = sum(venda.total for venda in vendas)
      self.numero_vendas = vendas.count()
      self.total_itens = sum(
          sum(item.quantidade for item in venda.itens.all()) 
          for venda in vendas
      )
      self.save()
      
      return produtos_resumo
  
  def formato_caderno(self):
      """Retorna texto formatado como no caderno do seu pai"""
      linhas = []
      linhas.append(f"Em {self.data.strftime('%d de %B de %Y')}")
      linhas.append("-" * 40)
      
      for produto, dados in self.resumo_produtos.items():
          linhas.append(f"{dados['quantidade']:02d} {produto}  total - R$ {dados['total']:.2f}")
      
      linhas.append("-" * 40)
      linhas.append(f"TOTAL DO DIA: R$ {self.total_vendido:.2f}")
      linhas.append(f"Número de vendas: {self.numero_vendas}")
      
      return "\n".join(linhas)

class RelatorioMensal(models.Model):
  """Consolidação mensal"""
  ano = models.IntegerField()
  mes = models.IntegerField()
  relatorios_diarios = models.ManyToManyField(RelatorioDiario)
  total_mensal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
  dias_com_vendas = models.IntegerField(default=0)
  
  class Meta:
      unique_together = ['ano', 'mes']
      ordering = ['-ano', '-mes']
      verbose_name = "Relatório Mensal"
      verbose_name_plural = "Relatórios Mensais"
  
  def __str__(self):
      meses = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
              'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
      return f"{meses[self.mes]} {self.ano} - R$ {self.total_mensal}"
  
  def gerar_consolidacao(self):
      """Consolida todos os relatórios diários do mês"""
      from calendar import monthrange
      
      dias_no_mes = monthrange(self.ano, self.mes)[1]
      relatorios = []
      
      for dia in range(1, dias_no_mes + 1):
          try:
              relatorio_dia = RelatorioDiario.objects.get(
                  data=date(self.ano, self.mes, dia)
              )
              relatorios.append(relatorio_dia)
          except RelatorioDiario.DoesNotExist:
              continue
      
      # Atualizar relacionamentos
      self.relatorios_diarios.set(relatorios)
      self.total_mensal = sum(r.total_vendido for r in relatorios)
      self.dias_com_vendas = len(relatorios)
      self.save()
      
      return relatorios