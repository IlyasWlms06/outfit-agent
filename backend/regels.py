# Kleuren die met alles combineren
NEUTRALE_KLEUREN = ["zwart", "wit", "grijs", "navy", "beige", "bruin"]


def weer_bepalen(temperatuur):
    """
    Kijkt welk weer het is en hoe warm de kleren mogen zijn.

    De functie:
    1. Kijkt of het koud, mild of warm is.
    2. Geeft de minimum en maximum warmte terug.
    3. Zegt of er een jas nodig is.
    4. Zegt of sandalen en slippers mogen (pas vanaf 23°C).

    Geen temperatuur = niet filteren op weer.
    """
    if temperatuur is None:
        weer = {"naam": "onbekend", "min_warmte": 1, "max_warmte": 5, "jas_nodig": False}
    elif temperatuur < 10:
        weer = {"naam": "koud", "min_warmte": 2, "max_warmte": 5, "jas_nodig": True}
    elif temperatuur < 20:
        weer = {"naam": "mild", "min_warmte": 1, "max_warmte": 4, "jas_nodig": False}
    else:
        weer = {"naam": "warm", "min_warmte": 1, "max_warmte": 3, "jas_nodig": False}

    weer["open_schoenen"] = temperatuur is None or temperatuur >= 23
    return weer


def is_neutraal(stuk):
    """Neutrale kleur of jeans = neutraal"""
    return stuk["kleur"] in NEUTRALE_KLEUREN or stuk["type"] == "Jeans"


def accentkleuren(outfit):
    """Alle kleuren in een outfit die niet neutraal zijn"""
    kleuren = []
    for stuk in outfit:
        if not is_neutraal(stuk) and stuk["kleur"] not in kleuren:
            kleuren.append(stuk["kleur"])
    return kleuren


def kleuren_passen(outfit):
    """Max 1 opvallende kleur, de rest neutraal"""
    return len(accentkleuren(outfit)) <= 1


def gelegenheden_passen(outfit):
    """
    Alle stukken moeten minstens 1 gelegenheid gemeen hebben.
    Anders krijg je bv. een trainingsbroek met nette schoenen.
    """
    gemeen = outfit[0]["gelegenheden"].split(";")
    for stuk in outfit[1:]:
        gelegenheden = stuk["gelegenheden"].split(";")
        gemeen = [g for g in gemeen if g in gelegenheden]
    return len(gemeen) > 0
