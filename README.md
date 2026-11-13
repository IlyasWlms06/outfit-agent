# 👕 Outfit Agent

De **Outfit Agent** stelt outfits samen uit je eigen kledingkast, op basis van **gelegenheid** en **weer** (temperatuur en regen). Bij elk outfit krijg je een korte uitleg waarom de stukken bij elkaar passen.

De aanbevelingen komen nu nog uit eenvoudige regels (baseline), zonder machine learning en zonder personalisatie.

![CI](https://github.com/IlyasWlms06/outfit-agent/actions/workflows/ci.yml/badge.svg)

---

## 🚀 Snel starten

### Vereisten
- [Git](https://git-scm.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (moet gestart zijn)

### Starten
1. Clone de repository en ga in de map:
   ```bash
   git clone https://github.com/IlyasWlms06/outfit-agent.git
   cd outfit-agent
   ```
2. Start alles met één commando:
   ```bash
   docker compose up --build
   ```
3. Open de website: http://localhost:8080

De API kan je ook rechtstreeks testen op http://localhost:5000/api/health

Stoppen doe je met `Ctrl + C`, of met `docker compose down`.

### Andere poorten gebruiken (optioneel)
Zonder `.env` is de website op poort **8080** en de API op poort **5000**. Is een poort al bezet? Maak dan een `.env`:
```bash
cp .env.dist .env
```
Pas `FRONTEND_PORT` of `BACKEND_PORT` aan in `.env` en start opnieuw met `docker compose up --build`.

---

## 🧱 Opbouw

De app bestaat uit 2 containers:

```
browser ──► frontend (nginx, poort 8080)
              ├─ /            → website (index.html, script.js, style.css)
              ├─ /api/...  ──┐
              └─ /fotos/... ─┴─► backend (Flask, poort 5000)
                                   ├─ kledingkast.csv + foto's
                                   └─ regels + recommender
```

| Container | Wat zit erin? |
|---|---|
| `frontend` | De website en een nginx-webserver. Vragen naar `/api` en `/fotos` stuurt nginx door naar de backend. |
| `backend` | De Flask-API met de recommender, de kledingkast (CSV) en de foto's. |

De browser praat alleen met de frontend. Daarom kan `script.js` gewoon `fetch("/api/...")` doen.

---

## 🐍 Backend starten zonder Docker

Vereist: Python 3.11 of nieuwer. Zo draait alleen de **API** (de website heeft de frontend-container nodig).

```bash
cd backend
pip install -r requirements.txt
python app.py
```
Test daarna: http://localhost:5000/api/health

---

## 🔐 Secrets en instellingen

- Instellingen komen uit **omgevingsvariabelen**, niet uit de code.
- `.env.dist` is een voorbeeld en staat in de repo. `.env` staat in `.gitignore` en komt **nooit** in de repo.
- De app heeft nu nog **geen secrets** nodig (geen wachtwoorden of API-keys). Komen die er later (bv. voor Azure), dan horen ze in `.env` (lokaal) of in de secrets van GitHub of Azure.

| Variabele | Waarvoor | Standaard |
|---|---|---|
| `FRONTEND_PORT` | Poort van de website op je pc | `8080` |
| `BACKEND_PORT` | Poort van de API op je pc | `5000` |
| `KLEDINGKAST_PAD` | Ander CSV-bestand gebruiken als kledingkast (om te testen) | `backend/data/kledingkast.csv` |

---

## ⚙️ CI (GitHub Actions)

Bij **elke push** en pull request draait [`.github/workflows/ci.yml`](.github/workflows/ci.yml):
1. **🐳 Build Docker Images:** bouwt de backend- en de frontend-image.
2. **🧪 Start stack en test endpoints:** start alles met `docker compose up` (zoals hierboven) en checkt via de frontend:
   - de website laadt;
   - `/api/health` geeft antwoord;
   - `/api/aanbevelingen` geeft outfits terug;
   - foute invoer geeft een fout 400.

---

## 🔌 Endpoints (backend)

| Methode | Pad | Wat doet het? |
|---|---|---|
| GET | `/api/health` | Draait de app? Hoeveel stukken zijn er ingeladen? |
| GET | `/api/kledingkast?gender=vrouw` | Alle stukken, of alleen die van `man` of `vrouw` |
| GET | `/api/aanbevelingen` | **Outfits met uitleg** |
| GET | `/fotos/<bestand>` | Een foto uit de kledingkast, bv. `/fotos/20008.jpg` |

### Parameters van `/api/aanbevelingen`

| Parameter | Waarden | Standaard |
|---|---|---|
| `gender` | `man` of `vrouw` | moet |
| `gelegenheid` | `casual`, `formeel` of `sport` | alle |
| `temperatuur` | getal in °C | onbekend |
| `regen` | `true` of `false` | `false` |
| `aantal` | 1 tot 10 | 3 |

Voorbeeld:

```
http://localhost:8080/api/aanbevelingen?gender=vrouw&gelegenheid=formeel&temperatuur=5&regen=true
```

Bij foute invoer krijg je een fout 400, bv. `{"error": "Ongeldige invoer: gender moet man of vrouw zijn"}`.

---

## 🧠 Hoe werkt de baseline?

1. **Filteren per slot** (top, broek, kleed, schoenen, jas):
   - op **gelegenheid**;
   - op **warmte**, afhankelijk van de temperatuur:

     | Temperatuur | Weer | Warmte van de stukken | Jas |
     |---|---|---|---|
     | onder 10 °C | koud | 2 tot 5 | altijd |
     | 10 tot 20 °C | mild | 1 tot 4 | alleen bij regen |
     | 20 °C of meer | warm | 1 tot 3 | alleen bij regen |

   - **sandalen en slippers** pas vanaf 23 °C;
   - bij **regen**: geen sandalen, slippers of korte broek, en liefst een waterdichte jas.
2. **Combineren**: top + broek + schoenen, of kleed + schoenen, met een jas als dat nodig is.
3. **Kleurregel**: neutrale kleuren (zwart, wit, grijs, navy, beige, bruin en jeans) met max 1 opvallende kleur.
4. **Gelegenheidsregel**: alle stukken moeten minstens 1 gelegenheid gemeen hebben.
5. **Variatie**: de combinaties worden geschud en elk outfit krijgt een andere top of kleed.
6. **Uitleg**: de regels die gebruikt werden, worden zinnen.

---

## 📊 Data

De kledingkast komt uit de dataset **[Fashion Product Images](https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-dataset)** van Kaggle (±44.000 producten met foto).
Het script `scripts/maak_kledingkast.py` kiest 126 stukken (man en vrouw), maakt hun foto's kleiner (300 × 400) en voegt zelf kenmerken toe op basis van het type stuk:

| Kolom | Betekenis | Hoe bepaald? |
|---|---|---|
| `slot` | top, broek, kleed, schoenen of jas | uit het type (bv. Jeans → broek) |
| `warmte` | 1 (luchtig) tot 5 (heel warm) | uit het type (bv. T-shirt = 1, trui = 4, jas = 5). Bij tops en kleedjes tellen de mouwen mee: lange mouwen = 1 warmer, korte of geen mouwen = 1 |
| `waterdicht` | True / False | alleen regenjassen |
| `gelegenheden` | casual, formeel, sport | uit `usage` van de dataset, plus eigen regels (bv. hakken passen ook formeel) |
| `kleur` | Nederlandse kleur | vertaald uit `baseColour` |

De kledingkast en de foto's zitten al in de repo. Het script moet je alleen opnieuw draaien als je een nieuwe kledingkast wil maken. Daarvoor moet de dataset uitgepakt staan in `../Dataset/fashion-dataset/` (naast de map van dit project):
```bash
pip install -r scripts/requirements.txt
python scripts/maak_kledingkast.py
```

---

## 📁 Projectstructuur

```
outfit-agent/
├── backend/
│   ├── app.py            # Flask: de endpoints
│   ├── kledingkast.py    # kledingkast inladen (pandas)
│   ├── regels.py         # regels voor weer en kleuren
│   ├── aanbevelen.py     # baseline: outfits maken + uitleg
│   ├── data/
│   │   ├── kledingkast.csv   # de kledingkast
│   │   └── fotos/            # foto's van de stukken
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html
│   ├── script.js
│   ├── style.css
│   ├── nginx.conf        # website tonen + /api en /fotos doorsturen
│   └── Dockerfile
├── scripts/
│   ├── maak_kledingkast.py   # maakt de kledingkast uit de dataset
│   └── requirements.txt
├── .github/workflows/ci.yml  # CI-pipeline
├── docker-compose.yml        # alles starten met 1 commando
└── .env.dist                 # voorbeeld van de instellingen
```
