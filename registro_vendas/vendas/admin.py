from django.contrib import admin
from .models import Produto, itemVenda, Venda

admin.site.register(Produto)
admin.site.register(itemVenda)
admin.site.register(Venda)