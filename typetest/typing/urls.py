from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_page, name='register_page'),
    path('login/', views.login_page, name='login_page'),
    path('test/', views.test_page, name='test_page'),
    path('api/get-text/', views.get_text, name='get_text'),
    path('api/register/', views.register, name='register'),
    path('api/login/', views.login_view, name='login'),
    path('api/save-score/', views.save_score, name='save_score'),
    path('api/scores/', views.get_scores, name='get_scores'),
] 