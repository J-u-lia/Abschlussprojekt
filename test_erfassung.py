import streamlit as st
import datetime
import pandas as pd
import json
import os

def test_anlegen():
    if "input_art_auswahl" not in st.session_state:
        st.session_state.input_art_auswahl = None
    if "test_liste" not in st.session_state:
        st.session_state.test_liste = []

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
            st.session_state.aktueller_test = test
            st.session_state.test_liste.append(test)
            st.session_state.input_art_auswahl = None
            st.success("CSV-Test gespeichert!")

    elif st.session_state.input_art_auswahl == "manuell":
        st.markdown("#### Manuelle Testdaten eingeben")
        
        st.markdown("**Bitte als Dezimaltrennzeichen einen Punkt (`.`) verwenden, kein Komma (`,`).**")

        st.markdown("### Belastungsdaten")
        # Eingabe für Stufendauer in Minuten
        stufendauer = st.number_input("Stufendauer (min)", min_value=1, max_value=60, value=5, step=1)
        # Eingabe für Anzahl der Stufen
        anzahl_stufen = st.number_input("Anzahl der Stufen", min_value=1, max_value=50, value=8, step=1)
        # Berechne automatisch die Zeiten basierend auf der Stufendauer und Anzahl
        belastung_zeiten = [stufendauer * (i + 1) for i in range(anzahl_stufen)]
        # Tabelle die sich automatisch anpasst
        belastung_df = st.data_editor(
            pd.DataFrame({
                "Zeit (min)": belastung_zeiten,
                "Leistung (Watt)": ["" for _ in range(anzahl_stufen)],
                "Herzfrequenz (bpm)": ["" for _ in range(anzahl_stufen)],
                "Laktat (mmol/l)": ["" for _ in range(anzahl_stufen)],
            }),
            num_rows="dynamic",
            key="belastung_editor"
        )

        st.markdown("### Erholungsdaten")
        # Benutzer kann Messintervall frei wählen
        erholungsintervall = st.number_input("Messintervall (Minuten)", min_value=1, max_value=30, value=1, step=1, key="erholungsintervall")
        # Benutzer kann Anzahl der Messpunkte festlegen
        anzahl_messpunkte = st.number_input("Anzahl der Messpunkte", min_value=1, max_value=20, value=5, step=1, key="anzahl_erholungsmesspunkte")
        # Automatisch die Zeitpunkte berechnen
        erholung_zeiten = [erholungsintervall * (i + 1) for i in range(anzahl_messpunkte)]
        # DataFrame mit editierbaren Feldern
        erholung_df = st.data_editor(
            pd.DataFrame({
                "Zeit (min)": erholung_zeiten,
                "Leistung (Watt)": ["" for _ in range(anzahl_messpunkte)],
                "Herzfrequenz (bpm)": ["" for _ in range(anzahl_messpunkte)],
                "Laktat (mmol/l)": ["" for _ in range(anzahl_messpunkte)],
            }),
            num_rows="dynamic",
            key="erholung_editor"
        )

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
            st.session_state.aktueller_test = test
            st.session_state.test_liste.append(test)
            st.session_state.input_art_auswahl = None
            st.success("Manueller Test gespeichert!")

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

def ersetze_csv(label, typ, daten_folder):
    st.markdown(f"**{label} ersetzen:**")
    uploaded_file = st.file_uploader(f"Neue Datei für {typ} hochladen", type="csv", key=f"upload_{typ}")
    if uploaded_file:
        test_key = st.session_state.get("selected_test_file")
        if test_key:
            neuer_name = f"{test_key}_{typ}.csv"
            pfad = os.path.join(daten_folder, neuer_name)
            with open(pfad, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"{label} wurde ersetzt.")

def lade_csv_als_dataframe(typ, daten_folder, base_key):
    dateiname = f"{base_key}_{typ}.csv"
    pfad = os.path.join(daten_folder, dateiname)
    if os.path.exists(pfad):
        try:
            df = pd.read_csv(pfad)
            return df, dateiname
        except Exception as e:
            st.error(f"Fehler beim Laden der Datei: {e}")
            return None, None
    return None, None

def speichere_dataframe(df, daten_folder, dateiname):
    pfad = os.path.join(daten_folder, dateiname)
    try:
        df.to_csv(pfad, index=False)
        st.success(f"{dateiname} gespeichert.")
    except Exception as e:
        st.error(f"Fehler beim Speichern: {e}")


def lade_json(pfad):
    with open(pfad, "r", encoding="utf-8") as f:
        return json.load(f)

def speichere_json(daten, pfad):
    with open(pfad, "w", encoding="utf-8") as f:
        json.dump(daten, f, indent=4, ensure_ascii=False)


def clean_for_json(obj):
    """Hilfsfunktion, um JSON-kompatible Daten zu erzeugen."""
    if isinstance(obj, dict):
        return {k: clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_for_json(i) for i in obj]
    elif isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    else:
        return str(obj)  # z. B. für UploadedFile: nur Name als String

