import sqlite3
import datetime
import streamlit as st

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
    </style>
""", unsafe_allow_html=True)

class TicketDatabase:
    """Manages SQLite database interactions for ticket system"""
    def __init__(self, db_path="tickets.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._initialize_table()

    def _initialize_table(self):
        """Create tickets table if it doesn't exist"""
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    priority TEXT NOT NULL CHECK(priority IN ('Niedrig', 'Mittel', 'Hoch')),
                    category TEXT NOT NULL CHECK(category IN ('Bug', 'Feature', 'Support')),
                    status TEXT NOT NULL CHECK(status IN ('Offen', 'In Bearbeitung', 'Gelöst')),
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            st.error(f"Datenbank Initialisierungsfehler: {e}")

    def add_ticket(self, title, description, priority, category):
        """Add new ticket to database with current timestamps"""
        try:
            created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute('''
                INSERT INTO tickets (title, description, priority, category, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, 'Offen', ?, ?)
            ''', (title, description, priority, category, created_at, created_at))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            st.error(f"Fehler beim Hinzufügen des Tickets: {e}")
            return None

    def get_tickets(self, search_query=None, priorities=None, statuses=None):
        """Retrieve tickets with optional search and filters"""
        try:
            query_conditions = []
            params = ()

            # Base query
            base_query = "SELECT id, title, description, priority, category, status, created_at, updated_at FROM tickets"

            # Add search condition
            if search_query:
                search_query = search_query.strip().lower()
                query_conditions.append("(LOWER(title) LIKE ? OR LOWER(description) LIKE ?)")
                params += (f"%{search_query}%", f"%{search_query}%")

            # Add priority filter
            if priorities and priorities != []:
                placeholders = ", ".join(["?"] * len(priorities))
                query_conditions.append(f"priority IN ({placeholders})")
                params += tuple(priorities)

            # Add status filter
            if statuses and statuses != []:
                placeholders = ", ".join(["?"] * len(statuses))
                query_conditions.append(f"status IN ({placeholders})")
                params += tuple(statuses)

            # Combine conditions
            if query_conditions:
                full_query = f"{base_query} WHERE {' AND '.join(query_conditions)} ORDER BY updated_at DESC"
            else:
                full_query = f"{base_query} ORDER BY updated_at DESC"

            self.cursor.execute(full_query, params)
            columns = [desc[0] for desc in self.cursor.description]
            return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            st.error(f"Fehler beim Abrufen der Tickets: {e}")
            return []

    def update_status(self, ticket_id, new_status):
        """Update ticket status and update timestamp"""
        try:
            updated_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute('''
                UPDATE tickets SET status=?, updated_at=? WHERE id=?
            ''', (new_status, updated_at, ticket_id))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            st.error(f"Fehler beim Aktualisieren des Status: {e}")
            return False

    def delete_ticket(self, ticket_id):
        """Delete ticket from database"""
        try:
            self.cursor.execute('''
                DELETE FROM tickets WHERE id=?
            ''', (ticket_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            st.error(f"Fehler beim Löschen des Tickets: {e}")
            return False

def create_ticket_page(db):
    """Renders the ticket creation form page"""
    st.title("Neues Ticket erstellen 🎫")
    with st.form("ticket_creation_form", clear_on_submit=True):
        st.write("Fülle das Formular aus um ein neues Ticket anzulegen:")

        title = st.text_input("Titel (erforderlich)", max_chars=100, key="title_input")
        description = st.text_area("Beschreibung", placeholder="Details zum Ticket...", key="description_input")
        priority = st.selectbox("Priorität", ["Niedrig", "Mittel", "Hoch"], index=1, key="priority_select")
        category = st.selectbox("Kategorie", ["Bug", "Feature", "Support"], index=0, key="category_select")

        submit_button = st.form_submit_button("Ticket erstellen")

        if submit_button:
            if not title.strip():
                st.error("Bitte gib einen Titel für das Ticket ein!")
            else:
                ticket_id = db.add_ticket(title, description, priority, category)
                if ticket_id:
                    st.success(f"TICKET #{ticket_id} erfolgreich erstellt! 🎉")
                else:
                    st.error("Fehler beim erstellen des Tickets. Bitte versuche es später erneut.")

def list_tickets_page(db):
    """Renders the ticket listing and management page"""
    st.title("Ticket-Liste 📊")
    st.subheader("Übersicht aller Tickets")

    # Search and filter controls
    search_query = st.text_input("Suche nach Titel oder Beschreibung", key="search_input")
    selected_priorities = st.multiselect(
        "Filtern nach Priorität", 
        ["Niedrig", "Mittel", "Hoch"], 
        default=["Niedrig", "Mittel", "Hoch"],
        key="priority_filter"
    )
    selected_statuses = st.multiselect(
        "Filtern nach Status", 
        ["Offen", "In Bearbeitung", "Gelöst"], 
        default=["Offen", "In Bearbeitung", "Gelöst"],
        key="status_filter"
    )

    # Get filtered tickets
    tickets = db.get_tickets(search_query, selected_priorities, selected_statuses)

    if not tickets:
        st.info("Keine Tickets gefunden. Erstelle das erste Ticket über die Menüleiste! 🎖️")
        return

    # Display tickets
    st.subheader(f"Anzeige von {len(tickets)} Tickets:")
    
    for ticket in tickets:
        # Create columns for ticket display
        col_id, col_info, col_status, col_actions = st.columns([1, 4, 2, 1])

        with col_id:
            st.markdown(f"<div class='ticket-id'>#{ticket['id']}</div>", unsafe_allow_html=True)

        with col_info:
            # Ticket title with emoji
            st.markdown(f"**{ticket['title']}** 🎫")
            
            # Description (with placeholder if empty)
            desc = ticket['description'] if ticket['description'] else "(Keine Beschreibung)"
            st.caption(f"{desc}")
            
            # Category display
            st.write(f"Kategorie: {ticket['category']}")
            
            # Priority badge with color coding
            priority_color = {
                "Niedrig": "#2ECC71",  # Green
                "Mittel": "#F1C40F",   # Yellow
                "Hoch": "#E74C3C"      # Red
            }[ticket['priority']]
            st.markdown(
                f"<span style='background-color: {priority_color}; color: white; class='priority-badge'>"
                f"{ticket['priority']}</span>",
                unsafe_allow_html=True
            )
            
            # Timestamps
            st.write(f"Geschaffen: {ticket['created_at']} | Zuletzt aktualisiert: {ticket['updated_at']}")

        with col_status:
            # Status dropdown with current value
            current_status = ticket['status']
            status_options = ["Offen", "In Bearbeitung", "Gelöst"]
            try:
                current_index = status_options.index(current_status)
            except ValueError:
                current_index = 0  # Fallback to first option if invalid
            
            new_status = st.selectbox(
                "Status", 
                status_options, 
                index=current_index, 
                key=f"status-{ticket['id']}", 
                label_visibility="hidden"
            )
            
            # Update status if changed
            if new_status != current_status:
                if db.update_status(ticket['id'], new_status):
                    st.success(f"Status von #{ticket['id']} geändert zu '{new_status}'!")

        with col_actions:
            # Delete button with confirmation
            if st.button("Löschen", key=f"delete-{ticket['id']}"):
                if db.delete_ticket(ticket['id']):
                    st.success(f"TICKET #{ticket['id']} erfolgreich gelöscht! 🗑️")

def main():
    # Configure page settings
    st.set_page_config(
        page_title="Ultra-Krasse Ticket-System",
        page_icon="🎫",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize database connection
    db = TicketDatabase()

    # Sidebar navigation
    st.sidebar.title("Navigation 🚀")
    page_selection = st.sidebar.radio(
        "Wähle eine Aktion", 
        ["Neues Ticket", "Ticket-Liste"], 
        key="page_radio", 
        index=1  # Start with Ticket-Liste by default
    )

    # Render selected page
    if page_selection == "Neues Ticket":
        create_ticket_page(db)
    else:
        list_tickets_page(db)

if __name__ == "__main__":
    main() 