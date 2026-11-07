# Visit Counter

Work in progress!

## Problemi na koje sam naišla

### Port 8080 je bio zauzet
**Problem:** 'docker run -p 8080:5000 visit-counter' je pao sa greškom 'failed to bind host port ... address already in use'.
**Uzrok:**   Na mom računaru je drugi program već slušao na portu 8080 (proverila sam sa 'sudo ss -tlnp | grep 8080').
**Rešenje:** Spoljni port sam izdvojila u promenljivu 'HOST_PORT' u '.env' fajlu. U '.env.example' je podrazumevano '8080', a lokalno koristim '8081'. Port unutar kontejnera ostaje 5000.

### Aplikacija nije mogla da se poveže na Redis (greška 111)
**Problem:**  Kada sam aplikaciju lokalno pokrenula sa 'python app.py', '/visits' je vraćao 500, a u logu je pisalo 'Error 111 connecting to localhost:6379. Connection refused'.
**Uzrok:**    Redis nije bio pokrenut, pa na portu 6379 niko nije slušao.
**Rešenje:**  Za lokalni razvoj sam Redis pokrenula u Dockeru ('docker run -d --name redis-dev -p 6379:6379 redis:7-alpine'). U Docker Compose-u sam dodala 'depends_on' sa 'condition:   service healthy', kako bi aplikacija čekala da redis prođe healthcheck pre pokretanja.

### Logovi su prikazivali vreme pomereno za sat
**Problem:** Vreme u logovima je kasnilo sat vremena u odnosu na lokalno.
**Uzrok:**   Kontejner podrazumevano radi u UTC zoni. Postavljanje 'TZ' promenljive nije bilo dovoljno jer 'python:3.12-slim' slika nema instaliran paket 'tzdata'
**Rešenje:** Dodala sam 'TZ=Europe/Belgrade' u '.env' i instalirala 'tzdata' u Dockerfile-u.
**Napomena:** U produkciji bih ostavila UTC, jer je to standard za logove sa više servera.


