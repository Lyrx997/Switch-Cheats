import json
import os
import re

INPUT_JSON = "cheats.json"

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_json_label_list_files(folder="label_files"):

    priority_order = [
        "US.en.json",
        "JP.ja.json",
        "IT.it.json",
        "KR.ko.json"
    ]

    ordered_files_names = []
    ordered_files = []

    try:
        files = [f for f in os.listdir(folder) if f.endswith(".json")]
    except FileNotFoundError:
        raise Exception(f"Cartella '{folder}' non trovata")

    # firstly add prioritary files, then the others
    for p in priority_order:
        if p in files:
            ordered_files_names.append(p)
            ordered_files.append(load_json(os.path.join(folder, p)))

    for f in sorted(files):
        if f not in ordered_files_names:
            ordered_files_names.append(f)
            ordered_files.append(load_json(os.path.join(folder, f)))


    return ordered_files


def sanitize_filename(name: str) -> str:

    # delete invalid Windows characters, newlines, carriage return and multiple spaces
    name = name.replace("\n", " ").replace("\r", " ")
    name = re.sub(r'[<>:"/\\|?*]', "", name)
    name = re.sub(r'\s+', " ", name)

    return name.strip()


def find_game_name(title_id, json_labels_list):

    for json_file in json_labels_list:
        for _, obj in json_file.items():
            if isinstance(obj, dict) and obj.get("id") == title_id:
                return obj.get("name", None)

    print("WARN: TitleId: " + title_id + " not found into any JSON label file.")
    return "unknown_game"

## MAIN FLOW STARTS HERE ##
data = load_json(INPUT_JSON)
print("Loading JSON label files...")
json_labels_list = get_json_label_list_files("label_files")
print("JSON label files loaded. Initiating extraction.")

for title_id, build_id_data in data.items():

    os.makedirs(title_id, exist_ok=True)
    game_name = sanitize_filename(find_game_name(title_id, json_labels_list))

    # txt file that contains the localized name of the current game
    info_path = os.path.join(title_id, f"{game_name}.txt")

    with open(info_path, "w", encoding="utf-8") as f:
        f.write(game_name + "\n")

    for build_id, cheats in build_id_data.items():

        for cheat_id, cheat_info in cheats.items():

            # ignore "version" element 
            # and any other JSON element that is not a dict type
            if not isinstance(cheat_info, dict):
                continue

            cheat_title = cheat_info.get("title", "")
            source = cheat_info.get("source", "")

            safe_cheat_title = sanitize_filename(cheat_title)

            base_dir = os.path.join(title_id, safe_cheat_title, "cheats")
            os.makedirs(base_dir, exist_ok=True)

            file_path = os.path.join(base_dir, f"{build_id}.txt")

            with open(file_path, "w", encoding="utf-8") as out:
                out.write(f"{cheat_title}\n")
                out.write(f"{source}\n")

print("Extraction done")