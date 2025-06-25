# Vollständig überarbeitete Version der Streamlit Stufentest App
import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from PIL import Image
import datetime
import read_data
from read_data import find_person_data_by_name

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

# Hilfsfunktion zum Speichern von Testdaten

def Testdaten_speichern(person_id, belastung_df, erholung_df, testnummer):
    test_Ordner = os.path.join(os.getcwd(), "data", "tests")
    os.makedirs(test_Ordner, exist_ok=True)
    test_dateipfad = os.path.join(test_Ordner, f"{person_id}_test{testnummer}.csv")

    # Speichern beide Teile als eine Datei mit Trennern
    with open(test_dateipfad, "w", encoding="utf-8") as f:
        f.write("# Belastung\n")
        belastung_df.to_csv(f, index=False)
        f.write("\n# Erholung\n")
        erholung_df.to_csv(f, index=False)

    return test_dateipfad

# Aufbau der Startseite
def Startseite():
    st.title("Stufentest Analyse APP")
    st.markdown("## Willkommen zur Stufentest Analyse APP")

    if st.button("Neue Versuchsperson anlegen"):
        st.session_state.page_mode = "neu"
    if st.button("Bestehende Versuchsperson auswählen"):
        st.session_state.page_mode = "bestehend"

# Neue Versuchsperson anlegen
def neue_Versuchsperson_anlegen():
    st.header("Neue Versuchsperson anlegen")
    person_dict = read_data.load_person_data()
    neue_id = f"vp{len(person_dict)+1:03d}"

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

    st.markdown("### Testdaten hinzufügen")
    col_csv, col_manuell = st.columns(2)
    with col_csv:
        if st.button("CSV-Datei hochladen"):
            st.session_state.pending_user_data = {
                "id": neue_id, "firstname": vorname, "lastname": nachname,
                "date_of_birth": str(geburtsjahr), "gender": geschlecht,
                "sportniveau": sportniveau, "picture_path": None
            }
            if bild:
                image_folder = os.path.join(os.getcwd(), "data", "images")
                os.makedirs(image_folder, exist_ok=True)
                bild_dateiname = f"{neue_id}.jpg"
                bild_speicherpfad = os.path.join(image_folder, bild_dateiname)
                with open(bild_speicherpfad, "wb") as f:
                    f.write(bild.getbuffer())
                st.session_state.pending_user_data["picture_path"] = bild_speicherpfad
            st.session_state.page_mode = "csv_upload"
            st.rerun()

    with col_manuell:
        if st.button("Daten eintragen"):
            st.session_state.pending_user_data = {
                "id": neue_id, "firstname": vorname, "lastname": nachname,
                "date_of_birth": str(geburtsjahr), "gender": geschlecht,
                "sportniveau": sportniveau, "picture_path": None
            }
            if bild:
                image_folder = os.path.join(os.getcwd(), "data", "images")
                os.makedirs(image_folder, exist_ok=True)
                bild_dateiname = f"{neue_id}.jpg"
                bild_speicherpfad = os.path.join(image_folder, bild_dateiname)
                with open(bild_speicherpfad, "wb") as f:
                    f.write(bild.getbuffer())
                st.session_state.pending_user_data["picture_path"] = bild_speicherpfad
            st.session_state.page_mode = "manuelle_eingabe"
            st.rerun()

# .csv Datei hochladen von Belastungs- und Erholungsdaten

def csv_hochladen():
    st.header("CSV-Testdaten hochladen")
    st.markdown("**Belastungsdaten hochladen**")
    belastung_datei = st.file_uploader("Belastung CSV", key="belastung")

    st.markdown("**Erholungsdaten hochladen (optional)**")
    erholung_datei = st.file_uploader("Erholung CSV", key="erholung")

    if st.button("Speichern und zurück zur Startseite"):
        testnummer = 1
        person_id = st.session_state.pending_user_data["id"]

        # Speichern Person in einer json-Datei
        personen_folder = os.path.join(os.getcwd(), "data")
        os.makedirs(personen_folder, exist_ok=True)
        person_path = os.path.join(personen_folder, f"{person_id}.json")
        with open(person_path, "w", encoding="utf-8") as f:
            json.dump(st.session_state.pending_user_data, f, indent=4)

        # Testdaten speichern in DataFrames
        df_belastung = pd.read_csv(belastung_datei) if belastung_datei else pd.DataFrame()
        df_erholung = pd.read_csv(erholung_datei) if erholung_datei else pd.DataFrame()

        Testdaten_speichern(person_id, df_belastung, df_erholung, testnummer)

        st.success("Alle Daten gespeichert!")
        st.session_state.page_mode = "start"
        st.rerun()

    if st.button("Zurück"):
        st.session_state.page_mode = "neu"
        st.rerun()

# manuelle Eingabe der gemessenen Werte in Tabellen
def manuelle_eingabe():
    st.header("Manuelle Eingabe der Testdaten")
    st.markdown("### Belastungsdaten")
    st.selectbox("Dauer einer Stufe (Minuten)", options=[1, 2, 3, 4, 5], key="stufendauer")

    belastung_df = st.data_editor(pd.DataFrame({
        "Leistung (Watt)": ["" for _ in range(8)],
        "Herzfrequenz": ["" for _ in range(8)],
        "Laktat": ["" for _ in range(8)],
    }), num_rows="dynamic")

    st.markdown("### Erholungsdaten")
    st.selectbox("Messintervall (Minuten)", options=[1, 2, 3, 5], key="erholungsintervall")

    erholung_df = st.data_editor(pd.DataFrame({
        "Zeit (min)": ["" for _ in range(5)],
        "Herzfrequenz": ["" for _ in range(5)],
        "Laktat": ["" for _ in range(5)],
    }), num_rows="dynamic")

    if st.button("Speichern und zurück zur Startseite"):
        person_id = st.session_state.pending_user_data["id"]
        testnummer = 1

        personen_folder = os.path.join(os.getcwd(), "data")
        os.makedirs(personen_folder, exist_ok=True)
        person_path = os.path.join(personen_folder, f"{person_id}.json")
        with open(person_path, "w", encoding="utf-8") as f:
            json.dump(st.session_state.pending_user_data, f, indent=4)

        Testdaten_speichern(person_id, belastung_df, erholung_df, testnummer)

        st.success("Testdaten gespeichert!")
        st.session_state.page_mode = "start"
        st.rerun()

    if st.button("Zurück"):
        st.session_state.page_mode = "neu"
        st.rerun()

# Bestehende Versuchsperson auswählen

def bestehende_versuchsperson_auswählen():
    st.header("Bestehende Versuchsperson auswählen")

    person_list = read_data.load_person_data()
    person_names = read_data.get_person_list(person_list)

    selected_person = st.selectbox("Person auswählen", options=person_names)

    if selected_person:
        person_data = find_person_data_by_name(selected_person)

        if person_data.get("picture_path"):
            st.image(person_data["picture_path"], caption=selected_person)
        else:
            st.warning("Kein Bild verfügbar.")

        st.markdown(f"**Name:** {person_data.get('firstname', '')} {person_data.get('lastname', '')}")
        st.markdown(f"**Geburtsjahr:** {person_data.get('date_of_birth', 'Unbekannt')}")
        st.markdown(f"**Geschlecht:** {person_data.get('gender', 'Unbekannt')}")
        st.markdown(f"**Sportniveau:** {person_data.get('sportniveau', 'Unbekannt')}")
        st.markdown(f"**ID:** {person_data.get('id', 'Unbekannt')}")

        # Nur Testdateien anzeigen – ohne Inhalt
        test_folder = os.path.join(os.getcwd(), "data", "tests")
        test_files = []

        if os.path.exists(test_folder) and person_data.get("id"):
            test_files = [f for f in os.listdir(test_folder) if f.startswith(person_data["id"])]

        if test_files:
            st.selectbox("Test auswählen", options=test_files)
        else:
            st.info("Keine Testdaten vorhanden.")

        if st.button("Zurück zur Startseite"):
            st.session_state.page_mode = "start"
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




# vor csv datei löschen
else:
            # bearbeiten der Personendaten
            st.subheader("Personendaten bearbeiten")
            person_data["firstname"] = st.text_input("Vorname", value=person_data.get("firstname", ""))
            person_data["lastname"] = st.text_input("Nachname", value=person_data.get("lastname", ""))
            person_data["date_of_birth"] = st.selectbox("Geburtsjahr", options=list(reversed(range(1950, datetime.date.today().year + 1))), index=0 if not person_data.get("date_of_birth") else list(reversed(range(1950, datetime.date.today().year + 1))).index(int(person_data["date_of_birth"])))
            person_data["gender"] = st.selectbox("Geschlecht", ["Männlich", "Weiblich"], index=0 if person_data.get("gender") == "Männlich" else 1)
            person_data["sportniveau"] = st.selectbox("Sportniveau", ["Einsteiger", "Hobbysportler", "Amateur", "Leistungssportler", "Profi"], index=["Einsteiger", "Hobbysportler", "Amateur", "Leistungssportler", "Profi"].index(person_data.get("sportniveau", "Einsteiger")))

            # Testdaten bearbeiten
            st.subheader("Testdaten bearbeiten")

            # Datum (ggf. in datetime umwandeln falls String)
            aktuelles_datum = datetime.date.today()
            if isinstance(person_data.get("Testdatum"), str):
                try:
                    aktuelles_datum = datetime.date.fromisoformat(person_data["Testdatum"])
                except ValueError:
                    pass  # falls das Format ungültig ist

            person_data["Testdatum"] = st.date_input("Testdatum", value=aktuelles_datum)
            person_data["Testdauer"] = st.number_input("Testdauer (Minuten)", min_value=1, max_value=180, value=int(person_data.get("Testdauer", 30)))

            # CSV-Datei austauschen
            if os.path.exists(daten_folder):
                vorhandene_csvs = sorted([f for f in os.listdir(daten_folder) if f.endswith(".csv")])
                if vorhandene_csvs:
                    aktuelle_csv = st.selectbox("Zugeordnete CSV-Datei", vorhandene_csvs, index=vorhandene_csvs.index(st.session_state.get("selected_test_csv", vorhandene_csvs[0])))
                    # Speichern der CSV-Auswahl (optional)
                    st.session_state["selected_test_csv"] = aktuelle_csv
                else:
                    st.warning("Keine CSV-Dateien im Testdaten-Ordner gefunden.")
            else:
                st.warning("Testdaten-Ordner existiert nicht.")



            if st.button("Änderungen speichern"):
                # Testdatum in String umwandeln, falls es ein datetime.date ist
                if isinstance(person_data.get("Testdatum"), datetime.date):
                    person_data["Testdatum"] = person_data["Testdatum"].isoformat()

                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(person_data, f, indent=4)

                st.success("Daten erfolgreich gespeichert.")
                st.session_state.edit_mode = False
                st.rerun()


            if st.button("Bearbeiten abbrechen"):
                st.session_state.edit_mode = False
                st.rerun()

        # CSV-Dateien Dropdown beibehalten
        st.subheader("Testdaten auswählen")
        if os.path.exists(daten_folder):
            test_files = sorted([f for f in os.listdir(daten_folder) if f.endswith(".csv")])
            if test_files:
                selected_test = st.selectbox("Test auswählen", options=test_files, key="selected_test_csv")
                st.info(f"Ausgewählter Test: {selected_test}")

                # Testdatum und -dauer anzeigen
                if selected_test:
                    testdatum = person_data.get("Testdatum", "Unbekannt")
                    testdauer = person_data.get("Testdauer", "Unbekannt")

                    st.markdown(f"**Testdatum:** {testdatum}")
                    st.markdown(f"**Testdauer:** {testdauer} Minuten")


            else:
                st.info("Keine Testdaten vorhanden.")
        else:
            st.info("Kein Testordner vorhanden.")

    if st.button("Zurück zur Startseite"):
        st.session_state.page_mode = "start"
        st.session_state.edit_mode = False
        st.rerun()
