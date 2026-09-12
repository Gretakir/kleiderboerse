# Kleiderbörse — Setup auf dem Raspberry Pi

## 1. Code auf den Pi bringen

**Über GitHub:**
```bash
git clone <eure-repo-url>
cd kleiderboerse
```

**Ohne GitHub (Ordner direkt vom Laptop übertragen):**
```bash
scp -r kleiderboerse pi@kleiderboerse.local:~/
```

## 2. Abhängigkeiten installieren

```bash
cd kleiderboerse
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 3. Firewall-Port freigeben (falls ufw aktiv ist)

```bash
sudo ufw allow 5000
```

## 4. Server starten

```bash
python3 app.py
```

## 5. Von einem Client aus testen

```
http://kleiderboerse.local:5000
```

## Neu in dieser Version: Netzwerk-Info-Seite

Über den Menüpunkt „📡 Netzwerk-Info" (oben in der Navigation) zeigt die App
live berechnete Werte zu Client, Server, IP-Adressen, Subnetzmaske,
Standard-Gateway, Port, Protokoll und DNS — direkt aus den echten
Verbindungsdaten, nicht als Beispieltext. Praktisch für Präsentation und
Screenshots im Arbeitsprotokoll (Kapitel 3 „Fachliche Hintergründe").

Hinweis: Subnetzmaske und Standard-Gateway werden über das Linux-Kommando
`ip` ausgelesen — das funktioniert nur auf dem Raspberry Pi selbst, nicht
bei lokalen Tests unter Windows/macOS (dort erscheint ein Hinweistext statt
eines Wertes, das ist kein Fehler).

## Für die Präsentation

- `debug=True` in `app.py` (letzte Zeile) vor der echten Präsentation auf
  `debug=False` stellen.
- Datenbank vor der Präsentation einmal zurücksetzen:
  ```bash
  rm kleiderboerse.db
  ```
