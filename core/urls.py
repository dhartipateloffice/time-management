from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    #PROJECTS
    path('', views.dashboard, name='dashboard'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('projects/<int:pk>/delete/', views.project_delete, name='project_delete'),
    path('projects/<int:pk>/', views.project_overview, name='project_overview'),
    path('projects/<int:pk>/invite/', views.project_invite, name='project_invite'),

    #TASKS
    path('projects/<int:pk>/tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/<int:pk>/edit/', views.task_edit, name='task_edit'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('tasks/<int:pk>/start/', views.start_timer, name='start_timer'),
    path('tasks/<int:pk>/stop/', views.stop_timer, name='stop_timer'),

    # AUTHENTICATION
    path('accounts/login/', views.CustomLoginView.as_view(), name='login'),
    path('accounts/logout/',auth_views.LogoutView.as_view(next_page='login'),name='logout'),
    path('accounts/register/',views.register,name='register'),

]   