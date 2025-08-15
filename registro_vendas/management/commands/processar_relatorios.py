# management/commands/processar_relatorios.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta, datetime
from vendas.utils.relatorios import processar_vendas_do_dia, processar_vendas_do_mes

class Command(BaseCommand):
    help = 'Processa relatórios diários e mensais automaticamente'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--data',
            type=str,
            help='Data específica para processar (formato: YYYY-MM-DD)'
        )
        parser.add_argument(
            '--mes',
            type=str,
            help='Mês específico para processar (formato: YYYY-MM)'
        )
        parser.add_argument(
            '--ontem',
            action='store_true',
            help='Processar relatório de ontem'
        )
        parser.add_argument(
            '--hoje',
            action='store_true',
            help='Processar relatório de hoje'
        )
        parser.add_argument(
            '--mes-atual',
            action='store_true',
            help='Processar relatório do mês atual'
        )
    
    def handle(self, *args, **options):
        hoje = date.today()
        
        try:
            if options['data']:
                # Data específica
                data_proc = datetime.strptime(options['data'], '%Y-%m-%d').date()
                self.processar_dia(data_proc)
                
            elif options['mes']:
                # Mês específico
                ano_mes = options['mes'].split('-')
                ano = int(ano_mes[0])
                mes = int(ano_mes[1])
                self.processar_mes(ano, mes)
                
            elif options['ontem']:
                # Ontem
                ontem = hoje - timedelta(days=1)
                self.processar_dia(ontem)
                
            elif options['hoje']:
                # Hoje
                self.processar_dia(hoje)
                
            elif options['mes_atual']:
                # Mês atual
                self.processar_mes(hoje.year, hoje.month)
                
            else:
                # Padrão: processar ontem e mês atual
                ontem = hoje - timedelta(days=1)
                self.processar_dia(ontem)
                self.processar_mes(hoje.year, hoje.month)
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao processar relatórios: {str(e)}')
            )
    
    def processar_dia(self, data):
        self.stdout.write(f'Processando relatório do dia {data.strftime("%d/%m/%Y")}...')
        
        try:
            relatorio = processar_vendas_do_dia(data)
            
            if relatorio.numero_vendas > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Relatório processado: {relatorio.numero_vendas} vendas, '
                        f'R$ {relatorio.total_vendido:.2f}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Nenhuma venda encontrada para {data.strftime("%d/%m/%Y")}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao processar {data.strftime("%d/%m/%Y")}: {str(e)}')
            )
    
    def processar_mes(self, ano, mes):
        meses = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        
        self.stdout.write(f'Processando relatório mensal de {meses[mes]} {ano}...')
        
        try:
            relatorio = processar_vendas_do_mes(ano, mes)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Relatório mensal processado: {relatorio.dias_com_vendas} dias com vendas, '
                    f'R$ {relatorio.total_mensal:.2f}'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao processar {meses[mes]} {ano}: {str(e)}')
            )

# Exemplo de uso:
# python manage.py processar_relatorios --ontem
# python manage.py processar_relatorios --data 2025-08-12
# python manage.py processar_relatorios --mes 2025-08
# python manage.py processar_relatorios --mes-atual