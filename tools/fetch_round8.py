"""Round 8: Mario Characters (fan wiki) and Office Supplies (Wikipedia). Round 5: NBA Players, NFL Players (Wikipedia), Gilmore Girls Characters, MCU Characters (fan wikis).
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
 "Mario Characters": ("https://mario.fandom.com/api.php", L("""
Mario
Luigi
Princess Peach
Bowser
Yoshi
Toad
Donkey Kong
Diddy Kong
Wario
Waluigi
Princess Daisy
Rosalina
Bowser Jr.
Koopa Troopa
Goomba
Boo
Shy Guy
Toadette
Birdo
Kamek
Lakitu
Piranha Plant
Bob-omb
Chain Chomp
Blooper
Dry Bones
King Boo
Larry Koopa
Morton Koopa Jr.
Wendy O. Koopa
Iggy Koopa
Roy Koopa
Lemmy Koopa
Ludwig von Koopa
Pauline
Cappy
Nabbit
Toadsworth
Professor E. Gadd
Petey Piranha
Hammer Bro
Thwomp
Bullet Bill
Cheep Cheep
Wiggler
Monty Mole
Spiny
Funky Kong
Cranky Kong
Dixie Kong
King K. Rool
Captain Toad
Baby Mario
Dry Bowser
Lumas=Luma
Pianta
""")),
 "Office Supplies": (WP, L("""
Stapler
Paper clip
Binder clip
Sticky notes=Post-it Note
Highlighter
Tape dispenser
Hole punch
Rubber band
Thumbtack=Drawing pin
Scissors
Ruler
Calculator
Pencil sharpener
Eraser
Correction fluid
Envelope
Rolodex
Clipboard
Ring binder
Manila folder=File folder
Index card
Paper shredder
Label maker
Glue stick
Rubber stamp
Stamp pad=Ink pad
Letter opener
Staple remover
Pencil
Fountain pen
Ballpoint pen
Marker=Marker pen
Whiteboard
Bulletin board
Laminator=Lamination
Paperweight
Mouse pad=Mousepad
Legal pad
Business card
Paper cutter
Desk organizer=Desk organiser
Tape measure
Printer=Printer (computing)
Sticky tack=Adhesive putty
Masking tape
Pencil case
Composition notebook=Composition book
Hanging file folder=Hanging file
"""))
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
