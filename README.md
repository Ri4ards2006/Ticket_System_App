
# Ticket System Evolution: Native → Micro → Nano  

A progressive implementation of a ticketing system showcasing different architectural approaches, from full-stack enterprise solutions to ultra-minimal single-file prototypes. Designed for mid-sized companies (50-100 employees) as a learning project, this repository demonstrates how complexity and scalability can be adjusted to meet specific needs while maintaining core functionality.  


## 🏗️ Architecture Overview  

Three Implementations – One Purpose  
This project presents three versions of the ticket system, each optimized for distinct use cases through varying architectural choices.  

| Version       | Tech Stack                          | Database          | Key Characteristics                          | Best For                          |
|---------------|-------------------------------------|-------------------|----------------------------------------------|-----------------------------------|
| Native        | Flask + PostgreSQL + Docker         | PostgreSQL        | Enterprise-grade, secure, scalable            | Production environments            |
| Micro         | Flask + SQLite                      | SQLite            | Fast, lightweight, all-in-one                 | Rapid prototyping, small teams     |
| Nano          | Python + Streamlit (single file)     | SQLite (auto-created) | Ultra-minimal, zero-config                    | Learning, demos, quick setups      |  


## 🚀 Quick Start  

### Nano Version (Recommended for Beginners)  
```bash
# Clone the repository
git clone https://github.com/Ri4ards2006/Ticket_System_App.git
# Navigate to the Nano directory
cd Ticket_System_Nano
# Install dependencies (if not already installed)
pip install streamlit
# Run the application
streamlit run app.py
# Database is automatically created on first run
```  
Access the app at `http://localhost:8501`.  

### Micro Version (Lightweight)  
```bash
# Clone the repository
git clone [https://github.com/Ri4ards2006/Ticket_System_App.git]
# Navigate to the Micro directory
cd Ticket_System_Micro
# Install dependencies
pip install -r requirements.txt
# Run the application
python app.py
```  
Access the app at `http://localhost:5000`.  

### Native Version (Production-Ready, Docker)  
```bash
# Clone the repository
git clone [https://github.com/Ri4ards2006/Ticket_System_App.git]
# Navigate to the Native directory
cd Ticket_System_Native
# Build and start services (requires Docker)
docker-compose up --build
```  
Services are accessible at:  
- Frontend: `http://localhost:3000`  
- Backend API: `http://localhost:5000`  
- PostgreSQL Database: `localhost:5432` (via pgAdmin or CLI).  


## 📁 Project Structure  

```
TICKET_SYSTEM_APP/
├── Ticket_System_Native/       # Full-stack enterprise version
│   ├── backend/                # Flask REST API implementation
│   ├── frontend/               # React/HTML frontend (user interface)
│   ├── database/               # PostgreSQL configuration scripts
│   ├── Dockerfile              # Docker container setup
│   └── docker-compose.yml      # Multi-service orchestration (API, frontend, DB)
│
├── Ticket_System_Micro/        # Lightweight Flask version
│   ├── app.py                  # All-in-one Flask application logic
│   ├── static/                 # CSS/JS assets for styling and interactivity
│   ├── templates/              # HTML templates (Jinja2) for rendering pages
│   └── init_db.py              # Database initialization script
│
├── Ticket_System_Nano/         # Ultra-minimal version
│   └── app.py                  # Single-file solution (Streamlit + Python)
│
├── tests/                      # Test suites for all versions (unit, integration)
├── docs/                       # Documentation (system overviews, process diagrams)
└── data/                       # Sample data files and export examples
```  


## 🔧 Technical Stack Details  

### Native Version (Production-Ready)  
- **Frontend**: HTML/CSS/JavaScript or React (user interface)  
- **Backend**: Flask (Python REST API) for business logic  
- **Database**: PostgreSQL (with Docker) for enterprise scalability  
- **Security**: JWT authentication, password hashing (bcrypt)  
- **Infrastructure**: Docker containers, `docker-compose` for orchestration  
- **Storage**: Persistent volumes for database durability  
- **Features**:  
  - Role-based access control (User, Support, Admin)  
  - RESTful API endpoints for integration  
  - Database migrations (schema updates)  
  - Environment-based configuration (dev/prod)  
  - Email notifications, file attachments, audit logging  


### Micro Version (Lightweight)  
- **Framework**: Flask (monolithic) for simplified backend  
- **Database**: SQLite (file-based) for minimal setup  
- **Security**: Session-based authentication  
- **Templates**: Jinja2 with Bootstrap (responsive UI)  
- **Features**:  
  - Core ticket lifecycle management (create, edit, resolve)  
  - User role permissions (User, Support, Admin)  
  - Priority/category/status tracking (Low/Medium/High; Bug/Feature/Support)  
  - Search/filter functionality for tickets  
  - CSV exports for data reporting  
  - Responsive design (mobile/desktop compatibility)  


### Nano Version (Minimalist)  
- **File**: Single `app.py` (self-contained codebase)  
- **Database**: SQLite (auto-created on first run)  
- **Dependencies**: Only essential libraries (Streamlit, SQLite3)  
- **UI**: Streamlit (simplified, no HTML/CSS required)  
- **Features**:  
  - Zero-configuration setup (no complex installs)  
  - Full basic ticketing workflow (create, view, update)  
  - Support feedback system with user notifications  
  - Automatic database initialization  
  - Perfect for quick demos or educational use  


## 🗄️ Database Architecture  

All versions auto-initialize their databases with constraints and relationships.  

### Native (PostgreSQL Schema)  
```sql
-- Users table (enterprise-grade user management)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) CHECK (role IN ('user', 'support', 'admin')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tickets table (core ticket tracking)
CREATE TABLE tickets (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    priority VARCHAR(20) CHECK (priority IN ('low', 'medium', 'high')),
    status VARCHAR(20) CHECK (status IN ('open', 'in_progress', 'resolved', 'closed')),
    created_by INTEGER REFERENCES users(id),
    assigned_to INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```  


### Micro & Nano (SQLite Schema)  
```sql
-- Users table (simplified role-based management)
CREATE TABLE users (
    username TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('User', 'Support', 'Admin'))
);

-- Tickets table (core ticket system with feedback)
CREATE TABLE tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    priority TEXT CHECK (priority IN ('Low', 'Medium', 'High')),
    category TEXT CHECK (category IN ('Bug', 'Feature', 'Support')),
    status TEXT CHECK (status IN ('New', 'In Progress', 'Resolved')),
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    created_by TEXT NOT NULL,
    last_updated_by TEXT,
    support_feedback TEXT,  -- Feedback/comment field for Support → User communication
    assigned_to TEXT,
    user_read_feedback BOOLEAN DEFAULT FALSE  -- Flag to track if user viewed feedback (triggers notifications)
);
```  


## 🔒 Security Features  

All versions include:  
- Password hashing (SHA-256 or bcrypt)  
- SQL injection protection (parameterized queries)  
- XSS prevention (input sanitization)  
- Session management (secure cookies)  
- Role-based access control (RBAC)  

Native version adds:  
- JWT (JSON Web Token) authentication (stateless API security)  
- HTTPS enforcement (via Docker/Nginx)  
- Rate limiting (prevents abuse)  
- Strict input validation (schema checks)  
- CORS configuration (secure cross-origin requests)  


## 📊 Performance Comparison  

| Metric           | Native          | Micro          | Nano           |
|------------------|-----------------|----------------|----------------|
| Startup Time     | 30-60s          | 2-5s           | <1s            |
| Memory Usage     | ~500MB          | ~50MB          | ~20MB          |
| Database         | PostgreSQL      | SQLite         | SQLite         |
| Concurrent Users | 1000+           | 100+           | 10-50          |
| Setup Complexity  | High (Docker)   | Medium (Flask) | None (Streamlit) |  


## 🎯 Use Case Recommendations  

- **Choose Native If**:  
  You need enterprise scalability (1000+ users), multi-team deployment, advanced features (email/file attachments), or production-grade security (with DevOps support).  

- **Choose Micro If**:  
  You need a balance of features and simplicity (50-100 users), quick deployment (no Docker), basic security, or limited IT resources.  

- **Choose Nano If**:  
  You need a fast demo/prototype, are learning the system, have a small team (10-50 users), or require zero infrastructure (runs locally with Python/Streamlit).  


## 🧪 Testing  

Run tests for individual versions:  
```bash
cd tests
python test_native.py   # Tests for Native version
python test_micro.py    # Tests for Micro version
python test_nano.py     # Tests for Nano version
```  

Run comprehensive test suite with coverage:  
```bash
pytest --cov=.
```  


## 📈 Roadmap & Evolution  

The project evolves progressively, with each version building on the previous while preserving core ticketing functionality:  
- **Nano**: Proof of concept (MVP) with minimal code and dependencies.  
- **Micro**: Adds features (CSV exports, UI polish) and robustness.  
- **Native**: Production-ready with enterprise security, scalability, and advanced tools (Docker, PostgreSQL).  


## 🤝 Contributing  

1. Fork the repository.  
2. Create a feature branch: `git checkout -b feature/YourFeature`  
3. Commit changes: `git commit -m 'Add/Update: YourFeature'`  
4. Push to your branch: `git push origin feature/YourFeature`  
5. Open a Pull Request.  


## 📄 License  

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.  


## 🙏 Acknowledgments  

Special thanks to:  
- The Flask team for their excellent Python web framework.  
- PostgreSQL for robust, enterprise-grade database solutions.  
- SQLite for lightweight, embedded database capabilities.  
- Docker for simplifying containerization and deployment.
