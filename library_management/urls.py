from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.LibraryDashboardView.as_view(), name='library_dashboard'),
    
    # Book URLs
    path('books/', views.BookListView.as_view(), name='book_list'),
    path('books/create/', views.BookCreateView.as_view(), name='book_create'),
    path('books/<int:book_id>/', views.BookDetailView.as_view(), name='book_detail'),
    path('books/<int:book_id>/update/', views.BookUpdateView.as_view(), name='book_update'),
    path('books/<int:book_id>/delete/', views.BookDeleteView.as_view(), name='book_delete'),
    
    # Book Issue URLs
    path('issues/', views.BookIssueListView.as_view(), name='book_issue_list'),
    path('issues/create/', views.BookIssueCreateView.as_view(), name='book_issue_create'),
    path('issues/<int:issue_id>/', views.BookIssueDetailView.as_view(), name='book_issue_detail'),
    path('issues/<int:issue_id>/update/', views.BookIssueUpdateView.as_view(), name='book_issue_update'),
    path('issues/<int:issue_id>/return/', views.BookReturnView.as_view(), name='book_return'),
    
    # Student Books URLs
    path('student/<int:student_id>/books/', views.StudentBooksView.as_view(), name='student_books'),
]
