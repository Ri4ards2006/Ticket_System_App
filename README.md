🎫 FlashTicket Nano: High-Speed Native Engine
FlashTicket Nano represents the pinnacle of streamlined IT service management. By collapsing complex multi-container architectures into a single, high-performance Native Python Engine, we achieved a system that is not only quicker to host but significantly easier to maintain and reach across local servers.

⚡ The "Nano" Advantage: Why it's Better
While the Native stage was too raw and the Micro stage was too complex for rapid deployment, the Nano architecture strikes the perfect balance:

Zero-Overhead Hosting: No Docker or complex web server configuration required; it runs natively via the Python interpreter.

Instant Server Reachability: Once executed, the system is immediately accessible via the Network URL (e.g., http://172.17.12.164:8501).

Native SQLite Performance: Uses a direct-access database layer for sub-millisecond query times.

Self-Healing Infrastructure: Automatically provisions the data/ directory and migrates the database schema on-the-fly if components are missing.

📊 IT-Service Lifecycle (Process Map)
This diagram illustrates the streamlined service process implemented in the Nano engine, fulfilling the core project requirements for status tracking and feedback.

Ticket Initialization: User creates a ticket; system assigns a unique ID and "Neu" status.

Active Support Interaction: Support staff enters real-time feedback directly into the ticket.

Status Synchronization: The system updates the view instantly for the user once the status changes to "In Bearbeitung".

Full Loop Communication: The user sees the specific "Support Rückmeldung" in their dashboard, ensuring transparency.

📁 Optimized Project Structure
The Nano version utilizes a flat, efficient directory structure designed for quick server deployment:

Plaintext

Ticket_System_Nano/
├── app.py             # Single-File Engine: UI, Logic, & Auth
├── requirements.txt   # Minimum dependencies (Streamlit)
└── data/              # Auto-created Persistent Storage
    └── tickets.db     # SQLite3 Database with SHA-256 Security
🚀 Server Deployment & Access
1. Requirements
Ensure Python 3.13+ is installed on the host server.

2. Launching the Engine
Run the system using the module wrapper to ensure all internal paths are correctly mapped:

Bash

python3 -m streamlit run app.py
3. Network Access
The system will output a Network URL. Use this IP address to reach the Ticket System from any device within the same network.

🔐 Security & Roles
Administrator: Complete control over users and the database.

Support: Capability to update statuses and provide technical feedback.

Anwender: Secure ticket creation and personal dashboard to view support replies.
