"""Replacement photos. 'wp:' lines use the Wikipedia page image; 'cs:' lines take the top Wikimedia Commons file search hit.
Format: Category|Answer|wp:Page title  or  Category|Answer|cs:search words"""
import json, os, re, subprocess, sys, time, urllib.parse
OUT = os.path.expanduser("~/Desktop/Square Off Photos/_candidates")
UA = "SquareOffPartyGame/1.0 (personal party trivia)"
ITEMS = [l.split("|") for l in """
Flowers|Rose|cs:red rose flower bloom
Flowers|Daffodil|cs:yellow daffodil Narcissus pseudonarcissus flower
Flowers|Daisy|cs:Leucanthemum vulgare flower
Flowers|Hydrangea|cs:Hydrangea macrophylla blue flowers
Flowers|Peony|cs:Paeonia lactiflora pink flower
Musical Instruments|Acoustic guitar|cs:acoustic guitar steel string
Musical Instruments|Electric guitar|cs:Fender Stratocaster guitar
Musical Instruments|Banjo|cs:five-string banjo
Musical Instruments|Harp|cs:concert pedal harp
Musical Instruments|Drum kit|cs:drum kit set
Ballroom Dance|Waltz|cs:waltz ballroom dance couple competition
Ballroom Dance|Foxtrot|cs:foxtrot ballroom dancesport couple
Ballroom Dance|Quickstep|cs:quickstep dancesport couple
Ballroom Dance|Rumba|cs:rumba dancesport couple
Ballroom Dance|Paso Doble|cs:paso doble dancesport couple
Ballroom Dance|Swing|cs:swing dance couple
Ballroom Dance|Bachata|cs:bachata dance couple
Ballroom Dance|Polka|cs:polka dancing couple
Ballroom Dance|Two-Step|cs:country two-step dance couple
Ballroom Dance|Jitterbug|cs:jitterbug dance
Commercial Mascots|GEICO Gecko|cs:GEICO gecko mascot
Commercial Mascots|Aflac Duck|cs:Aflac duck plush
Commercial Mascots|M&M's characters|cs:M&M's characters World store
Commercial Mascots|Jolly Green Giant|cs:Jolly Green Giant statue Blue Earth Minnesota
Commercial Mascots|Michelin Man|cs:Michelin Man Bibendum mascot costume
Commercial Mascots|Mr. Peanut|cs:Mr. Peanut costume mascot
Commercial Mascots|Grimace|cs:Grimace McDonald's costume
Commercial Mascots|Energizer Bunny|cs:Energizer Bunny balloon
Commercial Mascots|LiMu Emu (Liberty Mutual)|cs:LiMu Emu
Commercial Mascots|Lucky the Leprechaun|cs:Lucky the Leprechaun mascot
Commercial Mascots|The Burger King|cs:Burger King mascot king costume
Commercial Mascots|Captain Morgan|cs:Captain Morgan statue mascot
Commercial Mascots|Big Boy|cs:Big Boy statue restaurant
Commercial Mascots|Mr. Peanut|cs:Mr Peanut statue
Pop Stars (more)|Ed Sheeran|wp:Ed Sheeran
Pop Stars (more)|Elton John|wp:Elton John
Pop Stars (more)|Nick Jonas|wp:Nick Jonas
Human Anatomy|Nose|wp:Human nose
Human Anatomy|Lips|wp:Lip
Human Anatomy|Belly button|wp:Navel
Human Anatomy|Knee|wp:Knee
Human Anatomy|Elbow|wp:Elbow
Human Anatomy|Thumb|wp:Thumb
Human Anatomy|Eyebrow|wp:Eyebrow
Human Anatomy|Eyelashes|wp:Eyelash
Human Anatomy|Fingerprint|wp:Fingerprint
Human Anatomy|Toes|wp:Toe
Human Anatomy|Skull|wp:Human skull
Human Anatomy|Skeleton|wp:Human skeleton
Human Anatomy|Hair|wp:Hair
Human Anatomy|Chin|wp:Chin
Human Anatomy|Wrist|wp:Wrist
Human Anatomy|Shoulder|wp:Shoulder
Human Anatomy|Freckles|wp:Freckle
""".strip().splitlines()]

def get(url):
    for k in range(4):
        r = subprocess.run(["curl", "-sSfL", "--max-time", "40", "--retry", "5", "--retry-max-time", "120", "-A", UA, url], capture_output=True)
        if r.returncode == 0: return r.stdout
        time.sleep(15 * (k + 1))
    raise IOError(r.stderr.decode(errors="ignore")[:100])

def url_for(src):
    kind, q = src.split(":", 1)
    if kind == "wp":
        pg = json.loads(get("https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(dict(action="query", titles=q, redirects=1,
             prop="pageimages", piprop="thumbnail", pithumbsize=800, pilicense="any", format="json", formatversion="2"))))["query"]["pages"][0]
        return (pg.get("thumbnail") or {}).get("source")
    r = json.loads(get("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(dict(action="query", generator="search", gsrsearch=q + " filetype:bitmap",
        gsrnamespace=6, gsrlimit=1, prop="imageinfo", iiprop="url", iiurlwidth=800, format="json", formatversion="2"))))
    pages = r.get("query", {}).get("pages", [])
    return pages[0]["imageinfo"][0].get("thumburl") if pages else None

miss = []
for cat, ans, src in ITEMS:
    d = os.path.join(OUT, cat); os.makedirs(d, exist_ok=True)
    if any(os.path.splitext(f)[0] == ans for f in os.listdir(d)): continue
    try:
        u = url_for(src)
        if not u: miss.append(ans); continue
        ext = os.path.splitext(urllib.parse.urlparse(u).path)[1].lower()
        open(os.path.join(d, ans + (ext if ext in (".jpg", ".jpeg", ".png") else ".jpg")), "wb").write(get(u))
    except Exception as e: miss.append(f"{ans} ({e})")
    time.sleep(1.5)
print("fixups done; missing:", ", ".join(miss) or "none")
