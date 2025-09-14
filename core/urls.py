from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('volunteer/signup/', views.volunteer_signup, name='volunteer_signup'),
    path('volunteer/login/', views.volunteer_login, name='volunteer_login'),
    path('volunteer/dashboard/', views.volunteer_dashboard, name='volunteer_dashboard'),
    path('manager/signup/', views.manager_signup, name='manager_signup'),
    path('manager/login/', views.manager_login, name='manager_login'),
    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('event/create/', views.create_event, name='create_event'),
    path('event/<int:event_id>/edit/', views.edit_event, name='edit_event'),
    path('event/past/', views.past_events, name='past_events'),
    path('event/participate/<int:event_id>/', views.participate_event, name='participate_event'),
    path('my-events/', views.my_events, name='my_events'),
    path('logout/', views.user_logout, name='logout'),
    path('event/<int:event_id>/manage-requests/', views.manage_requests, name='manage_requests'),
    path('save-location/', views.save_user_location, name='save_user_location'),
    path('download-certificate/<int:event_id>/', views.download_certificate, name='download_certificate'),
    path('events/', views.events_list, name='events_list'),
    path('event/<int:event_id>/detail/', views.event_detail, name='event_detail'),
    path('event/<int:event_id>/request/<int:user_id>/approve/', views.approve_request, name='approve_request'),
    path('event/<int:event_id>/request/<int:user_id>/reject/', views.reject_request, name='reject_request'),
    path('event/<int:event_id>/feedback/', views.submit_feedback, name='submit_feedback'),
]
