from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    # Dashboard
    path('', views.LibraryDashboardView.as_view(), name='library_dashboard'),
    path('dashboard/', views.LibraryDashboardView.as_view(), name='library_dashboard_alt'),
    
    # API endpoints
    path('api/dashboard-data/', api_views.library_dashboard_data, name='library_dashboard_data'),
    path('api/statistics/', api_views.library_statistics, name='library_statistics'),
      # Book URLs
    path('books/', views.BookListView.as_view(), name='book_list'),
    path('books/create/', views.BookCreateView.as_view(), name='book_create'),
    path('books/add/', views.BookCreateView.as_view(), name='add_book'),
    path('books/<int:book_id>/', views.BookDetailView.as_view(), name='book_detail'),
    path('books/<int:book_id>/update/', views.BookUpdateView.as_view(), name='book_update'),
    path('books/<int:book_id>/delete/', views.BookDeleteView.as_view(), name='book_delete'),
      # Book Issue URLs
    path('issues/', views.BookIssueListView.as_view(), name='book_issue_list'),
    path('issues/create/', views.BookIssueCreateView.as_view(), name='book_issue_create'),
    path('issues/issue/', views.BookIssueCreateView.as_view(), name='issue_book'),
    path('issues/<int:issue_id>/', views.BookIssueDetailView.as_view(), name='book_issue_detail'),
    path('issues/<int:issue_id>/update/', views.BookIssueUpdateView.as_view(), name='book_issue_update'),
    path('issues/<int:issue_id>/return/', views.BookReturnView.as_view(), name='book_return'),
    
    # Student Books URLs
    path('student/<int:student_id>/books/', views.StudentBooksView.as_view(), name='student_books'),
]
