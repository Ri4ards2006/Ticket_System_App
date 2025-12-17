# Database Setup für Ticket-System

## Ordnerstruktur
- `docker-entrypoint-initdb.d/`
  - 01-init.sql → DB, User, Tabellen
  - 02-seed_users.sql → Beispiel-User
  - 03-seed_tickets.sql → Beispiel-Tickets

## Hinweise
- Beim Start eines PostgreSQL Containers werden alle SQL-Dateien in `docker-entrypoint-initdb.d` automatisch ausgeführt.
- Passwort und Benutzer können nach Bedarf angepasst werden.
- Seed-Daten dienen nur zu Testzwecken.
