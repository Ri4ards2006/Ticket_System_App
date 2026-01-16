🎫 FlashTicket: Nano-Micro-Native Support Engine
FlashTicket is a high-performance, lightweight ticket system built for IT infrastructure efficiency. It removes unnecessary overhead and offers a "Zero-Training" interface, letting end-users and support teams operate without prior training.

🚀 Architecture Evolution: From Native to Micro to Nano
FlashTicket’s design evolved in three stages to balance speed, stability, and real-world usability. Here’s the journey:

1. Native Stage: Speed Over All (Initial Foundation)
The project began with a Native architecture, prioritizing raw performance. The core logic (ticket creation, status updates, database interactions) was optimized for minimal computational overhead. For example:

Direct SQLite3 database calls without abstraction layers reduced function call delays.
No extra features (like user roles or feedback tools) were added—focus was purely on speed.
However, this monolithic design had flaws: adding new features (e.g., role-based access) required modifying central code, making scaling difficult. It worked for simple needs but couldn’t grow with complex IT infrastructure demands.

2. Micro Stage: Scalability Through Modularity (Iterative Improvement)
To fix the Native stage’s rigidity, we transitioned to Micro architecture. This phase split the system into modular components to enable flexible scaling:

User Management Module: Separated authentication (password hashing) and role storage from ticket logic.
Ticket Processing Module: Focused on ticket CRUD (Create, Read, Update, Delete) operations, including status transitions and feedback handling.
UI Rendering Module: Isolated frontend display logic (e.g., form layouts, table designs) from backend logic.
Modularity let teams work on separate parts without conflicts. For instance, the UI team could refine ticket forms while the backend team added new database checks. But it introduced complexity: modules had to communicate carefully, and setup became less straightforward for new users.

3. Nano Stage: Current Design (Unified, User-Centric)
The Nano stage merges the best of Native and Micro into a streamlined, user-friendly system. Key goals:

Simplicity: Single entry point (no need to manage multiple modules).
Responsiveness: Real-time updates via Streamlit’s reactive UI.
Future-Proofing: Minimal dependencies and adaptive styling.
What Changed?
Streamlit Frontend: Replaced custom UI code with Streamlit, a Python library that auto-renders interactive interfaces. This cut development time and ensures a consistent, intuitive experience (no training needed!).
SQLite Integration: Retained SQLite3 for its lightweight nature but added safeguards:
Auto-creates the data/ directory if missing (os.makedirs(...)).
Adds backward compatibility (e.g., auto-inserts support_feedback column into older databases).
Enforces Foreign Keys to protect data integrity (links users to tickets).
Single-Point-of-Entry: All logic (UI, database, authentication) lives in one file (src/app.py), simplifying deployment and reducing confusion.
This stage addresses the pain points of earlier versions: it’s fast (Native’s speed), scalable (Micro’s modularity), and easy to use (user-centric design).

📁 Project Structure
FlashTicket’s codebase is organized to reflect its Nano architecture, with clear separation of concerns. Here’s the structure:


Collapse
Copy
1
2
3
4
5
6
7
FlashTicket/  
├── README.md          # This file: project overview, architecture, and usage  
├── requirements.txt   # List of Python dependencies (auto-generated if requested)  
├── src/               # Source code directory  
│   └── app.py         # Main application file (contains all core logic)  
└── data/              # Auto-created directory for SQLite database storage  
    └── tickets.db     # Central database storing user data and tickets  
Key Components Explained
1. src/app.py (The Core of FlashTicket)
This file contains all critical logic:

Streamlit Setup: Configures the app’s title, icon, layout, and sidebar menu.
Database Initialization: Uses the TicketDatabase class to connect to SQLite, create tables, and handle compatibility (e.g., older databases).
Authentication: Manages user login (checks credentials via _check_user method).
Page Routing: Switches between pages (Ticket Overview, New Ticket, User Management) based on the sidebar menu.
Role-Based Access: Restricts features (e.g., only admins see User Management).
2. TicketDatabase Class (Database Handler)
Defined inside app.py, this class manages database interactions:

Directory Safety: Auto-creates the data/ folder if missing (os.makedirs(...)).
Table Creation: Sets up users (credentials) and tickets (ticket data) tables with strict schemas.
Compatibility Fixes: Adds missing columns (like support_feedback) to older databases.
CRUD Operations: Functions to add/delete users, create/update tickets, and fetch data.
Permission Checks: Validates if users can edit ticket statuses or delete tickets (e.g., only admins or ticket creators).
3. data/tickets.db (Database Storage)
Stores two tables:

users: Tracks usernames, SHA-256 hashed passwords, and roles (Anwender/Support/Administrator).
tickets: Stores ticket details (ID, title, description, priority, status) with timestamps, creator/assignee info, and feedback fields (feedback for users, support_feedback for support teams).
⚡ Quick Start
Run the System
Execute this command from the project root to start FlashTicket:

bash

Collapse
Copy
1
python3 -m streamlit run src/app.py  
Access Features
After logging in, your role determines what you can do:

End-user: Create tickets, view support feedback, and track ticket statuses.
Support: Update ticket statuses (e.g., "New" → "In Progress"), add real-time feedback, and manage assigned tickets.
Administrator: Add/delete users, modify roles, and oversee all ticket operations.
🛠️ Technical Notes
Terminal Issue Fix: If streamlit isn’t recognized, use python3 -m streamlit run ... (avoids PATH configuration problems).
Documentation Screenshots (Jan 27th):
System Overview: Show the Tech Stack and note the system is accessible via Network URL company-wide.
Service Process: Draw a diagram of ticket flow (creation → status update → resolution with feedback).
Support Feedback Feature: Highlight the bold statement: "Direct Communication: Support can write real-time feedback directly into tickets—you’ll see updates instantly."
Requirements.txt: Need a script to auto-generate dependencies? Let me know—I can provide one!
