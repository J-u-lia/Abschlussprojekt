import os
import re


def ermittle_nächste_testnummer(person_id):
    daten_folder = os.path.join("data", person_id, "daten")
    if not os.path.exists(daten_folder):
        return 1
    test_nums = []
    for f in os.listdir(daten_folder):
        m = re.search(r'Test(\d+)_Belastung\.csv', f)
        if m:
            test_nums.append(int(m.group(1)))
    if test_nums:
        return max(test_nums) + 1
    else:
        return 1
