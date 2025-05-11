"""
URL configuration for WWE_CHAMPION_PREDICTOR project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib.auth import views as auth_views
from django.urls import path, include
from predictor.views import admin_login_view
from predictor.admin_views import custom_admin_site  #Import your custom admin site
import predictor.views as views  # Import the module instead of the function

urlpatterns = [
    #Custom admin panel only — removed default Django admin
    path('custom-admin/', custom_admin_site.urls),

    #Authentication-related URLs
    path('accounts/', include('django.contrib.auth.urls')),  # Includes login, logout, password reset
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),  # Login view
    path('admin-login/', admin_login_view, name='admin_login'),  # Optional custom admin login

    #Logout redirection to home
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    #Main application URLs
    path('', include(('predictor.urls', 'predictor'), namespace='predictor')),

    path('admin-login/', views.admin_login_view, name='admin_login'),

    path('', include(('predictor.urls', 'predictor'), namespace='predictor')),

]
