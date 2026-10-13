# Employee Management System

A full-stack Employee Management System built using React, Django REST Framework, and PostgreSQL. The application supports employee and department management, employee search, filtering, sorting, pagination, and configuration-driven forms.

## Project Structure

employee-management-system/
├── .env.example
├── .gitignore
├── README.md
├── screenshots/
├── postman/
│   └── Employee_Management_System_API_Testing.json
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/
│   ├── employees/
│   └── database/
│       ├── schema.sql
│       └── seed.sql
└── frontend/
    ├── .env.example
    ├── package.json
    ├── package-lock.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── api/
        ├── components/
        ├── context/
        ├── pages/
        ├── utils/
        ├── App.jsx
        ├── main.jsx
        └── styles.css


## Features

### 1. Dashboard
- Displays employee and department statistics.
- Shows employee distribution by department.
- Includes loading, error, and empty states.

### 2. Employee Management
- Create, view, edit, and soft-delete employee records.
- Search employees using supported search criteria.
- Filter employees by department and status.
- Sort employees by name and joining date.
- Server-side pagination, with 10 records per page by default.
- Generates employee codes through the backend.
- Validates employee information on the frontend and backend.
- Displays confirmation before employee deletion.
- Excludes soft-deleted employees from normal listings.

### 3. Department Management
- View departments and employee counts.
- Create and edit departments.
- Activate and deactivate departments.
- Prevent deletion of departments that have assigned employee records.

### 4. Configuration-Driven Employee Form
- Retrieves employee form definitions from the backend.
- Uses database configuration for employee form fields.
- Shows the contract end date only for Contract and Intern employees.
- Loads designations according to the selected department.
- Clears the selected designation when the department changes.

### 5. Form Validation
- Validates required employee information.
- Validates email addresses and salary values.
- Rejects future joining dates.
- Enforces applicable employee and contract-related business rules.

### 6. API and Database
- RESTful APIs built using Django REST Framework.
- PostgreSQL database integration.
- Database schema and seed SQL scripts.
- Postman collection for API testing.
- Automated backend API validation tests.

### 7. CSV Export — Bonus Feature
- Exports employee records to a downloadable CSV file.
- Exports matching records rather than only the current page.
- Supports the implemented search, filter, and sorting criteria.
- Excludes soft-deleted employees.
- Includes employee and organizational information in the exported file.
- Generates a date-stamped filename.
- Displays success or error notifications during export.

**How to export employee data:**

1. Open the Employees page.
2. Optionally apply search, department, status, or sorting criteria.
3. Click **Export CSV**.
4. Save the downloaded file and open it in Excel or another spreadsheet application.

API endpoint: `GET /api/employees/export`

### 8. Additional Features
- Centralized API communication and error handling.
- Reusable React components.
- Success and error notifications.
- Confirmation dialogs.
- Environment-based configuration.
- Backend API tests.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React |
| Frontend tooling | Vite |
| Routing | React Router |
| Backend | Python and Django |
| REST API | Django REST Framework |
| Database | PostgreSQL |
| API testing | Postman |
| Styling | CSS |

## Software Requirements

The project dependencies are specified in `backend/requirements.txt` and `frontend/package.json`.

| Software | Version / Requirement |
|---|---|
| Python | 3.10 or newer |
| Django | 5.2 series |
| Django REST Framework | 3.16 series |
| PostgreSQL | 13 or newer |
| Node.js | 18 or newer |
| React | 18.x |
| React Router | 6.x |

Check the dependency files and installed versions before setting up the project.

## Installation and Setup

The following instructions use Windows PowerShell.

### Prerequisites

Install the following software:

- Python
- PostgreSQL
- Node.js and npm
- Git

### 1. Clone the repository

```powershell
git clone https://github.com/Manashree129/employee-management-system.git
cd employee-management-system
```

### 2. Create the PostgreSQL database

Open PostgreSQL SQL Shell (`psql`) or another PostgreSQL client.

Create the database:


CREATE DATABASE employee_db;


Use a PostgreSQL account with permission to connect to and modify this database.

### 3. Configure environment variables

From the project root, create the local environment file:

```powershell
Copy-Item .env.example .env
```

Update `.env` with your local configuration. For example:

```dotenv
DJANGO_SECRET_KEY=replace-with-a-unique-secret
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_TIME_ZONE=Asia/Kolkata

DB_NAME=employee_db
DB_USER=your_postgres_username
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432

FRONTEND_ORIGIN=http://localhost:5173
```

Replace the example values with your own PostgreSQL credentials and a unique Django secret key.

Do not commit actual `.env` files or passwords to GitHub.

### 4. Install backend dependencies

From the project root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks virtual environment activation, use a terminal with permission to run the activation script or invoke the virtual environment's Python executable directly.

### 5. Initialize the database

First, inspect `database/schema.sql` and `database/seed.sql` from the `backend` directory.

The database schema must be initialized before inserting seed data. Django migrations may also create application tables, so follow the schema and migration approach used by this project without creating the same tables twice.

For a migration-managed database, run:

```powershell
python manage.py check
python manage.py migrate
```

If `schema.sql` is required to create additional database objects or tables not managed by Django migrations, execute it using the PostgreSQL command-line client after confirming it does not conflict with the migrations:

```powershell
psql -U your_postgres_username -d employee_db -f database/schema.sql
```

Replace `your_postgres_username` with your PostgreSQL username.

### 6. Load sample data

After initializing the required database schema, load the sample data:

```powershell
psql -U your_postgres_username -d employee_db -f database/seed.sql
```

Use the PostgreSQL username configured for your database.

If the seed script depends on tables or records that have not been created, initialize those prerequisites first. Avoid running seed scripts repeatedly if they insert duplicate records.

### 7. Start the backend

From the `backend` directory, with the virtual environment activated:

```powershell
python manage.py runserver
```

Default backend URL:

`http://localhost:8000`

API base URL:

`http://localhost:8000/api`

Keep the backend terminal running.

### 8. Configure and start the frontend

Open a second terminal at the project root.

```powershell
cd frontend
Copy-Item .env.example .env
npm install
npm run dev
```

Ensure `frontend/.env` contains:

```dotenv
VITE_API_BASE_URL=http://localhost:8000/api
```

Open the frontend at:

`http://localhost:5173`

Keep the frontend terminal running.

The frontend origin must match the origin permitted by the backend CORS configuration.

## Default URLs and Ports

| Service | URL | Port |
|---|---|---|
| Frontend | `http://localhost:5173` | 5173 |
| Backend | `http://localhost:8000` | 8000 |
| API base URL | `http://localhost:8000/api` | 8000 |
| PostgreSQL | `localhost` | 5432 |

## Frontend Routes

| Route | Description |
|---|---|
| `/` | Redirects to the dashboard |
| `/dashboard` | Dashboard and employee statistics |
| `/employees` | Employee list and controls |
| `/employees/new` | Add employee |
| `/employees/:id/edit` | Edit employee |
| `/departments` | Department management |

Employee details are displayed through a details dialog opened from the employee list.

## Configuration-Driven Form

The employee form retrieves its field definitions from:

`GET /api/form-config/employee`

The form configuration is stored in the `form_field_configs` database table. The frontend interprets the configuration through reusable form components and the form rules utility.

The form supports the implemented input types, including text, email, telephone, number, date, select, textarea, and checkbox inputs.

The contract end date is displayed for Contract and Intern employees. Designation options depend on the selected department.

Backend validation remains authoritative; changing frontend form configuration does not automatically change the backend's validation rules.

## API Overview

All endpoints use the `/api` base path.

| Resource | Method and Endpoint | Purpose |
|---|---|---|
| Employees | `GET /employees` | List, search, filter, sort, and paginate |
| Employees | `POST /employees` | Create an employee |
| Employees | `GET /employees/{id}` | Retrieve employee details |
| Employees | `PUT /employees/{id}` | Update an employee |
| Employees | `DELETE /employees/{id}` | Soft-delete an employee |
| Employee export | `GET /employees/export` | Export matching employee records to CSV |
| Departments | `GET /departments` | Retrieve departments |
| Departments | `POST /departments` | Create a department |
| Departments | `PUT /departments/{id}` | Update a department |
| Departments | `DELETE /departments/{id}` | Delete a department when permitted |
| Designations | `GET /departments/{id}/designations` | Retrieve department designations |
| Lookups | `GET /lookups/{category}` | Retrieve lookup options |
| Form configuration | `GET /form-config/employee` | Retrieve employee form configuration |
| Dashboard | `GET /dashboard/summary` | Retrieve dashboard statistics |

Employee listing supports query parameters including `page`, `size`, `search`, `departmentId`, `status`, `sortBy`, and `sortDir`.

### Postman Collection

The exported Postman collection is located at:

`postman/Employee_Management_System_API_Testing.json`

Import this JSON file into Postman to access the API requests.

## Validation and Business Rules

- Employee codes are generated by the backend.
- Employee email addresses are normalized and unique across employee records, including soft-deleted records.
- Mobile numbers must contain exactly 10 digits.
- Employee information is validated according to the implemented business rules.
- Permanent employees do not require a contract end date.
- Contract and Intern employees require a valid contract end date.
- Designations must correspond to the selected department.
- Departments with assigned employee records cannot be deleted.
- Soft-deleted employees are excluded from normal employee listings.

## Testing

Run the following commands from the `backend` directory with the virtual environment activated.

### Django system check

```powershell
python manage.py check
```

### Migration consistency check

```powershell
python manage.py makemigrations --check --dry-run
```

### Backend tests

```powershell
python manage.py test employees
```

The backend tests cover employee listing and input validation, including required fields, invalid email addresses, invalid salary values, and future joining dates.

With both servers running, manually verify:

1. Dashboard statistics and department distribution.
2. Employee search, filters, sorting, and pagination.
3. Employee creation, details, editing, and deletion.
4. Required fields and invalid-input validation.
5. Duplicate-email handling.
6. Conditional contract end date and department-designation dependency.
7. Department creation, editing, activation, and deactivation.
8. Department deletion restrictions.
9. Correct handling of soft-deleted employees.
10. CSV export with and without filters.

The supplied Postman collection can also be used to test the API endpoints.

## Screenshots

The `screenshots/` directory contains screenshots demonstrating the application's main screens and functionality.

Recommended screenshot coverage:

| Filename | Description |
|---|---|
| `01-dashboard.png` | Dashboard and employee statistics |
| `02-employee-list.png` | Employee list |
| `03-filtered-employees.png` | Filtered employee results |
| `04-add-employee.png` | Add employee form |
| `05-edit-employee.png` | Edit employee form |
| `06-validation-errors.png` | Employee form validation errors |
| `07-employee-details.png` | Employee details dialog |
| `08-delete-confirmation.png` | Employee deletion confirmation |
| `09-departments.png` | Department management |
| `10-department-delete-blocked.png` | Department deletion restriction |
| `11-department-form.png` | Department creation or editing form |

Ensure the filenames match the actual image files committed to the repository.

## Demo Video

The demonstration video showcases the Employee Management System, including employee CRUD operations, department management, and dynamic form functionality.

**[Watch Employee Management System Demo](https://drive.google.com/file/d/1DHDsAbBCcP6Vo5gSf0TFV7x0HN5h2wT3/view?usp=sharing)**

The video is hosted on Google Drive. Ensure that anyone with the link can view it.

## Known Limitations and Incomplete Features

- The application is intended to run locally using the setup instructions in this README.
- The project does not claim bonus features such as JWT authentication with role-based access, profile photo uploads, audit history, frontend component tests, Swagger/OpenAPI documentation, Docker Compose, or a UI for editing form configuration unless those features are present and working in the submitted code.
- Any additional incomplete assignment requirement should be documented here accurately.

## Assumptions

- PostgreSQL is used as the persistent database.
- Database credentials and environment-specific settings are supplied through environment variables.
- Employee records are soft-deleted where the application implements soft deletion.
- The evaluator will use the documented setup instructions and included sample data to run and evaluate the application.
- The database initialization process must follow the actual schema, seed script, and migration dependencies in the repository.

## Security Considerations

- Do not commit actual environment files containing credentials.
- Use `.env.example` files as configuration templates without local secrets.
- Exclude virtual environments, installed dependencies, and generated build files from version control.
- Production deployment requires appropriate secret-key management, debug settings, allowed hosts, database permissions, and CORS configuration.

## License

No open-source license is specified in this repository.
