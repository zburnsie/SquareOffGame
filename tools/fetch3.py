"""Second photo bank: download one image per answer. Entries are 'Answer' or 'Answer=Wikipedia title'."""
import json, os, re, subprocess, sys, time, urllib.parse

OUT = os.path.expanduser("~/Desktop/Square Off Photos")
UA = "SquareOffPartyGame/1.0 (personal party trivia)"

def L(s):
    out = []
    for line in s.strip().splitlines():
        line = line.strip()
        if not line: continue
        a, _, t = line.partition("=")
        out.append((a.strip(), (t or a).strip()))
    return out

SPEC = {
 "Pro Sports Logos": ("wiki", L("""
Detroit Red Wings
Boston Bruins
Philadelphia Flyers
San Jose Sharks
Tampa Bay Lightning
Vegas Golden Knights
Nashville Predators
Colorado Avalanche
Montreal Canadiens
Seattle Kraken
Anaheim Ducks
Minnesota Wild
Chicago White Sox
Milwaukee Bucks
""")),
 "Toys": ("wiki", L("""
Rubber duck
Army men=Toy soldier
Toy train
Dollhouse
Bouncy ball
Paper airplane
Pinwheel=Pinwheel (toy)
Snow globe
Slime=Slime (toy)
Kaleidoscope
Bubble wand=Soap bubble
Jump rope=Skipping rope
Sock monkey
Puppet=Marionette
Toy robot
Wind-up toy=Clockwork toy
Kazoo
Dominoes
""")),
 "Arts and Crafts": ("wiki", L("""
Quilling
Pumpkin carving=Jack-o'-lantern
Gingerbread house
Needlepoint
Bobbin lace
Leather carving
Sand art=Sandpainting
String art
Chalk art=Street painting
Graffiti
Charcoal drawing=Charcoal (art)
Oil painting
Wreath
Ice sculpture
Sand castle=Sandcastle
Rug hooking
""")),
 "Makeup": ("wiki", L("""
Curling iron
Hair straightener=Hair iron
Hair dryer
Hairbrush
Bobby pin
Nail clippers=Nail clipper
Cotton swabs=Cotton swab
Sheet mask=Facial mask
Makeup bag=Cosmetic bag
Hand mirror
Nail art
Hair clip
Toothbrush
""")),
 "Cereal": ("cereal", L("""
Cocoa Pebbles
Crunch Berries=Cap'n Crunch's Crunch Berries
Cracklin' Oat Bran
Cinnamon Life
Fruity Cheerios
Frosted Cheerios
Oreo O's
Rice Chex
Corn Chex
Shredded Wheat
Total=Total (cereal)
Krave
Peanut Butter Crunch
Honey Graham Oh's
Mueslix
""")),
}

POKEMON = {"Pikachu":25,"Charizard":6,"Bulbasaur":1,"Charmander":4,"Squirtle":7,"Jigglypuff":39,"Meowth":52,"Psyduck":54,
 "Snorlax":143,"Eevee":133,"Mewtwo":150,"Mew":151,"Gengar":94,"Magikarp":129,"Gyarados":130,"Ditto":132,"Vaporeon":134,
 "Jolteon":135,"Flareon":136,"Lapras":131,"Dragonite":149,"Onix":95,"Machamp":68,"Slowpoke":79,"Togepi":175,"Pichu":172,
 "Lugia":249,"Ho-Oh":250,"Wobbuffet":202,"Umbreon":197,"Espeon":196,"Mudkip":258,"Torchic":255,"Treecko":252,"Rayquaza":384,
 "Lucario":448,"Piplup":393,"Greninja":658,"Sylveon":700,"Rowlet":722,"Mimikyu":778,"Gardevoir":282,"Blastoise":9,
 "Venusaur":3,"Butterfree":12,"Vulpix":37,"Cubone":104,"Clefairy":35,"Sprigatito":906,"Pidgey":16}


def get(url, tries=4):
    for k in range(tries):
        r = subprocess.run(["curl", "-sSfL", "--max-time", "40", "--retry", "5", "--retry-max-time", "120", "-A", UA, url], capture_output=True)
        if r.returncode == 0:
            return r.stdout
        time.sleep(20 * (k + 1))
    raise IOError(r.stderr.decode(errors="ignore").strip()[:100])


def api(host, **p):
    p.update(format="json", formatversion="2")
    return json.loads(get(f"https://{host}/w/api.php?" + urllib.parse.urlencode(p)))


def wiki_batch(titles):
    res = {}
    for i in range(0, len(titles), 40):
        q = api("en.wikipedia.org", action="query", titles="|".join(titles[i:i+40]), redirects=1, prop="pageimages|pageprops",
                piprop="thumbnail", pithumbsize=960, pilicense="any", ppprop="disambiguation")["query"]
        back = {}
        for n in q.get("normalized", []): back[n["to"]] = n["from"]
        for r in q.get("redirects", []): back[r["to"]] = back.get(r["from"], r["from"])
        for pg in q.get("pages", []):
            if pg.get("missing") or "disambiguation" in pg.get("pageprops", {}): continue
            src = (pg.get("thumbnail") or {}).get("source")
            if src: res[back.get(pg["title"], pg["title"])] = src
        time.sleep(2)
    return res


def wiki_search(q):
    d = api("en.wikipedia.org", action="query", generator="search", gsrsearch=q, gsrlimit=3, prop="pageimages",
            piprop="thumbnail", pithumbsize=960, pilicense="any")
    for pg in sorted(d.get("query", {}).get("pages", []), key=lambda p: p.get("index", 99)):
        if pg.get("thumbnail"): return pg["thumbnail"]["source"]


def commons(q):
    d = api("commons.wikimedia.org", action="query", generator="search", gsrsearch=q + " filetype:bitmap", gsrnamespace=6,
            gsrlimit=3, prop="imageinfo", iiprop="url", iiurlwidth=960)
    for pg in sorted(d.get("query", {}).get("pages", []), key=lambda p: p.get("index", 99)):
        ii = (pg.get("imageinfo") or [{}])[0]
        if ii.get("thumburl"): return ii["thumburl"]


def safe(n): return re.sub(r'[\\/:*?"<>|]', "", n).strip()


def save(d, ans, url):
    data = get(url)
    ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower()
    ext = ext if ext in (".jpg", ".jpeg", ".png", ".gif", ".webp") else ".jpg"
    open(os.path.join(d, safe(ans) + ext), "wb").write(data)


def run():
    POKE_SKIP = True
    # Pokémon first (different host, no rate limit)
    d = os.path.join(OUT, "Pokemon"); os.makedirs(d, exist_ok=True)
    miss = []
    for name, n in ({} if POKE_SKIP else POKEMON).items():
        if any(f.startswith(safe(name) + ".") for f in os.listdir(d)): continue
        try: save(d, name, f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{n}.png")
        except Exception: miss.append(name)
        time.sleep(0.2)
    print(f"Pokemon: {len(os.listdir(d))} saved, missing: {', '.join(miss) or 'none'}", flush=True)

    for cat, (mode, items) in SPEC.items():
        d = os.path.join(OUT, cat); os.makedirs(d, exist_ok=True)
        have = {os.path.splitext(f)[0] for f in os.listdir(d)}
        seen = set(); todo = []
        for a, t in items:
            if a in seen or safe(a) in have: continue
            seen.add(a); todo.append((a, t))
        batch = {}
        if mode in ("wiki", "hp"):
            try: batch = wiki_batch([t for _, t in todo])
            except Exception as e: print(f"  batch lookup failed for {cat}: {e}", flush=True)
        miss = []
        for a, t in todo:
            try:
                url = None
                if mode == "cereal":
                    url = commons(f"{a} cereal") or wiki_search(f"{t} breakfast cereal")
                else:
                    url = batch.get(t)
                    if not url and mode == "hp": url = wiki_search(f"{a} Harry Potter character")
                    if not url: url = commons(a)
                if url: save(d, a, url)
                else: miss.append(a)
            except Exception as e:
                miss.append(a)
            time.sleep(1.5)
        print(f"{cat}: {len([f for f in os.listdir(d) if not f.startswith('.')])} saved, missing: {', '.join(miss) or 'none'}", flush=True)

run()
