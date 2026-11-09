![CI](https://github.com/Danica003/visit-counter/actions/workflows/ci.yml/badge.svg)

# Visit Counter

Mala Flask aplikacija koja broji posete i čuva brojač u Redis bazi. Aplikacija je spakovana u Docker kontejner, pokreće se zajedno sa Redisom preko Docker Compose-a i automatski se proverava kroz GitHub Actions CI pipeline.
Glavni deo projekta su `Dockerfile`, `docker-compose.yml`, CI pipeline i `scripts/healthcheck.sh`.

## Arhitektura

```
                 ┌──────────────── Docker Compose ──────────────────┐
                 │                                                  │
  korisnik  ───► │  app (Flask, port 5000)  ───►  redis (port 6379) │
  (curl/browser) │        ▲                             │           │
  localhost:8080 │        │                             ▼           │
                 │  HOST_PORT:5000               volume: redis-data │
                 └──────────────────────────────────────────────────┘
```

                
- **app** – Flask aplikacija; 
- **redis** – čuva brojač;
- **redis-data** – imenovani volume, pa se brojač ne resetuje posle `docker compose down`.

## Endpointi
 
| Endpoint | Ponašanje |
|---|---|
| `GET /` | `{"message": "Hello DevOps", "host": "<id kontejnera>"}` |
| `GET /visits` | Uvećava brojač u Redisu i vraća `{"visits": N}` |
| `GET /health` | `200 {"status": "ok"}` ako je Redis dostupan, inače `503 {"status": "error"}` |

## Preduslovi
 
- Git
- Docker Engine + Docker Compose plugin (Linux) ili Docker Desktop (Windows/macOS)
- `make`, za skraćene komande. Sve komande mogu da se pokrenu i bez njega.
- Python 3.12, za lokalni razvoj bez Dockera.

  Na Linuxu, ako Docker zahteva `sudo`, dodajte korisnika u `docker` grupu (`sudo usermod -aG docker $USER`) i ponovo se prijavite.

## Pokretanje
 
### Linux / macOS
 
```bash
git clone https://github.com/Danica003/visit-counter.git
cd visit-counter
cp .env.example .env
docker compose up -d --build
```
Provera:
 
```bash
curl http://localhost:8080/visits    # {"visits": 1}
curl http://localhost:8080/visits    # {"visits": 2}
docker compose down && docker compose up -d
curl http://localhost:8080/visits    # {"visits": 3}  
./scripts/healthcheck.sh http://localhost:8080
```


### Windows (PowerShell)
 
Potreban je Docker Desktop sa WSL2.
 
```powershell
git clone https://github.com/Danica003/visit-counter.git
cd visit-counter
copy .env.example .env
docker compose up -d --build
```
Provera:
 
```powershell
curl.exe http://localhost:8080/visits    # {"visits": 1}
curl.exe http://localhost:8080/visits    # {"visits": 2}
docker compose down; docker compose up -d
curl.exe http://localhost:8080/visits    # {"visits": 3}  
```

```bash
bash scripts/healthcheck.sh http://localhost:8080
```
Bash skripta se pokreće iz WSL2 ili Git Bash-a, ne iz PowerShell-a.

Ako je port 8080 zauzet, promenite `HOST_PORT` u `.env` (npr. `HOST_PORT=8081`) i koristite taj port. Ovo važi za sve operativne sisteme.

 
### Make komande
 
| Komanda | Šta radi |
|---|---|
| `make build` | Pravi Docker sliku |
| `make up` | Podiže aplikaciju i Redis |
| `make down` | Gasi servise, volume ostaje |
| `make test` | Pokreće linter (ruff) i testove (pytest) |
| `make logs` | Prikazuje logove aplikacije uživo |
| `make healthcheck` | Pokreće `scripts/healthcheck.sh` na portu iz `.env` |

## Konfiguracija
 
Sva podešavanja se čitaju iz promenljivih okruženja (`.env`, šablon je u `.env.example`):
 
| Promenljiva | U `.env.example` | Ako nije zadata | Opis |
|---|---|---|---|
| `APP_PORT` | `5000` | `5000` | Port na kom aplikacija sluša unutar kontejnera |
| `REDIS_HOST` | `redis` | `localhost` | Adresa Redisa (u Compose-u je to ime servisa `redis`) |
| `REDIS_PORT` | `6379` | `6379` | Port Redisa |
| `HOST_PORT` | `8080` | `8080` | Port na host mašini na koji Compose mapira aplikaciju |
| `TZ` | `Europe/Belgrade` | UTC | Vremenska zona za logove |
 
`.env` nije u repozitorijumu (nalazi se u `.gitignore`), jer u realnom projektu može da sadrži tajne.

## CI pipeline
 
`.github/workflows/ci.yml` se pokreće na svaki push i pull request ka `main` i redom:
 
1. preuzima kod (checkout),
2. instalira zavisnosti,
3. pokreće linter (`ruff`),
4. pokreće testove (`pytest`),
5. builduje Docker sliku,
6. skenira sliku Trivy-jem,
7. podiže ceo stack kroz Docker Compose i pokreće `healthcheck.sh` i proveru `/visits`,
8. na push u `main` objavljuje sliku na GitHub Container Registry, tagovanu SHA-om commit-a.

Ako bilo koji korak ne prođe, pipeline pada.
 
Objavljena slika:
 
```bash
docker pull ghcr.io/danica003/visit-counter:<sha-commita>
```
## Važnije odluke
 
- **Python + Flask** – mala i jednostavna aplikacija, jer fokus zadatka nije programiranje.
- **Alpine osnovna slika sa tačnom verzijom (`python:3.12-alpine`)** – mala, zvanična slika; tačna verzija (umesto `latest`) daje ponovljiv build.
- **Multi-stage build** – builder faza instalira zavisnosti, a runtime faza kopira samo instalirane pakete. Veličina slike:

  | Verzija | Veličina |
  |---|---|
  | Jedna faza, `python:3.12-slim` | 193 MB |
  | Multi-stage, `python:3.12-alpine` | 89,4 MB |

  Najveći deo uštede dolazi od manje osnovne slike, jer zavisnosti ne zahtevaju kompajlere koje bi multi-stage inače ostavio u builder fazi.
- **Zavisnosti se instaliraju pre kopiranja koda** – Docker kešira sloj sa zavisnostima, pa su rebuild-ovi brzi dok se `requirements.txt` ne promeni.
- **Aplikacija ne radi kao root** – koristi se korisnik `appuser`, da kompromitovana aplikacija ima što manje privilegija.
- **Redis nije izložen ka host mašini** – dostupan je samo aplikaciji kroz internu mrežu, što smanjuje površinu napada.
- **Imenovani volume + AOF (`--appendonly yes`)** – brojač preživljava `docker compose down` i naglo gašenje.
- **`depends_on` sa `condition: service_healthy`** – aplikacija se pokreće tek kada Redis prođe healthcheck.
- **`restart: unless-stopped`** – Docker ponovo pokreće servis ako padne, osim ako je ručno zaustavljen.
- **Logovi na stdout** – standard za kontejnere; Docker ih prikazuje kroz `docker logs`.
- **Testovi sa `monkeypatch`** – unit testovi zamenjuju Redis klijenta lažnim funkcijama, pa rade u CI-ju bez prave baze. Stvarna veza sa Redisom proverava se integracionim testom u CI-ju.
- **`ubuntu-24.04` umesto `ubuntu-latest` u CI-ju** – okruženje se ne menja bez moje izmene.
- **Trivy akcija vezana za tačnu verziju** – zbog napada na Trivy-jeve GitHub oznake u martu 2026.

## Problemi na koje sam naišla

### Port 8080 je bio zauzet
**Problem:** `docker run -p 8080:5000 visit-counter` je pao sa greškom `failed to bind host port ... address already in use`. \
**Uzrok:**   Na mom računaru je drugi program već slušao na portu 8080. \
**Rešenje:** Spoljni port sam izdvojila u promenljivu `HOST_PORT` u `.env` fajlu. U `.env.example` je podrazumevano `8080`, a lokalno koristim `8081`. Port unutar kontejnera ostaje 5000. \

### Aplikacija nije mogla da se poveže na Redis (greška 111)
**Problem:**  Kada sam aplikaciju lokalno pokrenula sa `python app.py`, `/visits` je vraćao 500, a u logu je pisalo `Error 111 connecting to localhost:6379. Connection refused`. \
**Uzrok:**    Redis nije bio pokrenut, pa na portu 6379 niko nije slušao. \
**Rešenje:**  Za lokalni razvoj sam Redis pokrenula u Dockeru (`docker run -d --name redis-dev -p 6379:6379 redis:7-alpine`). U Docker Compose-u sam dodala `depends_on` sa `condition: service_healthy`, kako bi aplikacija čekala da redis prođe healthcheck pre pokretanja. \

### Logovi su prikazivali vreme pomereno za sat
**Problem:** Vreme u logovima je kasnilo sat vremena u odnosu na lokalno. \
**Uzrok:**   Kontejner podrazumevano radi u UTC zoni. \
**Rešenje:** Dodala sam `TZ=Europe/Belgrade` u `.env` i instalirala `tzdata` u Dockerfile-u. \
**Napomena:** U daljem radu bih ostavila UTC, jer je to standard za logove sa više servera. \

## Šta bih unapredila da imam više vremena
- **Produkcijski server (gunicorn)** umesto Flask razvojnog servera.
- **Nginx reverse proxy** ispred dve instance aplikacije (razlika bi se videla po polju `host`).
- **Kubernetes manifesti** (Deployment, Service, ConfigMap) za lokalni kind klaster.
- **`/visits` da vraća 503** kada Redis nije dostupan, umesto 500.
- **GitHub akcije vezane za pun SHA commit-a**, umesto oznake verzije.

## Korišćeni alati
 
- **Claude (AI asistent)** – objašnjenja Docker, Git i CI koncepata, pomoć pri pisanju koda i konfiguracije (Dockerfile, Compose, CI, Bash skripta), pomoć pri otklanjanju grešaka i strukturi ovog README-a. Svaki deo sam pokrenula, testirala i prošla red po red.
- Zvanična dokumentacija: Docker, Docker Compose, Flask, redis-py, GitHub Actions, Trivy.



