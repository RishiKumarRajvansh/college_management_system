# functional_test.py
"""
This script contains functional tests for the College Management System's new features:
1. Dashboard visualizations with Chart.js
2. Notification system
3. Report export functionality
4. UI improvements
"""
from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

from reporting.models import Report, Notification
from student_management.models import Student
from faculty_management.models import Faculty
from course_management.models import Course

class FunctionalTest(LiveServerTestCase):
    def setUp(self):
        # Set up a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.user.is_staff = True
        self.user.save()
        
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Set up Selenium WebDriver
        self.browser = webdriver.Chrome(options=chrome_options)
        
        # Create test data
        self._create_test_data()
        
    def tearDown(self):
        self.browser.quit()
        
    def _create_test_data(self):
        """Create test data for the tests"""
        # Create notifications
        Notification.objects.create(
            user=self.user,
            message="Test notification 1",
            notification_type="info"
        )
        Notification.objects.create(
            user=self.user,
            message="Test notification 2",
            notification_type="success"
        )
        
        # Create reports
        Report.objects.create(
            title="Test Report 1",
            report_type="student",
            generated_by=self.user
        )
        Report.objects.create(
            title="Test Report 2",
            report_type="attendance",
            generated_by=self.user
        )
        
    def test_dashboard_charts(self):
        """Test that dashboard charts are rendered correctly"""
        # Login
        self.browser.get(f"{self.live_server_url}/login/")
        self.browser.find_element(By.NAME, "username").send_keys("testuser")
        self.browser.find_element(By.NAME, "password").send_keys("testpassword123")
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Go to the reporting dashboard
        self.browser.get(f"{self.live_server_url}/reporting/")
        
        # Check that charts are loaded
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "attendanceChartCanvas"))
        )
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "examPerformanceCanvas"))
        )
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "enrollmentChartCanvas"))
        )
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "feeCollectionCanvas"))
        )
        
        # Assert that Chart.js has rendered the charts
        self.assertTrue(self.browser.execute_script(
            "return document.querySelector('#attendanceChartCanvas').chart !== undefined"
        ))
        
    def test_notification_system(self):
        """Test that the notification system works correctly"""
        # Login
        self.browser.get(f"{self.live_server_url}/login/")
        self.browser.find_element(By.NAME, "username").send_keys("testuser")
        self.browser.find_element(By.NAME, "password").send_keys("testpassword123")
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Check notification counter
        notification_counter = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "notificationCounter"))
        )
        self.assertEqual(notification_counter.text, "2")
        
        # Open notification dropdown
        self.browser.find_element(By.ID, "notificationsDropdown").click()
        
        # Check notification content
        notification_items = WebDriverWait(self.browser, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".notification-item"))
        )
        self.assertEqual(len(notification_items), 2)
        
        # Mark notification as read
        mark_read_button = self.browser.find_element(By.CSS_SELECTOR, ".mark-read")
        mark_read_button.click()
        
        time.sleep(1)  # Wait for AJAX
        
        # Check updated counter
        self.assertEqual(notification_counter.text, "1")
        
    def test_report_export(self):
        """Test that report export functionality works"""
        # Login
        self.browser.get(f"{self.live_server_url}/login/")
        self.browser.find_element(By.NAME, "username").send_keys("testuser")
        self.browser.find_element(By.NAME, "password").send_keys("testpassword123")
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Go to report detail
        self.browser.get(f"{self.live_server_url}/reporting/reports/1/")
        
        # Check export dropdown
        export_dropdown = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "exportDropdown"))
        )
        export_dropdown.click()
        
        # Check export options
        export_options = WebDriverWait(self.browser, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".dropdown-menu .dropdown-item"))
        )
        self.assertEqual(len(export_options), 3)
        
        # Check URLs of export options
        pdf_option = self.browser.find_element(By.XPATH, "//a[contains(text(), 'PDF Format')]")
        self.assertTrue("format=pdf" in pdf_option.get_attribute("href"))
        
        excel_option = self.browser.find_element(By.XPATH, "//a[contains(text(), 'Excel Format')]")
        self.assertTrue("format=excel" in excel_option.get_attribute("href"))
        
        csv_option = self.browser.find_element(By.XPATH, "//a[contains(text(), 'CSV Format')]")
        self.assertTrue("format=csv" in csv_option.get_attribute("href"))

    def test_ui_improvements(self):
        """Test UI improvements"""
        # Test non-authenticated UI
        self.browser.get(self.live_server_url)
        content_wrapper = self.browser.find_element(By.ID, "content-wrapper")
        self.assertTrue("full-width" in content_wrapper.get_attribute("class"))
        
        # Login
        self.browser.get(f"{self.live_server_url}/login/")
        self.browser.find_element(By.NAME, "username").send_keys("testuser")
        self.browser.find_element(By.NAME, "password").send_keys("testpassword123")
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Test authenticated UI
        content_wrapper = self.browser.find_element(By.ID, "content-wrapper")
        self.assertFalse("full-width" in content_wrapper.get_attribute("class"))
        
        # Check notification badge position
        notification_badge = self.browser.find_element(By.ID, "notificationCounter")
        badge_style = notification_badge.get_attribute("style")
        self.assertTrue("display: inline-block" in badge_style)

def run_tests():
    """Run the functional tests"""
    import unittest
    unittest.main()

if __name__ == '__main__':
    run_tests()
