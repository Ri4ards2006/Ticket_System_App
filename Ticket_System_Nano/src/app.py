import datetime
import streamlit as st
import hashlib
import sqlite3
import os

# Dark Mode Styling mit UI-Optimierungen
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
        border: 1px solid #444;
    }
    .stTextArea textarea {
        background-color: #333;
        color: white;
        border-radius: 4px;
        padding: 8px;
        border: 1px solid #444;
    }
    .stSelectbox select {
        background-color: #333;
        color: white;
        border-radius: 4px;
        padding: 4px;
        border: 1px solid #444;
    }
    .stButton>button {
        background-color: #444;
        color: white;
        border-radius: 4px;
        padding: 6px 12px;
        border: 1px solid #666;
        transition: background-color 0.3s, border-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #666;
        border-color: #007bff;
    }
    .priority-badge {
        padding: 4px 8px;
        border-radius: 3px;
        font-weight: bold;
        display: inline-block;
    }
    .status-badge {
        padding: 4px 8px;
        border-radius: 3px;
        font-weight: bold;
        display: inline-block;
    }
    .status-badge.Neu { background-color: #90ee90; color: black; }
    .status-badge.In-Bearbeitung { background-color: #ffd700; color: black; }
    .status-badge.Erledigt { background-color: #ff4500; color: white; }
    .priority-badge.Niedrig { background-color: #90ee90; color: black; }
    .priority-badge.Mittel { background-color: #ffd700; color: black; }
    .priority-badge.Hoch { background-color: #ff4500; color: white; }
    .ticket-id { font-weight: bold; color: #ffd700; } 
    .feedback-section { 
        margin-top: 10px; 
        padding: 8px; 
        background-color: #333; 
        border-radius: 4px;
    }
    /* Login-Container */
    .login-container {
        max-width: 450px;
        margin: 8rem auto;
        padding: 2.5rem;
        background-color: #222;
        border-radius: 15px;
        box-shadow: 0 6px 15px rgba(0,0,0,0.3);
        border: 1px solid #444;
    }
    .company-header {
        color: #007bff;
        text-align: center;
        margin-bottom: 1.5rem;
        font-size: 2rem;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }
    .company-header span {
        font-size: 2.5rem;
    }
    .login-title {
        text-align: center;
        margin-bottom: 2rem;
        color: white;
    }
    /* Input-Felder Fokus */
    .stTextInput input:focus, 
    .stTextArea textarea:focus, 
    .stSelectbox select:focus {
        outline: 2px solid #007bff !important;
        border-color: #007bff !important;
        background-color: #444;
    }
    /* Kanban Board */
    .kanban-board {
        display: flex;
        gap: 2rem;
        padding: 2rem 0;
    }
    .kanban-column {
        flex: 1;
        background-color: #1A1A1A;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        min-height: 80vh;
    }
    .kanban-column-header {
        color: #007bff;
        font-weight: bold;
        margin-bottom: 1rem;
        text-align: center;
        border-bottom: 3px solid #007bff;
        padding-bottom: 0.5rem;
        font-size: 1.2rem;
    }
    /* Expander (Kanban Card) */
    .stExpander {
        background-color: #222;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border: 1px solid #444;
        transition: background-color 0.3s, border-color 0.3s;
        cursor: pointer;
    }
    .stExpander:hover {
        background-color: #333;
        border-color: #007bff;
    }
    .stExpanderLabel {
        color: white;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .stExpanderContent {
        background-color: inherit;
    }
    </style>
""", unsafe_allow_html=True)

def get_sentiment(text):
    positive_words = ['glücklich', 'super', 'gut', 'freut', 'freude', 'erfreut', 'positiv']
    negative_words = ['böse', 'schlecht', 'problem', 'fehler', 'frust', 'negativ', 'möglicherweise']
    text_lower = text.lower()
    if any(word in text_lower for word in positive_words):
        return '😊'
    elif any(word in text_lower for word in negative_words):
        return '😡'
    else:
        return '😐'

class TicketDatabase:
    def __init__(self, db_path="data/tickets.db"):
        self.db_path = db_path
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON")
        self._initialize_tables()

    def close_connection(self):
        try:
            self.conn.close()
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Verbindung schließen): {e}")

    def get_open_ticket_count(self):
        try:
            self.cursor.execute("SELECT COUNT(*) FROM tickets WHERE status IN ('Neu', 'In Bearbeitung')")
            return self.cursor.fetchone()[0]
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Offene Tickets zählen): {e}")
            return 0

    def get_average_processing_time(self):
        try:
            self.cursor.execute('''
                SELECT (strftime('%s', updated_at) - strftime('%s', created_at)) AS duration 
                FROM tickets 
                WHERE status = 'Erledigt' AND updated_at IS NOT NULL AND created_at IS NOT NULL
            ''')
            durations = self.cursor.fetchall()
            if not durations:
                return "Keine Daten"
            total_seconds = sum(duration[0] for duration in durations)
            avg_seconds = total_seconds / len(durations)
            avg_hours = int(avg_seconds // 3600)
            avg_minutes = int((avg_seconds % 3600) // 60)
            avg_seconds_remaining = int(avg_seconds % 60)
            return f"{avg_hours}h {avg_minutes}m {avg_seconds_remaining}s"
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Durchschnittszeit berechnen): {e}")
            return "Fehler"

    def _initialize_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('Anwender', 'Support', 'Administrator'))
            )
        ''')
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
                support_feedback TEXT,
                internal_notes TEXT DEFAULT NULL,
                sentiment TEXT DEFAULT NULL,
                assigned_to TEXT,
                FOREIGN KEY (created_by) REFERENCES users(username),
                FOREIGN KEY (last_updated_by) REFERENCES users(username),
                FOREIGN KEY (assigned_to) REFERENCES users(username)
            )
        ''')
        self.cursor.execute("PRAGMA table_info(tickets)")
        columns = [col[1] for col in self.cursor.fetchall()]
        
        if 'support_feedback' not in columns:
            self.cursor.execute('ALTER TABLE tickets ADD COLUMN support_feedback TEXT DEFAULT NULL')
            st.success("Spalte 'support_feedback' hinzugefügt.")
        
        if 'internal_notes' not in columns:
            self.cursor.execute('ALTER TABLE tickets ADD COLUMN internal_notes TEXT DEFAULT NULL')
            st.success("Spalte 'internal_notes' hinzugefügt.")
        
        if 'sentiment' not in columns:
            self.cursor.execute('ALTER TABLE tickets ADD COLUMN sentiment TEXT DEFAULT NULL')
            st.success("Spalte 'sentiment' hinzugefügt.")
        
        self.cursor.execute("SELECT username FROM users WHERE username='admin'")
        if not self.cursor.fetchone():
            self.add_user("admin", "admin123", "Administrator")
        
        self.conn.commit()

    def add_user(self, username, password, role):
        if not username.strip() or not password.strip():
            st.error("Benutzername/Passwort darf nicht leer sein!")
            return False
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        try:
            self.cursor.execute('''
                INSERT INTO users (username, password_hash, role)
                VALUES (?, ?, ?)
            ''', (username, password_hash, role))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            st.error("Benutzer existiert bereits!")
            return False
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Benutzer hinzufügen): {e}")
            return False

    def check_user(self, username, password):
        if not username.strip() or not password.strip():
            return None
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        try:
            self.cursor.execute('''
                SELECT role FROM users 
                WHERE username=? AND password_hash=?
            ''', (username, password_hash))
            role = self.cursor.fetchone()
            return role[0] if role else None
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Benutzer prüfen): {e}")
            return None

    def add_ticket(self, title, description, priority, category, created_by):
        if not title.strip():
            st.error("Titel darf nicht leer sein!")
            return None
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        text = f"{title} {description}" if description else title
        sentiment = get_sentiment(text)
        try:
            self.cursor.execute('''
                INSERT INTO tickets (
                    title, description, priority, category, status, 
                    created_at, updated_at, created_by, support_feedback, internal_notes, sentiment
                ) VALUES (?, ?, ?, ?, 'Neu', ?, ?, ?, ?, NULL, ?)
            ''', (title, description, priority, category, current_time, current_time, created_by, None, sentiment))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Ticket erstellen): {e}")
            return None

    def get_tickets(self, search_query=None, priorities=None, statuses=None, created_by=None, assigned_to=None):
        try:
            query = "SELECT * FROM tickets"
            params = []
            conditions = []
            
            if search_query:
                search = search_query.strip().lower()
                conditions.append("(LOWER(title) LIKE ? OR LOWER(description) LIKE ?)")
                params.extend([f"%{search}%", f"%{search}%"])
            
            if priorities and priorities:
                placeholders = ", ".join(["?"] * len(priorities))
                conditions.append(f"priority IN ({placeholders})")
                params.extend(priorities)
            
            if statuses and statuses:
                placeholders = ", ".join(["?"] * len(statuses))
                conditions.append(f"status IN ({placeholders})")
                params.extend(statuses)
            
            if created_by:
                conditions.append("created_by = ?")
                params.append(created_by)
            
            if assigned_to:
                conditions.append("assigned_to = ?")
                params.append(assigned_to)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY updated_at DESC"
            
            self.cursor.execute(query, params)
            columns = [desc[0] for desc in self.cursor.description]
            return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Tickets abrufen): {e}")
            return []

    def update_status(self, ticket_id, new_status, support_feedback, internal_notes, updated_by):
        if not self._has_permission(ticket_id, updated_by):
            st.error("Zugriff verweigert! Keine Berechtigung zum Ändern des Status.")
            return False
        
        updated_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.cursor.execute('''
                UPDATE tickets 
                SET status=?, updated_at=?, last_updated_by=?, support_feedback=?, internal_notes=? 
                WHERE id=?
            ''', (new_status, updated_at, updated_by, support_feedback, internal_notes, ticket_id))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Status aktualisieren): {e}")
            return False

    def update_feedback(self, ticket_id, feedback, updated_by):
        ticket = self.get_ticket_by_id(ticket_id)
        if not ticket or ticket['created_by'] != updated_by or ticket['status'] != 'Erledigt':
            st.error("Zugriff verweigert! Keine Berechtigung zur Rückmeldung.")
            return False
        
        updated_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.cursor.execute('''
                UPDATE tickets 
                SET feedback=?, updated_at=?, last_updated_by=? 
                WHERE id=?
            ''', (feedback, updated_at, updated_by, ticket_id))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Feedback aktualisieren): {e}")
            return False

    def delete_ticket(self, ticket_id, deleted_by):
        if not self._can_delete_ticket(ticket_id, deleted_by):
            st.error("Zugriff verweigert! Du darfst dieses Ticket nicht löschen.")
            return False
        
        try:
            self.cursor.execute('DELETE FROM tickets WHERE id=?', (ticket_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Ticket löschen): {e}")
            return False

    def get_users(self):
        try:
            self.cursor.execute("SELECT username, role FROM users")
            columns = [desc[0] for desc in self.cursor.description]
            return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Benutzer abrufen): {e}")
            return []

    def delete_user(self, username):
        self.cursor.execute("SELECT username FROM users WHERE username=?", (username,))
        if not self.cursor.fetchone():
            st.error("Benutzer existiert nicht!")
            return False
        
        self.cursor.execute("SELECT COUNT(*) FROM tickets WHERE created_by=? OR last_updated_by=? OR assigned_to=?", 
                           (username, username, username))
        ticket_count = self.cursor.fetchone()[0]
        if ticket_count > 0:
            st.error("Benutzer kann nicht gelöscht werden! Er ist mit Tickets verbunden.")
            return False
        
        try:
            self.cursor.execute("DELETE FROM users WHERE username=?", (username,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Benutzer löschen): {e}")
            return False

    def _can_delete_ticket(self, ticket_id, username):
        try:
            self.cursor.execute('''
                SELECT 1 FROM tickets 
                WHERE id=? 
                AND (created_by=? OR (SELECT role FROM users WHERE username=?)='Administrator')
            ''', (ticket_id, username, username))
            return self.cursor.fetchone() is not None
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Zugriff prüfen): {e}")
            return False

    def _has_permission(self, ticket_id, username):
        user_role = self._get_user_role(username)
        if not user_role:
            return False
        
        ticket = self.get_ticket_by_id(ticket_id)
        if not ticket:
            return False
        
        if user_role == "Administrator":
            return True
        if user_role == "Support" and ticket['status'] != 'Erledigt':
            return True
        return False

    def _get_user_role(self, username):
        try:
            self.cursor.execute("SELECT role FROM users WHERE username=?", (username,))
            role = self.cursor.fetchone()
            return role[0] if role else None
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Rolle abrufen): {e}")
            return None

    def get_ticket_by_id(self, ticket_id):
        try:
            self.cursor.execute("SELECT * FROM tickets WHERE id=?", (ticket_id,))
            columns = [desc[0] for desc in self.cursor.description]
            ticket_data = self.cursor.fetchone()
            return dict(zip(columns, ticket_data)) if ticket_data else None
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Ticket abrufen): {e}")
            return None

def create_ticket_page(db):
    if st.session_state.role != "Anwender":
        st.error("Nur Anwender dürfen Tickets erstellen!")
        return
    
    st.title("Neues Ticket 🎫")
    with st.form("ticket_creation", clear_on_submit=True):
        title = st.text_input("Titel (erforderlich)", max_chars=100, key="title")
        description = st.text_area("Beschreibung", placeholder="Details...", key="desc")
        priority = st.selectbox("Priorität", ["Niedrig", "Mittel", "Hoch"], index=1, key="priority")
        category = st.selectbox("Kategorie", ["Bug", "Feature", "Support"], index=0, key="category")
        submit = st.form_submit_button("Erstellen")
        
        if submit:
            if not title.strip():
                st.error("Titel darf nicht leer sein!")
                return
            ticket_id = db.add_ticket(title, description, priority, category, st.session_state.username)
            if ticket_id:
                st.success(f"TICKET #{ticket_id} erstellt! 🎉")
            else:
                st.error("Ticket konnte nicht erstellt werden.")

def list_tickets_page(db):
    st.title("Ticket-Übersicht 📄")
    search_query = st.text_input("Suche...", key="search")
    priorities = st.multiselect("Priorität filtern", ["Niedrig", "Mittel", "Hoch"], default=["Niedrig", "Mittel", "Hoch"], key="priority")
    
    default_statuses = ["Neu", "In Bearbeitung"] if st.session_state.role == "Support" else ["Neu", "In Bearbeitung", "Erledigt"]
    statuses = st.multiselect("Status filtern", ["Neu", "In Bearbeitung", "Erledigt"], default=default_statuses, key="status")
    
    created_by_filter = st.session_state.username if st.session_state.role == "Anwender" else None
    tickets = db.get_tickets(search_query, priorities, statuses, created_by_filter)
    
    if not tickets:
        st.info("Keine Tickets gefunden. Erstelle eines über 'Neues Ticket'! 🎯")
        return
    
    tickets_by_status = {
        "Neu": [],
        "In Bearbeitung": [],
        "Erledigt": []
    }
    for ticket in tickets:
        tickets_by_status[ticket['status']].append(ticket)
    
    # Kanban Board Layout
    st.markdown('<div class="kanban-board">', unsafe_allow_html=True)
    col_neu, col_in_bearbeitung, col_erledigt = st.columns(3, gap="large")
    st.markdown('</div>', unsafe_allow_html=True)

    # Hilfsfunktion zum Anzeigen eines Tickets in einer Column
    def display_ticket(ticket):
        sentiment_emoji = ticket.get('sentiment', '')
        expander_label = f"Ticket #{ticket['id']} ({ticket['priority']}) {sentiment_emoji}"
        with st.expander(expander_label, expanded=False):
            # Titel mit Badge
            st.subheader(ticket['title'])
            
            # Priorität Badge
            priority_badge = f'<span class="priority-badge {ticket["priority"].lower()}">{ticket["priority"]}</span>'
            st.write("**Priorität:**", priority_badge, unsafe_allow_html=True)
            
            # Status Badge
            status_class = ticket["status"].replace(' ', '-')
            status_badge = f'<span class="status-badge {status_class}">{ticket["status"]}</span>'
            st.write("**Status:**", status_badge, unsafe_allow_html=True)
            
            st.write("**Beschreibung:**", ticket['description'] or "Keine Beschreibung")
            st.write("**Kategorie:**", ticket['category'])
            support_feedback = ticket.get('support_feedback', "Keine Rückmeldung")
            st.write("**Support-Rückmeldung:**", support_feedback)
            st.write("**Erstellt am:**", ticket['created_at'])
            updated_at = ticket['updated_at'] or "Nie aktualisiert"
            st.write("**Zuletzt aktualisiert:**", updated_at)
            
            # Status-Update-Form (nur berechtigt)
            if db._has_permission(ticket['id'], st.session_state.username):
                current_status = ticket['status']
                status_options = {
                    "Administrator": ["Neu", "In Bearbeitung", "Erledigt"],
                    "Support": ["In Bearbeitung", "Erledigt"] if current_status != "Erledigt" else [current_status],
                    "Anwender": [current_status]
                }.get(st.session_state.role, [current_status])
                if current_status not in status_options:
                    status_options.insert(0, current_status)
                
                with st.form(f"status-update-{ticket['id']}", clear_on_submit=True):
                    new_status = st.selectbox(
                        "Status", 
                        status_options, 
                        index=status_options.index(current_status), 
                        key=f"status-select-{ticket['id']}", 
                        label_visibility="hidden"
                    )
                    current_feedback = ticket.get('support_feedback', "")
                    support_feedback = st.text_area(
                        "Support-Rückmeldung",
                        value=current_feedback,
                        key=f"support-feedback-{ticket['id']}",
                        height=70,
                        label_visibility="visible"
                    )
                    current_internal_notes = ticket.get('internal_notes', "")
                    internal_notes = current_internal_notes
                    if st.session_state.role in ["Support", "Administrator"]:
                        internal_notes = st.text_area(
                            "Interne Notizen",
                            value=current_internal_notes,
                            key=f"internal-notes-{ticket['id']}",
                            height=70,
                            label_visibility="visible"
                        )
                    submit_btn = st.form_submit_button("Status aktualisieren")
                    if submit_btn:
                        success = db.update_status(
                            ticket_id=ticket['id'],
                            new_status=new_status,
                            support_feedback=support_feedback,
                            internal_notes=internal_notes,
                            updated_by=st.session_state.username
                        )
                        if success:
                            msg = f"Status #{ticket['id']} auf '{new_status}' aktualisiert! ✅" if new_status != current_status else f"TICKET #{ticket['id']} aktualisiert! ✅"
                            st.success(msg)
                        else:
                            st.error("Aktualisierung fehlgeschlagen.")

    # Tickets in Columns anzeigen
    with col_neu:
        st.markdown('<div class="kanban-column">', unsafe_allow_html=True)
        st.markdown('<h3 class="kanban-column-header">Neu</h3>', unsafe_allow_html=True)
        for ticket in tickets_by_status["Neu"]:
            display_ticket(ticket)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_in_bearbeitung:
        st.markdown('<div class="kanban-column">', unsafe_allow_html=True)
        st.markdown('<h3 class="kanban-column-header">In Bearbeitung</h3>', unsafe_allow_html=True)
        for ticket in tickets_by_status["In Bearbeitung"]:
            display_ticket(ticket)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_erledigt:
        st.markdown('<div class="kanban-column">', unsafe_allow_html=True)
        st.markdown('<h3 class="kanban-column-header">Erledigt</h3>', unsafe_allow_html=True)
        for ticket in tickets_by_status["Erledigt"]:
            display_ticket(ticket)
        st.markdown('</div>', unsafe_allow_html=True)

def user_management_page(db):
    if st.session_state.role != "Administrator":
        st.error("Zugriff verweigert! Nur Admins können Benutzer verwalten.")
        return
    
    st.title("Benutzer Verwaltung 🔐")
    
    # Neuen Benutzer anlegen
    with st.form("add_user", clear_on_submit=True):
        new_user = st.text_input("Benutzername", key="new_user")
        new_pw = st.text_input("Passwort", type="password", key="new_pw")
        new_role = st.selectbox("Rolle", ["Anwender", "Support", "Administrator"], key="new_role")
        if st.form_submit_button("Benutzer anlegen"):
            if not new_user.strip() or not new_pw.strip():
                st.error("Benutzername und Passwort müssen angegeben werden!")
            else:
                if db.add_user(new_user, new_pw, new_role):
                    st.success(f"Benutzer '{new_user}' angelegt! 🎉")
                else:
                    st.error("Benutzer konnte nicht angelegt werden (doppelter Benutzername?)")

    # Bestehende Benutzer anzeigen
    st.subheader("Aktive Benutzer")
    users = db.get_users()
    if not users:
        st.info("Keine Benutzer gefunden (außer Standard-Admin).")
        return
    
    # Benutzer-Tabelle via DataFrame
    st.dataframe(users, use_container_width=True)

    # Benutzer löschen (per Button)
    for user in users:
        col_name, col_role, col_delete = st.columns([3, 2, 1])
        with col_name:
            st.write(user['username'])
        with col_role:
            st.write(f"({user['role']})")
        with col_delete:
            if st.button(f"Löschen", key=f"del_user-{user['username']}"):
                if db.delete_user(user['username']):
                    st.success(f"Benutzer '{user['username']}' gelöscht! 🗑️")
                    st.rerun()

def admin_dashboard_page(db):
    st.title("Admin Dashboard 🌐")
    st.markdown("---")
    
    # Offene Tickets Statistik
    open_count = db.get_open_ticket_count()
    st.metric("Offene Tickets (Gesamt)", open_count)
    
    # Durchschnittliche Bearbeitungszeit
    avg_time = db.get_average_processing_time()
    st.metric("Durchschnittliche Bearbeitungszeit", avg_time)

def main():
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'role' not in st.session_state:
        st.session_state.role = None
    
    st.set_page_config(
        page_title="Schacht GmbH Ticket-System",
        page_icon="♟️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    db = TicketDatabase()
    
    if not st.session_state.username:
        # Login-Bereich
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="company-header">Schacht GmbH <span>♟️</span></div>', unsafe_allow_html=True)
        st.markdown('<h2 class="login-title">Anmeldung zum Ticket-System</h2>', unsafe_allow_html=True)
        
        username = st.text_input("Benutzername", key="login_user")
        password = st.text_input("Passwort", type="password", key="login_pw")
        
        if st.button("Einloggen"):
            role = db.check_user(username, password)
            if role:
                st.session_state.username = username
                st.session_state.role = role
                st.success("Erfolgreich angemeldet! 🎉")
                st.rerun()
            else:
                st.error("Falscher Benutzername oder Passwort! ❌")
        
        st.markdown('</div>', unsafe_allow_html=True)
        db.close_connection()
        return
    
    # Sidebar-Menü
    st.sidebar.title("Menü 📁")
    st.sidebar.write(f"Angemeldet als: {st.session_state.username} ({st.session_state.role})")
    page_options = ["Ticket-Übersicht", "Neues Ticket"]
    if st.session_state.role == "Administrator":
        page_options.extend(["Benutzer Verwaltung", "Admin Dashboard"])
    page = st.sidebar.radio("Wähle eine Seite", page_options, key="page", index=0)
    
    # Seite rendern
    if page == "Ticket-Übersicht":
        list_tickets_page(db)
    elif page == "Neues Ticket":
        create_ticket_page(db)
    elif page == "Benutzer Verwaltung":
        user_management_page(db)
    elif page == "Admin Dashboard":
        admin_dashboard_page(db)
    
    db.close_connection()

if __name__ == "__main__":
    main()