import re
import os

def generiere_neue_id():
    """Ermittelt die nächste freie Versuchspersonen-ID basierend auf vorhandenen Ordnern."""
    data_path = "data"
    if not os.path.exists(data_path):
        os.makedirs(data_path)

    vorhandene_ids = [
        d for d in os.listdir(data_path)
        if os.path.isdir(os.path.join(data_path, d)) and re.match(r"vp\d{3}", d)
    ]

    nummern = [
        int(re.search(r"vp(\d{3})", vp).group(1))
        for vp in vorhandene_ids
        if re.search(r"vp(\d{3})", vp)
    ]

    neue_nummer = max(nummern, default=0) + 1
    return f"vp{neue_nummer:03d}"
