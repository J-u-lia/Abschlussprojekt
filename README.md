# Abschlussprojekt
## Versuchspersonen-Analyse & Leistungsdiagnostik-App
Diese App ist eine interaktive Streamlit-Anwendung, mit der sich Versuchspersonen verwalten und leistungsdiagnostische Tests analysieren lassen. Sie eignet sich besonders für sportwissenschaftliche Studien, Trainer:innen, Sportärzt:innen oder alle, die physiologische Testdaten übersichtlich erfassen und auswerten möchten.

Zu den zentralen Funktionen gehört das Anlegen neuer Versuchspersonen, bei dem persönliche Daten (Name, Geschlecht, Geburtsjahr, Sportniveau) angegeben und ein Bild hochgeladen werden können. Jede Versuchsperson erhält eine eindeutige ID – über diese kann sie später eindeutig aufgerufen werden, auch wenn es mehrere Personen mit gleichem Namen gibt. Anschließend können beliebig viele Tests hinzugefügt werden – wahlweise durch CSV-Upload oder manuelle Eingabe.

Beim Aufruf einer bestehenden Person werden zunächst deren Stammdaten rechts neben dem Bild übersichtlich dargestellt. Darunter lassen sich in einem Dropdown-Menü die vorhandenen Tests (inkl. Testdatum und -dauer) auswählen. Sämtliche Daten – sowohl persönliche Angaben als auch Testdaten – lassen sich bei Bedarf bearbeiten: Das umfasst z. B. das Austauschen des Fotos, das Anlegen weiterer Tests (ebenfalls per CSV oder manuell), sowie das Editieren bestehender Tests, bei dem entweder CSV-Dateien ersetzt oder einzelne Werte direkt angepasst werden können. Alle Änderungen lassen sich anschließend speichern.

Im Tab Leistungsdatenanalyse wird zunächst ein Test ausgewählt. Danach werden verschiedene Auswertungen vorgenommen:

- Plot von Leistung und Herzfrequenz über die Zeit mit farblich hinterlegten Herzfrequenzzonen
- Plot von Leistung und Herzfrequenz über Stufen hinweg
- Anzeige von Maximalleistung und durchschnittlicher Leistung
- Verweildauer in den einzelnen Herzfrequenzzonen
- Durchschnittliche Leistung und Herzfrequenz pro Herzfrequenzzone
- Durchschnittliche Leistung und Herzfrequenz pro Stufe

Im Tab Laktattest Analyse kann zwischen den gespeicherten Tests gewählt werden. Je nachdem, ob die Belastungsdatei oder die Erholungsdatei ausgewählt wurde, zeigt die App unterschiedliche Auswertungen:

- Belastungsdaten:
    - Plot von Laktat- und Herzfrequenzwerten über die Leistung, mit farblich markierten Laktatzonen
    - Berechnung und Anzeige der Laktatschwellen (LT1 und LT2)
    - Visualisierung von Laktatzonen, Laktatkurven und die empfohlenen Trainingsherzfrequenzbereiche basierend auf den Schwellen

- Erholungsdaten:
    - Plot von Laktat und Herzfrequenz über die Zeit, ebenfalls mit Laktatzonen im Hintergrund
    - Anzeige des durchschnittlichen Laktatabbaus pro Minute als Leistungsindikator

## Installation und Start (mit PDM)
Die Anwendung basiert auf Python und verwendet zur Paket- und Projektverwaltung das Tool PDM, das eine einfache Verwaltung von Abhängigkeiten und virtuellen Umgebungen ermöglicht.

Um die App zu starten, wird zunächst PDM benötigt. Falls es noch nicht installiert ist, kann es mit dem folgenden Befehl über pip installiert werden: "pip install pdm". Nach der Installation kann das Repository mit der App geklont und in das Projektverzeichnis gewechselt werden. Dort lassen sich alle benötigten Bibliotheken bequem über PDM installieren. PDM liest dabei die Abhängigkeiten aus der Datei pyproject.toml und erstellt automatisch eine pdm.lock, die genaue Versionen für reproduzierbare Umgebungen festlegt. Falls zusätzliche Pakete benötigt werden (z. B. beim Entwickeln neuer Funktionen), können diese wie folgt hinzugefügt werden: "pdm add paketname"Nach erfolgreicher Installation kann die App mit folgendem Befehl gestartet werden: "streamlit run main.py".