
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

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
      path('delete-result/<str:id>/', views.delete_result, name='delete_result'),

      
    ]

if settings.DEBUG:
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

