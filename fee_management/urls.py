from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.FeeDashboardView.as_view(), name='fee_dashboard'),
    
    # Fee Category URLs
    path('categories/', views.FeeCategoryListView.as_view(), name='fee_category_list'),
    path('categories/create/', views.FeeCategoryCreateView.as_view(), name='fee_category_create'),
    path('categories/<int:category_id>/', views.FeeCategoryDetailView.as_view(), name='fee_category_detail'),
    path('categories/<int:category_id>/update/', views.FeeCategoryUpdateView.as_view(), name='fee_category_update'),
    path('categories/<int:category_id>/delete/', views.FeeCategoryDeleteView.as_view(), name='fee_category_delete'),
    
    # Fee Structure URLs
    path('structures/', views.FeeStructureListView.as_view(), name='fee_structure_list'),
    path('structures/create/', views.FeeStructureCreateView.as_view(), name='fee_structure_create'),
    path('structures/<int:structure_id>/', views.FeeStructureDetailView.as_view(), name='fee_structure_detail'),
    path('structures/<int:structure_id>/update/', views.FeeStructureUpdateView.as_view(), name='fee_structure_update'),
    path('structures/<int:structure_id>/delete/', views.FeeStructureDeleteView.as_view(), name='fee_structure_delete'),
    
    # Payment URLs
    path('payments/', views.PaymentListView.as_view(), name='payment_list'),
    path('payments/create/', views.PaymentCreateView.as_view(), name='payment_create'),
    path('payments/<int:payment_id>/', views.PaymentDetailView.as_view(), name='payment_detail'),
    path('payments/<int:payment_id>/update/', views.PaymentUpdateView.as_view(), name='payment_update'),
    path('payments/<int:payment_id>/delete/', views.PaymentDeleteView.as_view(), name='payment_delete'),
    
    # Student Fee URLs
    path('student/<int:student_id>/fees/', views.StudentFeeView.as_view(), name='student_fees'),
]
