from django.contrib import admin
from .models import Produto, ItemVenda, Venda, RelatorioDiario, RelatorioMensal

admin.site.register(Produto)
admin.site.register(ItemVenda)
admin.site.register(Venda)
admin.site.register(RelatorioDiario)
admin.site.register(RelatorioMensal)
