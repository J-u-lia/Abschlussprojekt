import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import re
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
    #person_dict = read_data.load_person_data()
    neue_id = generiere_neue_id()


    col1, col2 = st.columns(2)
    with col1:
        vorname = st.text_input("Vorname")
        geschlecht = st.selectbox("Geschlecht", ["Männlich", "Weiblich"])
        sportniveau = st.selectbox("Sportniveau", ["Einsteiger", "Hobbysportler", "Amateur", "Leistungssportler", "Profi"])
        st.text_input("ID", value=neue_id, disabled=True)

    with col2:
        nachname = st.text_input("Nachname")
        geburtsjahr = st.selectbox("Geburtsjahr", list(reversed(range(1950, datetime.date.today().year + 1))))
        
        testdatum = st.date_input("Testdatum", value=datetime.date.today())
        testdauer = st.number_input("Testdauer (Minuten)", min_value=1, max_value=180, value=30) 

        bild = st.file_uploader("Bild hochladen", type=["jpg", "jpeg", "png"])

    st.markdown("### Testdaten hinzufügen")
    testdatum = st.date_input("Testdatum", datetime.date.today(), key="testdatum")
    testdauer = st.number_input("Testdauer (Minuten)", min_value=1, key="testdauer")

    
    col_csv, col_manuell = st.columns(2)
    with col_csv:
        #testdatum = st.date_input("Testdatum", datetime.date.today())

        if st.button("CSV-Datei hochladen"):
            st.session_state.pending_user_data = {
                "id": neue_id, "firstname": vorname, "lastname": nachname,
                "date_of_birth": str(geburtsjahr), "gender": geschlecht,
                "sportniveau": sportniveau, "picture_path": None,
                "Testdatum": str(testdatum), "Testdauer": testdauer
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
        #testdauer = st.number_input("Testdauer (Minuten)", min_value=1)

        if st.button("Daten eintragen"):
            st.session_state.pending_user_data = {
                "id": neue_id, "firstname": vorname, "lastname": nachname,
                "date_of_birth": str(geburtsjahr), "gender": geschlecht,
                "sportniveau": sportniveau, "picture_path": None,
                "Testdatum": str(testdatum), "Testdauer": testdauer
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
        person_id = st.session_state.pending_user_data["id"]
        testnummer = ermittle_nächste_testnummer(person_id)

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
        "Leistung (Watt)": ["" for _ in range(5)],
        "Herzfrequenz": ["" for _ in range(5)],
        "Laktat": ["" for _ in range(5)],
    }), num_rows="dynamic")

    if st.button("Speichern und zurück zur Startseite"):
        person_id = st.session_state.pending_user_data["id"]
        testnummer = ermittle_nächste_testnummer(person_id)

        # Spaltennamen anpassen, da sonst bei der entstandenen csv Datei die Spaltennamen nicht den Erwartungen entsprechen
        belastung_df.rename(columns={
            "Herzfrequenz": "Herzfrequenz (bpm)",
            "Laktat": "Laktat (mmol/l)"
        }, inplace=True)

        erholung_df.rename(columns={
            "Herzfrequenz": "Herzfrequenz (bpm)",
            "Laktat": "Laktat (mmol/l)"
        }, inplace=True)

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
    """Zeigt eine Liste aller vorhandenen Versuchspersonen an, ermöglicht Auswahl und Bearbeiten."""
    st.header("Versuchsperson anzeigen oder bearbeiten")

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

        if not st.session_state.edit_mode:
            # Anzeigen der Personendaten
            st.markdown(f"**Name:** {person_data.get('firstname', '')} {person_data.get('lastname', '')}")
            st.markdown(f"**Geburtsjahr:** {person_data.get('date_of_birth', 'Unbekannt')}")
            st.markdown(f"**Geschlecht:** {person_data.get('gender', 'Unbekannt')}")
            st.markdown(f"**Sportniveau:** {person_data.get('sportniveau', 'Unbekannt')}")
            st.markdown(f"**ID:** {person_data.get('id', 'Unbekannt')}")

            if st.button("Daten editieren"):
                st.session_state.edit_mode = True
                st.rerun()
        else:
            # bearbeiten der Personendaten
            st.subheader("Personendaten bearbeiten")
            person_data["firstname"] = st.text_input("Vorname", value=person_data.get("firstname", ""))
            person_data["lastname"] = st.text_input("Nachname", value=person_data.get("lastname", ""))
            person_data["date_of_birth"] = st.selectbox("Geburtsjahr", options=list(reversed(range(1950, datetime.date.today().year + 1))), index=0 if not person_data.get("date_of_birth") else list(reversed(range(1950, datetime.date.today().year + 1))).index(int(person_data["date_of_birth"])))
            person_data["gender"] = st.selectbox("Geschlecht", ["Männlich", "Weiblich"], index=0 if person_data.get("gender") == "Männlich" else 1)
            person_data["sportniveau"] = st.selectbox("Sportniveau", ["Einsteiger", "Hobbysportler", "Amateur", "Leistungssportler", "Profi"], index=["Einsteiger", "Hobbysportler", "Amateur", "Leistungssportler", "Profi"].index(person_data.get("sportniveau", "Einsteiger")))

            if st.button("Änderungen speichern"):
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

        selected_test = st.session_state.get("selected_test_csv")
        if selected_test:
            laktat_path = os.path.join(daten_folder, selected_test)

            try:
                # Suche nach Belastungsdatei mit Laktatwerten
                #laktat_file = next(
                #    f for f in os.listdir(daten_folder)
                #    if "Belastung" in f and f.endswith(".csv")
                #)
                #laktat_path = os.path.join(daten_folder, laktat_file)

                # CSV-Datei laden
                df = Laktat.csv_Datei_laden(laktat_path)

                if "Laktat (mmol/l)" in df.columns and not df["Laktat (mmol/l)"].isnull().all():
                    # Analyse nur, wenn Laktatdaten vorhanden sind
                    Lt1, Lt2 = Laktat.schwellenwerte_berechnen(df)
                    df = Laktat.laktatzonen_berechnen(df, Lt1, Lt2)
                    
                    # Wähle richtigen Plot-Typ basierend auf dem Dateinamen
                    if "Belastung" in selected_test:
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

                    elif "Erholung" in selected_test:
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
