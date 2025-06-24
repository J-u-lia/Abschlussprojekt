import json
import os

# Ordner mit allen Personen-Daten
pfad_route = os.getcwd()
speicherpfad = os.path.join(pfad_route, "Data")

def load_person_data():
    """
    Diese Funktion lädt alle JSON-Dateien aus dem Data-Ordner und gibt eine Liste mit Personendaten zurück.
    """
    persons = {}
    if not os.path.exists(speicherpfad):
        return persons  # falls Ordner nicht existiert, leere Liste zurück

    for filename in os.listdir(speicherpfad):
        if filename.endswith(".json"):
            filepath = os.path.join(speicherpfad, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    person = json.load(f)
                    if isinstance(person, dict) and "id" in person:
                        persons[person["id"]] = person
            except Exception as e:
                print(f"Fehler bei Datei {filename}: {e}")
    return persons

def get_person_list(person_data):
    """Gibt eine Liste der Personennamen im Format 'Vorname, Nachname' zurück."""
    person_name_list = []
    for person in person_data.values():
        person_name_list.append(f"{person['firstname']}, {person['lastname']}")
    return person_name_list

def find_person_data_by_name(suchstring):
    """Findet eine Person in den geladenen Daten anhand von 'Vorname, Nachname'."""
    if suchstring == "None" or not suchstring:
        return {}

    person_data = load_person_data()
    two_names = suchstring.split(", ")
    if len(two_names) != 2:
        return {}

    vorname, nachname = two_names

    for person in person_data.values():
        if person.get("firstname") == vorname and person.get("lastname") == nachname:
            return person
    return {}

# Zum Testen (kann weg, wenn du möchtest)
if __name__ == "__main__":
    persons = load_person_data()
    names = get_person_list(persons)
    print("Gefundene Personen:", names)
    test_person = find_person_data_by_name("Julian, Huber")
    print("Daten für Julian Huber:", test_person)