# test_components.py - Test script for validating all implemented features
import os
import sys
import unittest
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from student_management.models import Student
from course_management.models import Course
from reporting.models import Report, Notification
from attendance_management.models import Attendance
import json

class DashboardViewsTestCase(TestCase):
    """Test case for dashboard views and components"""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpassword123')
        
        # Create test data
        self._create_test_data()
    
    def _create_test_data(self):
        # Create notifications
        for i in range(3):
            Notification.objects.create(
                user=self.user,
                message=f"Test notification {i+1}",
                notification_type="info",
                read=(i == 0)  # Make first one read
            )
        
        # Create reports
        Report.objects.create(
            title="Test Student Report",
            report_type="student",
            generated_by=self.user,
            parameters={"student_filter": "all"}
        )
    
    def test_dashboard_view(self):
        """Test the dashboard view returns successfully"""
        response = self.client.get(reverse('reporting_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reporting/dashboard.html')
    
    def test_notification_api(self):
        """Test the notification API endpoints"""
        # Get notifications
        response = self.client.get(reverse('api_get_notifications'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('notifications', data)
        self.assertIn('unread_count', data)
        self.assertEqual(data['unread_count'], 2)  # We created 2 unread notifications
        
        # Mark one notification as read
        unread_notifications = [n for n in data['notifications'] if not n.get('read', False)]
        if unread_notifications:
            notification_id = unread_notifications[0]['id']
            mark_read_url = reverse('api_mark_notification_read', args=[notification_id])
            response = self.client.post(mark_read_url)
            self.assertEqual(response.status_code, 200)
            
            # Verify count decreased
            response = self.client.get(reverse('api_get_notifications'))
            data = json.loads(response.content)
            self.assertEqual(data['unread_count'], 1)
        
        # Mark all as read
        response = self.client.post(reverse('api_mark_all_notifications_read'))
        self.assertEqual(response.status_code, 200)
        
        # Verify all marked as read
        response = self.client.get(reverse('api_get_notifications'))
        data = json.loads(response.content)
        self.assertEqual(data['unread_count'], 0)
    
    def test_chart_api_endpoints(self):
        """Test the chart data API endpoints"""
        # Test attendance stats endpoint
        response = self.client.get(reverse('api_attendance_stats'))
        self.assertEqual(response.status_code, 200)
        attendance_data = json.loads(response.content)
        self.assertIn('present_count', attendance_data)
        self.assertIn('absent_count', attendance_data)
        
        # Test exam performance endpoint
        response = self.client.get(reverse('api_exam_performance'))
        self.assertEqual(response.status_code, 200)
        exam_data = json.loads(response.content)
        self.assertIn('courses', exam_data)
        self.assertIn('average_scores', exam_data)
        
        # Test enrollment stats endpoint
        response = self.client.get(reverse('api_enrollment_stats'))
        self.assertEqual(response.status_code, 200)
        enrollment_data = json.loads(response.content)
        self.assertIn('months', enrollment_data)
        self.assertIn('enrollment_counts', enrollment_data)
        
        # Test fee collection stats endpoint
        response = self.client.get(reverse('api_fee_collection_stats'))
        self.assertEqual(response.status_code, 200)
        fee_data = json.loads(response.content)
        self.assertIn('months', fee_data)
        self.assertIn('amounts', fee_data)
    
    def test_report_export(self):
        """Test the report export functionality"""
        report = Report.objects.first()
        
        # Test PDF export
        pdf_url = f"{reverse('report_export', args=[report.report_id])}?format=pdf"
        response = self.client.get(pdf_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
        # Test Excel export
        excel_url = f"{reverse('report_export', args=[report.report_id])}?format=excel"
        response = self.client.get(excel_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/ms-excel')
        
        # Test CSV export
        csv_url = f"{reverse('report_export', args=[report.report_id])}?format=csv"
        response = self.client.get(csv_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')

class UIResponsivenessTest(TestCase):
    """Tests for UI responsiveness and sidebar functionality"""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.client = Client()
    
    def test_sidebar_for_authenticated_user(self):
        """Test sidebar is present for authenticated users"""
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('home'))
        self.assertNotContains(response, 'class="full-width"')
    
    def test_sidebar_for_anonymous_user(self):
        """Test sidebar is hidden for non-authenticated users"""
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'class="full-width"')

if __name__ == "__main__":
    # Run the tests
    unittest.main()
