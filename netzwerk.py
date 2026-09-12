"""
netzwerk.py
------------
Dieses Modul demonstriert die im Anforderungsdokument geforderten
Netzwerk-Fachbegriffe nicht nur in Textform, sondern berechnet sie live
aus echten Daten der laufenden Verbindung und des Raspberry Pi selbst.
Wird von der Route /netzwerk in app.py genutzt.
"""

import socket
import subprocess
import ipaddress


def eigene_ip_ermitteln():
    """
    Ermittelt die tatsächliche LAN-IP-Adresse des Servers (Raspberry Pi).
    Trick: Ein UDP-Socket wird 'verbunden' (es werden dabei keine echten
    Daten verschickt) — dadurch wählt das Betriebssystem automatisch die
    passende Netzwerkschnittstelle, deren Absenderadresse wir auslesen.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"


def subnetz_und_gateway_ermitteln():
    """
    Liest Subnetzmaske und Standard-Gateway über die Linux-Kommandos
    'ip route' und 'ip addr' aus. Funktioniert auf dem Raspberry Pi
    (Raspberry Pi OS/Debian); unter Windows/macOS bei der Entwicklung
    liefert es einen Hinweistext statt eines Fehlers.
    """
    subnetzmaske = None
    gateway = None
    try:
        route = subprocess.run(["ip", "route", "show", "default"],
                                capture_output=True, text=True, timeout=2)
        for teil in route.stdout.split():
            stellen = teil.split(".")
            if len(stellen) == 4 and all(s.isdigit() for s in stellen):
                gateway = teil
                break

        addr = subprocess.run(["ip", "-4", "-o", "addr", "show"],
                               capture_output=True, text=True, timeout=2)
        for zeile in addr.stdout.splitlines():
            if "inet " in zeile and "127.0.0.1" not in zeile:
                cidr = zeile.split("inet ")[1].split()[0]  # z. B. "192.168.1.50/24"
                netz = ipaddress.ip_network(cidr, strict=False)
                subnetzmaske = str(netz.netmask)
                break
    except (FileNotFoundError, subprocess.SubprocessError):
        pass

    return (subnetzmaske or "nicht ermittelbar (nur unter Linux/Raspberry Pi OS)",
            gateway or "nicht ermittelbar (nur unter Linux/Raspberry Pi OS)")


def ip_analysieren(ip_text, subnetzmaske_text):
    """
    Berechnet aus einer IP-Adresse und der Subnetzmaske den Netzwerk- und
    Hostanteil und bestimmt per Bibliotheksfunktion, ob es sich um eine
    private oder öffentliche IP-Adresse handelt. Demonstriert die Begriffe
    damit anhand echter Berechnung statt nur in Worten.
    """
    ergebnis = {
        "ip": ip_text,
        "ist_privat": None,
        "netzwerkanteil": "–",
        "hostanteil": "–",
    }
    try:
        adresse = ipaddress.ip_address(ip_text)
        ergebnis["ist_privat"] = adresse.is_private

        if subnetzmaske_text and "nicht ermittelbar" not in subnetzmaske_text:
            netz = ipaddress.ip_network(f"{ip_text}/{subnetzmaske_text}", strict=False)
            ergebnis["netzwerkanteil"] = str(netz.network_address)
            ergebnis["hostanteil"] = str(int(adresse) - int(netz.network_address))
    except ValueError:
        pass
    return ergebnis


def dns_aufloesen(hostname):
    """
    Löst einen Hostnamen per DNS auf. Demonstriert den DNS-Begriff live:
    der Client (unser Server-Prozess) fragt einen DNS-Server nach der zum
    Namen gehörenden IP-Adresse.
    """
    try:
        ip = socket.gethostbyname(hostname)
        return {"erfolg": True, "ip": ip}
    except socket.error as fehler:
        return {"erfolg": False, "fehler": str(fehler)}
