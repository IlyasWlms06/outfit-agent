document.addEventListener("DOMContentLoaded", function() {
    let formulier = document.getElementById("formulier");
    let melding = document.getElementById("melding");
    let resultaten = document.getElementById("resultaten");

    // Namen van de slots
    let slotNamen = { top: "Top", broek: "Broek", kleed: "Kleed", schoenen: "Schoenen", jas: "Jas" };

    // Formulier versturen = outfits vragen aan de API
    formulier.addEventListener("submit", async function(event) {
        event.preventDefault(); // Pagina niet herladen

        // Keuzes in de url zetten
        let parameters = new URLSearchParams();
        parameters.append("gender", document.getElementById("gender").value);
        parameters.append("gelegenheid", document.getElementById("gelegenheid").value);
        parameters.append("temperatuur", document.getElementById("temperatuur").value);
        parameters.append("regen", document.getElementById("regen").checked);
        parameters.append("aantal", document.getElementById("aantal").value);

        melding.textContent = "Outfits worden gezocht...";
        resultaten.innerHTML = "";

        try {
            let res = await fetch("/api/aanbevelingen?" + parameters.toString());
            let data = await res.json();

            // Fout van de API tonen
            if (!res.ok) {
                melding.textContent = data.error || "Er ging iets mis";
                return;
            }

            if (data.outfits.length === 0) {
                melding.textContent = data.bericht;
                return;
            }

            melding.textContent = "";
            for (let i = 0; i < data.outfits.length; i++) {
                toonOutfit(data.outfits[i], i + 1);
            }
        } catch (err) {
            melding.textContent = "Er ging iets mis: kan de API niet bereiken";
        }
    });

    // Zet 1 outfit als kaart op de pagina
    function toonOutfit(outfit, nummer) {
        let kaart = document.createElement("div");
        kaart.className = "card outfit";

        let titel = document.createElement("h2");
        titel.textContent = "Outfit " + nummer;
        kaart.appendChild(titel);

        // Stukken met foto
        let stukken = document.createElement("div");
        stukken.className = "stukken";
        for (let stuk of outfit.stukken) {
            let blok = document.createElement("div");
            blok.className = "stuk";
            blok.innerHTML = `
                <img src="/${stuk.foto}" alt="${stuk.naam}">
                <p class="slot">${slotNamen[stuk.slot]}</p>
                <p class="naam">${stuk.naam}</p>
                <p class="kleur">${stuk.kleur}</p>
            `;
            stukken.appendChild(blok);
        }
        kaart.appendChild(stukken);

        // Uitleg
        let lijst = document.createElement("ul");
        lijst.className = "uitleg";
        for (let zin of outfit.uitleg) {
            let item = document.createElement("li");
            item.textContent = zin;
            lijst.appendChild(item);
        }
        kaart.appendChild(lijst);

        resultaten.appendChild(kaart);
    }
});
