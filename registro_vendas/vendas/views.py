import json
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils import timezone
from datetime import date
from calendar import monthrange
from django.core import serializers

from .models import Produto, Venda, ItemVenda, RelatorioDiario, RelatorioMensal
from .utils.relatorios import GeradorRelatorios

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

def visualizar_relatorios(request):
  """Página principal de visualização de relatórios"""
  ano_atual = date.today().year
  mes_atual = date.today().month
  
  # Buscar anos disponíveis
  anos_disponiveis = []
  vendas_anos = Venda.objects.dates('data_venda', 'year', order='DESC')
  for venda_ano in vendas_anos:
      anos_disponiveis.append(venda_ano.year)
  
  # Se não há vendas, adicionar ano atual
  if not anos_disponiveis:
      anos_disponiveis = [ano_atual]
  
  context = {
      'anos_disponiveis': anos_disponiveis,
      'ano_atual': ano_atual,
      'mes_atual': mes_atual,
      'meses': [
          {'numero': 1, 'nome': 'Janeiro'},
          {'numero': 2, 'nome': 'Fevereiro'},
          {'numero': 3, 'nome': 'Março'},
          {'numero': 4, 'nome': 'Abril'},
          {'numero': 5, 'nome': 'Maio'},
          {'numero': 6, 'nome': 'Junho'},
          {'numero': 7, 'nome': 'Julho'},
          {'numero': 8, 'nome': 'Agosto'},
          {'numero': 9, 'nome': 'Setembro'},
          {'numero': 10, 'nome': 'Outubro'},
          {'numero': 11, 'nome': 'Novembro'},
          {'numero': 12, 'nome': 'Dezembro'},
      ]
  }
  
  return render(request, 'vendas/visualizar_relatorios.html', context)

@require_http_methods(["GET"])
def buscar_relatorios_mes(request):
  """API para buscar relatórios de um mês específico"""
  try:
      ano = int(request.GET.get('ano'))
      mes = int(request.GET.get('mes'))
      
      # Validar dados
      if not (1 <= mes <= 12):
          return JsonResponse({'erro': 'Mês inválido'}, status=400)
      
      # Processar relatório mensal (gera se não existir)
      relatorio_mensal = GeradorRelatorios.processar_vendas_do_mes(ano, mes)
      
      # Buscar relatórios diários do mês
      dias_no_mes = monthrange(ano, mes)[1]
      relatorios_diarios = []
      
      for dia in range(1, dias_no_mes + 1):
          data_dia = date(ano, mes, dia)
          
          try:
              relatorio_dia = RelatorioDiario.objects.get(data=data_dia)
              relatorios_diarios.append({
                  'dia': dia,
                  'data': data_dia.strftime('%d/%m/%Y'),
                  'total': float(relatorio_dia.total_vendido),
                  'numero_vendas': relatorio_dia.numero_vendas,
                  'tem_vendas': relatorio_dia.numero_vendas > 0,
                  'produtos_resumo': relatorio_dia.resumo_produtos
              })
          except RelatorioDiario.DoesNotExist:
              relatorios_diarios.append({
                  'dia': dia,
                  'data': data_dia.strftime('%d/%m/%Y'),
                  'total': 0.0,
                  'numero_vendas': 0,
                  'tem_vendas': False,
                  'produtos_resumo': {}
              })
      
      # Dados do mês
      meses_nomes = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
      
      response_data = {
          'mes_nome': meses_nomes[mes],
          'ano': ano,
          'total_mensal': float(relatorio_mensal.total_mensal),
          'dias_com_vendas': relatorio_mensal.dias_com_vendas,
          'relatorios_diarios': relatorios_diarios,
          'sucesso': True
      }
      
      return JsonResponse(response_data)
      
  except (ValueError, TypeError) as e:
      return JsonResponse({'erro': 'Parâmetros inválidos'}, status=400)
  except Exception as e:
      return JsonResponse({'erro': 'Erro interno do servidor'}, status=500)

def download_relatorio_diario(request, ano, mes, dia):
  """Download do relatório diário em PDF"""
  try:
      data_escolhida = date(ano, mes, dia)
      
      # Verificar se há vendas neste dia
      relatorio = GeradorRelatorios.processar_vendas_do_dia(data_escolhida)
      
      if relatorio.numero_vendas == 0:
          messages.warning(request, f'Não há vendas registradas para {data_escolhida.strftime("%d/%m/%Y")}')
          return JsonResponse({'erro': 'Sem vendas neste dia'}, status=404)
      
      # Gerar PDF
      buffer = GeradorRelatorios.pdf_diario(data_escolhida)
      
      # Preparar resposta
      response = HttpResponse(buffer, content_type='application/pdf')
      filename = f'relatorio_diario_{data_escolhida.strftime("%d_%m_%Y")}.pdf'
      response['Content-Disposition'] = f'attachment; filename="{filename}"'
      
      return response
      
  except ValueError:
      messages.error(request, 'Data inválida fornecida')
      return JsonResponse({'erro': 'Data inválida'}, status=400)
  except Exception as e:
      messages.error(request, 'Erro ao gerar relatório')
      return JsonResponse({'erro': 'Erro ao gerar PDF'}, status=500)

def download_relatorio_mensal(request, ano, mes):
  """Download do relatório mensal em PDF"""
  try:
      # Verificar se há vendas neste mês
      relatorio_mensal = GeradorRelatorios.processar_vendas_do_mes(ano, mes)
      
      if relatorio_mensal.dias_com_vendas == 0:
          meses_nomes = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
          messages.warning(request, f'Não há vendas registradas para {meses_nomes[mes]} de {ano}')
          return JsonResponse({'erro': 'Sem vendas neste mês'}, status=404)
      
      # Gerar PDF
      buffer = GeradorRelatorios.pdf_mensal(ano, mes)
      
      # Preparar resposta
      response = HttpResponse(buffer, content_type='application/pdf')
      meses_nomes = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
      filename = f'relatorio_mensal_{meses_nomes[mes].lower()}_{ano}.pdf'
      response['Content-Disposition'] = f'attachment; filename="{filename}"'
      
      return response
      
  except Exception as e:
      messages.error(request, 'Erro ao gerar relatório mensal')
      return JsonResponse({'erro': 'Erro ao gerar PDF'}, status=500)

def preview_relatorio_diario(request, ano, mes, dia):
  """Preview do relatório diário sem download"""
  try:
      data_escolhida = date(ano, mes, dia)
      relatorio = GeradorRelatorios.processar_vendas_do_dia(data_escolhida)
      
      # Formato texto como no caderno
      texto_formatado = relatorio.formato_caderno()
      
      return JsonResponse({
          'sucesso': True,
          'data': data_escolhida.strftime('%d/%m/%Y'),
          'texto_formatado': texto_formatado,
          'total_vendido': float(relatorio.total_vendido),
          'numero_vendas': relatorio.numero_vendas,
          'produtos': relatorio.resumo_produtos
      })
      
  except Exception as e:
      return JsonResponse({'erro': 'Erro ao gerar preview'}, status=500)

def estatisticas_rapidas(request):
  """Estatísticas rápidas para dashboard"""
  try:
      hoje = date.today()
      
      # Relatório de hoje
      relatorio_hoje = GeradorRelatorios.processar_vendas_do_dia(hoje)
      
      # Relatório do mês atual
      relatorio_mes = GeradorRelatorios.processar_vendas_do_mes(hoje.year, hoje.month)
      
      # Comparativo com ontem
      ontem = date(hoje.year, hoje.month, hoje.day - 1) if hoje.day > 1 else None
      vendas_ontem = 0
      if ontem:
          try:
              relatorio_ontem = RelatorioDiario.objects.get(data=ontem)
              vendas_ontem = float(relatorio_ontem.total_vendido)
          except RelatorioDiario.DoesNotExist:
              vendas_ontem = 0
      
      return JsonResponse({
          'hoje': {
              'total': float(relatorio_hoje.total_vendido),
              'vendas': relatorio_hoje.numero_vendas,
              'itens': relatorio_hoje.total_itens
          },
          'mes_atual': {
              'total': float(relatorio_mes.total_mensal),
              'dias_vendas': relatorio_mes.dias_com_vendas
          },
          'comparativo': {
              'ontem': vendas_ontem,
              'diferenca': float(relatorio_hoje.total_vendido) - vendas_ontem
          }
      })
      
  except Exception as e:
      return JsonResponse({'erro': 'Erro ao buscar estatísticas'}, status=500)
  
@csrf_exempt
@require_http_methods(["POST"])
def finalizar_venda(request):
    """Finaliza uma venda recebendo os itens via JSON"""
    try:
        # Receber dados JSON do frontend
        dados = json.loads(request.body)
        itens_venda = dados.get('itens', [])
        
        # Validar se tem itens
        if not itens_venda:
            return JsonResponse({
                'erro': True,
                'mensagem': 'Nenhum item na venda para finalizar'
            }, status=400)
        
        # Calcular total
        total_calculado = 0
        itens_validados = []
        
        for item in itens_venda:
            try:
                produto = Produto.objects.get(id=item['produto_id'])
                quantidade = int(item['quantidade'])
                
                # Verificar estoque
                if produto.quantidade_estoque < quantidade:
                    return JsonResponse({
                        'erro': True,
                        'mensagem': f'Estoque insuficiente para {produto.nome}. Disponível: {produto.quantidade_estoque}'
                    }, status=400)
                
                subtotal = quantidade * produto.preco
                total_calculado += subtotal
                
                itens_validados.append({
                    'produto': produto,
                    'quantidade': quantidade,
                    'preco_unitario': produto.preco,
                    'subtotal': subtotal
                })
                
            except Produto.DoesNotExist:
                return JsonResponse({
                    'erro': True,
                    'mensagem': f'Produto com ID {item["produto_id"]} não encontrado'
                }, status=400)
            except (ValueError, KeyError):
                return JsonResponse({
                    'erro': True,
                    'mensagem': 'Dados inválidos na venda'
                }, status=400)
        
        # Criar a venda
        venda = Venda.objects.create(
            data_venda=timezone.now(),
            total=total_calculado,
            finalizada=True
        )
        
        # Criar os itens da venda e atualizar estoque
        for item_data in itens_validados:
            # Criar item da venda
            ItemVenda.objects.create(
                venda=venda,
                produto=item_data['produto'],
                quantidade=item_data['quantidade'],
                preco_unitario=item_data['preco_unitario'],
                subtotal=item_data['subtotal']
            )
            
            # Atualizar estoque
            produto = item_data['produto']
            produto.quantidade_estoque -= item_data['quantidade']
            produto.quantidade_vendidos += item_data['quantidade']
            produto.save()
        
        # Processar relatório do dia
        try:
            GeradorRelatorios.processar_vendas_do_dia(venda.data_venda.date())
        except Exception as e:
            # Não falhar a venda se der erro no relatório
            print(f"Erro ao processar relatório: {e}")
        
        return JsonResponse({
            'sucesso': True,
            'venda_id': venda.id,
            'total': float(venda.total),
            'data_venda': venda.data_venda.strftime('%d/%m/%Y %H:%M'),
            'mensagem': f'Venda finalizada com sucesso! Total: R$ {venda.total:.2f}'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'erro': True,
            'mensagem': 'Dados JSON inválidos'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'erro': True,
            'mensagem': f'Erro interno: {str(e)}'
        }, status=500)