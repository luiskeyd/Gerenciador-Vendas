import json
from django.shortcuts import render
from django.core import serializers
from .models import Produto, Venda

def home(request):
  return render(request, 'base.html')

def produtos(request):
  produtos = Produto.objects.all().order_by('-data_cadastro')
  return render(request, 'vendas/produtos.html', {'produtos': produtos})

def registrar_vendas(request):
  produtos = Produto.objects.filter(quantidade_estoque__gt=0)

  produtos_json = json.dumps([{
    'id': p.id,
    'nome': p.nome,
    'preco': float(p.preco),
    'estoque': p.quantidade_estoque
  } for p in produtos])
  
  return render(request, 'vendas/registrar_vendas.html', {'produtos': produtos_json})
