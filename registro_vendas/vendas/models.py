from django.db import models


class Produto(models.Model):
  nome = models.CharField(max_length=100)
  preco = models.DecimalField(max_digits=100, decimal_places=2)
  quantidade_estoque = models.PositiveIntegerField()
  quantidade_vendidos = models.PositiveIntegerField(default=0)
  data_cadastro = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.nome
  
class Venda(models.Model):
  data_venda = models.DateTimeField(auto_now_add=True)

  @property
  def total(self):
    return sum(item.subtotal for item in self.itens.all())
  
  def __str__(self):
    return f"Venda {self.id} - {self.data_venda.strftime('%d/%m/%Y %H:%M')}"
  
class itemVenda(models.Model):
  venda = models.ForeignKey(Venda, related_name="itens", on_delete=models.CASCADE)
  produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
  quantidade = models.PositiveIntegerField()
  preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

  @property
  def subtotal(self):
    return self.quantidade * self.preco_unitario
  
  def __str__(self):
    return f"{self.quantidade}x {self.produto.nome} (R${self.preco_unitario})"
