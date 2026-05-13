from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.db.models import Count, Sum, F, DecimalField, ExpressionWrapper
from django.db.models.functions import TruncDay
from datetime import timedelta
from django.utils import timezone
import json
from .models import Order


@method_decorator(staff_member_required, name='dispatch')
class StoreStatisticsView(TemplateView):
    template_name = "admin/store_statistics.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Determine time range
        days_param = self.request.GET.get('days', '30')
        try:
            filter_days = int(days_param)
        except ValueError:
            filter_days = 30
        start_date = timezone.now() - timedelta(days=filter_days)
        # Base queryset for paid orders in range
        qs_paid = Order.objects.filter(created_at__gte=start_date, paid='paid')
        # Daily orders and revenue
        # Revenue is sum of items__price * items__quantity (ignoring order discount for simplicity in graph, or you can calculate exact)
        daily_stats = (
            qs_paid
            .annotate(day=TruncDay('created_at'))
            .values('day')
            .annotate(
                count=Count('id', distinct=True),
                revenue=Sum(
                    ExpressionWrapper(
                        F('items__price') * F('items__quantity'),
                        output_field=DecimalField()
                    )
                )
            )
            .order_by('day')
        )
        days = [d['day'].strftime('%Y-%m-%d') for d in daily_stats if d['day']]
        counts = [d['count'] for d in daily_stats]
        revenues = [float(d['revenue'] or 0) for d in daily_stats]
        if not days:
            days = ['No data']
            counts = [0]
            revenues = [0]
        # Total Revenue & Count
        total_revenue = sum(revenues)
        total_orders = sum(counts)
        # Status distribution
        status_distribution = (
            Order.objects.filter(created_at__gte=start_date)
            .values('paid')
            .annotate(count=Count('id'))
        )
        statuses = [str(s['paid']).capitalize() for s in status_distribution]
        status_counts = [s['count'] for s in status_distribution]
        if not statuses:
            statuses = ['No data']
            status_counts = [0]
        context['chart_data'] = json.dumps({
            'daily': {
                'labels': days,
                'orders_data': counts,
                'revenue_data': revenues,
            },
            'status': {
                'labels': statuses,
                'data': status_counts,
            }
        })
        context['title'] = 'Store Dashboard'
        context['site_header'] = 'Micron Admin'
        context['selected_days'] = filter_days
        context['total_revenue'] = total_revenue
        context['total_orders'] = total_orders
        return context
