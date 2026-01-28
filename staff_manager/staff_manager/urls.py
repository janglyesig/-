# team_manager/urls.py
from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('edit-team/<int:team_id>/', views.edit_team, name='edit_team'),
    path('delete-team/<int:team_id>/', views.delete_team, name='delete_team'),
]