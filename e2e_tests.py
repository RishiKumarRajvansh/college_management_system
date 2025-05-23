import os
import sys
import unittest
from django.test import LiveServerTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from student_management.models import Student
from course_management.models import Course
from reporting.models import Report, Notification
from attendance_management.models import Attendance
import time
import json

class EndToEndTests(StaticLiveServerTestCase):
    """End-to-end test cases for validating the complete College Management System."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run headless for CI environments
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")  # Set window size
        
        # Initialize the WebDriver
        try:
            cls.selenium = webdriver.Chrome(options=chrome_options)
            cls.selenium.implicitly_wait(10)
        except Exception as e:
            print(f"WebDriver initialization error: {e}")
            cls.selenium = None
            
    @classmethod
    def tearDownClass(cls):
        if cls.selenium:
            cls.selenium.quit()
        super().tearDownClass()
    
    def setUp(self):
        # Skip tests if WebDriver couldn't be initialized
        if not self.selenium:
            self.skipTest("WebDriver could not be initialized")
            
        # Create a test user
        self.username = "testuser"
        self.password = "testpassword123"
        self.user = User.objects.create_user(
            username=self.username,
            email="testuser@example.com",
            password=self.password,
            is_staff=True
        )
        
        # Create sample data
        self._create_test_data()
        
        # Base URL for the live server
        self.live_server_url = self.live_server_url
        
    def _create_test_data(self):
        """Create sample data for testing."""
        # Create notifications
        for i in range(5):
            Notification.objects.create(
                user=self.user,
                message=f"Test notification {i+1}",
                notification_type=["info", "warning", "danger", "success", "info"][i],
                read=(i < 2)  # First two are read
            )
            
        # Create reports
        Report.objects.create(
            title="Student Performance Report",
            report_type="student",
            generated_by=self.user,
            parameters={"student_filter": "all"}
        )
        
        Report.objects.create(
            title="Attendance Summary Report",
            report_type="attendance",
            generated_by=self.user,
            parameters={"date_range": "last_month"}
        )
        
        # Create courses (assuming Course model structure)
        for i in range(3):
            Course.objects.create(
                name=f"Test Course {i+1}",
                code=f"TC10{i+1}",
                credits=4,
                description=f"Test course description {i+1}"
            )
        
        # Create students (assuming Student model structure)
        for i in range(10):
            Student.objects.create(
                name=f"Student {i+1}",
                registration_number=f"S2023{i+1:04d}",
                email=f"student{i+1}@example.com",
                date_of_birth="2000-01-01"
            )

    def test_login_dashboard_flow(self):
        """Test login functionality and dashboard access."""
        # Navigate to the login page
        self.selenium.get(f"{self.live_server_url}/login/")
        
        # Fill in login credentials
        username_input = self.selenium.find_element(By.NAME, "username")
        password_input = self.selenium.find_element(By.NAME, "password")
        username_input.send_keys(self.username)
        password_input.send_keys(self.password)
        
        # Submit login form
        self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Wait for dashboard to load
        try:
            WebDriverWait(self.selenium, 10).until(
                EC.presence_of_element_located((By.ID, "dashboardPage"))
            )
            
            # Check if charts are loaded
            WebDriverWait(self.selenium, 10).until(
                EC.presence_of_element_located((By.ID, "attendanceChartCanvas"))
            )
            
            # Verify notification badge is present
            notification_badge = self.selenium.find_element(By.ID, "notificationCounter")
            self.assertIsNotNone(notification_badge)
            
            # Verify unread notification count matches expected
            expected_unread_count = Notification.objects.filter(user=self.user, read=False).count()
            badge_text = notification_badge.text
            self.assertEqual(int(badge_text), expected_unread_count)
            
        except TimeoutException:
            self.fail("Dashboard page did not load within timeout period")
    
    def test_notification_system(self):
        """Test the notification system functionality."""
        # Login first
        self.selenium.get(f"{self.live_server_url}/login/")
        username_input = self.selenium.find_element(By.NAME, "username")
        password_input = self.selenium.find_element(By.NAME, "password")
        username_input.send_keys(self.username)
        password_input.send_keys(self.password)
        self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Wait for dashboard to load
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, "dashboardPage"))
        )
        
        # Click notification icon
        notification_icon = self.selenium.find_element(By.ID, "notificationDropdown")
        notification_icon.click()
        
        # Wait for notification dropdown to appear
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located((By.ID, "notificationDropdownContainer"))
        )
        
        # Check if notifications are displayed
        notifications = self.selenium.find_elements(By.CSS_SELECTOR, ".notification-item")
        self.assertTrue(len(notifications) > 0)
        
        # Click "Mark as read" on first unread notification
        mark_read_buttons = self.selenium.find_elements(By.CSS_SELECTOR, ".mark-read")
        if mark_read_buttons:
            initial_count = self.selenium.find_element(By.ID, "notificationCounter").text
            mark_read_buttons[0].click()
            
            # Wait for count to update
            time.sleep(1)
            
            # Check if notification count decreased
            updated_count = self.selenium.find_element(By.ID, "notificationCounter").text
            if updated_count:
                self.assertLess(int(updated_count), int(initial_count))
        
        # Test "Mark all as read" functionality
        notification_icon.click()  # Close and reopen dropdown
        notification_icon.click()
        mark_all_read = WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.ID, "markAllReadDropdown"))
        )
        mark_all_read.click()
        
        # Wait for notifications to be marked as read
        time.sleep(1)
        
        # Counter should be empty or "0"
        counter = self.selenium.find_element(By.ID, "notificationCounter").text
        self.assertTrue(counter == "" or counter == "0")
    
    def test_report_export(self):
        """Test report export functionality."""
        # Login first
        self.selenium.get(f"{self.live_server_url}/login/")
        username_input = self.selenium.find_element(By.NAME, "username")
        password_input = self.selenium.find_element(By.NAME, "password")
        username_input.send_keys(self.username)
        password_input.send_keys(self.password)
        self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Navigate to reports page
        self.selenium.get(f"{self.live_server_url}/reports/")
        
        # Wait for reports to load
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".report-item"))
        )
        
        # Click on first report
        self.selenium.find_elements(By.CSS_SELECTOR, ".report-item")[0].click()
        
        # Wait for report detail to load
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, "exportDropdown"))
        )
        
        # Click export dropdown
        export_button = self.selenium.find_element(By.ID, "exportDropdown")
        export_button.click()
        
        # Wait for dropdown to appear
        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "dropdown-menu"))
        )
        
        # Check if all export options are available
        export_links = self.selenium.find_elements(By.CSS_SELECTOR, ".export-link")
        export_formats = [link.get_attribute("data-format") for link in export_links]
        
        self.assertIn("pdf", export_formats)
        self.assertIn("excel", export_formats)
        self.assertIn("csv", export_formats)
    
    def test_mobile_responsiveness(self):
        """Test mobile responsiveness by resizing window."""
        # Login first
        self.selenium.get(f"{self.live_server_url}/login/")
        username_input = self.selenium.find_element(By.NAME, "username")
        password_input = self.selenium.find_element(By.NAME, "password")
        username_input.send_keys(self.username)
        password_input.send_keys(self.password)
        self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Wait for dashboard to load
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, "dashboardPage"))
        )
        
        # Test desktop view
        self.selenium.set_window_size(1200, 800)
        time.sleep(1)
        
        # Check sidebar visibility
        sidebar = self.selenium.find_element(By.ID, "accordionSidebar")
        self.assertTrue(sidebar.is_displayed())
        
        # Test tablet view
        self.selenium.set_window_size(768, 1024)
        time.sleep(1)
        
        # Check if charts have proper mobile classes
        chart_containers = self.selenium.find_elements(By.CSS_SELECTOR, ".chart-container")
        for container in chart_containers:
            parent_element = container.find_element(By.XPATH, "./..")
            if "col-lg-6" in parent_element.get_attribute("class"):
                self.assertIn("mobile-full-width", parent_element.get_attribute("class"))
        
        # Test mobile phone view
        self.selenium.set_window_size(375, 667)
        time.sleep(1)
        
        # Check that sidebar is hidden in mobile view
        sidebar_display = self.selenium.execute_script(
            "return window.getComputedStyle(document.getElementById('accordionSidebar')).display"
        )
        self.assertEqual(sidebar_display, "none")
        
        # Test toggling sidebar in mobile view
        sidebarToggleTop = self.selenium.find_element(By.CLASS_NAME, "sidebar-toggler")
        sidebarToggleTop.click()
        time.sleep(1)
        
        # Sidebar should be visible after toggle
        sidebar_display = self.selenium.execute_script(
            "return window.getComputedStyle(document.getElementById('accordionSidebar')).display"
        )
        self.assertNotEqual(sidebar_display, "none")
        
    def test_chart_refresh_functionality(self):
        """Test chart refresh buttons and functionality."""
        # Login first
        self.selenium.get(f"{self.live_server_url}/login/")
        username_input = self.selenium.find_element(By.NAME, "username")
        password_input = self.selenium.find_element(By.NAME, "password")
        username_input.send_keys(self.username)
        password_input.send_keys(self.password)
        self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Wait for dashboard to load
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, "dashboardPage"))
        )
        
        # Find and click a chart refresh button
        refresh_button = self.selenium.find_element(By.CSS_SELECTOR, ".refresh-chart")
        
        # Check if the button has a tooltip
        tooltip_text = refresh_button.get_attribute("data-bs-original-title")
        self.assertIsNotNone(tooltip_text)
        
        # Click the refresh button
        refresh_button.click()
        
        # Check if the refresh icon is spinning (has fa-spin class)
        refresh_icon = refresh_button.find_element(By.CSS_SELECTOR, "i")
        self.assertIn("fa-spin", refresh_icon.get_attribute("class"))
        
        # Wait for animation to complete (1 second)
        time.sleep(1.5)
        
        # Check if the refresh icon is no longer spinning
        refresh_icon = refresh_button.find_element(By.CSS_SELECTOR, "i")
        self.assertNotIn("fa-spin", refresh_icon.get_attribute("class"))


if __name__ == "__main__":
    unittest.main()
