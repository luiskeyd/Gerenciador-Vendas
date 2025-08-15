# utils/relatorios.py
from django.http import HttpResponse
from django.template.loader import render_to_string
from datetime import date, datetime, timedelta
from calendar import monthrange
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT

class GeradorRelatorios:
  """Gerador otimizado de relatórios no formato do caderno"""
  
  @staticmethod
  def gerar_relatorio_diario(data_escolhida):
    """Gera ou recupera relatório diário"""
    from vendas.models import RelatorioDiario, Venda
    
    # Buscar ou criar relatório
    relatorio, created = RelatorioDiario.objects.get_or_create(
        data=data_escolhida,
        defaults={'total_vendido': 0}
    )
    
    # Se é novo ou precisa atualizar
    if created or relatorio.gerado_em < datetime.now() - timedelta(hours=1):
        # Buscar vendas do dia
        vendas_do_dia = Venda.objects.filter(
            data_venda__date=data_escolhida,
            finalizada=True
        )
        
        relatorio.vendas_do_dia.set(vendas_do_dia)
        relatorio.gerar_resumo()
    
    return relatorio
  
  @staticmethod
  def gerar_relatorio_mensal(ano, mes):
    """Gera consolidação mensal"""
    from vendas.models import RelatorioMensal
    
    relatorio, created = RelatorioMensal.objects.get_or_create(
        ano=ano,
        mes=mes,
        defaults={'total_mensal': 0}
    )
    
    relatorio.gerar_consolidacao()
    return relatorio
  
  @staticmethod
  def pdf_diario(data_escolhida):
    """Gera PDF do relatório diário - formato caderno"""
    relatorio = GeradorRelatorios.gerar_relatorio_diario(data_escolhida)
    
    # Criar buffer
    buffer = io.BytesIO()
    
    # Configurar documento
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=16,
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12,
        fontName='Courier'  # Fonte monoespaçada como caderno
    )
    
    # Conteúdo
    content = []
    
    # Título
    titulo = f"Relatório de Vendas - {relatorio.data.strftime('%d de %B de %Y')}"
    content.append(Paragraph(titulo, title_style))
    content.append(Spacer(1, 20))
    
    # Lista de produtos (formato caderno)
    if relatorio.resumo_produtos:
        # Cabeçalho da tabela
        data_table = [['Qtd', 'Produto', 'Total']]
        
        for produto, dados in relatorio.resumo_produtos.items():
            data_table.append([
                f"{dados['quantidade']:02d}",
                produto,
                f"R$ {dados['total']:.2f}"
            ])
        
        # Linha de total
        data_table.append(['', '', ''])  # Linha vazia
        data_table.append(['TOTAL', '', f"R$ {relatorio.total_vendido:.2f}"])
        
        # Criar tabela
        table = Table(data_table, colWidths=[2*cm, 10*cm, 3*cm])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Courier'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -2), 0.5, colors.black),
            ('LINEBELOW', (0, -2), (-1, -2), 2, colors.black),
            ('FONTNAME', (0, -1), (-1, -1), 'Courier-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 14),
        ]))
        
        content.append(table)
        
    else:
        content.append(Paragraph("Nenhuma venda registrada neste dia.", normal_style))
    
    # Resumo
    content.append(Spacer(1, 30))
    resumo_text = f"""
    <b>Resumo do Dia:</b><br/>
    Número de vendas: {relatorio.numero_vendas}<br/>
    Total de itens vendidos: {relatorio.total_itens}<br/>
    Valor total: R$ {relatorio.total_vendido:.2f}
    """
    content.append(Paragraph(resumo_text, normal_style))
    
    # Gerar PDF
    doc.build(content)
    buffer.seek(0)
    
    return buffer
  
  @staticmethod
  def pdf_mensal(ano, mes):
    """Gera PDF do relatório mensal"""
    relatorio = GeradorRelatorios.gerar_relatorio_mensal(ano, mes)
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Title'], fontSize=18, spaceAfter=30, alignment=TA_CENTER)
    
    content = []
    
    # Título
    meses = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    titulo = f"Relatório Mensal - {meses[mes]} {ano}"
    content.append(Paragraph(titulo, title_style))
    content.append(Spacer(1, 20))
    
    # Tabela com dias
    data_table = [['Data', 'Total do Dia', 'Nº Vendas']]
    
    for relatorio_diario in relatorio.relatorios_diarios.all().order_by('data'):
        data_table.append([
            relatorio_diario.data.strftime('%d/%m/%Y'),
            f"R$ {relatorio_diario.total_vendido:.2f}",
            str(relatorio_diario.numero_vendas)
        ])
    
    # Total mensal
    data_table.append(['', '', ''])
    data_table.append(['TOTAL MENSAL', f"R$ {relatorio.total_mensal:.2f}", str(relatorio.dias_com_vendas) + ' dias'])
    
    table = Table(data_table, colWidths=[4*cm, 4*cm, 3*cm])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.black),
        ('LINEBELOW', (0, -2), (-1, -2), 2, colors.black),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
    ]))
    
    content.append(table)
    
    doc.build(content)
    buffer.seek(0)
    
    return buffer

  def processar_vendas_do_dia(data=None):
    """Processa vendas do dia automaticamente"""
    if data is None:
        data = date.today()
    
    return GeradorRelatorios.gerar_relatorio_diario(data)

  def processar_vendas_do_mes(ano=None, mes=None):
    """Processa vendas do mês automaticamente"""
    if ano is None or mes is None:
        hoje = date.today()
        ano = hoje.year
        mes = hoje.month
    
    return GeradorRelatorios.gerar_relatorio_mensal(ano, mes)
