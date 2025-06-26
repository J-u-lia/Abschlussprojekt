import streamlit as st
import pandas as pd
import numpy as np
import os
from PIL import Image
from Leistung import Leistung
from Laktat import Laktat
from test_erfassung import lade_json
from csv_hochladen import csv_hochladen
from manuelle_eingabe import manuelle_eingabe
from bestehende_versuchsperson_anlegen import bestehende_versuchsperson_auswählen
from neue_Versuchsperson_anlegen import neue_Versuchsperson_anlegen


# Streamlit Aufbau der session_states
# Initialisierung aller benötigten Session-State-Variablen
if "page_mode" not in st.session_state:
    st.session_state.page_mode = "start"
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "pending_user_data" not in st.session_state:
    st.session_state.pending_user_data = None
if "input_art_auswahl" not in st.session_state:
    st.session_state.input_art_auswahl = None
if "aktueller_test" not in st.session_state:
    st.session_state.aktueller_test = None
if "test_liste" not in st.session_state:
    st.session_state.test_liste = []
if "show_testdaten" not in st.session_state:
    st.session_state.show_testdaten = False
if "show_test_löschen" not in st.session_state:
    st.session_state.show_test_löschen = False
if "person_reset" not in st.session_state:
    st.session_state.person_reset = True





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

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Neue Versuchsperson anlegen"):
            st.session_state.page_mode = "neu"
            st.session_state.neue_person_anlegen = True

    with col2:
        if st.button("Bestehende Versuchsperson auswählen"):
            st.session_state.page_mode = "bestehend"


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
            with col2:
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

        # Lade alle CSV-Dateien im Datenordner
        all_csv_files = [f for f in os.listdir(daten_folder) if f.endswith(".csv")]

        if not all_csv_files:
            st.warning("Keine CSV-Dateien im Datenordner gefunden.")
            st.stop()

        # Dropdown-Menü zur Auswahl der CSV-Datei
        selected_file = st.selectbox(
            "Wähle einen Laktattest (Belastung oder Erholung)",
            options=all_csv_files
        )

        # Absoluter Pfad zur ausgewählten Datei
        laktat_path = os.path.join(daten_folder, selected_file)

        try:
            # CSV-Datei laden
            df = Laktat.csv_Datei_laden(laktat_path)

            if "Laktat (mmol/l)" in df.columns and not df["Laktat (mmol/l)"].isnull().all():
                # Analyse nur, wenn Laktatdaten vorhanden sind
                Lt1, Lt2 = Laktat.schwellenwerte_berechnen(df)
                df = Laktat.laktatzonen_berechnen(df, Lt1, Lt2)

                if "belastung" in selected_file:
                    fig = Laktat.Belastung_plot_erstellen(df, Lt1, Lt2)

                    st.plotly_chart(fig, use_container_width=True)

                    st.subheader("Laktatschwellen")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("LT1", f"{Lt1:.0f} Watt")
                    with col2:
                        st.metric("LT2", f"{Lt2:.0f} Watt")

                    st.subheader("Laktatdaten mit Laktatzonen")
                    st.dataframe(df[["Leistung (Watt)", "Laktat (mmol/l)", "Herzfrequenz (bpm)", "Laktatzone"]])

                    st.subheader("Empfohlene Trainingsherzfrequenzbereiche")
                    hf_fig = Laktat.Trainingsbereiche_HF_plot(df, Lt1, Lt2)
                    st.plotly_chart(hf_fig, use_container_width=True)

                elif "erholung" in selected_file:
                    fig = Laktat.Erholung_plot_erstellen(df, Lt1, Lt2)
                    st.plotly_chart(fig, use_container_width=True)

                    abbau_rate = Laktat.Laktatabbau(df)
                    if abbau_rate is not None:
                        st.metric("durchschnittlicher Laktatabbau", f"{abbau_rate:.2f} mmol/l pro min")
                    else:
                        st.warning("Laktatabbau konnte nicht berechnet werden.")

                else:
                    st.info("Dateiname enthält weder 'belastung' noch 'erholung'. Es wird Standard-Laktat-Plot verwendet.")
                    fig = Laktat.Belastung_plot_erstellen(df, Lt1, Lt2)
                    st.plotly_chart(fig, use_container_width=True)

            else:
                st.warning("Keine gültigen Laktatdaten in der Datei gefunden.")

        except Exception as e:
            st.error(f"Fehler beim Verarbeiten der Datei: {e}")

    else:
        st.info("Bitte zuerst eine Versuchsperson auf der Startseite auswählen.")
