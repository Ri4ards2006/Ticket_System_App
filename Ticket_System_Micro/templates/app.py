import sqlite3
import datetime
import streamlit as st
import hashlib

# Apply dark mode styling with emojis and visual hierarchy
st.markdown("""
    <style>
    body {
        color: white;
        background-color: #1E1E1E;
        font-family: 'Arial', sans-serif;
    }
    .stTextInput input {
        background-color: #333;
        color: white;
        border-radius: 4px;
        padding: 8px;
    }
    .stTextArea textarea {
        background-color: #333;
        color: white;
        border-radius: 4px;
        padding: 8px;
    }
    .stSelectbox select {
        background-color: #333;
        color: white;
        border-radius: 4px;
        padding: 4px;
    }
    .stButton>button {
        background-color: #444;
        color: white;
        border-radius: 4px;
        padding: 6px 12px;
        border: 1px solid #666;
    }
    .stButton>button:hover {
        background-color: #666;
    }
    .priority-badge {
        padding: 4px 8px;
        border-radius: 3px;
        font-weight: bold;
    }
    .status-badge {
        padding: 4px 8px;
        border-radius: 3px;
    }
    .ticket-id { font-weight: bold; }
    .feedback-section { margin-top: 10px; padding: 8px; background-color: #333; }
    </style>
""", unsafe_allow_html=True)

class TicketDatabase:
    def __init__(self, db_path="tickets.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON")  # Enable foreign key enforcement
        self._initialize_tables()

    def _initialize_tables(self):
        # Users table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('Anwender', 'Support', 'Administrator'))
            )
        ''')
        # Tickets table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT NOT NULL CHECK(priority IN ('Niedrig', 'Mittel', 'Hoch')),
                category TEXT NOT NULL CHECK(category IN ('Bug', 'Feature', 'Support')),
                status TEXT NOT NULL CHECK(status IN ('Neu', 'In Bearbeitung', 'Erledigt')),
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                created_by TEXT NOT NULL,
                last_updated_by TEXT,
                feedback TEXT,
                assigned_to TEXT,
                FOREIGN KEY (created_by) REFERENCES users(username),
                FOREIGN KEY (last_updated_by) REFERENCES users(username),
                FOREIGN KEY (assigned_to) REFERENCES users(username)
            )
        ''')
        # Create default admin user if not exists
        self.cursor.execute("SELECT username FROM users WHERE username='admin'")
        if not self.cursor.fetchone():
            self.add_user("admin", "admin123", "Administrator")
        self.conn.commit()

    def add_user(self, username, password, role):
        """Add new user to database with hashed password"""
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            self.cursor.execute('''
                INSERT INTO users (username, password_hash, role)
                VALUES (?, ?, ?)
            ''', (username, password_hash, role))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Benutzer hinzufügen): {e}")
            return False

    def check_user(self, username, password):
        """Check if user credentials are valid and return role"""
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            self.cursor.execute('''
                SELECT role FROM users WHERE username=? AND password_hash=?
            ''', (username, password_hash))
            role = self.cursor.fetchone()
            return role[0] if role else None
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Benutzer prüfen): {e}")
            return None

    def add_ticket(self, title, description, priority, category, created_by):
        """Add new ticket with initial status 'Neu'"""
        try:
            created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            updated_at = created_at  # Initialer Zeitstempel = Erstellungszeit
            self.cursor.execute('''
                INSERT INTO tickets (title, description, priority, category, status, created_at, updated_at, created_by)
                VALUES (?, ?, ?, ?, 'Neu', ?, ?, ?)
            ''', (title, description, priority, category, created_at, updated_at, created_by))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Ticket erstellen): {e}")
            return None

    def get_tickets(self, search_query=None, priorities=None, statuses=None, created_by=None, assigned_to=None):
        """Retrieve tickets with optional search and filters"""
        try:
            query_conditions = []
            params = ()

            base_query = "SELECT id, title, description, priority, category, status, created_at, updated_at, created_by, last_updated_by, feedback FROM tickets"

            # Search condition
            if search_query:
                search_query = search_query.strip().lower()
                query_conditions.append("(LOWER(title) LIKE ? OR LOWER(description) LIKE ?)")
                params += (f"%{search_query}%", f"%{search_query}%")

            # Priorities filter
            if priorities and priorities != []:
                placeholders = ", ".join(["?"] * len(priorities))
                query_conditions.append(f"priority IN ({placeholders})")
                params += tuple(priorities)

            # Statuses filter
            if statuses and statuses != []:
                placeholders = ", ".join(["?"] * len(statuses))
                query_conditions.append(f"status IN ({placeholders})")
                params += tuple(statuses)

            # Created by filter
            if created_by is not None:
                query_conditions.append("created_by = ?")
                params += (created_by,)

            # Assigned to filter (for Support/Admin)
            if assigned_to is not None:
                query_conditions.append("assigned_to = ?")
                params += (assigned_to,)

            # Combine conditions
            if query_conditions:
                full_query = f"{base_query} WHERE {' AND '.join(query_conditions)} ORDER BY updated_at DESC"
            else:
                full_query = f"{base_query} ORDER BY updated_at DESC"

            self.cursor.execute(full_query, params)
            columns = [desc[0] for desc in self.cursor.description]
            return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Tickets abrufen): {e}")
            return []

    def update_status(self, ticket_id, new_status, updated_by):
        """Update ticket status and update timestamp"""
        try:
            updated_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute('''
                UPDATE tickets SET status=?, updated_at=?, last_updated_by=? WHERE id=?
            ''', (new_status, updated_at, updated_by, ticket_id))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Status aktualisieren): {e}")
            return False

    def update_feedback(self, ticket_id, feedback, updated_by):
        """Update ticket feedback and timestamp"""
        try:
            updated_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute('''
                UPDATE tickets SET feedback=?, updated_at=?, last_updated_by=? WHERE id=?
            ''', (feedback, updated_at, updated_by, ticket_id))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Feedback aktualisieren): {e}")
            return False

    def delete_ticket(self, ticket_id, deleted_by):
        """Delete ticket if user has permissions"""
        try:
            # Check if user is owner or admin
            self.cursor.execute('''
                SELECT created_by FROM tickets WHERE id=? AND (created_by=? OR (SELECT role FROM users WHERE username=?)='Administrator')
            ''', (ticket_id, deleted_by, deleted_by))
            result = self.cursor.fetchone()
            if not result:
                return False  # Permission denied
            
            self.cursor.execute('''
                DELETE FROM tickets WHERE id=?
            ''', (ticket_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Ticket löschen): {e}")
            return False

    def get_users(self):
        """Retrieve all users"""
        try:
            self.cursor.execute("SELECT username, role FROM users")
            columns = [desc[0] for desc in self.cursor.description]
            return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Benutzer abrufen): {e}")
            return []

    def delete_user(self, username):
        """Delete user (requires admin role)"""
        try:
            self.cursor.execute('''
                DELETE FROM users WHERE username=?
            ''', (username,))
            self.conn.commit()
            # Verify deletion
            self.cursor.execute("SELECT username FROM users WHERE username=?", (username,))
            if not self.cursor.fetchone():
                return True
            else:
                st.error(f"Benutzer {username} konnte nicht gelöscht werden (hängende Tickets?)")
                return False
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Benutzer löschen): {e}")
            return False

def create_ticket_page(db):
    """Renders ticket creation form with role checks"""
    if st.session_state.role not in ["Anwender", "Support", "Administrator"]:
        st.error("Du bist kein Anwender! Tickets können nur von Projektteilnehmern erstellt werden.")
        return

    st.title("Neues Ticket erstellen 🎫")
    with st.form("ticket_creation", clear_on_submit=True):
        st.write("Gib Details zu deinem Problem/Forderung ein:")

        title = st.text_input("Titel (erforderlich)", max_chars=100, key="title")
        description = st.text_area("Beschreibung", placeholder="Genauere Details...", key="desc")
        priority = st.selectbox("Priorität", ["Niedrig", "Mittel", "Hoch"], index=1, key="priority")
        category = st.selectbox("Kategorie", ["Bug", "Feature", "Support"], index=0, key="category")

        submit = st.form_submit_button("Ticket erstellen")

        if submit:
            if not title.strip():
                st.error("Titel ist erforderlich!")
                return
            
            ticket_id = db.add_ticket(title, description, priority, category, st.session_state.username)
            if ticket_id:
                st.success(f"TICKET #{ticket_id} erfolgreich erstellt! 🎉")
                st.rerun()  # Refresh UI after creation
            else:
                st.error("Ticket konnte nicht erstellt werden. Bitte versuche es erneut.")

def list_tickets_page(db):
    """Renders ticket list with role-based filters and actions"""
    st.title("Ticket-Übersicht 📊")
    st.subheader("Aktuelle Tickets")

    # Role-based status filter defaults
    if st.session_state.role == "Support":
        default_statuses = ["Neu", "In Bearbeitung"]
    else:
        default_statuses = ["Neu", "In Bearbeitung", "Erledigt"]

    # Search/filters
    search = st.text_input("Suche nach Titel/Beschreibung", key="search")
    priorities = st.multiselect("Filter Priorität", ["Niedrig", "Mittel", "Hoch"], default=["Niedrig", "Mittel", "Hoch"], key="priority_filter")
    statuses = st.multiselect("Filter Status", ["Neu", "In Bearbeitung", "Erledigt"], default=default_statuses, key="status_filter")

    # Additional filters based on role
    filters = {}
    if st.session_state.role == "Anwender":
        filters["created_by"] = st.session_state.username
    elif st.session_state.role == "Support":
        # Support sees tickets assigned to them (if implemented) or all unassigned
        # For simplicity: Show all tickets unless filtered
        pass

    tickets = db.get_tickets(search, priorities, statuses, **filters)

    if not tickets:
        st.info("Keine Tickets gefunden. Erstelle eines via 'Neues Ticket'! 🎯")
        return

    st.subheader(f"{len(tickets)} Tickets angezeigt:")

    for ticket in tickets:
        col1, col2, col3, col4 = st.columns([1, 4, 2, 1])

        with col1:
            st.markdown(f"<div class='ticket-id'>#{ticket['id']}</div>", unsafe_allow_html=True)

        with col2:
            # Ticket title with emoji
            st.markdown(f"**{ticket['title']}** 🎫")
            
            # Description
            desc = ticket['description'] if ticket['description'] else "(Keine Details)"
            st.caption(desc)
            
            # Priority badge
            prio_color = {
                "Niedrig": "#2ECC71", 
                "Mittel": "#F1C40F", 
                "Hoch": "#E74C3C"
            }[ticket['priority']]
            st.markdown(f"<span style='background-color: {prio_color}; color: white; class='priority-badge'>"
                        f"{ticket['priority']}</span>", unsafe_allow_html=True)
            
            # Category
            st.write(f"Kategorie: {ticket['category']}")

            # Created by info
            st.write(f"Geschaffen von: {ticket['created_by']} ({ticket['created_at']})")

            # Last updated info
            last_update = ticket['last_updated_by'] or "Kein Bearbeiter"
            st.write(f"Zuletzt bearbeitet von: {last_update} ({ticket['updated_at']})")

            # Feedback display
            if ticket['feedback']:
                st.markdown(f"<div class='feedback-section'>"
                            f"Rückmeldung von {ticket['created_by']}: {ticket['feedback']}</div>",
                            unsafe_allow_html=True)

        with col3:
            current_status = ticket['status']
            status_options = []

            # Define allowed status transitions based on role
            if st.session_state.role == "Administrator":
                status_options = ["Neu", "In Bearbeitung", "Erledigt"]
            elif st.session_state.role == "Support":
                if current_status == "Neu":
                    status_options = ["In Bearbeitung"]
                elif current_status == "In Bearbeitung":
                    status_options = ["Erledigt"]
                else:
                    status_options = [current_status]  # No changes allowed for "Erledigt"
            else:  # Anwender
                status_options = [current_status]  # Anwender can't change status

            # Show status selector only if allowed
            if status_options:
                try:
                    current_idx = status_options.index(current_status)
                except ValueError:
                    current_idx = 0  # Fallback for admin
                
                new_status = st.selectbox(
                    "Status", 
                    status_options, 
                    index=current_idx, 
                    key=f"status-{ticket['id']}", 
                    label_visibility="hidden"
                )

                if new_status != current_status:
                    success = db.update_status(ticket['id'], new_status, st.session_state.username)
                    if success:
                        st.success(f"Status von #{ticket['id']} geändert zu '{new_status}'!")
            else:
                st.write(f"Status: {current_status}")

        with col4:
            # Delete button (only for owner or admin)
            if db.delete_ticket(ticket['id'], st.session_state.username):
                delete_btn = st.button("Löschen", key=f"delete-{ticket['id']}")
                if delete_btn:
                    if db.delete_ticket(ticket['id'], st.session_state.username):
                        st.success(f"TICKET #{ticket['id']} gelöscht! 🗑️")
                        st.rerun()  # Refresh UI after deletion
            else:
                # Hide delete button if no permission
                pass

            # Feedback button (only for Anwender when ticket is closed)
            if ticket['status'] == "Erledigt" and ticket['created_by'] == st.session_state.username and st.session_state.role == "Anwender":
                feedback_btn = st.button("Rückmeldung", key=f"feedback-{ticket['id']}")
                if feedback_btn:
                    # Show feedback input
                    feedback = st.text_area("Deine Rückmeldung", value=ticket['feedback'], key=f"feedback-area-{ticket['id']}", 
                                            label_visibility="hidden")
                    if st.button("Speichern", key=f"save-feedback-{ticket['id']}"):
                        if db.update_feedback(ticket['id'], feedback, st.session_state.username):
                            st.success("Rückmeldung gespeichert! ✅")
                            st.rerun()  # Refresh UI after feedback save

def user_management_page(db):
    """Renders admin user management interface"""
    if st.session_state.role != "Administrator":
        st.error("Zugriff verweigert! Diese Seite ist nur für Administratoren.")
        return

    st.title("Benutzer Verwaltung 🔐")
    st.subheader("Neue Benutzer hinzufügen")

    with st.form("add_user", clear_on_submit=True):
        new_user = st.text_input("Benutzername", key="new_user")
        new_pw = st.text_input("Passwort", type="password", key="new_pw")
        new_role = st.selectbox("Rolle", ["Anwender", "Support", "Administrator"], key="new_role")
        add_btn = st.form_submit_button("Benutzer anlegen")

        if add_btn:
            if not new_user.strip() or not new_pw.strip():
                st.error("Benutzername und Passwort sind erforderlich!")
                return
            if db.add_user(new_user, new_pw, new_role):
                st.success(f"Benutzer {new_user} mit Rolle {new_role} angelegt! 🎉")
                st.rerun()  # Refresh UI after user creation
            else:
                st.error("Benutzer konnte nicht angelegt werden. Doppelte Benutzername?")

    st.subheader("Bestehende Benutzer")
    users = db.get_users()
    if users:
        st.write("Aktive Benutzer:")
        for user in users:
            username = user['username']
            role = user['role']
            col_user, col_role, col_delete = st.columns([2, 2, 1])
            with col_user:
                st.write(f"{username}")
            with col_role:
                st.write(f"({role})")
            with col_delete:
                if st.button(f"Löschen", key=f"del_user-{username}"):
                    if db.delete_user(username):
                        st.success(f"Benutzer {username} gelöscht! 🗑️")
                        st.rerun()  # Refresh UI after user deletion
    else:
        st.info("Keine Benutzer gefunden (außer Standard-Admin).")

def main():
    # Session state initialization
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'role' not in st.session_state:
        st.session_state.role = None

    st.set_page_config(
        page_title="Ultra-Krasse Ticket-System",
        page_icon="🎫",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    db = TicketDatabase()

    # Login section
    if not st.session_state.username:
        st.title("Einloggen 🚪")
        username = st.text_input("Benutzername", key="login_user")
        password = st.text_input("Passwort", type="password", key="login_pw")
        login_btn = st.button("Einloggen")

        if login_btn:
            role = db.check_user(username, password)
            if role:
                st.session_state.username = username
                st.session_state.role = role
                st.success("Erfolgreich angemeldet! 🎉")
                st.rerun()  # Refresh to load user-specific UI
            else:
                st.error("Falscher Benutzername oder Passwort! ❌")
        return  # Exit if not logged in

    # Authenticated user interface
    st.sidebar.title("Menü 🚀")
    st.sidebar.write(f"Angemeldet als: {st.session_state.username} ({st.session_state.role})")
    
    # Role-based page options
    page_options = ["Neues Ticket", "Ticket-Liste"]
    if st.session_state.role == "Administrator":
        page_options.append("Benutzer Verwaltung")
    
    page = st.sidebar.radio("Wähle eine Aktion", page_options, key="page", index=1)

    # Render selected page
    if page == "Neues Ticket":
        create_ticket_page(db)
    elif page == "Ticket-Liste":
        list_tickets_page(db)
    elif page == "Benutzer Verwaltung":
        user_management_page(db)

if __name__ == "__main__":
    main()