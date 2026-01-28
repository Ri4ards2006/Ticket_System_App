# -*- coding: utf-8 -*-
"""Ticket‑System für Schacht GmbH – mit Kanban‑Board und minimaler Streamlit‑API."""

import datetime
import hashlib
import os
import sqlite3
import streamlit as st


# -------------------------------------------------
# Seite‑Konfiguration und CSS
# -------------------------------------------------
st.set_page_config(
    page_title="Schacht GmbH Ticket‑System",
    page_icon="♟️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    body { color: white; background-color: #1E1E1E; font-family: 'Arial', sans-serif; }
    .stTextInput input { background-color: #333; color: white; border-radius: 4px; padding: 8px; border: 1px solid #444; }
    .stTextArea textarea { background-color: #333; color: white; border-radius: 4px; padding: 8px; border: 1px solid #444; }
    .stSelectbox select { background-color: #333; color: white; border-radius: 4px; padding: 4px; border: 1px solid #444; }
    .stButton>button { background-color: #444; color: white; border-radius: 4px; padding: 6px 12px; border: 1px solid #666; transition: background-color 0.3s, border-color 0.3s; }
    .stButton>button:hover { background-color: #666; border-color: #007bff; }
    .priority-badge, .status-badge { padding: 4px 8px; border-radius: 3px; font-weight: bold; display: inline-block; }
    .status-badge.Neu { background-color: #90ee90; color: black; }
    .status-badge.In-Bearbeitung { background-color: #ffd700; color: black; }
    .status-badge.Erledigt { background-color: #ff4500; color: white; }
    .priority-badge.Niedrig { background-color: #90ee90; color: black; }
    .priority-badge.Mittel { background-color: #ffd700; color: black; }
    .priority-badge.Hoch { background-color: #ff4500; color: white; }
    .ticket-id { font-weight: bold; color: #ffd700; }
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
    .company-header span { font-size: 2.5rem; }
    .login-title { text-align: center; margin-bottom: 2rem; color: white; }
    .stTextInput input:focus,
    .stTextArea textarea:focus,
    .stSelectbox select:focus {
        outline: 2px solid #007bff !important;
        border-color: #007bff !important;
        background-color: #444;
    }
    .kanban-board { display: flex; gap: 2rem; padding: 2rem 0; }
    .kanban-column {
        flex: 1;
        background-color: #1A1A1A;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        min-height: 80vh;
        max-height: 80vh;
        overflow-y: auto;
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
    .stExpanderContent { background-color: inherit; }
</style>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------
# Hilfs‑Funktionen
# -------------------------------------------------
def get_sentiment(text: str) -> str:
    """Entscheidet per einfacher Wortliste, ob ein Ticket positiv, negativ oder neutral klingt."""
    positive = ["glücklich", "super", "gut", "freut", "freude", "erfreut", "positiv"]
    negative = ["böse", "schlecht", "problem", "fehler", "frust", "negativ", "möglicherweise"]
    lowered = text.lower()
    if any(w in lowered for w in positive):
        return "😊"
    if any(w in lowered for w in negative):
        return "😡"
    return "😐"


def _status_badge_html(status: str) -> str:
    return f'<span class="status-badge {status.replace(" ", "-")}">{status}</span>'


def _priority_badge_html(priority: str) -> str:
    return f'<span class="priority-badge {priority.lower()}">{priority}</span>'


# -------------------------------------------------
# SQLite‑Wrapper‑Klasse
# -------------------------------------------------
class TicketDatabase:
    def __init__(self, db_path: str = "data/tickets.db"):
        self.db_path = db_path
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.isdir(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            self.cursor.execute("PRAGMA foreign_keys = ON")
            self._create_schema()
        except sqlite3.Error as e:
            st.error(f"Konnte Datenbank nicht öffnen: {e}")
            raise

    def close(self):
        """Datenbank sauber schließen."""
        try:
            self.conn.close()
        except Exception:
            pass

    # ---- Schema ----
    def _create_schema(self):
        """Tabellen créer und ggf. fehlende Spalten ergänzen."""
        # Users
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('Anwender', 'Support', 'Administrator'))
            )
            """
        )

        # Tickets
        self.cursor.execute(
            """
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
            """
        )
        self.conn.commit()

        # Add extra columns only if they do not yet exist
        for col in ("support_feedback", "internal_notes", "sentiment"):
            self.cursor.execute(
                "SELECT * FROM pragma_table_info('tickets') WHERE name = ?", (col,)
            )
            if not self.cursor.fetchone():
                self.cursor.execute(f"ALTER TABLE tickets ADD COLUMN {col} TEXT DEFAULT NULL")
                self.conn.commit()

        # Ensure default admin user exists
        self.cursor.execute("SELECT username FROM users WHERE username = ?", ("admin",))
        if not self.cursor.fetchone():
            self.cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                ("admin", hashlib.sha256(b"admin123").hexdigest(), "Administrator"),
            )
            self.conn.commit()

    # ---- CRUD ----
    def add_user(self, username: str, password: str, role: str) -> bool:
        if not username.strip() or not password.strip():
            st.error("Benutzername und Passwort dürfen nicht leer sein.")
            return False
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        try:
            self.cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, pwd_hash, role),
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            st.error("Benutzer existiert bereits.")
            return False
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Benutzer anlegen): {e}")
            return False

    def check_user(self, username: str, password: str) -> str | None:
        if not username.strip() or not password.strip():
            return None
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        try:
            self.cursor.execute(
                "SELECT role FROM users WHERE username = ? AND password_hash = ?",
                (username, pwd_hash),
            )
            row = self.cursor.fetchone()
            return row["role"] if row else None
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Benutzer prüfen): {e}")
            return None

    def remove_user(self, username: str) -> bool:
        """Löschen nur, wenn die Person nicht mehr in Tickets vorkommt. """
        self.cursor.execute(
            """
            SELECT COUNT(*) FROM tickets 
            WHERE created_by = ? 
               OR last_updated_by = ? 
               OR assigned_to = ?
            """,
            (username, username, username),
        )
        if self.cursor.fetchone()[0] > 0:
            st.error("Benutzer ist an einem Ticket gebunden und kann nicht gelöscht werden.")
            return False
        try:
            self.cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Benutzer löschen): {e}")
            return False

    def add_ticket(
        self,
        title: str,
        description: str,
        priority: str,
        category: str,
        created_by: str,
    ) -> int | None:
        if not title.strip():
            st.error("Titel darf nicht leer sein.")
            return None
        full_text = f"{title} {description}".strip()
        sentiment = get_sentiment(full_text)
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.cursor.execute(
                """
                INSERT INTO tickets (
                    title, description, priority, category, status,
                    created_at, updated_at, created_by,
                    support_feedback, internal_notes, sentiment
                ) VALUES (?, ?, ?, ?, 'Neu', ?, ?, ?, ?, NULL, ?)
                """,
                (
                    title,
                    description,
                    priority,
                    category,
                    now,
                    now,
                    created_by,
                    None,
                    sentiment,
                ),
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Ticket anlegen): {e}")
            return None

    # ---- Abfragen ----
    def _build_ticket_query(
        self,
        search: str | None,
        priorities: list[str] | None,
        statuses: list[str] | None,
        created_by: str | None,
        assigned_to: str | None,
    ) -> tuple[str, list]:
        base = "SELECT * FROM tickets"
        conditions = []
        params: list = []

        if search:
            term = f"%{search.strip().lower()}%"
            conditions.append("(LOWER(title) LIKE ? OR LOWER(description) LIKE ?)")
            params.extend([term, term])

        if priorities:
            placeholders = ", ".join(["?"] * len(priorities))
            conditions.append(f"priority IN ({placeholders})")
            params.extend(priorities)

        if statuses:
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
            base += " WHERE " + " AND ".join(conditions)

        base += " ORDER BY updated_at DESC"
        return base, params

    def get_tickets(
        self,
        search: str | None = None,
        priorities: list[str] | None = None,
        statuses: list[str] | None = None,
        created_by: str | None = None,
        assigned_to: str | None = None,
    ) -> list[dict]:
        query, params = self._build_ticket_query(search, priorities, statuses, created_by, assigned_to)
        try:
            self.cursor.execute(query, tuple(params))
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Ticket‑Abfrage): {e}")
            return []

    def get_ticket_by_id(self, ticket_id: int) -> dict | None:
        try:
            self.cursor.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Ticket‑Abfrage ID={ticket_id}): {e}")
            return None

    def _get_user_role(self, username: str) -> str | None:
        try:
            self.cursor.execute("SELECT role FROM users WHERE username = ?", (username,))
            row = self.cursor.fetchone()
            return row["role"] if row else None
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Rollen‑Abfrage): {e}")
            return None

    def _has_permission(self, ticket_id: int, username: str) -> bool:
        """Erlaubt Administrator alles, Support alle offenen Tickets, Anwender nur Sicht‑Berechtigung."""
        role = self._get_user_role(username)
        if not role:
            return False
        ticket = self.get_ticket_by_id(ticket_id)
        if not ticket:
            return False
        if role == "Administrator":
            return True
        if role == "Support" and ticket["status"] != "Erledigt":
            return True
        # Anwender dürfen nur einsehen (keine Änderungen)
        return False

    # ---- Update / Delete ----
    def update_status(
        self,
        ticket_id: int,
        new_status: str,
        support_feedback: str | None,
        internal_notes: str | None,
        updated_by: str,
    ) -> bool:
        if not self._has_permission(ticket_id, updated_by):
            st.error("Keine Berechtigung, den Status zu ändern.")
            return False
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.cursor.execute(
                """
                UPDATE tickets
                SET status = ?, updated_at = ?, last_updated_by = ?, support_feedback = ?, internal_notes = ?
                WHERE id = ?
                """,
                (
                    new_status,
                    now,
                    updated_by,
                    support_feedback,
                    internal_notes,
                    ticket_id,
                ),
            )
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Status‑Update): {e}")
            return False

    def delete_ticket(self, ticket_id: int, deleted_by: str) -> bool:
        if not self._has_permission(ticket_id, deleted_by):
            st.error("Keine Berechtigung, das Ticket zu löschen.")
            return False
        try:
            self.cursor.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Ticket‑Löschen): {e}")
            return False

    def get_users(self) -> list[dict]:
        try:
            self.cursor.execute("SELECT username, role FROM users")
            rows = self.cursor.fetchall()
            return [{"username": r["username"], "role": r["role"]} for r in rows]
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Nutzerliste): {e}")
            return []

    # ---- Reporting ----
    def get_open_ticket_count(self) -> int:
        try:
            self.cursor.execute(
                "SELECT COUNT(*) FROM tickets WHERE status IN ('Neu', 'In Bearbeitung')"
            )
            return self.cursor.fetchone()[0]
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Offene Tickets zählen): {e}")
            return 0

    def get_average_processing_time(self) -> str:
        try:
            self.cursor.execute(
                """
                SELECT (strftime('%s', updated_at) - strftime('%s', created_at)) AS duration
                FROM tickets
                WHERE status = 'Erledigt' AND updated_at IS NOT NULL AND created_at IS NOT NULL
                """
            )
            rows = self.cursor.fetchall()
            if not rows:
                return "Keine Daten"
            total_sec = sum(r["duration"] for r in rows)
            avg_sec = total_sec / len(rows)
            h = int(avg_sec // 3600)
            m = int((avg_sec % 3600) // 60)
            s = int(avg_sec % 60)
            return f"{h}h {m}m {s}s"
        except sqlite3.Error as e:
            st.error(f"Datenbankfehler (Durchschnittliche Bearbeitungszeit): {e}")
            return "Fehler"


# -------------------------------------------------
# UI‑Funktionen
# -------------------------------------------------
def create_ticket_page(db: TicketDatabase) -> None:
    """Seite zum Anlegen eines neuen Tickets – nur für Rolle 'Anwender'."""
    if st.session_state.role != "Anwender":
        st.error("Nur Anwender dürfen neue Tickets erstellen.")
        return

    st.title("Neues Ticket 🎫")
    with st.form(key="ticket_creation"):
        title = st.text_input("Titel (erforderlich)", max_chars=100, key="t_title")
        description = st.text_area("Beschreibung", placeholder="Details…", key="t_desc")
        priority = st.selectbox(
            "Priorität", ["Niedrig", "Mittel", "Hoch"], index=1, key="t_priority"
        )
        category = st.selectbox(
            "Kategorie", ["Bug", "Feature", "Support"], index=0, key="t_category"
        )
        submit = st.form_submit_button("Ticket anlegen")
        if submit:
            if not title.strip():
                st.error("Titel darf nicht leer sein.")
                return
            ticket_id = db.add_ticket(
                title=title,
                description=description,
                priority=priority,
                category=category,
                created_by=st.session_state.username,
            )
            if ticket_id:
                st.success(f"Ticket #{ticket_id} erfolgreich erstellt! 🎉")
            else:
                st.error("Ticket konnte nicht erstellt werden.")


def list_tickets_page(db: TicketDatabase) -> None:
    """Übersicht mit Kanban‑Board."""
    st.title("Ticket‑Übersicht 📄")

    # ---- Filter ----
    search = st.text_input("Suche…", key="search")
    prio_filter = st.multiselect(
        "Priorität filtern",
        options=["Niedrig", "Mittel", "Hoch"],
        default=["Niedrig", "Mittel", "Hoch"],
        key="prio_filter",
    )
    # Status‑Filter hängt von Rolle ab
    allowed_statuses = (
        ["Neu", "In Bearbeitung"]
        if st.session_state.role == "Support"
        else ["Neu", "In Bearbeitung", "Erledigt"]
    )
    status_filter = st.multiselect(
        "Status filtern",
        options=["Neu", "In Bearbeitung", "Erledigt"],
        default=allowed_statuses,
        key="status_filter",
    )

    # ---- Daten abfragen ----
    tickets = db.get_tickets(
        search=search,
        priorities=prio_filter,
        statuses=status_filter,
    )
    if not tickets:
        st.info("Keine Tickets gefunden – erstelle eines mittels *Neues Ticket*! 🎯")
        return

    # ---- Einteilen in Spalten ----
    tickets_by_status = {"Neu": [], "In Bearbeitung": [], "Erledigt": []}
    for t in tickets:
        tickets_by_status[t["status"]].append(t)

    # ---- Kanban‑Layout (Flex‑Board) ----
    st.markdown('<div class="kanban-board">', unsafe_allow_html=True)
    with st.container():
        col_new, col_in, col_done = st.columns(3, gap="large")

        # ---- Hilfsfunktion für eine einzelne Spalte ----
     # ---- Hilfsfunktion für eine einzelne Spalte ----
        def render_column(status: str, tickets: list[dict]) -> None:
            """Rendert Header und Cards sauber innerhalb eines Streamlit-Containers."""
            
            # Wir nutzen den nativen st.container mit Border anstatt manuellem HTML-DIV
            with st.container(border=True):
                # Header direkt über Streamlit-Markdown (zentriert & blau)
                st.markdown(f'<h3 style="text-align:center; color:#007bff; border-bottom:2px solid #007bff; padding-bottom:5px;">{status}</h3>', unsafe_allow_html=True)

                if not tickets:
                    # Kleiner Text statt fetter blauer Kachel (verhindert das "Kachel-Problem")
                    st.caption(f"Keine Tickets in '{status}'")
                    return

                # Jedes Ticket = Expander
                for ticket in tickets:
                    sentiment = ticket.get("sentiment", "") or ""
                    label = f"Ticket #{ticket['id']} ({ticket['priority']}) {sentiment}"
                    
                    with st.expander(label, expanded=False):
                        st.subheader(ticket["title"])
                        # Hier folgen deine restlichen st.write und st.form Befehle...

                    # Badges
                    st.write(
                        "**Priorität:**",
                        _priority_badge_html(ticket["priority"]),
                        unsafe_allow_html=True,
                    )
                    st.write(
                        "**Status:**",
                        _status_badge_html(ticket["status"]),
                        unsafe_allow_html=True,
                    )

                    # Weitere Infos
                    st.write("**Beschreibung:**", ticket["description"] or "Keine Beschreibung")
                    st.write("**Kategorie:**", ticket["category"])
                    st.write("**Erstellt am:**", ticket["created_at"])
                    st.write("**Zuletzt aktualisiert:**", ticket["updated_at"] or "Nie")
                    st.write("**Support‑Rückmeldung:**", ticket.get("support_feedback", "Keine"))
                    st.write("**Interne Notizen:**", ticket.get("internal_notes", "Keine"))

                    # ---- Status‑Update‑Formular (nur wenn berechtigt) ----
                    if db._has_permission(ticket["id"], st.session_state.username):
                        cur_status = ticket["status"]
                        role = st.session_state.role

                        # Welche Status‑Optionen dürfen angezeigt werden?
                        if role == "Administrator":
                            opts = ["Neu", "In Bearbeitung", "Erledigt"]
                        elif role == "Support":
                            opts = ["In Bearbeitung", "Erledigt"]
                        else:  # Anwender
                            opts = [cur_status]

                        # Falls die aktuelle Status‑Option nicht mehr erlaubt ist, vorne einreihen
                        if cur_status not in opts:
                            opts.insert(0, cur_status)

                        with st.form(f"status_update_{ticket['id']}", clear_on_submit=True):
                            new_status = st.selectbox(
                                "Status",
                                opts,
                                index=opts.index(cur_status),
                                key=f"status_sel_{ticket['id']}",
                                label_visibility="hidden",
                            )
                            # Support‑Feedback immer zeigen
                            feedback = st.text_area(
                                "Support‑Rückmeldung",
                                value=ticket.get("support_feedback", ""),
                                key=f"feedback_{ticket['id']}",
                                height=70,
                            )
                            # Interne Notizen nur für Support/ADMIN
                            notes = (
                                st.text_area(
                                    "Interne Notizen",
                                    value=ticket.get("internal_notes", ""),
                                    key=f"notes_{ticket['id']}",
                                    height=70,
                                )
                                if role in {"Support", "Administrator"}
                                else None
                            )
                            submit_btn = st.form_submit_button("Änderungen speichern")
                            if submit_btn:
                                ok = db.update_status(
                                    ticket_id=ticket["id"],
                                    new_status=new_status,
                                    support_feedback=feedback,
                                    internal_notes=notes,
                                    updated_by=st.session_state.username,
                                )
                                if ok:
                                    msg = (
                                        f"Status von Ticket #{ticket['id']} auf **{new_status}** geändert."
                                        if new_status != cur_status
                                        else f"Ticket #{ticket['id']} gespeichert."
                                    )
                                    st.success(msg)
                                else:
                                    st.error("Der Status konnte nicht aktualisiert werden.")
                    # ---- Ende Formular ----
            # Spalten‑Wrapper schließen
            st.markdown('</div>', unsafe_allow_html=True)

        # ---- Einzelne Spalten rendern ----
        with col_new:
            render_column("Neu", tickets_by_status["Neu"])
        with col_in:
            render_column("In Bearbeitung", tickets_by_status["In Bearbeitung"])
        with col_done:
            render_column("Erledigt", tickets_by_status["Erledigt"])

    # Board‑Wrapper schließen
    st.markdown('</div>', unsafe_allow_html=True)


def user_management_page(db: TicketDatabase) -> None:
    """Nur Administrator kann Benutzer anlegen / löschen."""
    if st.session_state.role != "Administrator":
        st.error("Nur Administrator kann Benutzer verwalten.")
        return

    st.title("Benutzer Verwaltung 🔐")

    # ---- Neuen Benutzer anlegen ----
    with st.form(key="add_user"):
        user_name = st.text_input("Benutzername", key="new_user")
        user_pwd = st.text_input("Passwort", type="password", key="new_pw")
        user_role = st.selectbox(
            "Rolle",
            ["Anwender", "Support", "Administrator"],
            index=0,
            key="new_role",
        )
        submit_new = st.form_submit_button("Benutzer anlegen")
        if submit_new:
            if user_name.strip() and user_pwd.strip():
                db.add_user(user_name, user_pwd, user_role)
            else:
                st.error("Benutzername und Passwort dürfen nicht leer sein.")

    # ---- Aktuelle Nutzer listieren ----
    st.subheader("Aktive Nutzer")
    users = db.get_users()
    if not users:
        st.info("Keine weiteren Nutzer vorhanden.")
        return

    # Tabellarische Ansicht (lesbar, aber nicht editierbar)
    st.dataframe(users, use_container_width=True, hide_index=True)

    # ---- Nutzer löschen (Button pro Zeilen‑Entry) ----
    for user in users:
        col_name, col_role, col_btn = st.columns([3, 2, 1])
        with col_name:
            st.write(user["username"])
        with col_role:
            st.write(f"({user['role']})")
        with col_btn:
            if st.button(f"✕ Löschen", key=f"del_user_{user['username']}"):
                if db.remove_user(user["username"]):
                    st.success(f"Benutzer '{user['username']}' gelöscht.")
                else:
                    st.error("Benutzer konnte nicht gelöscht werden.")
                # No explicit rerun needed – die Button‑Interaktion löst automatisch einen fresh Run aus


def admin_dashboard_page(db: TicketDatabase) -> None:
    """Kurze Statistiken für Administrator."""
    st.title("Admin Dashboard 🌐")
    st.markdown("---")

    # Offene Tickets
    st.metric("Offene Tickets (gesamt)", db.get_open_ticket_count())

    # Durchschnittliche Bearbeitungszeit
    avg = db.get_average_processing_time()
    if avg.startswith("Keine"):
        st.caption(avg)
    else:
        st.metric("Durchschnittliche Bearbeitungszeit", avg)


# -------------------------------------------------
# Haupt‑Programm
# -------------------------------------------------
def main() -> None:
    # Session‑State initialisieren (erste Ausführung)
    if "username" not in st.session_state:
        st.session_state.username = None
    if "role" not in st.session_state:
        st.session_state.role = None

    # DB‑Verbindung für den aktuellen Lauf öffnen
    try:
        db = TicketDatabase()
    except Exception as exc:
        st.error(f"Konnte Datenbank nicht initialisieren: {exc}")
        st.stop()

    # --------------------------- Login ---------------------------
    if not st.session_state.username:
        # Login‑UI nur das allererste Mal
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="company-header">Schacht GmbH <span>♟️</span></div>', unsafe_allow_html=True)
        st.markdown('<h2 class="login-title">Anmeldung zum Ticket‑System</h2>', unsafe_allow_html=True)

        login_user = st.text_input("Benutzername", key="login_user")
        login_pass = st.text_input("Passwort", type="password", key="login_pw")

        if st.button("Einloggen"):
            role = db.check_user(login_user, login_pass)
            if role:
                st.session_state.username = login_user
                st.session_state.role = role
                st.success("Erfolgreich angemeldet! 🎉")

                # DB sauber schließen – im nächsten Run wird sie erneut aufgebaut
                db.close()
                # Durch das `return` endet die aktuelle Ausführung.
                # Der nächste Streamlit‑Run wird automatisch ausgelöst, weil sich
                # `session_state.username` geändert hat.
                return
            else:
                st.error("Falscher Benutzername oder Passwort.")
        st.markdown('</div>', unsafe_allow_html=True)

        # Login‑Verlauf beendigt – DB schließen und Skript fertig.
        db.close()
        return

    # --------------------------- Logged‑in UI ---------------------------
    st.sidebar.title("Menü 📁")
    st.sidebar.write(f"🧑‍💼 {st.session_state.username} ({st.session_state.role})")

    page_options = ["Ticket‑Übersicht", "Neues Ticket"]
    if st.session_state.role == "Administrator":
        page_options += ["Benutzer Verwaltung", "Admin Dashboard"]
    current_page = st.sidebar.radio("Seite wählen", page_options, index=0)

    if current_page == "Ticket‑Übersicht":
        list_tickets_page(db)
    elif current_page == "Neues Ticket":
        create_ticket_page(db)
    elif current_page == "Benutzer Verwaltung":
        user_management_page(db)
    elif current_page == "Admin Dashboard":
        admin_dashboard_page(db)

    # Aufräumen (Datenbank schließen – wird jedes Mal neu gebaut)
    db.close()


if __name__ == "__main__":
    # Streamlit‑Version in den Logs ausgeben (hilft beim Debuggen)
    print(f"Streamlit‑Version: {st.__version__}")
    main()