from django.utils import timezone
from django.db.models import Sum, Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import IsAdmin
from apps.sales.models import Transaction


class DailyReportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        today = timezone.now().date()

        transactions = Transaction.objects.filter(
            created_at__date=today,
            status='CONFIRMED'
        )

        return Response({
            'date': str(today),
            'total_transactions': transactions.count(),
            'total_sales': str(
                transactions.aggregate(total=Sum('price'))['total'] or 0
            ),
            'agents': self._agents_summary(transactions)
        })

    def _agents_summary(self, transactions):
        data = []
        agents = transactions.values('agent__username').annotate(
            total_sales=Sum('price'),
            total_transactions=Count('id')
        )

        for a in agents:
            data.append({
                'agent': a['agent__username'],
                'total_transactions': a['total_transactions'],
                'total_sales': str(a['total_sales'])
            })

        return data


class MonthlyReportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        now = timezone.now()

        transactions = Transaction.objects.filter(
            created_at__year=now.year,
            created_at__month=now.month,
            status='CONFIRMED'
        )

        return Response({
            'month': f"{now.year}-{now.month}",
            'total_transactions': transactions.count(),
            'total_sales': str(
                transactions.aggregate(total=Sum('price'))['total'] or 0
            ),
            'agents': self._agents_summary(transactions)
        })

    def _agents_summary(self, transactions):
        data = []
        agents = transactions.values('agent__username').annotate(
            total_sales=Sum('price'),
            total_transactions=Count('id')
        )

        for a in agents:
            data.append({
                'agent': a['agent__username'],
                'total_transactions': a['total_transactions'],
                'total_sales': str(a['total_sales'])
            })

        return data
class YearlyReportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        now = timezone.now()

        transactions = Transaction.objects.filter(
            created_at__year=now.year,
            status='CONFIRMED'
        )

        return Response({
            'year': str(now.year),
            'total_transactions': transactions.count(),
            'total_sales': str(
                transactions.aggregate(total=Sum('price'))['total'] or 0
            ),
            'agents': self._agents_summary(transactions)
        })

    def _agents_summary(self, transactions):
        data = []
        agents = transactions.values('agent__username').annotate(
            total_sales=Sum('price'),
            total_transactions=Count('id')
        )

        for a in agents:
            data.append({
                'agent': a['agent__username'],
                'total_transactions': a['total_transactions'],
                'total_sales': str(a['total_sales'])
            })

        return data
