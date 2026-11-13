import os
from flask import Flask, jsonify, request, send_from_directory
from kledingkast import kledingkast_inladen, stukken_voor
from aanbevelen import zoek_outfits

app = Flask(__name__)

# Foto's staan in data/fotos
script_dir = os.path.dirname(__file__)
FOTO_MAP = os.path.join(script_dir, "data", "fotos")

# Kledingkast 1 keer inladen bij het opstarten
# Ander CSV-bestand gebruiken? Zet KLEDINGKAST_PAD
tabel = kledingkast_inladen(os.getenv("KLEDINGKAST_PAD"))

GENDERS = ["man", "vrouw"]
GELEGENHEDEN = ["casual", "formeel", "sport"]


@app.route("/fotos/<bestand>")
def foto(bestand):
    """Geeft een foto uit data/fotos terug"""
    return send_from_directory(FOTO_MAP, bestand)


@app.route("/api/health")
def health():
    """Check of de app draait"""
    return jsonify({"status": "ok", "stukken": len(tabel)})


@app.route("/api/kledingkast")
def kledingkast():
    """Alle stukken, of alleen die van man of vrouw"""
    gender = request.args.get("gender")

    if gender is None:
        stukken = tabel
    elif gender in GENDERS:
        stukken = stukken_voor(tabel, gender)
    else:
        return jsonify({"error": "Ongeldige invoer: gender moet man of vrouw zijn"}), 400

    return jsonify(stukken.to_dict("records"))


@app.route("/api/aanbevelingen")
def aanbevelingen():
    """
    Geeft outfits met uitleg terug.

    Parameters in de url:
    - gender: man of vrouw (moet)
    - gelegenheid: casual, formeel of sport
    - temperatuur: in °C
    - regen: true of false
    - aantal: 1 tot 10 (standaard 3)
    """
    gender = request.args.get("gender")
    gelegenheid = request.args.get("gelegenheid") or None
    temperatuur = request.args.get("temperatuur") or None
    regen = request.args.get("regen", "false").lower() == "true"
    aantal = request.args.get("aantal") or "3"

    # Invoer checken
    if gender not in GENDERS:
        return jsonify({"error": "Ongeldige invoer: gender moet man of vrouw zijn"}), 400

    if gelegenheid is not None and gelegenheid not in GELEGENHEDEN:
        return jsonify({"error": "Ongeldige invoer: gelegenheid moet casual, formeel of sport zijn"}), 400

    if temperatuur is not None:
        try:
            temperatuur = float(temperatuur)
        except ValueError:
            return jsonify({"error": "Ongeldige invoer: temperatuur moet een getal zijn"}), 400

    try:
        aantal = int(aantal)
    except ValueError:
        return jsonify({"error": "Ongeldige invoer: aantal moet een getal zijn"}), 400
    if aantal < 1 or aantal > 10:
        return jsonify({"error": "Ongeldige invoer: aantal moet tussen 1 en 10 liggen"}), 400

    # Outfits zoeken
    outfits = zoek_outfits(stukken_voor(tabel, gender), gelegenheid, temperatuur, regen, aantal)

    bericht = None
    if len(outfits) == 0:
        bericht = "Geen outfit gevonden met deze keuzes. Probeer minder filters."

    return jsonify({
        "vraag": {
            "gender": gender,
            "gelegenheid": gelegenheid,
            "temperatuur": temperatuur,
            "regen": regen,
            "aantal": aantal,
        },
        "outfits": outfits,
        "bericht": bericht,
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
