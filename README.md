# Praktikum 2 - SWE

## Aufgabestellung

---
---
---

## Der Praktikumsbericht

Der Praktikumsbericht befindet sich [hier](./Pflegeplaner.md)

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
