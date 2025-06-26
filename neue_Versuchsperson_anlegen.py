import streamlit as st
import pandas as pd
from automatische_id_generieren import generiere_neue_id
import datetime
import json
import os
import copy

def neue_Versuchsperson_anlegen():
    """Diese Funktion ermöglicht die manuelle Eingabe von Versuchspersonen und deren Testdaten. Es wird eine neue ID generiert und die Daten werden in einem JSON-Format gespeichert.
    Eingabewerte: Keine
    Rückgabewerte: Keine
    """
    # Testliste zurücksetzen, wenn eine neue Person angelegt wird
    # Testliste immer zurücksetzen beim Start der Funktion
    if st.session_state.get("neue_person_anlegen", False):
        st.session_state.test_liste = []
        st.session_state.input_art_auswahl = None
        st.session_state.neue_person_anlegen = False  # zurücksetzen für spätere Eingaben



    
    st.header("Neue Versuchsperson anlegen")
    neue_id = generiere_neue_id()

    # Grunddaten zum eingeben
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

    # bildet ein graues Kästchen in dem Testdatum, Dauer und zwei Buttons sind
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
            st.session_state.test_liste.append(test)
            st.session_state.input_art_auswahl = None
            st.success("Manueller Test gespeichert!")


    # gespeicherte Tests sollen angezeigt werden
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

    # Button für Versuchsperson speichern
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
                f"test_{i+1:03}": test for i, test in enumerate(st.session_state.test_liste)
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

        # Testdaten speichern – alle in einem Ordner der die ID als Namen hat
        for i, test in enumerate(st.session_state.test_liste, start=1):
            test_id = f"test_{i:03}"
            test["id"] = test_id  # Optional: konsistente ID im Testobjekt


            if test["InputArt"] == "manuell":
                belastung_df = pd.DataFrame(test["Belastung"])
                erholung_df = pd.DataFrame(test["Erholung"])

                belastung_csv = os.path.join(daten_dir, f"{test_id}_belastung.csv")
                erholung_csv = os.path.join(daten_dir, f"{test_id}_erholung.csv")


                belastung_df.to_csv(belastung_csv, index=False)
                erholung_df.to_csv(erholung_csv, index=False)

                test["belastung_csv_path"] = belastung_csv
                test["erholung_csv_path"] = erholung_csv

            elif test["InputArt"] == "csv":
                belastung_file = test.get("belastung_file")
                erholung_file = test.get("erholung_file")

                if belastung_file:
                    belastung_pfad = os.path.join(daten_dir, f"{test_id}_belastung.csv")
                    with open(belastung_pfad, "wb") as f:
                        f.write(belastung_file.getbuffer())
                    test["belastung_csv_path"] = belastung_pfad

                if erholung_file:
                    erholung_pfad = os.path.join(daten_dir, f"{test_id}_erholung.csv")
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



        # Dadurch kommt man automatisch zur Startseite
        st.success("Versuchsperson wurde gespeichert!")
        st.session_state.page_mode = "start"
        #st.session_state.person_reset = False
        st.rerun()


    if st.button("Zurück zur Startseite"):
        st.session_state.page_mode = "start"
        st.rerun()