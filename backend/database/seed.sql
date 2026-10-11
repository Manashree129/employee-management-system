-- Employee Management System - seed data (PostgreSQL)
-- Run AFTER the tables exist (python manage.py migrate, or schema.sql). Safe to re-run:
-- every INSERT uses ON CONFLICT DO NOTHING. Salaries are annual amounts in INR (assumption).
BEGIN;

-- Departments (OPS is intentionally inactive for testing the 'department must be active' rule)
INSERT INTO departments (id, name, code, is_active, created_at, updated_at) VALUES
  (1, 'Engineering', 'ENG', TRUE, NOW(), NOW()),
  (2, 'Human Resources', 'HR', TRUE, NOW(), NOW()),
  (3, 'Finance', 'FIN', TRUE, NOW(), NOW()),
  (4, 'Marketing', 'MKT', TRUE, NOW(), NOW()),
  (5, 'Sales', 'SAL', TRUE, NOW(), NOW()),
  (6, 'Legacy Operations', 'OPS', FALSE, NOW(), NOW())
ON CONFLICT DO NOTHING;

-- Designations
INSERT INTO designations (id, department_id, name) VALUES
  (1, 1, 'Software Engineer'),
  (2, 1, 'Senior Software Engineer'),
  (3, 1, 'QA Engineer'),
  (4, 2, 'HR Executive'),
  (5, 2, 'Talent Acquisition Specialist'),
  (6, 3, 'Accountant'),
  (7, 3, 'Financial Analyst'),
  (8, 3, 'Payroll Specialist'),
  (9, 4, 'Marketing Executive'),
  (10, 4, 'Content Strategist'),
  (11, 4, 'SEO Specialist'),
  (12, 5, 'Sales Executive'),
  (13, 5, 'Account Manager'),
  (14, 6, 'Operations Coordinator'),
  (15, 6, 'Logistics Associate')
ON CONFLICT DO NOTHING;

-- Lookup values (dropdown options)
INSERT INTO lookup_values (category, value, label, display_order, is_active) VALUES
  ('gender', 'Male', 'Male', 1, TRUE),
  ('gender', 'Female', 'Female', 2, TRUE),
  ('gender', 'Other', 'Other', 3, TRUE),
  ('employment_type', 'Permanent', 'Permanent', 1, TRUE),
  ('employment_type', 'Contract', 'Contract', 2, TRUE),
  ('employment_type', 'Intern', 'Intern', 3, TRUE),
  ('employee_status', 'active', 'Active', 1, TRUE),
  ('employee_status', 'inactive', 'Inactive', 2, TRUE)
ON CONFLICT DO NOTHING;

-- Dynamic form configuration for the employee form
INSERT INTO form_field_configs (form_name, field_name, label, input_type, placeholder, display_order, is_required, validation_rules, conditional_rules, options_source, depends_on, default_value, is_active) VALUES
  ('employee', 'employeeCode', 'Employee Code', 'text', 'Generated automatically on save', 0, FALSE, $j${"readOnly":true}$j$::jsonb, NULL, '', '', NULL, TRUE),
  ('employee', 'firstName', 'First Name', 'text', 'Enter first name', 1, TRUE, $j${"minLength":2,"maxLength":50,"pattern":"^[A-Za-z]+$","patternMessage":"First name must contain letters only."}$j$::jsonb, NULL, '', '', NULL, TRUE),
  ('employee', 'lastName', 'Last Name', 'text', 'Enter last name', 2, TRUE, $j${"minLength":1,"maxLength":50}$j$::jsonb, NULL, '', '', NULL, TRUE),
  ('employee', 'email', 'Email', 'email', 'name@company.com', 3, TRUE, $j${"maxLength":254}$j$::jsonb, NULL, '', '', NULL, TRUE),
  ('employee', 'mobileNumber', 'Mobile Number', 'tel', '10-digit mobile number', 4, TRUE, $j${"pattern":"^[0-9]{10}$","patternMessage":"Mobile number must contain exactly 10 digits."}$j$::jsonb, NULL, '', '', NULL, TRUE),
  ('employee', 'dateOfBirth', 'Date of Birth', 'date', '', 5, TRUE, $j${"minAge":18,"notFuture":true}$j$::jsonb, NULL, '', '', NULL, TRUE),
  ('employee', 'gender', 'Gender', 'select', 'Select gender', 6, TRUE, $j${}$j$::jsonb, NULL, 'lookup:gender', '', NULL, TRUE),
  ('employee', 'departmentId', 'Department', 'select', 'Select department', 7, TRUE, $j${}$j$::jsonb, NULL, 'departments', '', NULL, TRUE),
  ('employee', 'designationId', 'Designation', 'select', 'Select designation', 8, TRUE, $j${}$j$::jsonb, NULL, 'designations', 'departmentId', NULL, TRUE),
  ('employee', 'employmentType', 'Employment Type', 'select', 'Select employment type', 9, TRUE, $j${}$j$::jsonb, NULL, 'lookup:employment_type', '', NULL, TRUE),
  ('employee', 'joiningDate', 'Joining Date', 'date', '', 10, TRUE, $j${"notFuture":true}$j$::jsonb, NULL, '', '', NULL, TRUE),
  ('employee', 'contractEndDate', 'Contract End Date', 'date', '', 11, TRUE, $j${"laterThanField":"joiningDate"}$j$::jsonb, $j${"field":"employmentType","operator":"in","value":["Contract","Intern"]}$j$::jsonb, '', '', NULL, TRUE),
  ('employee', 'salary', 'Salary', 'number', 'Enter salary', 12, TRUE, $j${"greaterThan":0,"step":0.01}$j$::jsonb, NULL, '', '', NULL, TRUE),
  ('employee', 'address', 'Address', 'textarea', 'Enter address (optional)', 13, FALSE, $j${"maxLength":250}$j$::jsonb, NULL, '', '', NULL, TRUE),
  ('employee', 'isActive', 'Active', 'checkbox', '', 14, FALSE, $j${}$j$::jsonb, NULL, '', '', $j$true$j$::jsonb, TRUE)
ON CONFLICT DO NOTHING;

-- Employees (28 visible: 24 active + 4 inactive; plus 1 soft-deleted record, EMP00029)
INSERT INTO employees (id, employee_code, first_name, last_name, email, mobile_number, date_of_birth, gender, department_id, designation_id, employment_type, joining_date, contract_end_date, salary, address, is_active, is_deleted, created_at, updated_at) VALUES
  (1, 'EMP00001', 'Aarav', 'Sharma', 'aarav.sharma@acmetech.example', '6043321819', '1990-03-14', 'Male', 1, 2, 'Permanent', '2018-06-04', NULL, 2200000.00, '12 MG Road, Bengaluru', TRUE, FALSE, NOW(), NOW()),
  (2, 'EMP00002', 'Priya', 'Patel', 'priya.patel@acmetech.example', '9001338908', '1993-07-22', 'Female', 1, 1, 'Permanent', '2021-01-11', NULL, 1400000.00, '45 Satellite Road, Ahmedabad', TRUE, FALSE, NOW(), NOW()),
  (3, 'EMP00003', 'Rohan', 'Mehta', 'rohan.mehta@acmetech.example', '7863794026', '1996-11-05', 'Male', 1, 1, 'Permanent', '2022-08-01', NULL, 1250000.00, '8 Linking Road, Mumbai', TRUE, FALSE, NOW(), NOW()),
  (4, 'EMP00004', 'Ananya', 'Iyer', 'ananya.iyer@acmetech.example', '8423511615', '1994-02-18', 'Female', 1, 3, 'Permanent', '2020-03-16', NULL, 1100000.00, '22 Anna Salai, Chennai', TRUE, FALSE, NOW(), NOW()),
  (5, 'EMP00005', 'Vikram', 'Singh', 'vikram.singh@acmetech.example', '8940781618', '1988-09-30', 'Male', 1, 2, 'Permanent', '2016-02-01', NULL, 2600000.00, '7 Civil Lines, Jaipur', TRUE, FALSE, NOW(), NOW()),
  (6, 'EMP00006', 'Sneha', 'Nair', 'sneha.nair@acmetech.example', '8959310341', '1998-05-09', 'Female', 1, 1, 'Contract', '2025-10-01', '2026-12-31', 1000000.00, '19 Marine Drive, Kochi', TRUE, FALSE, NOW(), NOW()),
  (7, 'EMP00007', 'Arjun', 'Reddy', 'arjun.reddy@acmetech.example', '7164752553', '2002-12-01', 'Male', 1, 3, 'Intern', '2026-07-01', '2026-12-31', 360000.00, '31 Banjara Hills, Hyderabad', TRUE, FALSE, NOW(), NOW()),
  (8, 'EMP00008', 'Kavya', 'Gupta', 'kavya.gupta@acmetech.example', '8192832764', '1995-04-27', 'Female', 1, 1, 'Permanent', '2019-09-23', NULL, 1350000.00, '', FALSE, FALSE, NOW(), NOW()),
  (9, 'EMP00009', 'Rahul', 'Verma', 'rahul.verma@acmetech.example', '7503056413', '1985-01-12', 'Male', 2, 4, 'Permanent', '2014-07-07', NULL, 950000.00, '3 Hazratganj, Lucknow', TRUE, FALSE, NOW(), NOW()),
  (10, 'EMP00010', 'Meera', 'Kulkarni', 'meera.kulkarni@acmetech.example', '8376724238', '1991-08-19', 'Female', 2, 5, 'Permanent', '2019-02-18', NULL, 1050000.00, '14 FC Road, Pune', TRUE, FALSE, NOW(), NOW()),
  (11, 'EMP00011', 'Siddharth', 'Joshi', 'siddharth.joshi@acmetech.example', '8969653287', '1997-06-06', 'Male', 2, 4, 'Contract', '2025-12-01', '2026-11-30', 720000.00, '', TRUE, FALSE, NOW(), NOW()),
  (12, 'EMP00012', 'Neha', 'Desai', 'neha.desai@acmetech.example', '6012269166', '1992-10-25', 'Female', 2, 5, 'Permanent', '2020-11-02', NULL, 1000000.00, '66 Ellis Bridge, Ahmedabad', FALSE, FALSE, NOW(), NOW()),
  (13, 'EMP00013', 'Karan', 'Kapoor', 'karan.kapoor@acmetech.example', '9848018451', '1987-03-03', 'Male', 3, 7, 'Permanent', '2015-04-13', NULL, 1800000.00, '9 Connaught Place, New Delhi', TRUE, FALSE, NOW(), NOW()),
  (14, 'EMP00014', 'Pooja', 'Bose', 'pooja.bose@acmetech.example', '8627048281', '1990-12-15', 'Female', 3, 6, 'Permanent', '2017-10-09', NULL, 1200000.00, '101 Park Street, Kolkata', TRUE, FALSE, NOW(), NOW()),
  (15, 'EMP00015', 'Aditya', 'Chopra', 'aditya.chopra@acmetech.example', '8893252880', '1994-09-08', 'Male', 3, 8, 'Permanent', '2021-06-21', NULL, 980000.00, '27 Sector 17, Chandigarh', TRUE, FALSE, NOW(), NOW()),
  (16, 'EMP00016', 'Ishita', 'Menon', 'ishita.menon@acmetech.example', '8701543039', '2003-02-20', 'Female', 3, 6, 'Intern', '2026-06-01', '2026-11-30', 300000.00, '', TRUE, FALSE, NOW(), NOW()),
  (17, 'EMP00017', 'Manish', 'Agarwal', 'manish.agarwal@acmetech.example', '6171822782', '1989-07-11', 'Male', 3, 7, 'Contract', '2025-04-01', '2026-12-31', 1500000.00, '52 Camac Street, Kolkata', TRUE, FALSE, NOW(), NOW()),
  (18, 'EMP00018', 'Divya', 'Pillai', 'divya.pillai@acmetech.example', '8896383465', '1996-01-29', 'Female', 4, 10, 'Permanent', '2021-09-06', NULL, 900000.00, '18 Palayam, Thiruvananthapuram', TRUE, FALSE, NOW(), NOW()),
  (19, 'EMP00019', 'Sanjay', 'Rao', 'sanjay.rao@acmetech.example', '9871331509', '1986-05-17', 'Male', 4, 9, 'Permanent', '2013-12-02', NULL, 1300000.00, '5 Jayanagar, Bengaluru', TRUE, FALSE, NOW(), NOW()),
  (20, 'EMP00020', 'Riya', 'Banerjee', 'riya.banerjee@acmetech.example', '7930103105', '1999-08-04', 'Female', 4, 11, 'Contract', '2025-08-18', '2026-10-31', 780000.00, '', TRUE, FALSE, NOW(), NOW()),
  (21, 'EMP00021', 'Amit', 'Shah', 'amit.shah@acmetech.example', '6834738299', '1993-11-23', 'Male', 4, 9, 'Permanent', '2020-01-20', NULL, 1000000.00, '90 CG Road, Ahmedabad', FALSE, FALSE, NOW(), NOW()),
  (22, 'EMP00022', 'Shruti', 'Malhotra', 'shruti.malhotra@acmetech.example', '9376311656', '2004-03-12', 'Female', 4, 10, 'Intern', '2026-05-04', '2026-11-04', 276000.00, '', TRUE, FALSE, NOW(), NOW()),
  (23, 'EMP00023', 'Nikhil', 'Khan', 'nikhil.khan@acmetech.example', '9701065133', '1991-02-07', 'Male', 5, 13, 'Permanent', '2018-03-05', NULL, 1600000.00, '33 Residency Road, Bengaluru', TRUE, FALSE, NOW(), NOW()),
  (24, 'EMP00024', 'Tanvi', 'Jain', 'tanvi.jain@acmetech.example', '7872624731', '1995-06-14', 'Female', 5, 12, 'Permanent', '2022-02-14', NULL, 850000.00, '11 MI Road, Jaipur', TRUE, FALSE, NOW(), NOW()),
  (25, 'EMP00025', 'Harsh', 'Saxena', 'harsh.saxena@acmetech.example', '9810801326', '1998-10-02', 'Male', 5, 12, 'Contract', '2026-01-12', '2026-12-31', 720000.00, '', TRUE, FALSE, NOW(), NOW()),
  (26, 'EMP00026', 'Pallavi', 'Bhatt', 'pallavi.bhatt@acmetech.example', '9736026064', '1990-04-21', 'Female', 5, 13, 'Permanent', '2017-05-15', NULL, 1550000.00, '72 Alkapuri, Vadodara', TRUE, FALSE, NOW(), NOW()),
  (27, 'EMP00027', 'Deepak', 'Naidu', 'deepak.naidu@acmetech.example', '9468723430', '1984-12-09', 'Male', 5, 13, 'Permanent', '2012-08-20', NULL, 1900000.00, '4 Jubilee Hills, Hyderabad', TRUE, FALSE, NOW(), NOW()),
  (28, 'EMP00028', 'Aisha', 'Das', 'aisha.das@acmetech.example', '6500978820', '1994-03-30', 'Female', 6, 14, 'Permanent', '2019-07-01', NULL, 800000.00, '15 Salt Lake, Kolkata', FALSE, FALSE, NOW(), NOW()),
  (29, 'EMP00029', 'Faisal', 'Sheikh', 'faisal.sheikh@acmetech.example', '6219136193', '1992-09-16', 'Male', 5, 12, 'Permanent', '2020-06-08', NULL, 820000.00, '60 Bandra West, Mumbai', TRUE, TRUE, NOW(), NOW())
ON CONFLICT DO NOTHING;

-- Re-sync identity sequences after inserting explicit ids
SELECT setval(pg_get_serial_sequence('departments', 'id'), (SELECT MAX(id) FROM departments));
SELECT setval(pg_get_serial_sequence('designations', 'id'), (SELECT MAX(id) FROM designations));
SELECT setval(pg_get_serial_sequence('lookup_values', 'id'), (SELECT MAX(id) FROM lookup_values));
SELECT setval(pg_get_serial_sequence('employees', 'id'), (SELECT MAX(id) FROM employees));
SELECT setval(pg_get_serial_sequence('form_field_configs', 'id'), (SELECT MAX(id) FROM form_field_configs));

COMMIT;
