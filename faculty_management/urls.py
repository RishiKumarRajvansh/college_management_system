from django.urls import path
from . import views

urlpatterns = [
    path('', views.faculty_list, name='faculty_list'),
    path('create/', views.faculty_create, name='faculty_create'),
    path('<int:pk>/', views.faculty_detail, name='faculty_detail'),
    path('<int:pk>/update/', views.faculty_update, name='faculty_update'),
    path('<int:pk>/delete/', views.faculty_delete, name='faculty_delete'),
]
