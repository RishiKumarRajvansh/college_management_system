# College Management System

A Django-based College Management System for managing academic and administrative workflows in an educational institution. The project uses Django, HTML templates, CSS, Tailwind CSS through CDN, JavaScript, and SQLite.

The system currently includes email-based authentication, role-aware dashboards, responsive Tailwind-styled pages, seeded testing data, activity logging, report generation support, and database backup tooling.

## Current Project Status

- Backend: Django with SQLite
- Frontend: Django templates, Tailwind CDN, compatibility CSS, Font Awesome, JavaScript
- Authentication: email-based login with case-sensitive password validation
- UI: responsive Tailwind application shell and redesigned login page
- Database: seeded SQLite database with realistic test data
- Activity logs: dynamic audit log page with filters, pagination, CSV export, and login/logout event capture
- Report artifact: generated academic project report in `.docx` format
- Local server used for verification: `http://127.0.0.1:8000/`

## Major Features

### Authentication and Access

- Email-based login instead of username-based login
- Case-sensitive password validation using Django's authentication backend
- User profiles with role types: administrator, faculty, and student
- Staff test account mapped to administrative portal access
- Password reset request workflow
- Login/logout audit logging through Django auth signals

### Academic Modules

- Student management
- Faculty management
- Course management
- Attendance management
- Examination scheduling
- Result and grade management
- Student profile and student self-service views
- Faculty profile and faculty-oriented views

### Administrative Modules

- Library management
- Book issue and return workflow
- Hostel management
- Room and allocation tracking
- Fee category, fee structure, and payment management
- Report metadata and export support
- Notification records
- Database backup history
- System activity logs

### UI and Responsiveness

- Tailwind CSS loaded through CDN in the base templates
- Responsive sidebar and header layout
- Mobile-friendly login screen
- Responsive tables and filter layouts
- Font Awesome icons for navigation and actions
- Compatibility CSS for legacy Bootstrap-style classes used by existing templates

## Seeded Test Accounts

The current `db.sqlite3` has been reset and seeded with realistic dummy data. Use these accounts for testing:

| Role | Email | Password |
|---|---|---|
| Admin | `admin@riverdale.edu` | `Admin@12345` |
| Faculty | `aisha.raman@riverdale.edu` | `Faculty@12345` |
| Student | `maya.patel@students.riverdale.edu` | `Student@12345` |
| Staff | `nora.wilson@riverdale.edu` | `Staff@12345` |

Note: the app schema currently supports `admin`, `faculty`, and `student` profile types. The staff account is a non-superuser Django staff account with admin-profile portal access for testing.

## Seeded Data Summary

The local SQLite database includes realistic test records:

- 32 users and profiles
- 6 faculty records
- 24 student records
- 8 courses
- 240 attendance records
- 24 examinations
- 24 result records
- Library books and book issue records
- Hostels, rooms, and hostel allocations
- Fee categories, fee structures, and payment records
- Reports, notifications, backups, and audit logs

## Important URLs

| Page | URL |
|---|---|
| Login | `/login/` |
| Admin Dashboard | `/dashboard/` |
| Student Management | `/students/` |
| Faculty Management | `/faculty/` |
| Course Management | `/courses/` |
| Attendance Management | `/attendance/` |
| Examination Management | `/examinations/` |
| Library Management | `/library/` |
| Hostel Management | `/hostel/` |
| Fee Management | `/fees/` |
| Reporting | `/reports/` |
| Activity Logs | `/auth/system-activity-logs/` |
| Password Reset Request | `/auth/password-reset/` |

## System Activity Logs

The activity log page is available at:

```text
/auth/system-activity-logs/
```

It supports:

- Dynamic records from the `AuditTrail` table
- Login/logout events
- Profile and user-management events
- Module filter
- Action filter
- User filter
- Date range filter
- Search across description, module, username, email, and IP address
- Pagination for larger log sets
- CSV export
- Responsive Tailwind UI

The legacy route `/system-logs/` delegates to the same improved activity log implementation.

## Project Report

A complete academic project report has been generated from the synopsis and the project codebase.

Generated report:

```text
reports/College_Management_System_Project_Report.docx
```

Generated assets:

```text
reports/assets/
```

The report includes:

- Cover page
- Certificate
- Acknowledgement
- Overview and problem profile
- Existing and proposed system
- Objectives and methodology
- Modules
- Technology stack
- Requirement analysis
- Functional and non-functional requirements
- Feasibility analysis
- Project planning and schedule
- DFD, ER diagram, use case diagram, architecture diagram
- Database schema
- Major code snippets with explanations
- Testing tables and validation details
- Implementation and deployment notes
- Screenshots of important pages
- Future recommendations
- Bibliography

The generated DOCX was validated with:

- 17,589 estimated words
- 969 paragraphs
- 24 tables
- 16 embedded diagrams/screenshots
- 194 explicit page breaks

## Report Generator

The project report can be regenerated with:

```powershell
python tools\generate_project_report.py
```

The generator expects the synopsis at:

```text
C:\Users\vega6\Desktop\Download backup\Synopsis.docx
```

It captures screenshots from the live local application at:

```text
http://127.0.0.1:8000
```

Before running the generator, start the server and ensure the seeded accounts exist.

Optional dependencies used by the generator:

```powershell
python -m pip install python-docx matplotlib websocket-client
```

## Database Backup Utility

The database backup utility is located at:

```text
tools/backup_database.py
```

Create a manual SQLite backup:

```powershell
python tools\backup_database.py --manual --notes "Manual backup before testing"
```

Create a backup attributed to a user ID:

```powershell
python tools\backup_database.py --manual --user 1 --notes "Admin-triggered backup"
```

Backups are written to:

```text
backups/
```

Backup metadata is recorded in the `DatabaseBackup` model.

## Requirements

Core requirements are listed in:

```text
requirements.txt
```

Main runtime requirements:

- Python 3.8+
- Django 3.2.x
- SQLite for local development
- Pillow
- ReportLab
- openpyxl
- python-dateutil
- psutil

Optional production and development packages are also listed in `requirements.txt`.

## Local Setup

1. Create and activate a virtual environment.

```powershell
python -m venv venv
.\venv\Scripts\activate
```

2. Install dependencies.

```powershell
python -m pip install -r requirements.txt
```

3. Apply migrations.

```powershell
python manage.py migrate
```

4. Run checks.

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate --check
```

5. Start the development server.

```powershell
python manage.py runserver 127.0.0.1:8000
```

If `DEBUG=False` is active in your environment and static CSS is not being served locally, use:

```powershell
python manage.py runserver 127.0.0.1:8000 --insecure
```

6. Open the app.

```text
http://127.0.0.1:8000/
```

## Useful Verification Commands

Run Django checks:

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate --check
```

Run the test suite:

```powershell
python manage.py test
```

Current note: the project currently has no formal Django test cases, so `python manage.py test` reports `0` tests but still runs Django system checks.

## Database Schema Overview

Important models include:

- `UserProfile`
- `AuditTrail`
- `PasswordResetRequest`
- `Student`
- `Faculty`
- `Course`
- `Attendance`
- `Examination`
- `Result`
- `Book`
- `BookIssue`
- `Hostel`
- `Room`
- `HostelAllocation`
- `FeeCategory`
- `FeeStructure`
- `Payment`
- `Notification`
- `Report`
- `DatabaseBackup`

Key relationships:

- User to UserProfile: one-to-one
- User to Student/Faculty profile: one-to-one
- Faculty to Course: one-to-many
- Course to Student: one-to-many
- Student and Course to Attendance: many-to-one links
- Course to Examination: one-to-many
- Student and Examination to Result: many-to-one links
- Student and Book to BookIssue: many-to-one links
- Hostel to Room: one-to-many
- Student to HostelAllocation: one-to-one
- FeeCategory and Course to FeeStructure: many-to-one links
- Student and FeeStructure to Payment: many-to-one links
- User to AuditTrail, Report, Notification, and DatabaseBackup records

## Project Structure

```text
college_management_system/
|-- attendance_management/
|-- college_management_system/
|-- course_management/
|-- examination/
|-- faculty_management/
|-- fee_management/
|-- hostel_management/
|-- library_management/
|-- reporting/
|-- student_management/
|-- user_authentication/
|-- static/
|-- templates/
|-- tools/
|-- reports/
|-- db.sqlite3
`-- manage.py
```

## Frontend Notes

- Tailwind is loaded from CDN in `templates/base.html` and `templates/base_minimal.html`.
- `static/css/tailwind-compat.css` keeps existing Bootstrap-style classes readable while the UI is modernized.
- The login page is redesigned in `templates/user_authentication/login.html`.
- The activity logs page is redesigned in `templates/system_activity_logs.html`.

## Production Notes

For production deployment:

- Set `DEBUG=False`.
- Set a strong `SECRET_KEY`.
- Configure `ALLOWED_HOSTS`.
- Use PostgreSQL or MySQL instead of SQLite for high-concurrency use.
- Run `python manage.py collectstatic`.
- Serve the app with Gunicorn or uWSGI behind Nginx or Apache.
- Use HTTPS.
- Schedule database backups.
- Add automated test coverage before production rollout.

## Maintenance Recommendations

- Add formal unit and integration tests for all modules.
- Add object-level permissions for sensitive records.
- Expand audit logging to cover every create, update, and delete event.
- Move report generation settings such as synopsis path into environment variables.
- Add a reusable seed command for test data.
- Consider PostgreSQL for production use.
- Add CI checks for migrations, formatting, and tests.

## License

This project is intended for academic submission and demonstration. Add a formal license file if the project will be distributed publicly.

## Acknowledgements

- Django
- Python
- SQLite
- Tailwind CSS
- Font Awesome
- ReportLab
- openpyxl
- python-docx
