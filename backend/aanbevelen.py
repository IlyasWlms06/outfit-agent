import random
from regels import weer_bepalen, kleuren_passen, gelegenheden_passen, accentkleuren, is_neutraal

# Gelegenheid in een zin
GELEGENHEID_ZIN = {
    "casual": "een casual gelegenheid",
    "formeel": "een formele gelegenheid",
    "sport": "sport",
}


def kandidaten_zoeken(tabel, slot, gelegenheid, weer, regen):
    """
    Zoekt alle stukken van 1 slot die passen.

    De functie:
    1. Neemt de stukken van het slot (top, broek, kleed, schoenen of jas).
    2. Filtert op gelegenheid en warmte.
    3. Bij regen: geen sandalen, slippers of korte broek en liefst een waterdichte jas.
    4. Onder 23°C: geen sandalen of slippers.
    5. Geeft de stukken terug als lijst.
    """
    stukken = tabel[tabel["slot"] == slot]

    if gelegenheid:
        stukken = stukken[stukken["gelegenheden"].str.contains(gelegenheid)]

    stukken = stukken[(stukken["warmte"] >= weer["min_warmte"]) & (stukken["warmte"] <= weer["max_warmte"])]

    # Bij regen geen shorts, rokjes, sandalen of slippers
    if regen and (slot == "schoenen" or slot == "broek"):
        stukken = stukken[stukken["warmte"] >= 2]

    # Sandalen en slippers pas vanaf 23°C
    if slot == "schoenen" and not weer["open_schoenen"]:
        stukken = stukken[stukken["warmte"] >= 2]

    # Liefst een waterdichte jas, anders gewoon een jas
    if regen and slot == "jas":
        waterdicht = stukken[stukken["waterdicht"] == True]
        if len(waterdicht) > 0:
            stukken = waterdicht

    return stukken.to_dict("records")


def uitleg_maken(outfit, gelegenheid, temperatuur, weer, regen):
    """Maakt de uitleg: waarom passen de stukken bij elkaar"""
    uitleg = []

    if gelegenheid:
        uitleg.append(f"Alle stukken passen bij {GELEGENHEID_ZIN[gelegenheid]}.")

    if temperatuur is not None:
        if weer["naam"] == "koud":
            uitleg.append(f"Bij {temperatuur:g}°C is het koud: geen luchtige stukken en een jas erover.")
        elif weer["naam"] == "mild":
            uitleg.append(f"Bij {temperatuur:g}°C is het mild: geen dikke winterjas nodig.")
        else:
            uitleg.append(f"Bij {temperatuur:g}°C is het warm: luchtige stukken, geen dikke truien.")

    for stuk in outfit:
        if stuk["slot"] == "kleed":
            uitleg.append("Een kleed vervangt een top en een broek.")
        if stuk["slot"] == "jas":
            if regen and stuk["waterdicht"]:
                uitleg.append("Het regent, dus een waterdichte jas.")
            elif regen:
                uitleg.append("Het regent, maar er is geen waterdichte jas: neem deze jas.")
            else:
                uitleg.append("De jas houdt je warm.")

    if regen:
        uitleg.append("Geen sandalen, slippers of korte broek, want het regent.")

    # Kleuren (jeans telt als neutraal)
    neutraal = []
    for stuk in outfit:
        if stuk["type"] == "Jeans":
            naam = "jeans"
        else:
            naam = stuk["kleur"]
        if is_neutraal(stuk) and naam not in neutraal:
            neutraal.append(naam)
    accenten = accentkleuren(outfit)
    if len(accenten) == 0:
        uitleg.append(f"Alleen neutrale kleuren ({', '.join(neutraal)}): dat combineert altijd.")
    elif len(neutraal) == 0:
        uitleg.append(f"Alles in dezelfde kleur ({accenten[0]}).")
    else:
        uitleg.append(f"Neutrale basis ({', '.join(neutraal)}) met {accenten[0]} als enige opvallende kleur.")

    return uitleg


def zoek_outfits(tabel, gelegenheid=None, temperatuur=None, regen=False, aantal=3):
    """
    Baseline: maakt outfits met simpele regels.

    De functie:
    1. Kijkt naar het weer en of er een jas nodig is.
    2. Zoekt per slot de stukken die passen.
    3. Maakt alle combinaties: top + broek + schoenen of kleed + schoenen (+ jas).
    4. Houdt alleen de combinaties waarvan de kleuren en gelegenheid passen.
    5. Schudt ze door elkaar en neemt outfits met telkens een andere top of kleed.
    6. Zet bij elk outfit een uitleg.
    """
    weer = weer_bepalen(temperatuur)
    jas_nodig = weer["jas_nodig"] or regen

    tops = kandidaten_zoeken(tabel, "top", gelegenheid, weer, regen)
    broeken = kandidaten_zoeken(tabel, "broek", gelegenheid, weer, regen)
    kleedjes = kandidaten_zoeken(tabel, "kleed", gelegenheid, weer, regen)
    schoenen = kandidaten_zoeken(tabel, "schoenen", gelegenheid, weer, regen)
    jassen = kandidaten_zoeken(tabel, "jas", gelegenheid, weer, regen)

    # Alle combinaties maken
    combinaties = []
    for top in tops:
        for broek in broeken:
            for schoen in schoenen:
                combinaties.append([top, broek, schoen])
    for kleed in kleedjes:
        for schoen in schoenen:
            combinaties.append([kleed, schoen])

    # Jas erbij als het koud is of regent
    if jas_nodig:
        met_jas = []
        for combinatie in combinaties:
            for jas in jassen:
                met_jas.append(combinatie + [jas])
        combinaties = met_jas

    # Alleen combinaties waarvan kleuren en gelegenheid passen
    goede_combinaties = []
    for combinatie in combinaties:
        if kleuren_passen(combinatie) and gelegenheden_passen(combinatie):
            goede_combinaties.append(combinatie)

    # Door elkaar schudden zodat je niet altijd hetzelfde krijgt
    random.shuffle(goede_combinaties)

    # Elk outfit een andere top of kleed
    outfits = []
    gebruikt = []
    for combinatie in goede_combinaties:
        if len(outfits) == aantal:
            break
        eerste_stuk = combinatie[0]["id"]
        if eerste_stuk in gebruikt:
            continue
        gebruikt.append(eerste_stuk)
        outfits.append({
            "stukken": combinatie,
            "uitleg": uitleg_maken(combinatie, gelegenheid, temperatuur, weer, regen),
        })

    return outfits
