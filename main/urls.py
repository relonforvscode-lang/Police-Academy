from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/member/<int:uid>/', views.admin_member_detail, name='admin_member_detail'),
    path('trainer-dashboard/', views.trainer_dashboard, name='trainer_dashboard'),
    path('cadet-dashboard/', views.cadet_dashboard, name='cadet_dashboard'),
    
    path('user/add/', views.admin_add_user, name='add_user'),
    path('user/edit/<int:uid>/', views.admin_edit_user, name='edit_user'),
    path('user/delete/<int:uid>/', views.admin_delete_user, name='delete_user'),
    path('admin/assignments/', views.admin_assignments_view, name='admin_assignments'),
    
    path('chat/<int:other_id>/', views.chat_view, name='chat'),
    path('evaluate/<int:cadet_id>/', views.evaluate_view, name='evaluate'),
    path('api/read/<int:nid>/', views.mark_read, name='mark_read'),
    path('chat/api/messages/<int:other_id>/', views.chat_messages_api, name='chat_messages_api'),
    path('api/unread-messages/', views.get_unread_messages_count, name='get_unread_messages_count'),
    
]    