import streamlit as st
import pandas as pd
import os
import json
import re
import copy
import datetime
from test_erfassung import test_anlegen
from test_erfassung import ersetze_csv
from test_erfassung import lade_csv_als_dataframe
from test_erfassung import speichere_dataframe
from test_erfassung import lade_json
from test_erfassung import speichere_json
from test_erfassung import clean_for_json


def bestehende_versuchsperson_auswählen():
    """Ermöglicht Anzeige und Bearbeitung einer bestehenden Versuchsperson."""

    # Session State initialisieren
    if "person_selected" not in st.session_state:
        st.session_state.person_selected = False

    # Falls current_user fehlt, person_selected zurücksetzen (z.B. nach Zurück zur Startseite)
    if st.session_state.get("person_selected", False) and not st.session_state.get("current_user"):
        st.session_state.person_selected = False


    if not st.session_state.get("person_selected", False):
        st.header("Versuchsperson suchen")
    else:
        st.header("Daten der ausgewählten Versuchsperson")

    if not st.session_state.person_selected:
        person_id_input = st.text_input("Versuchspersonen-ID eingeben (z.B. vp001):").strip().lower()

        if person_id_input:
            base_path = os.path.join("data", person_id_input)
            json_path = os.path.join(base_path, f"{person_id_input}.json")

            if not os.path.exists(json_path):
                st.error(f"Keine Daten für '{person_id_input}' gefunden.")
                return

            # Person erfolgreich gefunden → Zustand speichern
            st.session_state.current_user = person_id_input
            st.session_state.person_selected = True
            st.rerun()

        return  # Vorzeitig abbrechen, solange keine gültige Person ausgewählt wurde

    # Person wurde bereits ausgewählt – ID aus session_state verwenden
    # Person wurde bereits ausgewählt – ID aus session_state verwenden
    person_id_input = st.session_state.get("current_user")

    if not person_id_input:
        st.error("Fehler: Keine Versuchsperson ausgewählt.")
        return

    base_path = os.path.join("data", person_id_input)
    json_path = os.path.join(base_path, f"{person_id_input}.json")
    image_folder = os.path.join(base_path, "images")
    daten_folder = os.path.join(base_path, "daten")

    # Personendaten laden
    person_data = lade_json(json_path)
    stufentests = person_data.get("Stufentest", {})
    test_keys = sorted(stufentests.keys())

    # Button mit dem man zurück zur Auswahl kommt
    if st.button("Andere Person auswählen"):
        st.session_state.person_selected = False
        st.session_state.current_user = None
        st.rerun()

    # Bild anzeigen
    image_path = next((os.path.join(image_folder, f) for f in os.listdir(image_folder)
                      if f.lower().endswith((".jpg", ".jpeg", ".png"))), None) if os.path.exists(image_folder) else None
        
    col1, col2 = st.columns([1, 2])

    # Bild links anzeigen
    with col1:
        if image_path and os.path.exists(image_path):
            st.image(image_path, caption=f"Bild von {person_id_input}", use_container_width=True)
        else:
            st.warning("Kein Bild gefunden.")

    # Personendaten rechts anzeigen
    with col2:
        if not st.session_state.edit_mode:
            st.markdown(f"**Name:** {person_data.get('firstname', '')} {person_data.get('lastname', '')}")
            st.markdown(f"**Geburtsjahr:** {person_data.get('date_of_birth', 'Unbekannt')}")
            st.markdown(f"**Geschlecht:** {person_data.get('gender', 'Unbekannt')}")
            st.markdown(f"**Sportniveau:** {person_data.get('sportniveau', 'Unbekannt')}")
            st.markdown(f"**ID:** {person_data.get('id', 'Unbekannt')}")

    # Testdaten unterhalb (nicht im col2-Block!)
    if not st.session_state.edit_mode:
        st.divider()
        st.subheader("Testdaten auswählen")
        if test_keys:
            options_labels = {}
            for key in test_keys:
                test = stufentests[key]
                for typ in ["belastung", "erholung"]:
                    file_path = test.get(f"{typ}_csv_path", f"{key}_{typ}.csv")
                    filename = os.path.basename(file_path)
                    options_labels[f"{key}_{typ}"] = filename

            selected_label = st.selectbox("Datei auswählen", options=list(options_labels.values()), key="selected_test_label")
            selected_test_key = next(k for k, v in options_labels.items() if v == selected_label)
            st.session_state.selected_test_file = selected_test_key

            test_id = "_".join(selected_test_key.split("_")[:2])
            zugeordneter_test = stufentests.get(test_id, {})

            testdatum = zugeordneter_test.get("Testdatum", "Unbekannt")
            testdauer = zugeordneter_test.get("Testdauer", "Unbekannt")
            st.markdown(f"**Testdatum:** {testdatum}")
            st.markdown(f"**Testdauer:** {testdauer} Minuten")
        else:
            st.info("Keine Testdaten vorhanden.")
        
        if st.button("Daten editieren"):
            st.session_state.edit_mode = True
            st.rerun()

    # Edit-Modus: Bild hochladen und Personendaten bearbeiten
    else:
        st.markdown("### Bild hinzufügen oder ersetzen")
        neues_bild = st.file_uploader("Neues Bild hochladen (JPG, PNG)", type=["jpg", "jpeg", "png"], key="image_upload")

        if neues_bild:
            image_folder = os.path.join("data", st.session_state.current_user, "images")
            os.makedirs(image_folder, exist_ok=True)

            # Vorhandene Bilder löschen
            for f in os.listdir(image_folder):
                if f.lower().endswith((".jpg", ".jpeg", ".png")):
                    os.remove(os.path.join(image_folder, f))

            # Neues Bild speichern
            bildname = f"{person_data.get('id', 'bild')}.jpg"
            bildpfad = os.path.join(image_folder, bildname)

            with open(bildpfad, "wb") as f:
                f.write(neues_bild.getbuffer())
            st.success("Neues Bild gespeichert.")
            st.image(bildpfad, caption="Aktuelles Bild")


        st.subheader("Personendaten bearbeiten")

        col1, col2 = st.columns(2)

        with col1:
            person_data["firstname"] = st.text_input("Vorname", value=person_data.get("firstname", ""))
            jahr_liste = list(reversed(range(1950, datetime.date.today().year + 1)))
            person_data["date_of_birth"] = st.selectbox("Geburtsjahr", jahr_liste, index=jahr_liste.index(int(person_data.get("date_of_birth", datetime.date.today().year))))

        with col2:
            person_data["lastname"] = st.text_input("Nachname", value=person_data.get("lastname", ""))
            person_data["gender"] = st.selectbox("Geschlecht", ["Männlich", "Weiblich"], index=0 if person_data.get("gender") == "Männlich" else 1)

        # Eine Zeile weiter unten
        person_data["sportniveau"] = st.selectbox("Sportniveau", ["Einsteiger", "Hobbysportler", "Amateur", "Leistungssportler", "Profi"],
                                                index=["Einsteiger", "Hobbysportler", "Amateur", "Leistungssportler", "Profi"].index(person_data.get("sportniveau", "Einsteiger")))

        if st.button("Personendaten speichern"):
            st.session_state["person_data"] = person_data.copy()
            st.success("Personendaten wurden gespeichert!")
            
        # Test hinzufügen
        st.markdown("## Neuen Test hinzufügen")
        if "test_liste" not in st.session_state:
            bestehende_daten = lade_json(json_path)
            st.session_state.test_liste = list(bestehende_daten.get("Stufentest", {}).values())
        test_anlegen()

        if st.button("Tests speichern"):
            aktueller_test = st.session_state.get("aktueller_test")
            if aktueller_test:
                bestehende_daten = lade_json(json_path)
                bestehende_daten.setdefault("Stufentest", {})
                bestehende_ids = list(bestehende_daten["Stufentest"].keys())
                max_id = max([int(id.split("_")[1]) for id in bestehende_ids], default=0)
                test_id = f"test_{max_id + 1:03}"
                aktueller_test["id"] = test_id
                if aktueller_test["InputArt"] == "manuell":
                    for typ in ["belastung", "erholung"]:
                        df = pd.DataFrame(aktueller_test[typ.capitalize()])
                        path = os.path.join(daten_folder, f"{test_id}_{typ}.csv")
                        df.to_csv(path, index=False)
                        aktueller_test[f"{typ}_csv_path"] = path
                elif aktueller_test["InputArt"] == "csv":
                    for typ in ["belastung", "erholung"]:
                        file = aktueller_test.get(f"{typ}_file")
                        if file:
                            path = os.path.join(daten_folder, f"{test_id}_{typ}.csv")
                            with open(path, "wb") as f:
                                f.write(file.getbuffer())
                            aktueller_test[f"{typ}_csv_path"] = path
                for k in ["belastung_file", "erholung_file"]:
                    aktueller_test.pop(k, None)
                bestehende_daten["Stufentest"][test_id] = aktueller_test
                speichere_json(bestehende_daten, json_path)
                st.session_state.aktueller_test = None
                st.session_state.input_art_auswahl = None
                st.success(f"Test {test_id} gespeichert.")
                st.rerun()
            else:
                st.warning("Kein neuer Test zum Speichern gefunden.")

        if not st.session_state.show_testdaten:
            st.subheader("Testdaten bearbeiten")
            if st.button("Testdaten bearbeiten"):
                st.session_state.show_testdaten = True
                st.rerun()

        # Toggle für Tests löschen anzeigen
        if "show_test_löschen" not in st.session_state:
            st.session_state.show_test_löschen = False

        # Button: Tests löschen anzeigen
        if st.button("Tests löschen"):
            st.session_state.show_test_löschen = not st.session_state.show_test_löschen

        # Anzeige der Testlöschung
        if st.session_state.show_test_löschen:
            st.subheader("Test löschen")

            if not test_keys:
                st.info("Keine Tests vorhanden.")
            else:
                #test_labels = [f"{key} ({stufentests[key].get('Testdatum', 'kein Datum')})" for key in test_keys]
                ausgewählter_test_zum_löschen = st.radio("Test auswählen zum Löschen", test_keys, format_func=lambda x: f"{x} ({stufentests[x].get('Testdatum', '-')})", key="delete_test_radio")

                # Test löschen
                if st.button("Ausgewählten Test löschen"):
                    if ausgewählter_test_zum_löschen:
                        # Testdaten sichern, bevor gelöscht wird
                        zu_löschender_test = person_data["Stufentest"].get(ausgewählter_test_zum_löschen, {})

                        # Versuchspersonen-Ordner korrekt bestimmen
                        if "person_id" in st.session_state:
                            person_id = st.session_state.person_id
                        else:
                            person_id = person_id_input  # Fallback, wenn über TextInput eingegeben
                        versuchsperson_ordner = os.path.join("data", person_id)
                        daten_ordner = os.path.join(versuchsperson_ordner, "daten")

                        # CSV-Dateien zu diesem Test löschen
                        for typ in ["belastung", "erholung"]:
                            csv_name = zu_löschender_test.get(f"{typ}_csv_path")
                            if csv_name:
                                csv_pfad = os.path.join(daten_ordner, os.path.basename(csv_name))
                                st.write(f"Versuche zu löschen: {csv_pfad}")  # Debug-Ausgabe
                                if os.path.exists(csv_pfad):
                                    os.remove(csv_pfad)
                                else:
                                    st.warning(f"Datei nicht gefunden: {csv_pfad}")

                        # Test aus den JSON-Daten entfernen
                        del person_data["Stufentest"][ausgewählter_test_zum_löschen]

                        # Verbleibende Tests neu nummerieren & CSV-Dateien umbenennen
                        neue_tests = {}
                        for i, (old_key, test_data) in enumerate(sorted(person_data["Stufentest"].items()), start=1):
                            new_key = f"test_{i:03d}"

                            for typ in ["belastung", "erholung"]:
                                alter_pfad = test_data.get(f"{typ}_csv_path")
                                if alter_pfad:
                                    alter_dateiname = os.path.basename(alter_pfad)
                                    neuer_dateiname = f"{new_key}_{typ}.csv"

                                    alter_csv_pfad = os.path.join(daten_ordner, alter_dateiname)
                                    neuer_csv_pfad = os.path.join(daten_ordner, neuer_dateiname)

                                    # Datei umbenennen, falls vorhanden
                                    if os.path.exists(alter_csv_pfad):
                                        os.rename(alter_csv_pfad, neuer_csv_pfad)

                                    # Pfad im Testdaten-Eintrag aktualisieren
                                    test_data[f"{typ}_csv_path"] = neuer_dateiname

                            neue_tests[new_key] = test_data

                        # Neue Teststruktur speichern
                        person_data["Stufentest"] = neue_tests
                        speichere_json(person_data, json_path)

                        st.success(f"Test '{ausgewählter_test_zum_löschen}' wurde gelöscht und zugehörige Dateien entfernt.")
                        st.session_state.show_test_löschen = False
                        st.rerun()
                    else:
                        st.warning("Kein Test zum Löschen ausgewählt.")





        if st.session_state.show_testdaten:
            st.subheader("Testdaten bearbeiten")
            selected_test_full_key = st.session_state.get("selected_test_file")
            if not selected_test_full_key or "_" not in selected_test_full_key:
                st.warning("Kein gültiger Test ausgewählt.")
                st.stop()
            
            base_key, typ = selected_test_full_key.rsplit("_", 1)
            if base_key not in person_data.get("Stufentest", {}):
                st.warning("Test nicht gefunden.")
                st.stop()

            aktueller_test = person_data["Stufentest"][base_key]
            try:
                aktuelles_datum = datetime.date.fromisoformat(aktueller_test.get("Testdatum"))
            except:
                aktuelles_datum = datetime.date.today()

            testdatum_input = st.date_input("Testdatum", value=aktuelles_datum)
            testdauer_input = st.number_input("Testdauer (Minuten)", min_value=1, max_value=180,
                value=int(aktueller_test.get("Testdauer", 30)))

            modus = st.radio("Bearbeitungsmodus", ["CSV-Dateien editieren", "Manuelle Daten überarbeiten"])

            if modus == "CSV-Dateien editieren":
                for typ in ["belastung", "erholung"]:
                    ersetze_csv(f"{typ.capitalize()}sdatei", typ, daten_folder)
            else:
                for typ in ["belastung", "erholung"]:
                    df, fname = lade_csv_als_dataframe(typ, daten_folder, base_key)
                    if df is not None:
                        st.markdown(f"#### {typ.capitalize()}-Daten: {fname}")
                        edit_df = st.data_editor(df, num_rows="dynamic", key=f"edit_{typ}")
                        if st.button(f"{typ.capitalize()} speichern", key=f"save_{typ}"):
                            speichere_dataframe(edit_df, daten_folder, fname)
                    else:
                        st.warning(f"Keine Datei für {typ} gefunden.")

            if st.button("Änderungen speichern"):
                person_data["Stufentest"][base_key]["Testdatum"] = testdatum_input.isoformat()
                person_data["Stufentest"][base_key]["Testdauer"] = testdauer_input
                speichere_json(person_data, json_path)
                st.success("Gespeichert.")
                st.session_state.edit_mode = False
                st.session_state.show_testdaten = False
                st.rerun()



        if st.button("Zurück zu Personendaten"):
            st.session_state.edit_mode = False
            st.session_state.show_testdaten = False
            st.rerun()

    # Zurück zur Startseite
    if not st.session_state.edit_mode:
        if st.button("Zurück zur Startseite", key="back_to_home_edit_mode"):
            st.session_state.page_mode = "start"
            st.session_state.edit_mode = False
            st.session_state.current_user = None
            st.session_state.person_selected = False
            st.session_state.show_testdaten = False
            st.rerun()
