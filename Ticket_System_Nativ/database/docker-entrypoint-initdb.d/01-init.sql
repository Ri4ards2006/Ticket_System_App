-- Datenbank erstellen
CREATE DATABASE ticketdb;

-- Benutzer erstellen und Rechte vergeben
CREATE USER ticketuser WITH ENCRYPTED PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE ticketdb TO ticketuser;

-- Tabelle Users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL
);

-- Tabelle Tickets
CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(20) NOT NULL,  -- new, in_progress, closed
    category VARCHAR(50),
    priority VARCHAR(20),
    assigned_to INT REFERENCES users(id)
);
