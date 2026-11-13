import os
import pandas as pd


def kledingkast_inladen(pad=None):
    """
    Laadt de kledingkast in uit de CSV.
    Geen pad meegegeven? Dan neemt hij data/kledingkast.csv.
    """
    if pad is None:
        script_dir = os.path.dirname(__file__)
        pad = os.path.join(script_dir, "data", "kledingkast.csv")

    tabel = pd.read_csv(pad)
    print(f"{len(tabel)} kledingstukken ingeladen")
    return tabel


def stukken_voor(tabel, gender):
    """Alle stukken voor man of vrouw. Unisex hoort bij allebei."""
    mask = (tabel["gender"] == gender) | (tabel["gender"] == "unisex")
    return tabel[mask]
