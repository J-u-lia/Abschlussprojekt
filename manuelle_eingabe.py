import streamlit as st
import pandas as pd

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
