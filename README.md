# Employee Management System

A full-stack Employee Management System built using **React, Django REST Framework, and PostgreSQL**. The application supports employee and department management, employee search, filtering, sorting, pagination, and configuration-driven forms.

## Project Structure

```text
employee-management-system/
├── .env.example
├── .gitignore
├── README.md
├── screenshots/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── EMS.postman_collection.json
│   ├── config/
│   ├── employees/
│   └── database/
│       ├── schema.sql
│       └── seed.sql
└── frontend/
    ├── .env.example
    ├── package.json
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
```

## Features

### Dashboard
- Displays total, active, and inactive employee counts.
- Shows employee distribution by department.
- Includes loading, error, and empty states.

### Employee Management
- Create, view, edit, and soft-delete employee records.
- Search employees and filter by department or status.
- Sort by employee name and joining date.
- Server-side pagination, with 10 records per page by default.
- Backend-generated employee codes.
- Frontend and backend validation with field-specific error messages.
- Confirmation before deleting an employee.

### Department Management
- View departments and employee counts.
- Create and edit departments.
- Activate and deactivate departments.
- Prevent deletion of departments that have assigned employee records.

### Configuration-Driven Employee Form
- Retrieves form definitions from the backend.
- Uses database configuration for field labels, input types, display order, required status, validation rules, conditional visibility, and default values.
- Displays a read-only, backend-generated employee code.
- Shows the contract end date only for Contract and Intern employees.
- Loads designations according to the selected department.
- Clears dependent designation selections when the department changes.
- Displays backend validation errors alongside relevant fields.

### Additional Features
- Centralized API communication and error handling.
- Reusable React components.
- Success and error notifications.
- Confirmation dialogs.
- Environment-based configuration.
- PostgreSQL database scripts and a Postman collection.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React |
| Frontend tooling | Vite |
| Routing | React Router |
| Backend | Python, Django |
| REST API | Django REST Framework |
| Database | PostgreSQL |
| API testing | Postman |
| Styling | CSS |

## Dependency Requirements

| Software | Version |
|---|---|
| Python | 3.10 or newer |
| Django | 5.2 series |
| Django REST Framework | 3.16 series |
| PostgreSQL | 13 or newer |
| Node.js | 18 or newer |
| React | 18.x |
| React Router | 6.x |

The backend dependency versions are specified in `backend/requirements.txt`, and the frontend dependencies are specified in `frontend/package.json`.

## Installation and Setup

The following instructions use **Windows PowerShell**.

### Prerequisites

Install Python, PostgreSQL, Node.js, and npm before proceeding.

### 1. Create the database

Open PostgreSQL SQL Shell (`psql`) or another PostgreSQL client and create the database:

```sql
CREATE DATABASE employee_db;
```

Use a PostgreSQL account that has permission to connect to and modify this database.

### 2. Configure environment variables

From the project root, copy the environment template:

```powershell
Copy-Item .env.example .env
```

Update the root `.env` file with your local configuration. For example:

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

Replace the example database credentials with your own values. Use a unique Django secret key and keep `.env` out of version control.

### 3. Install backend dependencies

From the project root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 4. Apply database migrations

From the `backend` directory:

```powershell
python manage.py check
python manage.py migrate
```

### 5. Load sample data

From the `backend` directory:

```powershell
psql -U your_postgres_username -d employee_db -f database/seed.sql
```

Replace `your_postgres_username` with the PostgreSQL username configured for your database. Load the sample data after applying the Django migrations.

### 6. Start the backend

From the `backend` directory:

```powershell
python manage.py runserver
```

The backend runs at:

`http://localhost:8000`

The API base URL is:

`http://localhost:8000/api`

Keep this terminal running.

### 7. Install and start the frontend

Open a second terminal at the project root:

```powershell
cd frontend
Copy-Item .env.example .env
npm install
npm run dev
```

Ensure `frontend/.env` contains the API base URL:

```dotenv
VITE_API_BASE_URL=http://localhost:8000/api
```

Open the application at:

`http://localhost:5173`

The frontend origin must match the origin permitted by the backend CORS configuration.

### Initialization Order

1. Create the PostgreSQL database.
2. Configure the root `.env`.
3. Install backend dependencies.
4. Apply Django migrations.
5. Load sample data.
6. Start the backend server.
7. Configure and start the frontend.

## Configuration

| File | Variable | Purpose |
|---|---|---|
| Root `.env` | `DJANGO_SECRET_KEY` | Django secret key |
| Root `.env` | `DJANGO_DEBUG` | Debug mode |
| Root `.env` | `DJANGO_ALLOWED_HOSTS` | Allowed request hosts |
| Root `.env` | `DJANGO_TIME_ZONE` | Application time zone |
| Root `.env` | `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | PostgreSQL connection |
| Root `.env` | `FRONTEND_ORIGIN` | Permitted frontend origin for CORS |
| `frontend/.env` | `VITE_API_BASE_URL` | Backend API base URL |

Commit the `.env.example` templates, not the actual `.env` files.

## Frontend Routes

| Route | Description |
|---|---|
| `/dashboard` | Dashboard and employee statistics |
| `/employees` | Employee list and controls |
| `/employees/new` | Add employee |
| `/employees/:id/edit` | Edit employee |
| `/departments` | Department management |
| `/` | Redirects to `/dashboard` |

Employee details are displayed through a details dialog opened from the employee list.

## Configuration-Driven Form

The employee form retrieves its field definitions from:

`GET /api/form-config/employee`

The form uses the returned configuration to determine field labels, input types, display order, required status, validation rules, conditional visibility, dropdown sources, dependencies, and default values.

The form configuration is stored in the `form_field_configs` database table. The frontend interprets the rules through `src/utils/formRules.js` and renders fields using reusable form components.

The form supports text, email, telephone, number, date, select, textarea, and checkbox inputs.

Contract End Date is displayed for Contract and Intern employees. Designation options depend on the selected department.

Backend validation remains authoritative; changing frontend configuration does not automatically change the backend's validation rules.

## API Overview

All endpoints use the `/api` base path.

| Resource | Method and endpoint | Purpose |
|---|---|---|
| Employees | `GET /employees` | List, search, filter, sort, and paginate |
| Employees | `POST /employees` | Create an employee |
| Employees | `GET /employees/{id}` | Retrieve employee details |
| Employees | `PUT /employees/{id}` | Update an employee |
| Employees | `DELETE /employees/{id}` | Soft-delete an employee |
| Departments | `GET /departments` | Retrieve departments |
| Departments | `POST /departments` | Create a department |
| Departments | `PUT /departments/{id}` | Update a department |
| Departments | `DELETE /departments/{id}` | Delete a department when permitted |
| Designations | `GET /departments/{id}/designations` | Retrieve department designations |
| Lookups | `GET /lookups/{category}` | Retrieve lookup options |
| Form configuration | `GET /form-config/employee` | Retrieve employee form configuration |
| Dashboard | `GET /dashboard/summary` | Retrieve dashboard statistics |

Employee listing supports query parameters including `page`, `size`, `search`, `departmentId`, `status`, `sortBy`, and `sortDir`.

The API returns structured JSON responses. Validation errors include field-specific information where applicable.

The Postman collection is available at:

`backend/EMS.postman_collection.json`

## Validation and Business Rules

- Employee codes are generated by the backend.
- Employee email addresses are normalized and unique across employee records, including soft-deleted records.
- Mobile numbers must contain exactly 10 digits.
- Employee age, joining date, salary, and other fields are validated.
- Permanent employees do not require a contract end date.
- Contract and Intern employees require a valid contract end date.
- Designations must correspond to the selected department.
- Departments with assigned employee records cannot be deleted.
- Soft-deleted employees are excluded from normal employee listings.

## Testing

Run the following checks from the `backend` directory:

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
```

With both servers running, verify the following flows:

1. Dashboard statistics and department distribution.
2. Employee search, filters, sorting, and pagination.
3. Employee details, creation, editing, and deletion.
4. Required fields and invalid-input validation.
5. Duplicate-email handling.
6. Conditional contract end date and department-designation dependency.
7. Department creation, editing, activation, and deactivation.
8. Department deletion restrictions.
9. Correct handling of soft-deleted employees.

The supplied Postman collection can be used to test the API endpoints.

## Screenshots

The `screenshots/` directory contains screenshots demonstrating the application's main screens and functionality.

| Filename | Description |
|---|---|
| `01-dashboard.png` | Dashboard and employee statistics |
| `02-employee-list.png` | Employee list with search, filters, sorting, and pagination |
| `03-filtered-employees.png` | Filtered employee results |
| `04-add-employee.png` | Add employee form |
| `05-edit-employee.png` | Edit employee form |
| `06-validation-errors.png` | Employee form validation errors |
| `07-employee-details.png` | Employee details dialog |
| `08-delete-confirmation.png` | Employee deletion confirmation |
| `09-departments.png` | Department management |
| `10-department-delete-blocked.png` | Department deletion restriction |
| `11-department-form.png` | Department creation or editing form |

## Security Considerations

- Environment files containing credentials must not be committed.
- `.env.example` provides configuration templates without local secrets.
- Virtual environments, installed dependencies, and generated build files should be excluded from version control.
- Production deployment requires appropriate secret-key management, debug settings, allowed hosts, database permissions, and CORS configuration.

## License

Developed as a technical assignment. No open-source license is specified.
