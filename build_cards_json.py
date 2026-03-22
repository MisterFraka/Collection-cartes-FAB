import json
from pathlib import Path
from collections import defaultdict

# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------
# Mets ici le chemin vers le dossier RACINE du repo téléchargé
# the-fab-cube/flesh-and-blood-cards
REPO_ROOT = Path("./flesh-and-blood-cards-main")

# Fichiers attendus dans le repo
CARD_FILE = REPO_ROOT / "json" / "english" / "card.json"
CARD_PRINTING_FILE = REPO_ROOT / "json" / "english" / "card-printing.json"
SET_FILE = REPO_ROOT / "json" / "english" / "set.json"
SET_PRINTING_FILE = REPO_ROOT / "json" / "english" / "set-printing.json"
RARITY_FILE = REPO_ROOT / "json" / "english" / "rarity.json"
EDITION_FILE = REPO_ROOT / "json" / "english" / "edition.json"

OUTPUT_FILE = Path("./cards.json")


# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------
def load_json(path: Path):
    if not path.exists():
      raise FileNotFoundError(f"Fichier introuvable: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def index_by_unique_id(items):
    indexed = {}
    for item in items:
        uid = item.get("unique_id")
        if uid:
            indexed[uid] = item
    return indexed


def index_by_shorthand(items):
    indexed = {}
    for item in items:
        shorthand = item.get("shorthand")
        if shorthand:
            indexed[shorthand] = item
    return indexed


def get_first_non_empty(data, keys, default=None):
    for key in keys:
        value = data.get(key)
        if value not in (None, "", []):
            return value
    return default


def to_display_edition(edition_code, edition_index):
    if not edition_code:
        return ""
    edition = edition_index.get(edition_code)
    if edition:
        return edition.get("name") or edition_code
    return edition_code


def to_display_rarity(rarity_code, rarity_index):
    if not rarity_code:
        return ""
    rarity = rarity_index.get(rarity_code)
    if rarity:
        return rarity.get("name") or rarity_code
    return rarity_code


def safe_number_sort_key(value):
    if value is None:
        return (1, 999999, "")
    text = str(value).strip()
    digits = "".join(ch for ch in text if ch.isdigit())
    if digits:
        return (0, int(digits), text)
    return (1, 999999, text)


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
def main():
    print("Chargement des fichiers JSON source...")

    cards = load_json(CARD_FILE)
    card_printings = load_json(CARD_PRINTING_FILE)
    sets_data = load_json(SET_FILE)
    set_printings = load_json(SET_PRINTING_FILE)
    rarities = load_json(RARITY_FILE)
    editions = load_json(EDITION_FILE)

    cards_by_uid = index_by_unique_id(cards)
    sets_by_uid = index_by_unique_id(sets_data)
    set_printings_by_uid = index_by_unique_id(set_printings)
    rarity_by_shorthand = index_by_shorthand(rarities)
    edition_by_shorthand = index_by_shorthand(editions)

    grouped = defaultdict(list)

    for printing in card_printings:
        card_uid = get_first_non_empty(
            printing,
            ["card_unique_id", "card_id", "card_uid"]
        )
        card = cards_by_uid.get(card_uid, {})

        name = get_first_non_empty(
            card,
            ["name", "card_name"],
            default=get_first_non_empty(printing, ["card_name"], default="Carte inconnue")
        )

        pitch = get_first_non_empty(card, ["pitch", "pitch_value", "card_pitch"])

        set_printing_uid = get_first_non_empty(
            printing,
            ["set_printing_unique_id", "set_printing_id"]
        )
        set_printing = set_printings_by_uid.get(set_printing_uid, {})

        set_uid = get_first_non_empty(
            set_printing,
            ["set_unique_id", "set_id", "set_uid"]
        )
        set_obj = sets_by_uid.get(set_uid, {})

        set_code = get_first_non_empty(
            printing,
            ["set_id", "set_code"],
            default=get_first_non_empty(set_printing, ["id", "set_id"], default="")
        )

        set_name = get_first_non_empty(
            set_obj,
            ["name", "set_name"],
            default=get_first_non_empty(set_printing, ["name", "set_name"], default=set_code)
        )

        edition_code = get_first_non_empty(printing, ["edition"])
        rarity_code = get_first_non_empty(printing, ["rarity"])

        image_url = get_first_non_empty(
            printing,
            ["image_url", "image", "img", "card_image_url"],
            default=""
        )

        card_id_text = get_first_non_empty(
            printing,
            ["card_id", "printing_id", "id"],
            default=""
        )

        unique_id = get_first_non_empty(
            printing,
            ["unique_id"],
            default=card_id_text
        )

        art_variation = get_first_non_empty(printing, ["art_variation"], default="")
        foiling = get_first_non_empty(printing, ["foiling"], default="")
        expansion_slot = get_first_non_empty(printing, ["expansion_slot"], default=False)

        entry = {
            "printing_uid": unique_id,
            "card_id": card_id_text,
            "set_code": set_code,
            "set_name": set_name,
            "edition_code": edition_code or "",
            "edition_name": to_display_edition(edition_code, edition_by_shorthand),
            "rarity_code": rarity_code or "",
            "rarity_name": to_display_rarity(rarity_code, rarity_by_shorthand),
            "image": image_url or "",
            "art_variation": art_variation,
            "foiling": foiling,
            "expansion_slot": bool(expansion_slot),
        }

        grouped[(name, str(pitch) if pitch is not None else "")].append(entry)

    print("Transformation en format simplifié...")

    output = []

    for (name, pitch), editions_list in grouped.items():
        editions_list.sort(
            key=lambda x: (
                x["set_name"],
                safe_number_sort_key(x["card_id"]),
                x["edition_name"],
                x["foiling"],
                x["art_variation"],
            )
        )

        output.append({
            "name": name,
            "pitch": pitch if pitch != "" else None,
            "editions": editions_list
        })

    output.sort(key=lambda x: (x["name"].lower(), str(x["pitch"] or "")))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"OK: {OUTPUT_FILE} généré avec {len(output)} cartes uniques.")


if __name__ == "__main__":
    main()