# Daten speichern über button
        st.markdown("### Versuchsperson speichern")
        if st.button("Speichern"):
            new_person_data = {
                "id": neue_id,
                "firstname": vorname,
                "lastname": nachname,
                "date_of_birth": str(geburtsjahr),
                "gender": geschlecht,
                "sportniveau": sportniveau,
                "picture_path": bild_speicherpfad
            }

            if bild:
                # Speicherpfad für Bilder definieren
                pfad_route = os.getcwd() # aktueller Arbeitsordner
                #pfad_route = os.path.dirname(os.path.abspath(__file__))
                image_folder = os.path.join(pfad_route, "data", "images")
                os.makedirs(image_folder, exist_ok=True)  # schauen ob Ordner existiert
                # Bildpfad mit Dateiname erstellen
                bild_dateiname = f"{neue_id}.jpg"
                bild_speicherpfad = os.path.join(image_folder, bild_dateiname)
                # Bild speichern
                try:
                    with open(bild_speicherpfad, "wb") as f:
                        f.write(bild.getbuffer())
                except Exception as e:
                    st.error(f"Fehler beim Speichern des Bildes: {e}")
                # Pfad im Dictionary eintragen unter picture_path
                new_person_data["picture_path"] = bild_speicherpfad

if st.button("Zurück zur Startseite"):
                st.session_state.page_mode = "start"
            st.rerun()


elif st.session_state.page_mode == "bestehend":
        st.header("Bestehende Versuchsperson auswählen")
        st.session_state.current_user = None
        st.session_state.selected_test = None
        st.session_state.selected_test_index = None

        person_list = read_data.load_person_data()
        person_names = read_data.get_person_list(person_list)

        selected_person = st.selectbox("Versuchsperson auswählen", options=person_names, key="person_select")

        if selected_person:
            st.session_state.current_user = selected_person
            current_person = find_person_data_by_name(selected_person)

            if current_person["picture_path"] is not None:
                image = Image.open(current_person["picture_path"])
                st.image(image, caption=selected_person)
            else:
                st.warning("Kein Bildpfad vorhanden für die aktuelle Person.")

            #if current_person and "picture_path" in current_person:
            #    image = Image.open(current_person["picture_path"])
            #    st.image(image, caption=selected_person)
            #else:
            #    st.warning("Kein Bild für diese Person gefunden.")

            st.markdown(f"**Name:** {current_person['firstname']} {current_person['lastname']}")
            st.markdown(f"**Geburtsdatum:** {current_person['date_of_birth']}")
            st.markdown(f"**Geschlecht:** {current_person['gender']}")
            st.markdown(f"**Sportniveau:** {current_person['sportniveau']}")
            st.markdown(f"**ID:** {current_person['id']}")

        if st.button("Zurück zur Startseite"):
            st.session_state.page_mode = "start"
            st.rerun()

# unsre alte streamlit startseite

import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import plotly.express as px
from PIL import Image
import read_data
from read_data import find_person_data_by_name
import datetime

tab1, tab2, tab3 = st.tabs(["Startseite", "Leistungsdaten", "Laktattest"])

if "page_mode" not in st.session_state:
    st.session_state.page_mode = "start"
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False


# TAB 1 – STARTSEITE mit Seitensteuerung
with tab1:
    if st.session_state.page_mode == "start":
        st.title("Stufentest Analyse APP")
        st.markdown("## Willkommen zur Stufentest Analyse APP")
        st.write("Hier können Sie eine neue Versuchsperson anlegen oder eine bestehende auswählen.")
        
        if st.button("Neue Versuchsperson anlegen"):
            st.session_state.page_mode = "neu"

        if st.button("Bestehende Versuchsperson auswählen"):
            st.session_state.page_mode = "bestehend"

    elif st.session_state.page_mode == "neu":
        st.header("Neue Versuchsperson anlegen")
        st.session_state.current_user = None
        st.session_state.selected_test = None
        st.session_state.selected_test_index = None

        # Lade bestehende Daten zur ID-Generierung
        person_dict = read_data.load_person_data()
        neue_id_nummer = len(person_dict) + 1
        neue_id = f"vp{neue_id_nummer:03d}"

        # Eingabefelder
        col1, col2 = st.columns(2)
        with col1:
            vorname = st.text_input("Vorname")
            geschlecht = st.selectbox("Geschlecht", ["Männlich", "Weiblich"])
            sportniveau = st.selectbox("Sportniveau", ["Einsteiger", "Hobbysportler", "Amateur", "Leistungssportler", "Profi"])
            # Automatisch generierte ID anzeigen
            st.text_input("ID", value=neue_id, disabled=True)

        with col2:
            nachname = st.text_input("Nachname")
            heute = datetime.date.today()
            jahre = list(range(1950, heute.year + 1))
            geburtsjahr = st.selectbox("Geburtsjahr", reversed(jahre))
            bild = st.file_uploader("Bild hochladen", type=["jpg", "jpeg", "png"])


        # Daten speichern über button
        st.markdown("### Versuchsperson speichern")
        if st.button("Speichern"):

            bild_speicherpfad = None  # Standardwert, falls kein Bild da ist

            if bild:
                # Speicherpfad für Bilder definieren
                pfad_route = os.getcwd()
                image_folder = os.path.join(pfad_route, "data", "images")
                os.makedirs(image_folder, exist_ok=True)

                # Bildpfad mit Dateiname erstellen
                bild_dateiname = f"{neue_id}.jpg"
                bild_speicherpfad = os.path.join(image_folder, bild_dateiname)

                # Bild speichern
                try:
                    with open(bild_speicherpfad, "wb") as f:
                        f.write(bild.getbuffer())
                except Exception as e:
                    st.error(f"Fehler beim Speichern des Bildes: {e}")
                    bild_speicherpfad = None  # Zurücksetzen, falls speichern fehlschlägt

            # Jetzt erst Dictionary mit Bildpfad (auch wenn None)
            new_person_data = {
                "id": neue_id,
                "firstname": vorname,
                "lastname": nachname,
                "date_of_birth": str(geburtsjahr),
                "gender": geschlecht,
                "sportniveau": sportniveau,
                "picture_path": bild_speicherpfad
            }

            # Person speichern, z.B. in JSON oder Datenbank (optional)
            st.success("Versuchsperson wurde gespeichert.")

            st.markdown("### Testdaten hinzufügen")
            st.write("Hier können Sie später die Leistungsdaten und Laktattest-Daten hinzufügen und analysieren.")
            col_csv, col_manuell = st.columns(2)
            with col_csv:
                if st.button("CSV-Datei hochladen"):
                    st.session_state.page_mode = "csv_upload"
                    st.session_state.pending_user_data = new_person_data
                    st.rerun()

            with col_manuell:
                if st.button("Daten eintragen"):
                    st.session_state.page_mode = "manuelle_eingabe"
                    st.session_state.pending_user_data = new_person_data
                    st.rerun()

            # speichern als einzelne JSON-Datei nach Vor- und Nachname im jeweiligen Downloads ornder
            pfad_route = os.path.dirname(os.path.abspath(__file__))
            speicherpfad = os.path.join(pfad_route, "Data")
            file_name = f"{vorname}_{nachname}.json".replace(" ", "_")
            pfad = os.path.join(speicherpfad, file_name)

            with open(pfad, "w", encoding="utf-8") as f:
                json.dump(new_person_data, f, indent=4, ensure_ascii=False)

            st.success(f"Versuchsperson gespeichert unter:\n{pfad}")
            st.session_state.page_mode = "start"
            st.rerun()


    elif st.session_state.page_mode == "bestehend":
        st.header("Bestehende Versuchsperson auswählen")

        # Daten der Testperson ändern und anschließend speichern bzw. überschreiben
        if "edit_mode" not in st.session_state:
            st.session_state.edit_mode = False
        st.session_state.selected_test = None
        st.session_state.selected_test_index = None

        person_list = read_data.load_person_data()
        person_names = read_data.get_person_list(person_list)

        selected_person = st.selectbox("Versuchsperson auswählen", options=person_names, key="person_select")

        if selected_person:
            st.session_state.current_user = selected_person
            current_person = find_person_data_by_name(selected_person)

            if not st.session_state.edit_mode:
                # Bild anzeigen
                if current_person["picture_path"] is not None and os.path.exists(current_person["picture_path"]):
                    image = Image.open(current_person["picture_path"])
                    st.image(image, caption=selected_person)
                else:
                    st.warning("Kein Bildpfad vorhanden für die aktuelle Person.")

                # Daten anzeigen
                st.markdown(f"**Name:** {current_person['firstname']} {current_person['lastname']}")
                st.markdown(f"**Geburtsjahr:** {current_person['date_of_birth']}")
                st.markdown(f"**Geschlecht:** {current_person['gender']}")
                st.markdown(f"**Sportniveau:** {current_person['sportniveau']}")
                st.markdown(f"**ID:** {current_person['id']}")

                # Editier-Button
                if st.button("Daten editieren"):
                    st.session_state.edit_mode = True
                    st.rerun()

            else:
                # Bearbeitungsfelder
                col1, col2 = st.columns(2)
                with col1:
                    vorname = st.text_input("Vorname", value=current_person["firstname"])
                    geschlecht = st.selectbox("Geschlecht", ["Männlich", "Weiblich"],
                                            index=["Männlich", "Weiblich"].index(current_person["gender"]))
                    sportniveau = st.selectbox("Sportniveau", ["Einsteiger", "Hobbysportler", "Amateur", "Leistungssportler", "Profi"],
                                            index=["Einsteiger", "Hobbysportler", "Amateur", "Leistungssportler", "Profi"].index(current_person["sportniveau"]))
                with col2:
                    nachname = st.text_input("Nachname", value=current_person["lastname"])
                    jahre = list(reversed(range(1950, datetime.date.today().year + 1)))
                    geburtsjahr = st.selectbox("Geburtsjahr", jahre, index=jahre.index(int(current_person["date_of_birth"])))
                    neues_bild = st.file_uploader("Neues Bild hochladen", type=["jpg", "jpeg", "png"])

                if st.button("Änderungen speichern"):
                    bild_speicherpfad = current_person.get("picture_path")

                    if neues_bild:
                        pfad_route = os.getcwd()
                        image_folder = os.path.join(pfad_route, "data", "images")
                        os.makedirs(image_folder, exist_ok=True)
                        bild_dateiname = f"{current_person['id']}.jpg"
                        bild_speicherpfad = os.path.join(image_folder, bild_dateiname)
                        try:
                            with open(bild_speicherpfad, "wb") as f:
                                f.write(neues_bild.getbuffer())
                        except Exception as e:
                            st.error(f"Fehler beim Speichern des Bildes: {e}")
                            bild_speicherpfad = current_person.get("picture_path")

                    # Neue Daten zusammenstellen
                    updated_data = {
                        "id": current_person["id"],
                        "firstname": vorname,
                        "lastname": nachname,
                        "date_of_birth": str(geburtsjahr),
                        "gender": geschlecht,
                        "sportniveau": sportniveau,
                        "picture_path": bild_speicherpfad
                    }

                    # Speichern in JSON-Datei (überschreibt alte)
                    pfad_route = os.path.dirname(os.path.abspath(__file__))
                    speicherpfad = os.path.join(pfad_route, "Data")
                    os.makedirs(speicherpfad, exist_ok=True)
                    file_name = f"{vorname}_{nachname}.json".replace(" ", "_")
                    pfad = os.path.join(speicherpfad, file_name)

                    with open(pfad, "w", encoding="utf-8") as f:
                        json.dump(updated_data, f, indent=4, ensure_ascii=False)

                    st.success("Änderungen gespeichert.")
                    st.session_state.edit_mode = False
                    st.rerun()

        if st.button("Zurück zur Startseite"):
            st.session_state.page_mode = "start"
            st.session_state.edit_mode = False
            st.rerun()

    elif st.session_state.page_mode == "csv_upload":
        st.header("CSV-Datei hochladen")

        uploaded_file = st.file_uploader("Wähle eine CSV-Datei aus", type=["csv"])

        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                st.dataframe(df)
                st.success("CSV erfolgreich geladen.")
                # Hier könntest du df mit der Person verknüpfen
            except Exception as e:
                st.error(f"Fehler beim Lesen der Datei: {e}")

        if st.button("Zurück"):
            st.session_state.page_mode = "neu"
            st.rerun()

    elif st.session_state.page_mode == "manuelle_eingabe":
        st.header("Testdaten manuell eintragen")

        st.markdown("#### Stufentest-Daten")
        st.write("Gib die gemessenen Werte ein:")

        if "leistungsdaten" not in st.session_state:
            st.session_state.leistungsdaten = pd.DataFrame({
                "Herzfrequenz": ["" for _ in range(8)],
                "Laktat": ["" for _ in range(8)],
                "Leistung": ["" for _ in range(8)],
            })

        st.session_state.leistungsdaten = st.data_editor(
            st.session_state.leistungsdaten,
            num_rows="dynamic",
            use_container_width=True
        )

        st.markdown("#### Erholungsdaten")

        if "erholungsdaten" not in st.session_state:
            st.session_state.erholungsdaten = pd.DataFrame({
                "Zeit (min)": ["" for _ in range(5)],
                "Herzfrequenz": ["" for _ in range(5)],
                "Laktat": ["" for _ in range(5)],
            })

        st.session_state.erholungsdaten = st.data_editor(
            st.session_state.erholungsdaten,
            num_rows="dynamic",
            use_container_width=True
        )

        if st.button("Zurück"):
            st.session_state.page_mode = "neu"
            st.rerun()


# bestehende testperson auswählen funktion die aber DeltaGenerator Problem auf streamlit aufruft
def bestehende_versuchsperson_auswählen():
    st.header("Bestehende Versuchsperson auswählen")
    person_list = read_data.load_person_data()
    person_names = read_data.get_person_list(person_list)

    selected_person = st.selectbox("Person auswählen", options=person_names)
    if selected_person:
        person_data = find_person_data_by_name(selected_person)
        st.image(person_data["picture_path"], caption=selected_person) if person_data.get("picture_path") else st.warning("Kein Bild")

        st.markdown(f"**Name:** {person_data['firstname']} {person_data['lastname']}")
        st.markdown(f"**Geburtsjahr:** {person_data['date_of_birth']}")
        st.markdown(f"**Geschlecht:** {person_data['gender']}")
        st.markdown(f"**Sportniveau:** {person_data['sportniveau']}")
        st.markdown(f"**ID:** {person_data['id']}")

        # Tests laden
        test_folder = os.path.join(os.getcwd(), "data", "tests")
        test_files = [f for f in os.listdir(test_folder) if f.startswith(person_data['id'])] if os.path.exists(test_folder) else []
        if test_files:
            test_choice = st.selectbox("Test auswählen", options=test_files)
            if test_choice:
                test_path = os.path.join(test_folder, test_choice)
                with open(test_path, "r", encoding="utf-8") as f:
                    st.text(f.read())

        if st.button("Zurück zur Startseite"):
            st.session_state.page_mode = "start"
            st.rerun()



# GESAMTE MAIN:PY DATEI DIE NOCH MIT TABS GESCHRIEBEN WURDE
import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from PIL import Image
import datetime
import read_data
from Leistung import Leistung
from Laktat import Laktat
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
    """ Speichert die Testdaten in den entsprechenden Ordnern. """
    daten_folder = os.path.join("data", person_id, "daten")
    os.makedirs(daten_folder, exist_ok=True)

    belastung_path = os.path.join(daten_folder, f"{person_id}_Test{testnummer}_Belastung.csv")
    erholung_path = os.path.join(daten_folder, f"{person_id}_Test{testnummer}_Erholung.csv")

    belastung_df.to_csv(belastung_path, index=False)
    erholung_df.to_csv(erholung_path, index=False)

    return belastung_path, erholung_path


# Aufbau der Startseite
def Startseite():
    """Startseite der App."""
    st.title("Stufentest Analyse APP")
    st.markdown("## Willkommen zur Stufentest Analyse APP")

    if st.button("Neue Versuchsperson anlegen"):
        st.session_state.page_mode = "neu"
    if st.button("Bestehende Versuchsperson auswählen"):
        st.session_state.page_mode = "bestehend"

# Neue Versuchsperson anlegen
def neue_Versuchsperson_anlegen():
    """Ermöglicht die Erstellung einer neuen Versuchsperson, durch Eingabe von persönlichen Daten und optionalen Testdaten."""
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
    if st.button("Zurück zur Startseite"):
        st.session_state.page_mode = "start"
        st.rerun()


def csv_hochladen():
    """Ermöglicht das Hochladen von CSV-Dateien für Belastungs- und Erholungsdaten."""
    st.header("CSV-Testdaten hochladen")
    st.markdown("**Belastungsdaten hochladen**")
    belastung_datei = st.file_uploader("Belastung CSV", key="belastung")

    st.markdown("**Erholungsdaten hochladen (optional)**")
    erholung_datei = st.file_uploader("Erholung CSV", key="erholung")

    if st.button("Speichern und zurück zur Startseite"):
        testnummer = 1
        person_id = st.session_state.pending_user_data["id"]

        person_folder = os.path.join("data", person_id)
        os.makedirs(person_folder, exist_ok=True)

        # Bildpfad ggf. aktualisieren
        if st.session_state.pending_user_data["picture_path"]:
            alt_pfad = st.session_state.pending_user_data["picture_path"]
            image_folder = os.path.join(person_folder, "images")
            os.makedirs(image_folder, exist_ok=True)
            neues_bild = os.path.join(image_folder, f"{person_id}.jpg")
            if not os.path.exists(neues_bild):
                os.replace(alt_pfad, neues_bild)
            st.session_state.pending_user_data["picture_path"] = neues_bild

        # JSON-Datei speichern
        person_path = os.path.join(person_folder, f"{person_id}.json")
        with open(person_path, "w", encoding="utf-8") as f:
            json.dump(st.session_state.pending_user_data, f, indent=4)

        df_belastung = pd.read_csv(belastung_datei) if belastung_datei else pd.DataFrame()
        df_erholung = pd.read_csv(erholung_datei) if erholung_datei else pd.DataFrame()

        daten_folder = os.path.join(person_folder, "daten")
        os.makedirs(daten_folder, exist_ok=True)
        belastung_path = os.path.join(daten_folder, f"{person_id}_Test{testnummer}_Belastung.csv")
        erholung_path = os.path.join(daten_folder, f"{person_id}_Test{testnummer}_Erholung.csv")

        df_belastung.to_csv(belastung_path, index=False)
        df_erholung.to_csv(erholung_path, index=False)

        st.success("Alle Daten gespeichert!")
        st.session_state.page_mode = "start"
        st.rerun()

    if st.button("Zurück"):
        st.session_state.page_mode = "neu"
        st.rerun()


# manuelle Eingabe der gemessenen Werte in Tabellen
def manuelle_eingabe():
    """Ermöglicht die manuelle Eingabe von Belastungs- und Erholungsdaten."""
    st.header("Manuelle Eingabe der Testdaten")
    st.markdown("### Belastungsdaten")
    
    stufendauer = st.selectbox("Dauer einer Stufe (Minuten)", options=[1, 2, 3, 4, 5], key="stufendauer")
    zeit_minuten_belastung = [(i + 1) * stufendauer for i in range(8)]

    belastung_df = st.data_editor(pd.DataFrame({
        "Zeit (min)": zeit_minuten_belastung,
        "Leistung (Watt)": ["" for _ in range(8)],
        "Herzfrequenz": ["" for _ in range(8)],
        "Laktat": ["" for _ in range(8)],
    }), num_rows="dynamic")

    st.markdown("### Erholungsdaten")
    erholungsintervall = st.selectbox("Messintervall (Minuten)", options=[1, 2, 3, 5], key="erholungsintervall")

    zeit_minuten_erholung = [(i + 1) * erholungsintervall for i in range(5)]

    erholung_df = st.data_editor(pd.DataFrame({
        "Zeit (min)": zeit_minuten_erholung,
        "Herzfrequenz": ["" for _ in range(5)],
        "Laktat": ["" for _ in range(5)],
    }), num_rows="dynamic")

    if st.button("Speichern und zurück zur Startseite"):
        person_id = st.session_state.pending_user_data["id"]
        testnummer = 1

    person_folder = os.path.join("data", person_id)
    os.makedirs(person_folder, exist_ok=True)

    # Bildpfad ggf. aktualisieren
    if st.session_state.pending_user_data["picture_path"]:
        alt_pfad = st.session_state.pending_user_data["picture_path"]
        image_folder = os.path.join(person_folder, "images")
        os.makedirs(image_folder, exist_ok=True)
        neues_bild = os.path.join(image_folder, f"{person_id}.jpg")
        if not os.path.exists(neues_bild):
            os.replace(alt_pfad, neues_bild)
        st.session_state.pending_user_data["picture_path"] = neues_bild

        # Speichern Personendaten
        person_path = os.path.join(person_folder, f"{person_id}.json")
        with open(person_path, "w", encoding="utf-8") as f:
            json.dump(st.session_state.pending_user_data, f, indent=4)

        # Testdaten speichern
        daten_folder = os.path.join(person_folder, "daten")
        os.makedirs(daten_folder, exist_ok=True)
        belastung_path = os.path.join(daten_folder, f"{person_id}_Test{testnummer}_Belastung.csv")
        erholung_path = os.path.join(daten_folder, f"{person_id}_Test{testnummer}_Erholung.csv")

        belastung_df.to_csv(belastung_path, index=False)
        erholung_df.to_csv(erholung_path, index=False)

        st.success("Testdaten gespeichert!")
        st.session_state.page_mode = "start"
        st.rerun()


    if st.button("Zurück"):
        st.session_state.page_mode = "neu"
        st.rerun()



# Bestehende Versuchsperson auswählen

def bestehende_versuchsperson_auswählen():
    """Zeigt eine Liste aller vorhandenen Versuchspersonen an und ermöglicht die Auswahl einer Person."""
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

        # Bild anzeigen (erstes Bild im Ordner nehmen, z. B. JPG oder PNG)
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

        # JSON-Daten laden
        with open(json_path, "r", encoding="utf-8") as f:
            person_data = json.load(f)
        st.session_state.current_user = person_id_input

        st.markdown(f"**Name:** {person_data.get('firstname', '')} {person_data.get('lastname', '')}")
        st.markdown(f"**Geburtsjahr:** {person_data.get('date_of_birth', 'Unbekannt')}")
        st.markdown(f"**Geschlecht:** {person_data.get('gender', 'Unbekannt')}")
        st.markdown(f"**Sportniveau:** {person_data.get('sportniveau', 'Unbekannt')}")
        st.markdown(f"**ID:** {person_data.get('id', 'Unbekannt')}")

        # Testdateien anzeigen
        if os.path.exists(daten_folder):
            test_files = sorted([f for f in os.listdir(daten_folder) if f.endswith(".csv")])
            if test_files:
                selected_test = st.selectbox("Test auswählen", options=test_files)
                st.info(f"Ausgewählter Test: {selected_test}")
            else:
                st.info("Keine Testdaten vorhanden.")
        else:
            st.info("Kein Testordner vorhanden.")

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

# Leistungsdaten Tab
with leistungs_tab:
    st.header("Leistungsdatenanalyse")

    if st.session_state.current_user:
        person_id = st.session_state.current_user
        daten_folder = os.path.join("data", person_id, "daten")

        # Suche nach der ersten Belastungsdatei
        try:
            belastung_file = next(f for f in os.listdir(daten_folder) if "Belastung" in f and f.endswith(".csv"))
            pfad_zur_belastung = os.path.join(daten_folder, belastung_file)

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

        try:
            # Suche nach Belastungsdatei mit Laktatwerten
            laktat_file = next(
                f for f in os.listdir(daten_folder)
                if "Belastung" in f and f.endswith(".csv")
            )
            laktat_path = os.path.join(daten_folder, laktat_file)

            # CSV-Datei laden
            df = Laktat.csv_Datei_laden(laktat_path)

            if "Laktat (mmol/l)" in df.columns and not df["Laktat (mmol/l)"].isnull().all():
                # Analyse nur, wenn Laktatdaten vorhanden sind
                Lt1, Lt2 = Laktat.schwellenwerte_berechnen(df)
                df = Laktat.laktatzonen_berechnen(df, Lt1, Lt2)
                fig = Laktat.plot_erstellen(df, Lt1, Lt2)
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

                
            else:
                st.warning("Keine Laktatdaten in der Datei gefunden.")

        except StopIteration:
            st.warning("Keine geeignete Belastungsdatei mit Laktatwerten gefunden.")

    else:
        st.info("Bitte zuerst eine Versuchsperson auf der Startseite auswählen.")




# GESAAMTE APP MIT SIDEBAR NAVIGATION; HIER IST ABER NOCH KEIN DATEN EDITIEREN BUTTON DABEI
import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from PIL import Image
import datetime
import read_data
from Leistung import Leistung
from Laktat import Laktat

# Streamlit session states
if "page_mode" not in st.session_state:
    st.session_state.page_mode = "start"
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "pending_user_data" not in st.session_state:
    st.session_state.pending_user_data = None

# Sidebar-Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("", ["Startseite", "Leistungsdaten", "Laktattest"])

# Hilfsfunktion zum Speichern von Testdaten
def Testdaten_speichern(person_id, belastung_df, erholung_df, testnummer):
    """ Speichert die Testdaten für eine Versuchsperson in den entsprechenden Ordnern. """
    daten_folder = os.path.join("data", person_id, "daten")
    os.makedirs(daten_folder, exist_ok=True)
    belastung_path = os.path.join(daten_folder, f"{person_id}_Test{testnummer}_Belastung.csv")
    erholung_path = os.path.join(daten_folder, f"{person_id}_Test{testnummer}_Erholung.csv")
    belastung_df.to_csv(belastung_path, index=False)
    erholung_df.to_csv(erholung_path, index=False)
    return belastung_path, erholung_path

# Startseite-Funktionen
def Startseite():
    """ Startseite der App, wo Benutzer neue Versuchspersonen anlegen oder bestehende auswählen können. """
    st.title("Stufentest Analyse APP")
    st.markdown("## Willkommen zur Stufentest Analyse APP")
    if st.button("Neue Versuchsperson anlegen"):
        st.session_state.page_mode = "neu"
    if st.button("Bestehende Versuchsperson auswählen"):
        st.session_state.page_mode = "bestehend"

def neue_Versuchsperson_anlegen():
    """ Erlaubt es Benutzern, eine neue Versuchsperson anzulegen und Testdaten hochzuladen. """
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
    
    if st.button("Zurück zur Startseite"):
        st.session_state.page_mode = "start"
        st.rerun()

def csv_hochladen():
    """ Ermöglicht das Hochladen von CSV-Dateien für Belastungs- und Erholungsdaten. """
    st.header("CSV-Testdaten hochladen")
    st.markdown("**Belastungsdaten hochladen**")
    belastung_datei = st.file_uploader("Belastung CSV", key="belastung")
    
    st.markdown("**Erholungsdaten hochladen (optional)**")
    erholung_datei = st.file_uploader("Erholung CSV", key="erholung")
    
    if st.button("Speichern und zurück zur Startseite"):
        testnummer = 1
        person_id = st.session_state.pending_user_data["id"]
        person_folder = os.path.join("data", person_id)
        os.makedirs(person_folder, exist_ok=True)
        
        if st.session_state.pending_user_data["picture_path"]:
            alt_pfad = st.session_state.pending_user_data["picture_path"]
            image_folder = os.path.join(person_folder, "images")
            os.makedirs(image_folder, exist_ok=True)
            neues_bild = os.path.join(image_folder, f"{person_id}.jpg")
            if not os.path.exists(neues_bild):
                os.replace(alt_pfad, neues_bild)
            st.session_state.pending_user_data["picture_path"] = neues_bild
        
        person_path = os.path.join(person_folder, f"{person_id}.json")
        
        with open(person_path, "w", encoding="utf-8") as f:
            json.dump(st.session_state.pending_user_data, f, indent=4)
        
        df_belastung = pd.read_csv(belastung_datei) if belastung_datei else pd.DataFrame()
        df_erholung = pd.read_csv(erholung_datei) if erholung_datei else pd.DataFrame()
        
        daten_folder = os.path.join(person_folder, "daten")
        os.makedirs(daten_folder, exist_ok=True)
        
        belastung_path = os.path.join(daten_folder, f"{person_id}_Test{testnummer}_Belastung.csv")
        erholung_path = os.path.join(daten_folder, f"{person_id}_Test{testnummer}_Erholung.csv")
        
        df_belastung.to_csv(belastung_path, index=False)
        df_erholung.to_csv(erholung_path, index=False)
        
        st.success("Alle Daten gespeichert!")
        st.session_state.page_mode = "start"
        st.rerun()
    
    if st.button("Zurück"):
        st.session_state.page_mode = "neu"
        st.rerun()

def manuelle_eingabe():
    """ Ermöglicht die manuelle Eingabe von Testdaten für Belastung und Erholung. """
    st.header("Manuelle Eingabe der Testdaten")
    st.markdown("### Belastungsdaten")
    
    stufendauer = st.selectbox("Dauer einer Stufe (Minuten)", [1, 2, 3, 4, 5], key="stufendauer")
    zeit_minuten_belastung = [(i + 1) * stufendauer for i in range(8)]
    belastung_df = st.data_editor(pd.DataFrame({
        "Zeit (min)": zeit_minuten_belastung,
        "Leistung (Watt)": ["" for _ in range(8)],
        "Herzfrequenz": ["" for _ in range(8)],
        "Laktat": ["" for _ in range(8)],
    }), num_rows="dynamic")
    
    st.markdown("### Erholungsdaten")
    erholungsintervall = st.selectbox("Messintervall (Minuten)", [1, 2, 3, 5], key="erholungsintervall")
    zeit_minuten_erholung = [(i + 1) * erholungsintervall for i in range(5)]
    erholung_df = st.data_editor(pd.DataFrame({
        "Zeit (min)": zeit_minuten_erholung,
        "Herzfrequenz": ["" for _ in range(5)],
        "Laktat": ["" for _ in range(5)],
    }), num_rows="dynamic")
    
    if st.button("Speichern und zurück zur Startseite"):
        person_id = st.session_state.pending_user_data["id"]
        testnummer = 1
        person_folder = os.path.join("data", person_id)
        os.makedirs(person_folder, exist_ok=True)
        
        if st.session_state.pending_user_data["picture_path"]:
            alt_pfad = st.session_state.pending_user_data["picture_path"]
            image_folder = os.path.join(person_folder, "images")
            os.makedirs(image_folder, exist_ok=True)
            neues_bild = os.path.join(image_folder, f"{person_id}.jpg")
            if not os.path.exists(neues_bild):
                os.replace(alt_pfad, neues_bild)
            st.session_state.pending_user_data["picture_path"] = neues_bild
        
        person_path = os.path.join(person_folder, f"{person_id}.json")
        
        with open(person_path, "w", encoding="utf-8") as f:
            json.dump(st.session_state.pending_user_data, f, indent=4)
        daten_folder = os.path.join(person_folder, "daten")
        os.makedirs(daten_folder, exist_ok=True)
        belastung_df.to_csv(os.path.join(daten_folder, f"{person_id}_Test{testnummer}_Belastung.csv"), index=False)
        erholung_df.to_csv(os.path.join(daten_folder, f"{person_id}_Test{testnummer}_Erholung.csv"), index=False)
        st.success("Testdaten gespeichert!")
        st.session_state.page_mode = "start"
        st.rerun()
    
    if st.button("Zurück"):
        st.session_state.page_mode = "neu"
        st.rerun()

def bestehende_versuchsperson_auswählen():
    """ Ermöglicht die Auswahl und Anzeige von bestehenden Versuchspersonen. """
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
        
        with open(json_path, "r", encoding="utf-8") as f:
            person_data = json.load(f)
        
        st.session_state.current_user = person_id_input
        st.markdown(f"**Name:** {person_data.get('firstname', '')} {person_data.get('lastname', '')}")
        st.markdown(f"**Geburtsjahr:** {person_data.get('date_of_birth', 'Unbekannt')}")
        st.markdown(f"**Geschlecht:** {person_data.get('gender', 'Unbekannt')}")
        st.markdown(f"**Sportniveau:** {person_data.get('sportniveau', 'Unbekannt')}")
        st.markdown(f"**ID:** {person_data.get('id', 'Unbekannt')}")
        
        if os.path.exists(daten_folder):
            test_files = sorted([f for f in os.listdir(daten_folder) if f.endswith(".csv")])
            if test_files:
                selected_test = st.selectbox("Test auswählen", options=test_files)
                st.info(f"Ausgewählter Test: {selected_test}")
            else:
                st.info("Keine Testdaten vorhanden.")
        else:
            st.info("Kein Testordner vorhanden.")
    
    if st.button("Zurück zur Startseite"):
        st.session_state.page_mode = "start"
        st.rerun()

# Inhalte entsprechend Sidebar-Auswahl anzeigen
if page == "Startseite":
    if st.session_state.page_mode == "start":
        Startseite()
    elif st.session_state.page_mode == "neu":
        neue_Versuchsperson_anlegen()
    elif st.session_state.page_mode == "csv_upload":
        csv_hochladen()
    elif st.session_state.page_mode == "manuelle_eingabe":
        manuelle_eingabe()
    elif st.session_state.page_mode == "bestehend":
        bestehende_versuchsperson_auswählen()

elif page == "Leistungsdaten":
    st.header("Leistungsdatenanalyse")
    
    if st.session_state.current_user:
        person_id = st.session_state.current_user
        daten_folder = os.path.join("data", person_id, "daten")
        
        try:
            belastung_file = next(f for f in os.listdir(daten_folder) if "Belastung" in f and f.endswith(".csv"))
            pfad_zur_belastung = os.path.join(daten_folder, belastung_file)
            analyse = Leistung(pfad_zur_belastung)
            st.subheader("Herzfrequenz- und Leistungsdiagramm mit Zonen")
            st.plotly_chart(analyse.plot_herzfrequenz(mode="zonen"), use_container_width=True)
            st.subheader("Herzfrequenz- und Leistungsdiagramm mit Stufen")
            st.plotly_chart(analyse.plot_herzfrequenz(mode="stufen"), use_container_width=True)
            werte = analyse.Werte_berechnen()
            col1, col2 = st.columns(2)
           
            with col1:
                st.metric("Durchschnittliche Leistung", f"{werte['mean_power']:.1f} W")
                st.metric("Maximale Leistung", f"{werte['max_power']} W")
            st.subheader("Zeit in Herzfrequenz-Zonen")
            st.dataframe(werte["zeit_pro_zone"])
            st.subheader("Durchschnittswerte pro Zone")
            df_zone_summary = pd.concat([werte["hf_pro_zone"], werte["leistung_pro_zone"]], axis=1)
            df_zone_summary.columns = ["Durchschnittliche Herzfrequenz (bpm)", "Durchschnittliche Leistung (Watt)"]
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

elif page == "Laktattest":
    st.header("Laktattest Analyse")
    
    if st.session_state.current_user:
        person_id = st.session_state.current_user
        daten_folder = os.path.join("data", person_id, "daten")
        
        try:
            laktat_file = next(f for f in os.listdir(daten_folder) if "Belastung" in f and f.endswith(".csv"))
            laktat_path = os.path.join(daten_folder, laktat_file)
            df = Laktat.csv_Datei_laden(laktat_path)
            
            if "Laktat (mmol/l)" in df.columns and not df["Laktat (mmol/l)"].isnull().all():
                Lt1, Lt2 = Laktat.schwellenwerte_berechnen(df)
                df = Laktat.laktatzonen_berechnen(df, Lt1, Lt2)
                fig = Laktat.plot_erstellen(df, Lt1, Lt2)
                st.plotly_chart(fig, use_container_width=True)
                st.subheader("Laktatschwellen")
                st.metric("LT1", f"{Lt1:.0f} Watt")
                st.metric("LT2", f"{Lt2:.0f} Watt")
                st.subheader("Laktatdaten mit Zonen")
                st.dataframe(df[["Leistung (Watt)", "Laktat (mmol/l)", "Herzfrequenz (bpm)", "Laktatzone"]])
                st.subheader("Empfohlene Trainingsherzfrequenzbereiche")
                hf_fig = Laktat.Trainingsbereiche_HF_plot(df, Lt1, Lt2)
                st.plotly_chart(hf_fig, use_container_width=True)
            
            else:
                st.warning("Keine Laktatdaten in der Datei gefunden.")
       
        except StopIteration:
            st.warning("Keine geeignete Belastungsdatei mit Laktatwerten gefunden.")
   
    else:
        st.info("Bitte zuerst eine Versuchsperson auf der Startseite auswählen.")