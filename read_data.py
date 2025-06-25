import json
import os

# Ordner mit allen Personen-Daten
pfad_route = os.getcwd()
speicherpfad = os.path.join(pfad_route, "Data")

def load_person_data():
    """
    Diese Funktion lädt alle JSON-Dateien aus dem Data-Ordner und gibt eine Liste mit Personendaten zurück.
    Jede Datei sollte ein JSON-Objekt mit den Schlüsseln 'id', 'firstname' und 'lastname' enthalten.
    Die Funktion gibt ein Dictionary zurück, in dem die Schlüssel die IDs der Personen sind und die Werte die entsprechenden Personendaten.
    Wenn der Ordner nicht existiert oder keine JSON-Dateien enthält, wird ein leeres Dictionary zurückgegeben.
    Die Funktion fängt auch Fehler beim Laden der Dateien ab und gibt eine Fehlermeldung aus, falls eine Datei nicht korrekt gelesen werden kann.
    Eingabe: Keine
    Rückgabe: Dictionary mit Personendaten, z.B. {'vp001': {'id': 'vp001', 'firstname': 'Julian', 'lastname': 'Huber'}, ...}
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
    """Gibt eine Liste der Personennamen im Format 'Vorname, Nachname' zurück.
    Diese Funktion nimmt ein Dictionary mit Personendaten und erstellt eine Liste von Strings,
    wobei jeder String den Vornamen und Nachnamen einer Person enthält, getrennt durch ein Komma.
    Eingabe: Dictionary mit Personendaten, z.B. {'vp001': {'id': 'vp001', 'firstname': 'Julian', 'lastname': 'Huber'}, ...}
    Rückgabe: Liste von Strings, z.B. ['Julian, Huber', 'Max, Mustermann', ...]
    """
    person_name_list = []
    for person in person_data.values():
        person_name_list.append(f"{person['firstname']}, {person['lastname']}")
    return person_name_list

def find_person_data_by_name(suchstring):
    """Findet eine Person in den geladenen Daten anhand von 'Vorname, Nachname'.
    Diese Funktion nimmt einen String im Format 'Vorname, Nachname' und sucht in den Personendaten nach einer Übereinstimmung.
    Wenn eine Übereinstimmung gefunden wird, gibt sie die entsprechenden Personendaten zurück.
    Eingabe: String im Format 'Vorname, Nachname', z.B. 'Julian, Huber'
    Rückgabe: Dictionary mit den Personendaten, z.B. {'id': 'vp001', 'firstname': 'Julian', 'lastname': 'Huber'}
    Wenn keine Übereinstimmung gefunden wird, wird ein leeres Dictionary zurückgegeben."""
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