from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
from .views import admin_login_view

app_name = 'predictor'

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    # User panel (view for logged-in users)
    path('user-panel/', views.user_panel, name='user_panel'),  

    # User dashboard (mapped to the same view as user-panel for simplicity)
    path('dashboard/', views.user_panel, name='user_dashboard'), 

    # Admin dashboard (restricted to admins)
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Prediction result page (view where predictions are displayed)
    path('predict-result/', views.prediction_result, name='prediction_result'),

    # Logout (built-in Django logout view)
    path('logout/', LogoutView.as_view(), name='logout'),

    # Signup page (mapped to signup view for user registration)
    path('signup/', views.signup, name='signup'),

    # Profile editing page
    path('profile/edit/', views.profile_edit, name='profile_edit'),

    # Admin login (route for the admin login page)
    path('admin-login/', admin_login_view, name='admin_login'),  

    # Admin logout (using Django's built-in logout view)
    path('admin/logout/', LogoutView.as_view(), name='admin_logout'),

    path('dashboard/', views.user_dashboard, name='user_dashboard'),
]

