"""
app.py
------
Flask-Server der Second-Hand-Kleiderbörse.
Läuft auf dem Raspberry Pi und stellt die Webseite für alle Clients
im Netzwerk bereit (siehe README.md für den Start auf dem Pi).
"""

import uuid
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, flash, abort
from werkzeug.utils import secure_filename

import database as db
import netzwerk as nw

BASE_DIR = Path(__file__).parent
UPLOAD_ORDNER = BASE_DIR / "static" / "uploads"
ERLAUBTE_ENDUNGEN = {"png", "jpg", "jpeg", "webp"}

app = Flask(__name__)
app.config["SECRET_KEY"] = "kleiderboerse-gk-projekt"
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # max. 8 MB pro Upload


def datei_erlaubt(dateiname):
    return "." in dateiname and dateiname.rsplit(".", 1)[1].lower() in ERLAUBTE_ENDUNGEN


@app.route("/")
def index():
    """Startseite: Übersicht mit Such- und Filterfunktion."""
    suchbegriff = request.args.get("q", "").strip()
    kategorie = request.args.get("kategorie", "").strip()
    preis_min = request.args.get("preis_min", "").strip()
    preis_max = request.args.get("preis_max", "").strip()

    items = db.items_suchen(
        suchbegriff=suchbegriff or None,
        kategorie=kategorie or None,
        preis_min=float(preis_min) if preis_min else None,
        preis_max=float(preis_max) if preis_max else None,
    )

    return render_template(
        "index.html",
        items=items,
        kategorien=db.KATEGORIEN,
        suchbegriff=suchbegriff,
        gewaehlte_kategorie=kategorie,
        preis_min=preis_min,
        preis_max=preis_max,
    )


@app.route("/upload", methods=["GET", "POST"])
def upload():
    """Formular zum Einstellen eines neuen Kleidungsstücks."""
    if request.method == "POST":
        titel = request.form.get("titel", "").strip()
        kategorie = request.form.get("kategorie", "")
        preis = request.form.get("preis", "")
        bild = request.files.get("bild")

        if not titel or kategorie not in db.KATEGORIEN or not preis:
            flash("Bitte alle Felder ausfüllen.")
            return redirect(url_for("upload"))
        try:
            preis = float(preis)
        except ValueError:
            flash("Preis muss eine Zahl sein.")
            return redirect(url_for("upload"))
        if not bild or bild.filename == "" or not datei_erlaubt(bild.filename):
            flash("Bitte ein gültiges Bild auswählen (png, jpg, jpeg, webp).")
            return redirect(url_for("upload"))

        endung = secure_filename(bild.filename).rsplit(".", 1)[1].lower()
        neuer_dateiname = f"{uuid.uuid4().hex}.{endung}"
        UPLOAD_ORDNER.mkdir(parents=True, exist_ok=True)
        bild.save(UPLOAD_ORDNER / neuer_dateiname)

        db.item_erstellen(titel, kategorie, preis, neuer_dateiname)
        flash("Anzeige wurde erfolgreich erstellt.")
        return redirect(url_for("index"))

    return render_template("upload.html", kategorien=db.KATEGORIEN)


@app.route("/item/<int:item_id>")
def item_detail(item_id):
    """Detailansicht einer einzelnen Anzeige mit den Status-Buttons."""
    item = db.item_holen(item_id)
    if item is None:
        abort(404)
    return render_template("item_detail.html", item=item, STATUS_VERFUEGBAR=db.STATUS_VERFUEGBAR,
                            STATUS_RESERVIERT=db.STATUS_RESERVIERT, STATUS_VERKAUFT=db.STATUS_VERKAUFT)


@app.route("/item/<int:item_id>/reservieren", methods=["POST"])
def item_reservieren(item_id):
    item = db.item_holen(item_id)
    if item is None:
        abort(404)
    db.status_aendern(item_id, db.STATUS_RESERVIERT)
    flash("Anzeige wurde reserviert.")
    return redirect(url_for("item_detail", item_id=item_id))


@app.route("/item/<int:item_id>/bestaetigen", methods=["POST"])
def item_bestaetigen(item_id):
    item = db.item_holen(item_id)
    if item is None:
        abort(404)
    db.status_aendern(item_id, db.STATUS_VERKAUFT)
    flash("Erhalt wurde bestätigt. Die Anzeige ist jetzt abgeschlossen.")
    return redirect(url_for("index"))


@app.route("/netzwerk")
def netzwerk_info():
    """
    Zeigt die aktuellen Netzwerk-Fachbegriffe live anhand echter Daten der
    laufenden Verbindung und des Servers (Raspberry Pi) an — für Protokoll
    und Präsentation ein anschauliches Beispiel, das die geforderten
    Fachbegriffe direkt über eine Programmfunktion demonstriert.
    """
    server_ip = nw.eigene_ip_ermitteln()
    subnetzmaske, gateway = nw.subnetz_und_gateway_ermitteln()
    server_info = nw.ip_analysieren(server_ip, subnetzmaske)

    client_ip = request.remote_addr
    client_info = nw.ip_analysieren(client_ip, subnetzmaske)

    dns_ziel = request.args.get("dns_ziel", "").strip()
    dns_ergebnis = nw.dns_aufloesen(dns_ziel) if dns_ziel else None

    host_header = request.host
    port = host_header.split(":")[1] if ":" in host_header else "80"

    return render_template(
        "netzwerk.html",
        server_ip=server_ip,
        server_info=server_info,
        client_ip=client_ip,
        client_info=client_info,
        subnetzmaske=subnetzmaske,
        gateway=gateway,
        protokoll=request.environ.get("SERVER_PROTOCOL", "HTTP/1.1"),
        methode=request.method,
        port=port,
        user_agent=request.headers.get("User-Agent", "unbekannt"),
        dns_ziel=dns_ziel,
        dns_ergebnis=dns_ergebnis,
    )


if __name__ == "__main__":
    db.init_db()
    # host="0.0.0.0" ist entscheidend: sonst wäre der Server nur vom Pi selbst
    # erreichbar, nicht von anderen Clients im Netzwerk (Pflichtanforderung!)
    app.run(host="0.0.0.0", port=5000, debug=True)
