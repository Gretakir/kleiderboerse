"""
database.py
------------
Kapselt den kompletten Zugriff auf die SQLite-Datenbank der Kleiderbörse.
"""

import sqlite3
from pathlib import Path

DB_PFAD = Path(__file__).parent / "kleiderboerse.db"

KATEGORIEN = ["Oberteil", "Hose", "Schuhe", "Jacke", "Accessoires", "Kopfbedeckung"]
STATUS_VERFUEGBAR = "verfügbar"
STATUS_RESERVIERT = "reserviert"
STATUS_VERKAUFT = "gekauft/versendet"


def get_connection():
    conn = sqlite3.connect(DB_PFAD)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titel TEXT NOT NULL,
            kategorie TEXT NOT NULL,
            preis REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'verfügbar',
            bild_dateiname TEXT NOT NULL,
            erstellt_am TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def item_erstellen(titel, kategorie, preis, bild_dateiname):
    conn = get_connection()
    conn.execute(
        "INSERT INTO items (titel, kategorie, preis, bild_dateiname) VALUES (?, ?, ?, ?)",
        (titel, kategorie, preis, bild_dateiname),
    )
    conn.commit()
    conn.close()


def items_suchen(suchbegriff=None, kategorie=None, preis_min=None, preis_max=None):
    conn = get_connection()
    query = "SELECT * FROM items WHERE status != ?"
    params = [STATUS_VERKAUFT]

    if suchbegriff:
        query += " AND titel LIKE ?"
        params.append(f"%{suchbegriff}%")
    if kategorie:
        query += " AND kategorie = ?"
        params.append(kategorie)
    if preis_min is not None:
        query += " AND preis >= ?"
        params.append(preis_min)
    if preis_max is not None:
        query += " AND preis <= ?"
        params.append(preis_max)

    query += " ORDER BY erstellt_am DESC"
    items = conn.execute(query, params).fetchall()
    conn.close()
    return items


def item_holen(item_id):
    conn = get_connection()
    item = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    conn.close()
    return item


def status_aendern(item_id, neuer_status):
    conn = get_connection()
    conn.execute("UPDATE items SET status = ? WHERE id = ?", (neuer_status, item_id))
    conn.commit()
    conn.close()
