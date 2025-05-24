from django.urls import path
from . import views

urlpatterns = [    path('', views.attendance_list, name='attendance_list'),    path('dashboard/', views.attendance_list, name='attendance_dashboard'),
    path('create/', views.attendance_create, name='attendance_create'),
    path('record/', views.attendance_create, name='record_attendance'),
    path('report/', views.attendance_list, name='attendance_report'),
    path('bulk/', views.bulk_attendance, name='bulk_attendance'),
    path('<int:pk>/', views.attendance_detail, name='attendance_detail'),
    path('<int:pk>/update/', views.attendance_update, name='attendance_update'),
    path('<int:pk>/delete/', views.attendance_delete, name='attendance_delete'),
    path('student/<int:student_id>/', views.student_attendance, name='student_attendance'),
]
