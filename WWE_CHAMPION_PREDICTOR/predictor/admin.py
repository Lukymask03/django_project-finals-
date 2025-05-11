from django.contrib import admin
from .models import Prediction, UserProfile


class PredictionAdmin(admin.ModelAdmin):
    list_display = ('wrestler_name', 'championship', 'prediction_date', 'success')
    search_fields = ('wrestler_name', 'championship')
    list_filter = ('championship', 'success')


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender')  # Adjust based on your actual fields
    search_fields = ('user__username',)
    list_filter = ('gender',)


admin.site.register(Prediction, PredictionAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
