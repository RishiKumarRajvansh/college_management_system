from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    path('', views.dashboard, name='course_dashboard'),
    path('list/', views.course_list, name='course_list'),
    path('create/', views.course_create, name='course_create'),    path('<int:pk>/', views.course_detail, name='course_detail'),
    path('<int:pk>/update/', views.course_update, name='course_update'),
    path('<int:pk>/delete/', views.course_delete, name='course_delete'),
    
    # API endpoints for charts
    path('api/course-credit-distribution/', api_views.course_credit_distribution, name='api_course_credit_distribution'),
    path('api/course-enrollment/', api_views.course_enrollment, name='api_course_enrollment'),
]
