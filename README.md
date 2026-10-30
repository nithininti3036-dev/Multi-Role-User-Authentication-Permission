# Multi-Role User Authentication & Dynamic Permission System (RBAC)

A production-ready **Backend API** built with **Python (FastAPI)** and **MySQL**, implementing **Dynamic Role-Based Access Control (RBAC)**, **JWT Authentication**, and granular **Permission Barriers**.

---

## 🌟 Key Features

- 🔐 **JWT Authentication & Bcrypt Security**:
  - Secure password hashing using Bcrypt (cost factor 12).
  - Short-lived Access Tokens (default 60 mins) & Long-lived Refresh Tokens (7 days).
  - Instant token revocation & user deactivation checks.

- 👥 **Dynamic Multi-Role RBAC**:
  - **Users** can hold **multiple roles** simultaneously.
  - **Roles** have sets of **granular permissions** (e.g., `user:create`, `report:read`, `role:assign`).
  - Permissions are aggregated dynamically across all user roles in real-time.
  - Roles and permissions can be created, edited, and assigned via API without modifying code.

- 👑 **SuperAdmin Override**:
  - Built-in root administrator support with wildcard permissions (`*:*`).

- 🛡️ **Reusable Security Dependencies**:
  - `require_permissions("perm1", "perm2", match_all=True|False)`
  - `require_roles("Role1", "Role2")`
  - Self-or-Admin authorization checks for user management.

- 📝 **Audit Trail Logging**:
  - Automatic audit records stored for logins, failed attempts, role reassignments, and account modifications.

- 🗄️ **Flexible MySQL & SQLAlchemy Integration**:
  - Native MySQL schema (`database/schema.sql`) and seed script (`database/seed.sql`).
  - Automatic schema generation & seeding on startup.
  - Built-in graceful SQLite fallback mode for rapid development and testing if MySQL is temporarily offline.

- 🚀 **Interactive OpenAPI & Swagger UI**:
  - Built-in interactive documentation at `http://127.0.0.1:8000/docs` with token authorization testing.

---

## 🏗️ Architecture & Database Design

### RBAC Entity-Relationship Diagram

```
+----------------+          +-------------------+          +----------------+
|     users      |          |    user_roles     |          |     roles      |
+----------------+          +-------------------+          +----------------+
| id (PK)        |<-------->| user_id (FK)      |<-------->| id (PK)        |
| username       |          | role_id (FK)      |          | name           |
| email          |          | assigned_at       |          | description    |
| hashed_password|          +-------------------+          | is_system      |
| full_name      |                                         +----------------+
| is_active      |                                                 |
| is_verified    |                                                 |
| created_at     |                                                 |
+----------------+                                                 v
        |                                                  +--------------------+
        |                                                  |  role_permissions  |
        v                                                  +--------------------+
+----------------+                                         | role_id (FK)       |
|   audit_logs   |                                         | permission_id (FK) |
+----------------+                                         +--------------------+
| id (PK)        |                                                 ^
| user_id (FK)   |                                                 |
| action         |                                                 |
| resource       |                                         +----------------+
| ip_address     |                                         |  permissions   |
| timestamp      |                                         +----------------+
+----------------+                                         | id (PK)        |
                                                           | name (unique)  |
                                                           | resource       |
                                                           | action         |
                                                           | description    |
                                                           +----------------+
```

### Pre-configured Default Roles & Permissions

| Role | Permissions Assigned | Purpose |
| :--- | :--- | :--- |
| **SuperAdmin** | `*:*` (Wildcard root access to all endpoints) | System Owner |
| **Admin** | `user:*`, `role:*`, `permission:*`, `content:*`, `report:*`, `audit:read` | System Administrator |
| **Manager** | `user:read`, `content:*`, `report:create`, `report:read`, `report:export` | Department Manager |
| **User** | `content:read`, `report:read` | Standard Registered User |

---

## 📂 Project Structure

```
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py             # Login, register, token refresh, profile
│   │       │   ├── users.py            # User management & role assignment
│   │       │   ├── roles.py            # Role CRUD & permission linking
│   │       │   ├── permissions.py      # Permission catalog endpoints
│   │       │   ├── audit.py            # Audit log inspection
│   │       │   └── demo_resources.py   # Guarded demo resources
│   │       └── router.py               # Aggregated v1 API router
│   ├── core/
│   │   ├── config.py                   # App settings & .env validation
│   │   ├── security.py                 # Bcrypt & JWT token functions
│   │   └── dependencies.py             # Auth & RBAC guard dependencies
│   ├── db/
│   │   ├── base.py                     # SQLAlchemy DeclarativeBase
│   │   ├── session.py                  # Database engine & sessionmaker
│   │   └── init_db.py                  # DB auto-initialization & seeder
│   ├── models/
│   │   ├── user.py                     # User model & user_roles table
│   │   ├── role.py                     # Role model & role_permissions table
│   │   ├── permission.py               # Permission model
│   │   └── audit_log.py                # Audit trail model
│   ├── schemas/                        # Pydantic validation schemas
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── role.py
│   │   ├── permission.py
│   │   └── audit_log.py
│   ├── services/                       # Business logic services
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── rbac_service.py
│   │   └── audit_service.py
│   └── main.py                         # FastAPI application entry point
├── database/
│   ├── schema.sql                      # Native MySQL DDL script
│   └── seed.sql                        # Native MySQL seed data
├── tests/
│   └── test_rbac.py                    # Pytest test suite
├── .env.example                        # Template environment variables
├── .env                                # Active environment configuration
├── requirements.txt                    # Project dependencies
├── run.py                              # Server launcher CLI
└── README.md                           # Documentation
```

---

## ⚡ Quick Start Guide

### 1. Prerequisites
- Python 3.10+
- MySQL Server 8.0+ / MariaDB 10.4+ (or XAMPP / Docker MySQL)

### 2. Configure Environment (`.env`)
Create or edit `.env` in the root folder:

```ini
# MySQL Configuration
MYSQL_SERVER=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=rbac_db

# Security
SECRET_KEY=super-secret-jwt-key-change-this-in-production-1234567890
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Fallback to local SQLite if MySQL is unreachable during local test
USE_SQLITE_FALLBACK_ON_ERROR=True
```

### 3. (Optional) Manual MySQL Setup
You can either let the backend create the tables automatically on startup, or import the SQL scripts directly into MySQL:

```bash
mysql -u root -p < database/schema.sql
mysql -u root -p < database/seed.sql
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Launch the Application
```bash
python run.py
```
Or with uvicorn directly:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

---

## 🔑 Default Accounts (Pre-Seeded)

| Account | Email | Password | Roles |
| :--- | :--- | :--- | :--- |
| **SuperAdmin** | `admin@example.com` | `Admin@123456` | `SuperAdmin`, `Admin` |
| **Manager** | `manager@example.com` | `Manager@123456` | `Manager` |
| **Standard User** | `user@example.com` | `User@123456` | `User` |

---

## 🧪 Testing the APIs via Swagger UI

1. Open your browser and navigate to:
   ```
   http://127.0.0.1:8000/docs
   ```
2. Scroll to `POST /api/v1/auth/login` and click **Try it out**.
3. Log in with `admin@example.com` and `Admin@123456`.
4. Copy the `access_token` from the response.
5. Click the green **Authorize** button at the top right of the Swagger UI.
6. Paste the token into the value box and click **Authorize**.
7. Now all protected endpoints can be executed directly from your browser!

---

## 📋 Key API Endpoints

### 🔐 Authentication (`/api/v1/auth`)
| Method | Endpoint | Description | Permission Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Register new user (assigns default 'User' role) | Public |
| `POST` | `/api/v1/auth/login` | Login and obtain JWT access & refresh tokens | Public |
| `POST` | `/api/v1/auth/refresh` | Renew access token with refresh token | Public |
| `GET` | `/api/v1/auth/me` | Current user profile, roles & effective permissions | Authenticated |
| `POST` | `/api/v1/auth/change-password` | Update current user's password | Authenticated |

### 👥 User Management (`/api/v1/users`)
| Method | Endpoint | Description | Permission Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/users/` | List all users (supports role/active filter) | `user:read` |
| `POST` | `/api/v1/users/` | Create a user with explicit roles | `user:create` |
| `GET` | `/api/v1/users/{id}` | Get user details and assigned roles | `user:read` or Self |
| `PUT` | `/api/v1/users/{id}` | Update user profile | `user:update` or Self |
| `PUT` | `/api/v1/users/{id}/status` | Activate or deactivate user | `user:manage` or `user:delete` |
| `POST` | `/api/v1/users/{id}/roles` | Assign role IDs to user | `role:assign` |
| `DELETE` | `/api/v1/users/{id}/roles/{role_id}` | Remove a role from user | `role:assign` |

### 🛡️ Role Management (`/api/v1/roles`)
| Method | Endpoint | Description | Permission Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/roles/` | List all roles and their attached permissions | `role:read` |
| `POST` | `/api/v1/roles/` | Create a custom role | `role:create` |
| `GET` | `/api/v1/roles/{id}` | Get role by ID | `role:read` |
| `PUT` | `/api/v1/roles/{id}` | Update role name, description, or permissions | `role:update` |
| `DELETE` | `/api/v1/roles/{id}` | Delete custom role (system roles protected) | `role:delete` |
| `POST` | `/api/v1/roles/{id}/permissions` | Assign permissions array to role | `role:update` |

### 📜 Permissions Catalog (`/api/v1/permissions`)
| Method | Endpoint | Description | Permission Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/permissions/` | List all system permissions | `permission:read` |
| `POST` | `/api/v1/permissions/` | Create custom permission | `permission:create` |

### 🔍 Security Audit Logs (`/api/v1/audit-logs`)
| Method | Endpoint | Description | Permission Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/audit-logs/` | View security audit logs with filtering | `audit:read` |

### 🎯 Demonstration Resources (`/api/v1/resources`)
| Method | Endpoint | Description | Access Requirement |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/resources/public` | Public resource | None |
| `GET` | `/api/v1/resources/user-profile` | General user area | Authenticated |
| `GET` | `/api/v1/resources/content` | Read content items | `content:read` |
| `POST` | `/api/v1/resources/content` | Create new content | `content:create` |
| `GET` | `/api/v1/resources/reports` | View analytical reports | `report:read` |
| `POST` | `/api/v1/resources/reports` | Create report | `report:create` |
| `DELETE` | `/api/v1/resources/reports/{id}` | Delete report | `report:delete` |
| `GET` | `/api/v1/resources/admin-system-settings` | High-security system panel | `system:admin` |

---

## 💻 cURL Usage Examples

### 1. User Login
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username_or_email": "admin@example.com", "password": "Admin@123456"}'
```

### 2. Inspect Profile and Permissions
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/auth/me" \
     -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```

### 3. Create a Custom Role with Specific Permissions
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/roles/" \
     -H "Authorization: Bearer <ADMIN_ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "BillingAuditor",
       "description": "Can view and export financial reports",
       "permission_ids": [19, 20]
     }'
```

### 4. Assign Role to User
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/users/3/roles" \
     -H "Authorization: Bearer <ADMIN_ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"role_ids": [4, 5]}'
```

---

## 🧪 Running Automated Tests

Run the full end-to-end RBAC test suite with pytest:

```bash
pytest tests/test_rbac.py -v
```
All tests verify authentication, token parsing, role barriers, and dynamic permission resolution.
