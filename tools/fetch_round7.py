"""Round 7: Bluey (fan wiki) and Argentina (Wikipedia). Round 5: NBA Players, NFL Players (Wikipedia), Gilmore Girls Characters, MCU Characters (fan wikis).
Saves into ~/Desktop/Square Off Photos/_candidates/<Category> for review. Lines are `Answer` or `Answer=Page title`."""
import json, os, re, subprocess, sys, time, urllib.parse

OUT = os.path.expanduser("~/Desktop/Square Off Photos/_candidates")
UA = "SquareOffPartyGame/1.0 (personal party trivia)"
WP = "https://en.wikipedia.org/w/api.php"

def L(s):
    out = []
    for line in s.strip().splitlines():
        a, _, t = line.strip().partition("=")
        if a: out.append((a.strip(), (t or a).strip()))
    return out

SPEC = {
 "Bluey": ("https://bluey.fandom.com/api.php", L("""
Bluey=Bluey Heeler
Bingo=Bingo Heeler
Bandit=Bandit Heeler
Chilli=Chilli Heeler
Muffin=Muffin Heeler
Socks=Socks Heeler
Stripe=Stripe Heeler
Trixie=Trixie Heeler
Nana=Chris Heeler
Grandad=Bob Heeler
Uncle Rad=Radley Heeler
Frisky
Coco
Snickers
Honey
Mackenzie
Rusty
Indy
Winton
Chloe
Lucky
Judo
Jack
Calypso
Pretzel
Missy
Bentley
Lila
Pom Pom
Bob Bilby
Wendy
Pat=Pat (Lucky's Dad)
Unicorse
Buddy
Juniper
Dougie
Bella
Chattermax
Captain
Mia
Brandy
Busker=The Busker
Jean-Luc
Mr. Retriever=Dad Retriever
Gruber
Hercules
Mort
""")),
 "Argentina": (WP, L("""
Lionel Messi
Diego Maradona
Pope Francis
Eva Perón
Che Guevara
Jorge Luis Borges
Anya Taylor-Joy
Lali Espósito
Tini Stoessel=Tini (singer)
Bizarrap
Duki=Duki (rapper)
María Becerra
Nicki Nicole
Emiliano Martínez
Ángel Di María
Julián Álvarez
Juan Martín del Potro
Gabriela Sabatini
Carlos Gardel
Mercedes Sosa
Gustavo Cerati
Diego Simeone
Javier Milei
Ricardo Darín
Juan Manuel Fangio
Juan Perón
Iguazú Falls=Iguazu Falls
Perito Moreno Glacier
Obelisco de Buenos Aires
Casa Rosada
Caminito (La Boca)=Caminito
Teatro Colón
Aconcagua
Ushuaia
Mount Fitz Roy
Recoleta Cemetery=La Recoleta Cemetery
Bariloche=San Carlos de Bariloche
Hill of Seven Colors=Cerro de los Siete Colores
Puente de la Mujer
Ischigualasto (Valley of the Moon)=Ischigualasto Provincial Park
Floralis Genérica
La Bombonera
Plaza de Mayo
Península Valdés
Asado
Empanada
Dulce de leche
Alfajor
Chimichurri
Mate=Mate (drink)
Milanesa
Choripán
Provoleta
Locro
Fugazzeta
Malbec
Matambre
Humita
Fernet con Coca=Fernet con coca
Pastafrola
Tango
Gaucho
Bandoneon
Fileteado
Flag of Argentina
Sun of May
Argentina national football team
""")),
}
def get(url):
    for k in range(4):
        r = subprocess.run(["curl", "-sSfL", "--max-time", "40", "--retry", "5", "--retry-max-time", "120", "-A", UA, url], capture_output=True)
        if r.returncode == 0: return r.stdout
        time.sleep(15 * (k + 1))
    raise IOError(r.stderr.decode(errors="ignore")[:100])

def lookup(api, titles):
    res = {}
    for i in range(0, len(titles), 40):
        q = json.loads(get(api + "?" + urllib.parse.urlencode(dict(action="query", titles="|".join(titles[i:i+40]), redirects=1,
            prop="pageimages|pageprops", piprop="thumbnail", pithumbsize=800, pilicense="any", ppprop="disambiguation", format="json", formatversion="2"))))["query"]
        back = {n["to"]: n["from"] for n in q.get("normalized", [])}
        for r in q.get("redirects", []): back[r["to"]] = back.get(r["from"], r["from"])
        for pg in q.get("pages", []):
            if pg.get("missing") or "disambiguation" in pg.get("pageprops", {}): continue
            src = (pg.get("thumbnail") or {}).get("source")
            if src: res[back.get(pg["title"], pg["title"])] = src
        time.sleep(2)
    return res

safe = lambda n: re.sub(r'[\\/:*?"<>|]', "", n).strip()
only = set(sys.argv[1:])
for cat, (api, items) in SPEC.items():
    if only and cat not in only: continue
    d = os.path.join(OUT, cat); os.makedirs(d, exist_ok=True)
    have = {os.path.splitext(f)[0] for f in os.listdir(d)}
    todo = [(a, t) for a, t in dict(items).items() if safe(a) not in have]
    try: urls = lookup(api, [t for _, t in todo])
    except Exception as e: print("lookup failed", cat, e, flush=True); continue
    miss = []
    for a, t in todo:
        u = urls.get(t)
        if not u: miss.append(a); continue
        ext = os.path.splitext(urllib.parse.urlparse(u).path.split("/revision")[0])[1].lower()
        ext = ext if ext in (".jpg", ".jpeg", ".png", ".gif", ".webp") else ".jpg"
        try: open(os.path.join(d, safe(a) + ext), "wb").write(get(u))
        except Exception: miss.append(a)
        time.sleep(1.2 if "wikipedia" in api else 0.3)
    print(f"{cat}: {len(os.listdir(d))} saved, missing: {', '.join(miss) or 'none'}", flush=True)
