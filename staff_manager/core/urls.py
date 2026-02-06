from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.main_hub, name='main_hub'),
    path('schedule/all/', views.full_schedule, name='full_schedule'),
    path('schedule/daily/', views.daily_schedule, name='daily_schedule'),

    # 인원 및 상설팀 관리
    path('personnel/', views.personnel_list, name='personnel_list'),
    path('personnel/add/', views.personnel_add, name='personnel_add'),
    path('personnel/edit/<int:pk>/', views.personnel_edit, name='personnel_edit'),
    path('personnel/delete/<int:pk>/', views.personnel_delete, name='personnel_delete'),
    path('personnel/team/create/', views.create_standing_team, name='create_standing_team'),
    path('personnel/team/delete/<int:pk>/', views.delete_standing_team, name='delete_standing_team'),

    # 공연 상세
    path('performance/<int:pk>/', views.performance_detail, name='performance_detail'),
    path('performance/<int:pk>/status/', views.update_status, name='update_status'),
    path('performance/<int:pk>/delete/', views.delete_performance, name='delete_performance'),

    # 팀 관리
    path('team/import/<int:perf_id>/', views.import_standing_team, name='import_standing_team'), # 핵심
    path('team/delete/<int:team_id>/', views.delete_team, name='delete_team'),
    path('team/add-members/<int:team_id>/', views.add_members_to_team, name='add_members_to_team'),
    path('assignment/delete/<int:assign_id>/', views.delete_assignment, name='delete_assignment'),

    # 더미
    path('team/create/<int:perf_id>/', views.create_team, name='create_team'),
    path('assignment/add-select/<int:perf_id>/', views.add_assignment_select, name='add_assignment_select'),
    path('assignment/add-direct/<int:perf_id>/', views.add_assignment_direct, name='add_assignment_direct'),
    path('assignment/update/<int:assign_id>/', views.update_assignment_role, name='update_assignment_role'),

    path('personnel/assign-bulk/', views.assign_personnel_bulk, name='assign_personnel_bulk'),


]

