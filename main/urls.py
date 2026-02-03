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
    # Discord OAuth
    path('apply/discord-login/', views.discord_oauth_login, name='discord_oauth_login'),
    path('apply/discord-callback/', views.discord_oauth_callback, name='discord_oauth_callback'),
    # Apply & Test URLs
    path('apply/', views.apply_page, name='apply_page'),
    path('api/apply_status/', views.apply_status_api, name='apply_status_api'),
    path('apply/submit/', views.apply_submit, name='apply_submit'),
    path('apply/start/<int:app_id>/', views.apply_start_test, name='apply_start_test'),
    path('apply/test/<int:session_id>/', views.apply_test_page, name='apply_test_page'),
    path('apply/test/<int:session_id>/answer/', views.apply_submit_answer, name='apply_submit_answer'),
    path('apply/finished/<int:app_id>/', views.apply_test_finished, name='apply_test_finished'),
    # Admin applications manager
    path('admin/applications/', views.admin_applications_view, name='admin_applications'),
    path('admin/application/<int:app_id>/action/', views.admin_application_action, name='admin_application_action'),
    path('admin/application/<int:app_id>/view/', views.admin_application_detail, name='admin_application_detail'),
    path('admin/applications/control/', views.admin_applications_control, name='admin_applications_control'),
    path('api/question/<int:qid>/', views.question_api, name='question_api'),
    
]    