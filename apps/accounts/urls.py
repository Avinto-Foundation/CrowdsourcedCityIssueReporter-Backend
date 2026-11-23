from django.urls import path

from apps.accounts import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('csrf/', views.csrf_token, name='csrf-token'),
    path('refresh/', views.refresh_token, name='refresh-token'),
    path('logout/', views.logout, name='logout'),
]