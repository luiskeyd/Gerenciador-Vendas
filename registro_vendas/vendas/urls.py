from django.urls import path
from . import views

urlpatterns = [
  path('', views.home, name='home'),
  path('produtos/', views.produtos, name='produtos'),
  path('registrar-vendas/', views.registrar_vendas, name='registrar_vendas'),
]