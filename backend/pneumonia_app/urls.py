# pneumonia_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
     path('', views.index_view, name='index'),
     path('signup/', views.signup_view, name='signup'),
      path('login/', views.login_view, name='login'),
      path('logout/', views.logout_view, name='logout'),
      path('dashboard/', views.dashboard_view, name='dashboard'),
      path('client/login/', views.login_view, name='login'),
      path('admin-panel/', views.admin_view, name='admin_view'),
      path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
      path('admin_dashboard/manage_users/', views.manage_users, name='manage_users'),
      path('manage_users/', views.manage_users, name='manage_users'),
      path('image/<str:filename>', views.get_image, name='get_image'),
      
      
]


