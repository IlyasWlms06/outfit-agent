import os
import json
import pandas as pd
from PIL import Image

# Waar de dataset staat: Fashion Product Images
script_dir = os.path.dirname(__file__)
BASE_DIR = os.path.join(script_dir, "..")
DATASET_MAP = os.path.join(BASE_DIR, "..", "Dataset", "fashion-dataset")

# Welke stukken in de kledingkast willen: (gender, articleType, usage, aantal)
# usage None = niet filteren op usage
KEUZE = [
    # Man - tops
    ("Men", "Tshirts", "Casual", 7),
    ("Men", "Tshirts", "Sports", 3),
    ("Men", "Shirts", "Casual", 4),
    ("Men", "Shirts", "Formal", 5),
    ("Men", "Sweaters", "Casual", 3),
    ("Men", "Sweatshirts", "Casual", 3),
    # Man - broeken
    ("Men", "Jeans", "Casual", 4),
    ("Men", "Trousers", "Formal", 4),
    ("Men", "Trousers", "Casual", 2),
    ("Men", "Shorts", "Casual", 3),
    ("Men", "Track Pants", "Sports", 3),
    # Man - schoenen
    ("Men", "Casual Shoes", "Casual", 4),
    ("Men", "Formal Shoes", "Formal", 3),
    ("Men", "Sports Shoes", "Sports", 3),
    ("Men", "Sandals", "Casual", 2),
    ("Men", "Flip Flops", "Casual", 1),
    # Man - jassen
    ("Men", "Jackets", "Casual", 5),
    # Vrouw - tops
    ("Women", "Tops", "Casual", 6),
    ("Women", "Tshirts", "Casual", 4),
    ("Women", "Tshirts", "Sports", 2),
    ("Women", "Shirts", "Casual", 2),
    ("Women", "Shirts", "Formal", 3),
    ("Women", "Tops", "Formal", 2),
    ("Women", "Sweaters", "Casual", 3),
    ("Women", "Sweatshirts", "Casual", 2),
    # Vrouw - broeken en rokken
    ("Women", "Jeans", "Casual", 4),
    ("Women", "Trousers", "Formal", 3),
    ("Women", "Leggings", "Casual", 2),
    ("Women", "Skirts", "Casual", 3),
    ("Women", "Shorts", "Casual", 2),
    ("Women", "Track Pants", "Sports", 2),
    ("Women", "Capris", "Casual", 1),
    # Vrouw - kleedjes
    ("Women", "Dresses", "Casual", 5),
    ("Women", "Dresses", "Formal", 2),
    # Vrouw - schoenen
    ("Women", "Heels", "Casual", 3),
    ("Women", "Flats", "Casual", 3),
    ("Women", "Casual Shoes", "Casual", 2),
    ("Women", "Sports Shoes", "Sports", 3),
    ("Women", "Flip Flops", "Casual", 1),
    # Vrouw - jassen
    ("Women", "Jackets", "Casual", 3),
    # Unisex - regenjassen (voor man en vrouw).
    ("Unisex", "Rain Jacket", None, 4),
]

# Per type: slot en warmte (1 = luchtig, 5 = heel warm)
TYPES = {
    "Tshirts": ("top", 1),
    "Tops": ("top", 1),
    "Shirts": ("top", 2),
    "Sweaters": ("top", 4),
    "Sweatshirts": ("top", 4),
    "Jeans": ("broek", 3),
    "Trousers": ("broek", 3),
    "Track Pants": ("broek", 3),
    "Leggings": ("broek", 2),
    "Shorts": ("broek", 1),
    "Skirts": ("broek", 1),
    "Capris": ("broek", 1),
    "Dresses": ("kleed", 2),
    "Casual Shoes": ("schoenen", 3),
    "Formal Shoes": ("schoenen", 3),
    "Sports Shoes": ("schoenen", 3),
    "Heels": ("schoenen", 2),
    "Flats": ("schoenen", 2),
    "Sandals": ("schoenen", 1),
    "Flip Flops": ("schoenen", 1),
    "Jackets": ("jas", 5),
    "Rain Jacket": ("jas", 3),
}

# usage uit de dataset -> onze gelegenheid
GELEGENHEID = {
    "Casual": "casual",
    "Formal": "formeel",
    "Smart Casual": "formeel",
    "Sports": "sport",
}

# Sommige stukken passen bij meer dan één gelegenheid
EXTRA_GELEGENHEDEN = {
    "Heels": ["formeel"],
    "Flats": ["formeel"],
    "Sports Shoes": ["casual"],
    "Sweatshirts": ["sport"],
    "Rain Jacket": ["formeel", "sport"],
}

# Engelse kleur -> Nederlandse kleur
KLEUREN = {
    "Black": "zwart", "White": "wit", "Off White": "wit", "Grey": "grijs", "Grey Melange": "grijs",
    "Charcoal": "grijs", "Silver": "grijs", "Steel": "grijs", "Navy Blue": "navy", "Beige": "beige",
    "Cream": "beige", "Khaki": "beige", "Skin": "beige", "Nude": "beige", "Brown": "bruin",
    "Coffee Brown": "bruin", "Tan": "bruin", "Blue": "blauw", "Turquoise Blue": "blauw",
    "Teal": "blauw", "Red": "rood", "Maroon": "bordeaux", "Burgundy": "bordeaux", "Green": "groen",
    "Olive": "olijfgroen", "Sea Green": "groen", "Lime Green": "groen", "Pink": "roze",
    "Peach": "roze", "Magenta": "roze", "Rose": "roze", "Purple": "paars", "Lavender": "paars",
    "Mauve": "paars", "Yellow": "geel", "Mustard": "geel", "Gold": "geel", "Orange": "oranje",
    "Rust": "oranje", "Multi": "meerkleurig",
}

# Breedte van de kleine foto's (origineel is 1800x2400)
FOTO_BREEDTE = 300


def dataset_inladen():
    """
    Laadt styles.csv uit de dataset in en houdt alleen de bruikbare stukken over.
    """
    csv_path = os.path.join(DATASET_MAP, "styles.csv")
    tabel = pd.read_csv(csv_path, on_bad_lines="skip")

    namen = tabel["productDisplayName"].fillna("")
    kinderen = namen.str.contains("Kids") | namen.str.contains("Boys") | namen.str.contains("Girls")
    tabel = tabel[~kinderen]

    tabel = tabel[tabel["baseColour"].notna()]

    fotos = os.listdir(os.path.join(DATASET_MAP, "images"))
    bestandsnamen = tabel["id"].astype(str) + ".jpg"
    tabel = tabel[bestandsnamen.isin(fotos)]

    print(f"{len(tabel)} bruikbare stukken in de dataset")
    return tabel


def mouwlengte(stuk_id):
    """Zoekt de mouwlengte op in het json bestand van het stuk"""
    json_path = os.path.join(DATASET_MAP, "styles", f"{stuk_id}.json")
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)["data"]
    kenmerken = data.get("articleAttributes") or {}
    return kenmerken.get("Sleeve Length")


def warmte_bepalen(soort, stuk_id):
    """
    Bepaalt hoe warm een stuk is (1 = luchtig, 5 = heel warm).
    Bij tops en kleedjes kijken we ook naar de mouwen:
    lange mouwen = 1 warmer, korte of geen mouwen = 1
    """
    slot, warmte = TYPES[soort]

    if slot == "top" or slot == "kleed":
        mouwen = mouwlengte(stuk_id)
        if mouwen == "Long Sleeves" and warmte < 5:
            warmte = warmte + 1
        elif mouwen == "Short Sleeves" or mouwen == "Sleeveless":
            warmte = 1

    return warmte


def foto_verkleinen(stuk_id, foto_map):
    """Maakt de foto kleiner en slaat ze op in backend/data/fotos"""
    origineel = os.path.join(DATASET_MAP, "images", f"{stuk_id}.jpg")
    img = Image.open(origineel)
    breedte, hoogte = img.size
    klein = img.resize((FOTO_BREEDTE, int(FOTO_BREEDTE * hoogte / breedte)))
    klein.save(os.path.join(foto_map, f"{stuk_id}.jpg"))


def maak_kledingkast():
    """
    Maakt de kledingkast (CSV + foto's) uit de dataset.

    De functie:
    1. Laadt de dataset in.
    2. Kiest per regel in KEUZE een aantal stukken.
    3. Voegt slot, warmte, waterdicht, gelegenheden en kleur toe.
    4. Maakt de foto's kleiner.
    5. Slaat alles op in backend/data/kledingkast.csv.
    """
    data_dir = os.path.join(BASE_DIR, "backend", "data")
    foto_map = os.path.join(data_dir, "fotos")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(foto_map, exist_ok=True)

    dataset = dataset_inladen()

    kledingkast = []
    for gender, soort, usage, aantal in KEUZE:
        mask = (dataset["gender"] == gender) & (dataset["articleType"] == soort)
        if usage is not None:
            mask = mask & (dataset["usage"] == usage)
        stukken = dataset[mask]

        if len(stukken) < aantal:
            print(f"Let op: maar {len(stukken)} stukken gevonden voor {gender} {soort} {usage}")
            aantal = len(stukken)

        # random_state = altijd dezelfde stukken
        stukken = stukken.sample(n=aantal, random_state=42)

        for _, stuk in stukken.iterrows():
            slot, _ = TYPES[soort]

            # Geen usage? Dan is het casual
            gelegenheden = [GELEGENHEID.get(stuk["usage"], "casual")]
            for extra in EXTRA_GELEGENHEDEN.get(soort, []):
                if extra not in gelegenheden:
                    gelegenheden.append(extra)

            kleur = KLEUREN.get(stuk["baseColour"], stuk["baseColour"].lower())

            # Jas in een neutrale kleur mag ook bij formeel
            if soort == "Jackets" and kleur in ["zwart", "grijs", "navy", "beige", "bruin"]:
                gelegenheden.append("formeel")

            foto_verkleinen(stuk["id"], foto_map)

            kledingkast.append([
                stuk["id"],
                stuk["productDisplayName"],
                {"Men": "man", "Women": "vrouw", "Unisex": "unisex"}[gender],
                slot,
                soort,
                kleur,
                warmte_bepalen(soort, stuk["id"]),
                soort == "Rain Jacket",
                ";".join(gelegenheden),
                f"fotos/{stuk['id']}.jpg",
            ])
        print(f"{gender} {soort} {usage}: {aantal} stukken")

    tabel = pd.DataFrame(kledingkast, columns=[
        "id", "naam", "gender", "slot", "type", "kleur",
        "warmte", "waterdicht", "gelegenheden", "foto",
    ])
    csv_path = os.path.join(data_dir, "kledingkast.csv")
    tabel.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"{len(tabel)} stukken opgeslagen in backend/data/kledingkast.csv")

    return tabel


if __name__ == "__main__":
    maak_kledingkast()
