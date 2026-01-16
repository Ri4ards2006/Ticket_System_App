import datetime
import streamlit as st
import hashlib
import sqlite3
import os  # Für Verzeichnis-Management

# Dark Mode Styling
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
    .ticket-id { font-weight: bold; color: #ffd700; }  /* Gelber Ticket-ID */
    .feedback-section { 
        margin-top: 10px; 
        padding: 8px; 
        background-color: #333; 
        border-radius: 4px;
    }
    </style>
""", unsafe_allow_html=True)

class TicketDatabase:
    def __init__(self, db_path="data/tickets.db"):  # Standardpfad: data/tickets.db
        self.db_path = db_path
        # Erstelle Unterordner 'data', falls nicht vorhanden
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON")  # Fremdschlüssel Enforcement
        self._initialize_tables()
    
    def close_connection(self):
        """Explizit die Datenbankverbindung schließen"""
        try:
            self.conn.close()
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Verbindung schließen): {e}")

    def _initialize_tables(self):
        # Benutzer-Tabelle
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('Anwender', 'Support', 'Administrator'))
            )
        ''')
        # Ticket-Tabelle (mit 'support_feedback'-Spalte)
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
                feedback TEXT,  -- Benutzer-Rückmeldung (bei Erledigung)
                support_feedback TEXT,  -- Support/Admin-Rückmeldung (bei Statusänderung)
                assigned_to TEXT,
                FOREIGN KEY (created_by) REFERENCES users(username),
                FOREIGN KEY (last_updated_by) REFERENCES users(username),
                FOREIGN KEY (assigned_to) REFERENCES users(username)
            )
        ''')
        # Prüfe, ob 'support_feedback'-Spalte existiert (falls ältere Datenbank verwendet wird)
        self.cursor.execute("PRAGMA table_info(tickets)")
        columns = [col[1] for col in self.cursor.fetchall()]
        if 'support_feedback' not in columns:
            try:
                self.cursor.execute('''
                    ALTER TABLE tickets ADD COLUMN support_feedback TEXT DEFAULT NULL
                ''')
                st.success("Spalte 'support_feedback' in Tabelle 'tickets' hinzugefügt.")
            except sqlite3.Error as e:
                st.error(f"Fehler beim Hinzufügen von 'support_feedback': {e}")
                self.close_connection()
                st.stop()  # App beenden, da Ticket-Operationen nicht möglich sind
        
        # Standard-Admin (falls nicht existent)
        self.cursor.execute("SELECT username FROM users WHERE username='admin'")
        if not self.cursor.fetchone():
            self.add_user("admin", "admin123", "Administrator")  # Achte auf Sicherheit!
        
        self.conn.commit()
    
    def add_user(self, username, password, role):
        """Benutzer mit gehashtem Passwort hinzufügen"""
        try:
            if not username.strip() or not password.strip():
                st.error("Benutzername/Passwort darf nicht leer sein!")
                return False
            password_hash = hashlib.sha256(password.encode()).hexdigest()
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
        """Benutzeranmeldecheck (gehashtes Passwort)"""
        try:
            if not username.strip() or not password.strip():
                return None
            password_hash = hashlib.sha256(password.encode()).hexdigest()
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
        """Neues Ticket hinzufügen (Status 'Neu', support_feedback NULL)"""
        try:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute('''
                INSERT INTO tickets (
                    title, description, priority, category, status, 
                    created_at, updated_at, created_by, support_feedback
                ) VALUES (?, ?, ?, ?, 'Neu', ?, ?, ?, ?)
            ''', (title, description, priority, category, current_time, current_time, created_by, None))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Ticket erstellen): {e}")
            return None
    
    def get_tickets(self, search_query=None, priorities=None, statuses=None, created_by=None, assigned_to=None):
        """Tickets laden mit Filtern (Suche, Priorität, Status, Ersteller, Assigned-To)"""
        try:
            query = "SELECT * FROM tickets"
            params = []
            conditions = []
            
            # Suche (Titel/Beschreibung)
            if search_query:
                search = search_query.strip().lower()
                conditions.append("(LOWER(title) LIKE ? OR LOWER(description) LIKE ?)")
                params.extend([f"%{search}%", f"%{search}%"])
            
            # Prioritätsfilter
            if priorities and priorities:
                placeholders = ", ".join(["?"] * len(priorities))
                conditions.append(f"priority IN ({placeholders})")
                params.extend(priorities)
            
            # Statusfilter
            if statuses and statuses:
                placeholders = ", ".join(["?"] * len(statuses))
                conditions.append(f"status IN ({placeholders})")
                params.extend(statuses)
            
            # Erstellerfilter (Anwender)
            if created_by:
                conditions.append("created_by = ?")
                params.append(created_by)
            
            # Assigned-To-Filter (Admin/Support)
            if assigned_to:
                conditions.append("assigned_to = ?")
                params.append(assigned_to)
            
            # Bedingungen anhängen
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            # Sortierung (neueste zuerst)
            query += " ORDER BY updated_at DESC"
            
            self.cursor.execute(query, params)
            columns = [desc[0] for desc in self.cursor.description]
            return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Tickets abrufen): {e}")
            return []
    
    def update_status(self, ticket_id, new_status, support_feedback, updated_by):
        """Status und Support-Feedback aktualisieren (rollenbasiert)"""
        try:
            if not self._has_permission(ticket_id, updated_by):
                st.error("Zugriff verweigert! Keine Berechtigung zum Ändern des Status.")
                return False
            
            updated_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute('''
                UPDATE tickets 
                SET status=?, updated_at=?, last_updated_by=?, support_feedback=? 
                WHERE id=?
            ''', (new_status, updated_at, updated_by, support_feedback, ticket_id))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Status aktualisieren): {e}")
            return False
    
    def update_feedback(self, ticket_id, feedback, updated_by):
        """Benutzer-Rückmeldung (Feedback) aktualisieren (nur bei Erledigt)"""
        try:
            ticket = self.get_ticket_by_id(ticket_id)
            if not ticket or ticket['created_by'] != updated_by or ticket['status'] != 'Erledigt':
                st.error("Zugriff verweigert! Keine Berechtigung zur Rückmeldung.")
                return False
            
            updated_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
        """Ticket löschen (nur Ersteller oder Admin)"""
        try:
            if not self._can_delete_ticket(ticket_id, deleted_by):
                st.error("Zugriff verweigert! Du darfst dieses Ticket nicht löschen.")
                return False
            
            self.cursor.execute('DELETE FROM tickets WHERE id=?', (ticket_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Ticket löschen): {e}")
            return False
    
    def get_users(self):
        """Alle Benutzer laden (Name + Rolle)"""
        try:
            self.cursor.execute("SELECT username, role FROM users")
            columns = [desc[0] for desc in self.cursor.description]
            return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Benutzer abrufen): {e}")
            return []
    
    def delete_user(self, username):
        """Benutzer löschen (nur Admin, bei fehlendem Ticket-Zusammenhang)"""
        try:
            # Benutzer existieren?
            self.cursor.execute("SELECT username FROM users WHERE username=?", (username,))
            if not self.cursor.fetchone():
                st.error("Benutzer existiert nicht!")
                return False
            
            # Benutzer mit Tickets verbunden?
            self.cursor.execute("SELECT COUNT(*) FROM tickets WHERE created_by=? OR last_updated_by=? OR assigned_to=?", 
                               (username, username, username))
            ticket_count = self.cursor.fetchone()[0]
            if ticket_count > 0:
                st.error("Benutzer kann nicht gelöscht werden! Er ist mit Tickets verbunden.")
                return False
            
            self.cursor.execute("DELETE FROM users WHERE username=?", (username,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Benutzer löschen): {e}")
            return False
    
    def _can_delete_ticket(self, ticket_id, username):
        """Prüfe, ob Benutzer Ticket löschen darf (Ersteller oder Admin)"""
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
        """Prüfe, ob Benutzer Status ändern darf (Admin oder Support bei nicht 'Erledigt')"""
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
        """Rolle eines Benutzers holen (oder None)"""
        try:
            self.cursor.execute("SELECT role FROM users WHERE username=?", (username,))
            role = self.cursor.fetchone()
            return role[0] if role else None
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Rolle abrufen): {e}")
            return None
    
    def get_ticket_by_id(self, ticket_id):
        """Ticket via ID holen (als Dictionary oder None)"""
        try:
            self.cursor.execute("SELECT * FROM tickets WHERE id=?", (ticket_id,))
            columns = [desc[0] for desc in self.cursor.description]
            ticket_data = self.cursor.fetchone()
            return dict(zip(columns, ticket_data)) if ticket_data else None
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Ticket abrufen): {e}")
            return None

def create_ticket_page(db):
    """Ticket erstellen (nur Anwender)"""
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
    """Ticket-Übersicht (mit Feedback-Anzeige und -Eingabe)"""
    st.title("Ticket-Übersicht 📄")
    search_query = st.text_input("Suche...", key="search")
    priorities = st.multiselect("Priorität filtern", ["Niedrig", "Mittel", "Hoch"], default=["Niedrig", "Mittel", "Hoch"], key="priority")
    
    # Status-Filter (Standard: Support sieht nur 'Neu'/'In Bearbeitung'; andere sehen alle)
    default_statuses = ["Neu", "In Bearbeitung"] if st.session_state.role == "Support" else ["Neu", "In Bearbeitung", "Erledigt"]
    statuses = st.multiselect("Status filtern", ["Neu", "In Bearbeitung", "Erledigt"], default=default_statuses, key="status")
    
    # Filter nach Ersteller (Anwender)
    created_by_filter = st.session_state.username if st.session_state.role == "Anwender" else None
    tickets = db.get_tickets(search_query, priorities, statuses, created_by_filter)
    
    if not tickets:
        st.info("Keine Tickets gefunden. Erstelle eines über 'Neues Ticket'! 🎯")
        return
    
    # Jedes Ticket anzeigen (Expander)
    for ticket in tickets:
        with st.expander(f"Ticket #{ticket['id']} ({ticket['priority']})", expanded=True):
            st.subheader(ticket['title'])
            
            # Spalten für Details und Aktionen
            col_details, col_actions = st.columns([2, 1])
            
            with col_details:
                # Ticket-Daten anzeige (inkl. Support-Feedback)
                st.write("**Beschreibung:**", ticket['description'] or "Keine Beschreibung")
                st.write("**Kategorie:**", ticket['category'])
                st.write("**Status:**", ticket['status'])
                # Support-Feedback anzeigen (falls vorhanden)
                support_feedback = ticket.get('support_feedback', "Keine Rückmeldung")
                st.write("**Support-Rückmeldung:**", support_feedback)
                st.write("**Erstellt am:**", ticket['created_at'])
                st.write("**Zuletzt aktualisiert:**", ticket['updated_at'] or "Nie aktualisiert")
            
            with col_actions:
                # Status ändern (falls berechtigt)
                if db._has_permission(ticket['id'], st.session_state.username):
                    current_status = ticket['status']
                    # Verfügbarer Status basierend auf Rolle
                    status_options = {
                        "Administrator": ["Neu", "In Bearbeitung", "Erledigt"],
                        "Support": ["In Bearbeitung", "Erledigt"] if current_status != "Erledigt" else [current_status],
                        "Anwender": [current_status]
                    }.get(st.session_state.role, [current_status])
                    
                    #Fallback, falls Status nicht in Optionen enthalten
                    if current_status not in status_options:
                        status_options.insert(0, current_status)
                    
                    # Formular für Status und Feedback
                    with st.form(f"status-update-{ticket['id']}", clear_on_submit=True):
                        new_status = st.selectbox(
                            "Status", 
                            status_options, 
                            index=status_options.index(current_status), 
                            key=f"status-select-{ticket['id']}", 
                            label_visibility="hidden"
                        )
                        # Support-Feedback-Eingabe (laden aktueller Wert)
                        current_feedback = ticket.get('support_feedback', "")
                        support_feedback = st.text_area(
                            "Support-Rückmeldung",
                            value=current_feedback,
                            key=f"support-feedback-{ticket['id']}",
                            height=70,
                            label_visibility="visible"
                        )
                        submit_btn = st.form_submit_button("Status aktualisieren")
                        
                        if submit_btn:
                            # Nur aktualisieren, wenn Status geändert wurde
                            if new_status != current_status:
                                success = db.update_status(ticket['id'], new_status, support_feedback, st.session_state.username)
                                if success:
                                    st.success(f"Status #{ticket['id']} auf '{new_status}' aktualisiert! ✅")
                
                # Ticket löschen (falls berechtigt)
                if db._can_delete_ticket(ticket['id'], st.session_state.username):
                    delete_btn = st.button("Löschen", key=f"delete-ticket-{ticket['id']}", use_container_width=True)
                    if delete_btn:
                        success = db.delete_ticket(ticket['id'], st.session_state.username)
                        if success:
                            st.success(f"TICKET #{ticket['id']} gelöscht! 🗑️")
                            st.rerun()
            
            # Benutzer-Feedback (nur Ersteller bei 'Erledigt')
            if ticket['status'] == "Erledigt" and ticket['created_by'] == st.session_state.username:
                feedback = st.text_area(
                    "Meine Rückmeldung", 
                    value=ticket.get('feedback', ""), 
                    key=f"feedback-area-{ticket['id']}", 
                    height=70,
                    label_visibility="hidden"
                )
                if st.button("Rückmeldung speichern", key=f"feedback-save-{ticket['id']}"):
                    if db.update_feedback(ticket['id'], feedback, st.session_state.username):
                        st.success("Rückmeldung gespeichert! ✅")
                        st.rerun()

def user_management_page(db):
    """Benutzer-Verwaltung (nur Admin)"""
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

def main():
    # Session State initialisieren
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'role' not in st.session_state:
        st.session_state.role = None
    
    # Streamlit Seiteneinstellungen
    st.set_page_config(
        page_title="Ticket-System",
        page_icon="🎫",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Datenbank-Objekt initialisieren
    db = TicketDatabase()
    
    # Login-Bereich (falls nicht angemeldet)
    if not st.session_state.username:
        st.title("Anmeldung 🚪")
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
        # Verbindung schließen, falls nicht angemeldet
        db.close_connection()
        return
    
    # Sidebar-Menü (angemeldet)
    st.sidebar.title("Menü 📁")
    st.sidebar.write(f"Angemeldet als: {st.session_state.username} ({st.session_state.role})")
    page_options = ["Ticket-Übersicht", "Neues Ticket"]
    if st.session_state.role == "Administrator":
        page_options.append("Benutzer Verwaltung")
    page = st.sidebar.radio("Wähle eine Seite", page_options, key="page", index=0)
    
    # Seite rendern
    if page == "Ticket-Übersicht":
        list_tickets_page(db)
    elif page == "Neues Ticket":
        create_ticket_page(db)
    elif page == "Benutzer Verwaltung":
        user_management_page(db)
    
    # Verbindung am Ende von main() schließen
    db.close_connection()

if __name__ == "__main__":
    main()