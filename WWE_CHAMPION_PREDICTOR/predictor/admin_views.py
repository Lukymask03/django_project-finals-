from django.shortcuts import render
from django.contrib.admin import AdminSite
from django.urls import path
from .models import Prediction
from django.db.models import Count

class CustomAdminSite(AdminSite):
    site_header = "WWE Champion Predictor Admin"
    site_title = "Admin"
    index_title = "Welcome to the Custom Admin Panel"

    def get_urls(self):
        # Get default Django admin URLs
        urls = super().get_urls()

        # Secure the custom view using self.admin_view (handles staff check)
        custom_urls = [
            path('admin-dashboard/', self.admin_view(self.admin_dashboard_view), name='admin_dashboard'),
        ]
        return custom_urls + urls

    def admin_dashboard_view(self, request):
        # Debug: print the user to verify
        print(request.user)

        # Collect prediction statistics
        wrestler_data = Prediction.objects.values('wrestler_name') \
            .annotate(total_predictions=Count('wrestler_name')) \
            .order_by('-total_predictions')

        success_count = Prediction.objects.filter(success=True).count()
        total_predictions = Prediction.objects.count()
        success_rate = (success_count / total_predictions) * 100 if total_predictions > 0 else 0

        context = {
            'wrestler_data': list(wrestler_data),
            'success_rate': success_rate,
            'total_predictions': total_predictions,
            'successful_predictions': success_count,
            'user': request.user,
            'site_header': self.site_header,
            'site_title': self.site_title,
        }

        return render(request, 'predictor/admin_dashboard.html', context)

# Instantiate and expose the custom admin site
custom_admin_site = CustomAdminSite(name='custom_admin')
