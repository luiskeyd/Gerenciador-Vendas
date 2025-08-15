from django.urls import path
from . import views

urlpatterns = [
  path('', views.home, name='home'),
  path('produtos/', views.produtos, name='produtos'),
  path('registrar-vendas/', views.registrar_vendas, name='registrar_vendas'),
  path('finalizar-venda/', views.finalizar_venda, name='finalizar_venda'),

  # URLs de Relatórios
  path('relatorios/', views.visualizar_relatorios, name='visualizar_relatorios'),
  path('buscar-relatorios-mes/', views.buscar_relatorios_mes, name='buscar_relatorios_mes'),
  path('estatisticas-rapidas/', views.estatisticas_rapidas, name='estatisticas_rapidas'),

  # Downloads de PDF
  path('download-relatorio-diario/<int:ano>/<int:mes>/<int:dia>/', views.download_relatorio_diario, name='download_relatorio_diario'),
  path('download-relatorio-mensal/<int:ano>/<int:mes>/', views.download_relatorio_mensal, name='download_relatorio_mensal'),

  # Preview
  path('preview-relatorio-diario/<int:ano>/<int:mes>/<int:dia>/', views.preview_relatorio_diario, name='preview_relatorio_diario'),
]