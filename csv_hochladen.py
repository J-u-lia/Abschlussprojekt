import streamlit as st
import pandas as pd

def csv_hochladen():
    """CSV-Dateien für Belastung/Erholung hochladen und speichern."""
    st.header("CSV-Testdaten hochladen")

    if "active_test_index" not in st.session_state:
        st.session_state.active_test_index = 0

    idx = st.session_state.active_test_index
    st.markdown("**Belastungsdaten hochladen**")
    belastung_datei = st.file_uploader("Belastung CSV", key=f"belastung_{idx}")

    st.markdown("**Erholungsdaten hochladen (optional)**")
    erholung_datei = st.file_uploader("Erholung CSV", key=f"erholung_{idx}")

    if st.button("Speichern und zurück"):
        if belastung_datei:
            df_belastung = pd.read_csv(belastung_datei)
            st.session_state.test_liste[idx]["Belastung"] = df_belastung
            st.session_state.test_liste[idx]["belastung_file"] = belastung_datei

        if erholung_datei:
            df_erholung = pd.read_csv(erholung_datei)
            st.session_state.test_liste[idx]["Erholung"] = df_erholung
            st.session_state.test_liste[idx]["erholung_file"] = erholung_datei

        st.session_state.test_liste[idx]["InputArt"] = "csv"

        if idx + 1 < len(st.session_state.test_liste):
            st.session_state.active_test_index += 1
        else:
            st.session_state.page_mode = "neu"
        st.rerun()

    if st.button("Zurück"):
        st.session_state.page_mode = "neu"
        st.rerun()
