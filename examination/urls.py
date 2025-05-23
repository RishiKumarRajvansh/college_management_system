from django.urls import path
from . import views

urlpatterns = [
    # Examination URLs
    path('', views.examination_list, name='examination_list'),
    path('create/', views.examination_create, name='examination_create'),
    path('<int:pk>/', views.examination_detail, name='examination_detail'),
    path('<int:pk>/update/', views.examination_update, name='examination_update'),
    path('<int:pk>/delete/', views.examination_delete, name='examination_delete'),
    
    # Result URLs
    path('results/', views.result_list, name='result_list'),
    path('results/create/', views.result_create, name='result_create'),
    path('results/bulk-create/', views.bulk_result_create, name='bulk_result_create'),
    path('exams/<int:examination_id>/results/create/', views.result_create, name='result_create_for_exam'),
    path('results/<int:pk>/', views.result_detail, name='result_detail'),
    path('results/<int:pk>/update/', views.result_update, name='result_update'),
    path('results/<int:pk>/delete/', views.result_delete, name='result_delete'),
    
    # Student Results
    path('student-results/', views.student_results, name='my_results'),
    path('student-results/<int:student_id>/', views.student_results, name='student_results'),
]
