# Praktikum 2 - SWE

## Aufgabestellung

---
Die Firma "Pflege für Alle", ein mobiler Pflegedienst, der Menschen in Not pflegerische und häusliche
Unterstützung bietet, hat uns gebeten, eine Software/App für sie zu entwickeln, damit sie mit dem
Management Schritt halten können, das sich aus der Expansion des Unternehmens ergibt.
Ursprünglich gab es 40 Mitarbeiter, aber seit sie letztes Jahr ein weiteres Pflegeheim erworben haben, hat sich
die Zahl auf etwa 60 geändert. Vor dem Erwerb konnte der Firmeninhaber Rudi Fleißig all das Management im
Kopf erledigen, aber jetzt fühlt er sich überfordert von der Anzahl der Mitarbeiter und Patienten, die
berücksichtigt werden müssen.
Die Software sollte den Mitarbeitern zugänglich sein und es den Pflegern ermöglichen, den Dienstplan
einzusehen (der Name und Standort jedes Patienten sowie Datum und Uhrzeit enthält, zu der die Pfleger bei
ihnen sein müssen), während es den Verwaltungsmitarbeitern ermöglicht, Dinge wie den Dienstplan zu
verwalten, einen Mitarbeiter oder Kunden hinzuzufügen oder zu entfernen und deren Verfügbarkeit zu
überprüfen.
Die Gestaltung des Programms bleibt uns überlassen.

---

## Der Praktikumsbericht

Der Praktikumsbericht befindet sich [hier](/docs/Pflegeplaner.md)

## How to run

### Install required modules
```sh
pip install flask flask_login pytest coverage
```

### Datenbank initialisieren
```sh
# wenn nötig alte datenbank löschen
rm src/instance/flaskr.sqlite

python -m flask --app src/flaskr init-db
```

### Run applicaion
```sh
# lokal ereichbar
python -m flask --app src/flaskr run

# im vpn ereichbar
python -m flask --app src/flaskr run --host=0.0.0.0
```

### Run tests
```sh
pytest
```

## Team

- Sebastian Botezatu
- Mentej-Mert Atalay
- Patrick Pirig
- Sinan Yildirim
