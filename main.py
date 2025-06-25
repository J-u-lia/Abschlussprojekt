import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import re
import copy
from PIL import Image
import datetime
import read_data
from Leistung import Leistung
from Laktat import Laktat
from automatische_id_generieren import generiere_neue_id
from Testnummer import ermittle_nächste_testnummer
#from read_data import load_person_data
#from read_data import get_person_list
#from read_data import find_person_data_by_name

# Streamlit Aufbau der session_states
if "page_mode" not in st.session_state:
    st.session_state.page_mode = "start"
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "pending_user_data" not in st.session_state:
    st.session_state.pending_user_data = None

# Tabs
start_tab, leistungs_tab, laktat_tab = st.tabs(["Startseite", "Leistungsdaten", "Laktattest"])
#tabs = st.tabs(["Startseite", "Versuchspersonen", "Leistungsdaten"])
# Hilfsfunktion zum Speichern von Testdaten

def Testdaten_speichern(person_id, belastung_df, erholung_df, testnummer):
    """ Diese Funktion speichert die Testdaten in den entsprechenden Ordnern. Es wird unterschieden zwischen Belastungs- und Erholungsdaten. 
    Die Daten werden in CSV-Dateien gespeichert.
    Eingabewerte: 
    - person_id: ID der Versuchsperson
    - belastung_df: DataFrame mit den Belastungsdaten
    - erholung_df: DataFrame mit den Erholungsdaten
    - testnummer: Nummer des Tests (z.B. 1, 2, 3)
    Rückgabewerte:
    - Pfad zu den gespeicherten Belastungs- und Erholungsdaten
    """
    daten_folder = os.path.join("data", person_id, "daten")
    os.makedirs(daten_folder, exist_ok=True)

    belastung_path = os.path.join(daten_folder, f"{person_id}_Test{testnummer}_Belastung.csv")
    erholung_path = os.path.join(daten_folder, f"{person_id}_Test{testnummer}_Erholung.csv")

    belastung_df.to_csv(belastung_path, index=False)
    erholung_df.to_csv(erholung_path, index=False)

    return belastung_path, erholung_path


# Aufbau der Startseite
def Startseite():
    """Diese Funktion definiert die Startseite der App. Es gibt zwei Buttons, um entweder eine neue Versuchsperson anzulegen oder eine bestehende auszuwählen.
    Eingabewerte: Keine
    Rückgabewerte: Keine
    """
    st.title("Stufentest Analyse APP")
    st.markdown("## Willkommen zur Stufentest Analyse APP")

    if st.button("Neue Versuchsperson anlegen"):
        st.session_state.page_mode = "neu"
    if st.button("Bestehende Versuchsperson auswählen"):
        st.session_state.page_mode = "bestehend"

# Neue Versuchsperson anlegen
def neue_Versuchsperson_anlegen():
    """Diese Funktion ermöglicht die manuelle Eingabe von Versuchspersonen und deren Testdaten. Es wird eine neue ID generiert und die Daten werden in einem JSON-Format gespeichert.
    Eingabewerte: Keine
    Rückgabewerte: Keine
    """
    st.header("Neue Versuchsperson anlegen")
    neue_id = generiere_neue_id()

    # Grunddaten
    col1, col2 = st.columns(2)
    with col1:
        vorname = st.text_input("Vorname")
        geschlecht = st.selectbox("Geschlecht", ["Männlich", "Weiblich"])
        sportniveau = st.selectbox("Sportniveau", ["Einsteiger", "Hobbysportler", "Amateur", "Leistungssportler", "Profi"])
        st.text_input("ID", value=neue_id, disabled=True)

    with col2:
        nachname = st.text_input("Nachname")
        geburtsjahr = st.selectbox("Geburtsjahr", list(reversed(range(1950, datetime.date.today().year + 1))))
        bild = st.file_uploader("Bild hochladen", type=["jpg", "jpeg", "png"])

    if "test_liste" not in st.session_state:
        st.session_state.test_liste = []

    if "input_art_auswahl" not in st.session_state:
        st.session_state.input_art_auswahl = None

    st.markdown("### Testdaten hinzufügen")

    # Graues Kasten: Testdatum, Dauer und zwei Buttons
    with st.form("test_form", border=True):
        testdatum = st.date_input("Testdatum", datetime.date.today(), key="testdatum_input")
        testdauer = st.number_input("Testdauer (Minuten)", min_value=1, key="testdauer_input")

        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Test via CSV"):
                st.session_state.input_art_auswahl = "csv"
        with col2:
            if st.form_submit_button("Test manuell eintragen"):
                st.session_state.input_art_auswahl = "manuell"

    # Nach Auswahl: Eingabe für CSV oder manuell
    if st.session_state.input_art_auswahl == "csv":
        st.markdown("#### CSV Testdaten eingeben")
        
        col1, col2 = st.columns(2)
        with col1:
            belastung_datei = st.file_uploader("Belastung CSV hochladen", type=["csv"], key="belastung_csv")
        with col2:
            erholung_datei = st.file_uploader("Erholung CSV hochladen", type=["csv"], key="erholung_csv")

        if st.button("Test speichern"):
            neue_testnummer = len(st.session_state.test_liste) + 1
            test = {
                "id": f"T{neue_testnummer:03}",
                "Testdatum": str(testdatum),
                "Testdauer": testdauer,
                "Belastung": belastung_datei.name if belastung_datei else None,
                "Erholung": erholung_datei.name if erholung_datei else None,
                "belastung_file": belastung_datei,
                "erholung_file": erholung_datei,
                "InputArt": "csv"
            }
            st.session_state.test_liste.append(test)
            st.session_state.input_art_auswahl = None
            st.success("CSV-Test gespeichert!")


    elif st.session_state.input_art_auswahl == "manuell":
        st.markdown("#### Manuelle Testdaten eingeben")

        st.markdown("### Belastung")
        stufendauer = st.selectbox("Dauer einer Stufe (Minuten)", options=[1, 2, 3, 4, 5], key="stufendauer")

        belastung_zeiten = [stufendauer * (i + 1) for i in range(8)]
        belastung_df = st.data_editor(pd.DataFrame({
            "Zeit (min)": belastung_zeiten,
            "Leistung (Watt)": ["" for _ in range(8)],
            "Herzfrequenz (bpm)": ["" for _ in range(8)],
            "Laktat (mmol/l)": ["" for _ in range(8)],
        }), num_rows="dynamic", key="belastung_editor")

        st.markdown("### Erholungsdaten")
        erholungsintervall = st.selectbox("Messintervall (Minuten)", options=[1, 2, 3, 5], key="erholungsintervall")

        erholung_zeiten = [erholungsintervall * (i + 1) for i in range(5)]
        erholung_df = st.data_editor(pd.DataFrame({
            "Zeit (min)": erholung_zeiten,
            "Leistung (Watt)": ["" for _ in range(5)],
            "Herzfrequenz (bpm)": ["" for _ in range(5)],
            "Laktat (mmol/l)": ["" for _ in range(5)],
        }), num_rows="dynamic", key="erholung_editor")

        if st.button("Test speichern"):
            neue_testnummer = len(st.session_state.test_liste) + 1
            test = {
                "id": f"T{neue_testnummer:03}",
                "Testdatum": str(testdatum),
                "Testdauer": testdauer,
                "Belastung": belastung_df.to_dict(orient="records"),
                "Erholung": erholung_df.to_dict(orient="records"),
                "Stufendauer": stufendauer,
                "Erholungsintervall": erholungsintervall,
                "InputArt": "manuell"
            }
            st.session_state.test_liste.append(test)
            st.session_state.input_art_auswahl = None
            st.success("Manueller Test gespeichert!")


    # Zeige gespeicherte Tests
    if st.session_state.test_liste:
        st.markdown("### Bereits hinzugefügte Tests")
        for test in st.session_state.test_liste:
            st.markdown(f"""
                **{test['id']}**  
                - Datum: {test['Testdatum']}  
                - Dauer: {test['Testdauer']} Minuten  
                - Eingabeart: {test['InputArt']}  
                - Belastung: {test['Belastung']}  
                - Erholung: {test['Erholung']}  
            """)

    st.markdown("---")

    # Versuchsperson speichern
    if st.button("Versuchsperson speichern"):
        st.session_state.pending_user_data = {
            "id": neue_id,
            "firstname": vorname,
            "lastname": nachname,
            "date_of_birth": str(geburtsjahr),
            "gender": geschlecht,
            "sportniveau": sportniveau,
            "picture_path": None,
            "Stufentest": {
                f"Test{i+1}": test for i, test in enumerate(st.session_state.test_liste)
            }
        }



        # Speicherstruktur vorbereiten
        person_id = st.session_state.pending_user_data["id"]
        person_dir = os.path.join("data", person_id)
        daten_dir = os.path.join(person_dir, "daten")
        images_dir = os.path.join(person_dir, "images")

        os.makedirs(daten_dir, exist_ok=True)
        os.makedirs(images_dir, exist_ok=True)


        # Versuchsperson-Bild speichern
        if bild:
            bild_dateiname = "bild.jpg"
            bild_speicherpfad = os.path.join(images_dir, bild_dateiname)
            with open(bild_speicherpfad, "wb") as f:
                f.write(bild.getbuffer())
            st.session_state.pending_user_data["picture_path"] = bild_speicherpfad

        # Testdaten speichern
        # Testdaten speichern – alle in einem Ordner
        for i, test in enumerate(st.session_state.test_liste, start=1):
            test_prefix = f"test_{i:03}"

            if test["InputArt"] == "manuell":
                belastung_df = pd.DataFrame(test["Belastung"])
                erholung_df = pd.DataFrame(test["Erholung"])

                belastung_csv = os.path.join(daten_dir, f"{test_prefix}_belastung.csv")
                erholung_csv = os.path.join(daten_dir, f"{test_prefix}_erholung.csv")

                belastung_df.to_csv(belastung_csv, index=False)
                erholung_df.to_csv(erholung_csv, index=False)

                test["belastung_csv_path"] = belastung_csv
                test["erholung_csv_path"] = erholung_csv

            elif test["InputArt"] == "csv":
                belastung_file = test.get("belastung_file")
                erholung_file = test.get("erholung_file")

                if belastung_file:
                    belastung_pfad = os.path.join(daten_dir, f"{test_prefix}_belastung.csv")
                    with open(belastung_pfad, "wb") as f:
                        f.write(belastung_file.getbuffer())
                    test["belastung_csv_path"] = belastung_pfad

                if erholung_file:
                    erholung_pfad = os.path.join(daten_dir, f"{test_prefix}_erholung.csv")
                    with open(erholung_pfad, "wb") as f:
                        f.write(erholung_file.getbuffer())
                    test["erholung_csv_path"] = erholung_pfad


        # JSON-Datei mit Metadaten speichern
        # Entferne nicht-serialisierbare Objekte für JSON
        json_safe_data = copy.deepcopy(st.session_state.pending_user_data)

        for test in json_safe_data["Stufentest"].values():
            if "belastung_file" in test:
                del test["belastung_file"]
            if "erholung_file" in test:
                del test["erholung_file"]

        # JSON-Datei mit Metadaten speichern
        json_path = os.path.join(person_dir, f"{person_id}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_safe_data, f, ensure_ascii=False, indent=4)



        # Weiterleitung zur Startseite
        st.success("Versuchsperson wurde gespeichert!")
        st.session_state.page_mode = "start"
        st.rerun()


    if st.button("Zurück zur Startseite"):
        st.session_state.page_mode = "start"
        st.rerun()




def csv_hochladen():
    """Diese Funktion ermöglicht das Hochladen von CSV-Dateien für Belastungs- und Erholungsdaten. Die Daten werden in die Testliste der aktuellen Sitzung gespeichert.
    Eingabewerte: Keine
    Rückgabewerte: Keine
    """
    st.header("CSV-Testdaten hochladen")

    if "active_test_index" not in st.session_state:
        st.session_state.active_test_index = 0

    idx = st.session_state.active_test_index
    st.markdown("**Belastungsdaten hochladen**")
    belastung_datei = st.file_uploader("Belastung CSV", key=f"belastung_{idx}")

    st.markdown("**Erholungsdaten hochladen (optional)**")
    erholung_datei = st.file_uploader("Erholung CSV", key=f"erholung_{idx}")

    if st.button("Speichern und zurück"):
        # Dateien lesen
        if belastung_datei:
            df_belastung = pd.read_csv(belastung_datei)
            st.session_state.test_liste[idx]["Belastung"] = df_belastung
            # Wichtig: Datei-Objekt speichern!
            st.session_state.test_liste[idx]["belastung_file"] = belastung_datei

        if erholung_datei:
            df_erholung = pd.read_csv(erholung_datei)
            st.session_state.test_liste[idx]["Erholung"] = df_erholung
            st.session_state.test_liste[idx]["erholung_file"] = erholung_datei

        st.session_state.test_liste[idx]["InputArt"] = "csv"

        # Weitergehen
        if idx + 1 < len(st.session_state.test_liste):
            st.session_state.active_test_index += 1
        else:
            st.session_state.page_mode = "neu"
        st.rerun()

    if st.button("Zurück"):
        st.session_state.page_mode = "neu"
        st.rerun()





# manuelle Eingabe der gemessenen Werte in Tabellen
def manuelle_eingabe():
    """Diese Funktion ermöglicht die manuelle Eingabe von Testdaten für Belastung und Erholung. 
    Die Daten werden aktuell in DataFrames gespeichert und können später verarbeitet werden. Später werden die Daten in einer csv Datei in einem bestimmten Ordner gespeichert.
    Eingabewerte: Keine
    Rückgabewerte: Keine
    """
    st.header("Manuelle Eingabe der Testdaten")

    if "active_test_index" not in st.session_state:
        st.session_state.active_test_index = 0

    idx = st.session_state.active_test_index

    st.markdown(f"### Eingabe für Test {idx + 1}")

    stufendauer = st.selectbox("Dauer einer Stufe (Minuten)", [1, 2, 3, 4, 5])
    zeit_belastung = [(i + 1) * stufendauer for i in range(8)]

    belastung_df = st.data_editor(pd.DataFrame({
        "Zeit (min)": zeit_belastung,
        "Leistung (Watt)": ["" for _ in range(8)],
        "Herzfrequenz (bpm)": ["" for _ in range(8)],
        "Laktat (mmol/l)": ["" for _ in range(8)],
    }), num_rows="dynamic")

    erholungsintervall = st.selectbox("Messintervall (Minuten)", [1, 2, 3, 5])
    zeit_erholung = [(i + 1) * erholungsintervall for i in range(5)]

    erholung_df = st.data_editor(pd.DataFrame({
        "Zeit (min)": zeit_erholung,
        "Leistung (Watt)": ["" for _ in range(5)],
        "Herzfrequenz (bpm)": ["" for _ in range(5)],
        "Laktat (mmol/l)": ["" for _ in range(5)],
    }), num_rows="dynamic")

    if st.button("Speichern und zurück"):
        st.session_state.test_liste[idx]["Belastung"] = belastung_df
        st.session_state.test_liste[idx]["Erholung"] = erholung_df
        st.session_state.test_liste[idx]["InputArt"] = "manuell"

        if idx + 1 < len(st.session_state.test_liste):
            st.session_state.active_test_index += 1
        else:
            st.session_state.page_mode = "neu"
        st.rerun()

    if st.button("Zurück"):
        st.session_state.page_mode = "neu"
        st.rerun()





# Bestehende Versuchsperson auswählen

def bestehende_versuchsperson_auswählen():
    """Diese Funktion ermöglicht die Auswahl und Anzeige/Bearbeitung einer bestehenden Versuchsperson. 
    Dabei können csv Dateien gelöscht und ersetzt werden und die manuelle Eingabe überarbeitet werden. Die Änderungen werden in der JSON Datei aktualisiert.
    Eingabewerte: Keine
    Rückgabewerte: Keine
    """
    st.header("Versuchsperson anzeigen")

    person_id_input = st.text_input("Versuchspersonen-ID eingeben (z.B. vp001):").strip().lower()

    if person_id_input:
        base_path = os.path.join("data", person_id_input)
        json_path = os.path.join(base_path, f"{person_id_input}.json")
        image_folder = os.path.join(base_path, "images")
        daten_folder = os.path.join(base_path, "daten")

        if not os.path.exists(json_path):
            st.error(f"Keine Daten für '{person_id_input}' gefunden.")
            return

        with open(json_path, "r", encoding="utf-8") as f:
            person_data = json.load(f)

        st.session_state.current_user = person_id_input

        # Bild anzeigen
        image_path = None
        if os.path.exists(image_folder):
            for file in os.listdir(image_folder):
                if file.lower().endswith((".jpg", ".jpeg", ".png")):
                    image_path = os.path.join(image_folder, file)
                    break
        if image_path and os.path.exists(image_path):
            st.image(image_path, caption=f"Bild von {person_id_input}")
        else:
            st.warning("Kein Bild gefunden.")

        # Wenn man nicht im Bearbeitungsmodus ist sollen nur Daten angezeigt werden
        if not st.session_state.edit_mode:
            st.markdown(f"**Name:** {person_data.get('firstname', '')} {person_data.get('lastname', '')}")
            st.markdown(f"**Geburtsjahr:** {person_data.get('date_of_birth', 'Unbekannt')}")
            st.markdown(f"**Geschlecht:** {person_data.get('gender', 'Unbekannt')}")
            st.markdown(f"**Sportniveau:** {person_data.get('sportniveau', 'Unbekannt')}")
            st.markdown(f"**ID:** {person_data.get('id', 'Unbekannt')}")

            # Testdaten anzeigen
            st.subheader("Testdaten auswählen")

            test_files = []

            # CSV-Dateien aus beiden Unterordnern sammeln
            if os.path.exists(daten_folder):
                test_files = [f for f in os.listdir(daten_folder) if f.endswith(".csv")]


            test_files = sorted(test_files)

            if test_files:
                selected_test = st.selectbox("Test auswählen", options=test_files, key="selected_test_csv")
                # Speichere die gewählte Datei für spätere Tabs (z. B. Leistung)
                st.session_state.selected_test_file = selected_test

                st.info(f"Ausgewählter Test: {selected_test}")

                # Suche den zugehörigen Testeintrag in Stufentest
                zugeordneter_test = None
                zugeordneter_test = person_data.get("Stufentest", {}).get(st.session_state.get("selected_test_file"))



                if zugeordneter_test:
                    testdatum = zugeordneter_test.get("Testdatum", "Unbekannt")
                    testdauer = zugeordneter_test.get("Testdauer", "Unbekannt")
                else:
                    testdatum = "Unbekannt"
                    testdauer = "Unbekannt"

                st.markdown(f"**Testdatum:** {testdatum}")
                st.markdown(f"**Testdauer:** {testdauer} Minuten")

                if st.button("Daten editieren"):
                    st.session_state.edit_mode = True
                    st.rerun()
            else:
                st.info("Keine Testdaten vorhanden.")



        # Bearbeitungsmodus aktiv - Daten können bearbeitet werden
        else:
            st.subheader("Personendaten bearbeiten")

            # Sicherstellen, dass Stufentest-Eintrag existiert
            if "Stufentest" not in person_data:
                person_data["Stufentest"] = {}

            # Allgemeine Personendaten bearbeiten
            person_data["firstname"] = st.text_input("Vorname", value=person_data.get("firstname", ""))
            person_data["lastname"] = st.text_input("Nachname", value=person_data.get("lastname", ""))
            person_data["date_of_birth"] = st.selectbox(
                "Geburtsjahr",
                options=list(reversed(range(1950, datetime.date.today().year + 1))),
                index=0 if not person_data.get("date_of_birth")
                else list(reversed(range(1950, datetime.date.today().year + 1))).index(int(person_data["date_of_birth"]))
            )
            person_data["gender"] = st.selectbox("Geschlecht", ["Männlich", "Weiblich"],
                                                index=0 if person_data.get("gender") == "Männlich" else 1)
            person_data["sportniveau"] = st.selectbox(
                "Sportniveau",
                ["Einsteiger", "Hobbysportler", "Amateur", "Leistungssportler", "Profi"],
                index=["Einsteiger", "Hobbysportler", "Amateur", "Leistungssportler", "Profi"].index(
                    person_data.get("sportniveau", "Einsteiger"))
            )

            st.subheader("Testdaten bearbeiten")

            # Hole den aktuell ausgewählten Testnamen
            stufentest_key = st.session_state.get("selected_test_file")

            if not stufentest_key:
                st.warning("Kein gültiger Test ausgewählt. Bitte wähle einen Test auf der Startseite aus.")
                st.stop()

            if "Stufentest" not in person_data or stufentest_key not in person_data["Stufentest"]:
                st.warning(f"Test '{stufentest_key}' wurde nicht in den Personendaten gefunden.")
                st.stop()

            aktueller_test = person_data["Stufentest"][stufentest_key]

            # Datenordner
            daten_folder = os.path.join("data", st.session_state.current_user, "daten")

            # Testdatum vorbereiten
            try:
                aktuelles_datum = datetime.date.fromisoformat(aktueller_test.get("Testdatum", datetime.date.today().isoformat()))
            except ValueError:
                aktuelles_datum = datetime.date.today()

            testdatum_input = st.date_input("Testdatum", value=aktuelles_datum)
            testdauer_input = st.number_input("Testdauer (Minuten)", min_value=1, max_value=180,
                                            value=int(aktueller_test.get("Testdauer", 30)))

            bearbeitungs_option = st.radio(
                "Bearbeitungsmodus für Testdaten wählen:",
                ["CSV-Dateien editieren", "Manuelle Daten überarbeiten"],
                key="testdaten_edit_modus"
            )

            if bearbeitungs_option == "CSV-Dateien editieren":
                def ersetze_csv(dateityp_label, datei_keyword, zielordner):
                    """Ersetzt oder löscht die CSV-Datei für Belastung oder Erholung.
                    Eingabewerte:
                    - dateityp_label: Label für die Datei (z.B. "Belastungsdatei")
                    - datei_keyword: Schlüsselwort für die Datei (z.B. "belastung" oder "erholung")
                    - zielordner: Zielordner, in dem die Datei gespeichert ist
                    Rückgabewerte: Keine
                    """
                    st.markdown(f"#### {dateityp_label}")
                    vorhandene_csvs = [f for f in os.listdir(zielordner) if f.endswith(".csv") and stufentest_key in f.lower() and datei_keyword in f.lower()]
                    if vorhandene_csvs:
                        st.markdown(f"Aktuelle Datei: `{vorhandene_csvs[0]}`")
                        if st.button(f"{dateityp_label} löschen", key=f"delete_{datei_keyword}"):
                            os.remove(os.path.join(zielordner, vorhandene_csvs[0]))
                            st.success(f"{dateityp_label} wurde gelöscht.")
                            st.rerun()
                    else:
                        st.info(f"Keine {dateityp_label}-Datei vorhanden.")
                    neue_datei = st.file_uploader(f"{dateityp_label} ersetzen", type="csv", key=f"upload_{datei_keyword}")
                    if neue_datei:
                        for file in vorhandene_csvs:
                            os.remove(os.path.join(zielordner, file))
                        neuer_pfad = os.path.join(zielordner, f"{stufentest_key}_{datei_keyword}.csv")
                        with open(neuer_pfad, "wb") as f:
                            f.write(neue_datei.getbuffer())
                        st.success(f"{dateityp_label} wurde erfolgreich ersetzt.")

                ersetze_csv("Belastungsdatei", "belastung", daten_folder)
                ersetze_csv("Erholungsdatei", "erholung", daten_folder)

            elif bearbeitungs_option == "Manuelle Daten überarbeiten":
                st.markdown("### CSV-Inhalte manuell bearbeiten")

                def lade_csv_als_dataframe(keyword, ordner, testkey):
                    """Lädt eine CSV-Datei als DataFrame basierend auf einem Schlüsselwort und Testkey.
                    Eingabewerte:
                    - keyword: Schlüsselwort für die Datei (z.B. "belastung" oder "erholung")
                    - ordner: Ordner, in dem die Datei gesucht wird
                    - testkey: Schlüssel für den Test (z.B. "Test001")
                    Rückgabewerte:
                    - DataFrame mit den geladenen Daten oder None, wenn keine Datei gefunden wurde
                    """
                    if os.path.exists(ordner):
                        for f in os.listdir(ordner):
                            if f.endswith(".csv") and keyword in f.lower() and testkey in f.lower():
                                return pd.read_csv(os.path.join(ordner, f)), f
                    return None, None

                def speichere_dataframe(df, ordner, filename):
                    """Speichert ein DataFrame als CSV-Datei in einem bestimmten Ordner.
                    Eingabewerte:
                    - df: DataFrame, das gespeichert werden soll
                    - ordner: Zielordner, in dem die Datei gespeichert werden soll
                    - filename: Name der Datei (z.B. "belastung.csv" oder "erholung.csv")
                    Rückgabewerte: Keine
                    """
                    pfad = os.path.join(ordner, filename)
                    df.to_csv(pfad, index=False)
                    st.success(f"{filename} wurde gespeichert.")

                for label, keyword in [("Belastung", "belastung"), ("Erholung", "erholung")]:
                    df, dateiname = lade_csv_als_dataframe(keyword, daten_folder, stufentest_key)
                    if df is not None:
                        st.markdown(f"#### {label}-Daten: `{dateiname}`")
                        edit_df = st.data_editor(df, num_rows="dynamic", key=f"edit_{keyword}")
                        if st.button(f"{label}-Tabelle speichern", key=f"save_{keyword}"):
                            speichere_dataframe(edit_df, daten_folder, dateiname)
                    else:
                        st.warning(f"Keine Datei für {label} zum aktuellen Test gefunden.")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Änderungen speichern"):
                    person_data["Stufentest"][stufentest_key] = {
                        "Testdatum": testdatum_input.isoformat(),
                        "Testdauer": testdauer_input,
                    }

                    json_path = os.path.join("data", st.session_state.current_user, f"{st.session_state.current_user}.json")
                    with open(json_path, "w", encoding="utf-8") as f:
                        json.dump(person_data, f, indent=4, ensure_ascii=False)

                    st.success("Daten erfolgreich gespeichert.")
                    st.session_state.edit_mode = False
                    st.rerun()

            with col2:
                if st.button("Zurück"):
                    st.session_state.edit_mode = False
                    st.rerun()

    if st.button("Zurück zur Startseite", key="back_to_home_edit_mode"):
        st.session_state.page_mode = "start"
        st.session_state.edit_mode = False
        st.session_state.current_user = None
        st.rerun()





# Struktur der verschiedenen Seiten
if st.session_state.page_mode == "start":
    with start_tab:
        Startseite()
elif st.session_state.page_mode == "neu":
    with start_tab:
        neue_Versuchsperson_anlegen()
elif st.session_state.page_mode == "csv_upload":
    with start_tab:
        csv_hochladen()
elif st.session_state.page_mode == "manuelle_eingabe":
    with start_tab:
        manuelle_eingabe()
elif st.session_state.page_mode == "bestehend":
    with start_tab:
        bestehende_versuchsperson_auswählen()

# Leistungsdaten Tab
with leistungs_tab:
    st.header("Leistungsdatenanalyse")

    if st.session_state.current_user:
        person_id = st.session_state.current_user
        daten_folder = os.path.join("data", person_id, "daten")

        # Suche nach der ersten Belastungsdatei
        try:
            belastung_files = sorted([f for f in os.listdir(daten_folder) if "belastung" in f and f.endswith(".csv")])
            # Vorauswahl aus Session übernehmen
            vorauswahl = st.session_state.get("selected_test_file")

            # Fallback zur ersten Datei, falls keine gültige Vorauswahl
            if vorauswahl not in belastung_files:
                vorauswahl = belastung_files[0] if belastung_files else None

            # Wenn eine Datei verfügbar ist, Selectbox anzeigen
            if vorauswahl:
                ausgewählte_datei = st.selectbox(
                    "Belastungsdatei auswählen",
                    options=belastung_files,
                    index=belastung_files.index(vorauswahl)
                )
            else:
                st.warning("Keine gültige Belastungsdatei gefunden.")
                st.stop()


            pfad_zur_belastung = os.path.join(daten_folder, ausgewählte_datei)

            # Leistungsklasse verwenden
            analyse = Leistung(pfad_zur_belastung)

            st.subheader("Herzfrequenz- und Leistungsdiagramm mit Zonen")
            fig_zonen = analyse.plot_herzfrequenz(mode="zonen")
            st.plotly_chart(fig_zonen, use_container_width=True)

            st.subheader("Herzfrequenz- und Leistungsdiagramm mit Stufen")
            fig_stufen = analyse.plot_herzfrequenz(mode="stufen")
            st.plotly_chart(fig_stufen, use_container_width=True)

            st.subheader("Leistungskennwerte")
            werte = analyse.Werte_berechnen()

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Durchschnittliche Leistung", f"{werte['mean_power']:.1f} W")
                st.metric("Maximale Leistung", f"{werte['max_power']} W")

            st.subheader("Zeit in Herzfrequenz-Zonen")
            st.dataframe(werte["zeit_pro_zone"])

            st.subheader("Durchschnittswerte pro Zone")
            # Kombiniere die beiden Series zu einem DataFrame, damit man eine Tabelle bekommt
            df_zone_summary = pd.concat([werte["hf_pro_zone"], werte["leistung_pro_zone"]], axis=1)
            df_zone_summary.columns = ["Durchschnittliche Herzfrequenz (bpm)", "Durchschnittliche Leistung (Watt)"]
            # Zeigt die zusammengefasste Tabelle an
            st.dataframe(df_zone_summary)

            st.subheader("Durchschnittswerte pro Stufe")
            werte["stufenwerte"].rename(columns={
                "durchschnitts_Leistung": "durchschnittliche Leistung (Watt)",
                "durchschnitts_HF": "durchschnittliche HF (bpm)"
            }, inplace=True)

            st.dataframe(werte["stufenwerte"])

        except StopIteration:
            st.warning("Keine Belastungsdaten gefunden.")
    else:
        st.info("Bitte zuerst eine Versuchsperson auf der Startseite auswählen.")



# Laktattest Tab
with laktat_tab:
    st.header("Laktattest Analyse")

    if st.session_state.current_user:
        person_id = st.session_state.current_user
        daten_folder = os.path.join("data", person_id, "daten")

        selected_test = st.session_state.get("selected_test_csv")
        if selected_test:
            laktat_path = os.path.join(daten_folder, selected_test)

            try:
                # CSV-Datei laden
                df = Laktat.csv_Datei_laden(laktat_path)

                if "Laktat (mmol/l)" in df.columns and not df["Laktat (mmol/l)"].isnull().all():
                    # Analyse nur, wenn Laktatdaten vorhanden sind
                    Lt1, Lt2 = Laktat.schwellenwerte_berechnen(df)
                    df = Laktat.laktatzonen_berechnen(df, Lt1, Lt2)
                    
                    # Wähle richtigen Plot-Typ basierend auf dem Dateinamen
                    if "belastung" in selected_test:
                        fig = Laktat.Belastung_plot_erstellen(df, Lt1, Lt2)

                        # Berechne Trainingsbereiche
                        trainingsbereiche = Laktat.Trainingsbereiche_berechnen(Lt1, Lt2)

                        # Plot mit Laktat und Herzfrequenz
                        st.plotly_chart(fig, use_container_width=True)

                        # Anzeige der Trainingsbereiche
                        st.subheader("Laktatschwellen")
                        st.metric("LT1", f"{Lt1:.0f} Watt")
                        st.metric("LT2", f"{Lt2:.0f} Watt")

                        st.subheader("Laktatdaten mit Zonen")
                        st.dataframe(df[["Leistung (Watt)", "Laktat (mmol/l)", "Herzfrequenz (bpm)", "Laktatzone"]])
                        
                        # Trainingsbereich-Plot
                        st.subheader("Empfohlene Trainingsherzfrequenzbereiche")
                        hf_fig = Laktat.Trainingsbereiche_HF_plot(df, Lt1, Lt2)
                        st.plotly_chart(hf_fig, use_container_width=True)

                    elif "erholung" in selected_test:
                        fig = Laktat.Erholung_plot_erstellen(df, Lt1, Lt2)
                        st.plotly_chart(fig, use_container_width=True)
                        # Laktatabbau berechnen
                        abbau_rate = Laktat.Laktatabbau(df)
                        if abbau_rate is not None:
                            st.metric("durchschnittlicher Laktatabbau", f"{abbau_rate:.2f} mmol/l pro min")
                        else:
                            st.warning("Laktatabbau konnte nicht berechnet werden.")

                    else:
                        fig = Laktat.Belastung_plot_erstellen(df, Lt1, Lt2)
                  
                else:
                    st.warning("Keine Laktatdaten in der Datei gefunden.")

            except StopIteration:
                st.warning("Keine geeignete Belastungsdatei mit Laktatwerten gefunden.")
        else:
            st.warning("Kein Test ausgewählt. Bitte wähle einen Test auf der Startseite aus.")
    else:
        st.info("Bitte zuerst eine Versuchsperson auf der Startseite auswählen.")


