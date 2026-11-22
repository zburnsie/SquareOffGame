"""Photo bank, round 4: Minecraft (minecraft.wiki), General Science and Girl Pop Singers (Wikipedia)."""
import json, os, re, subprocess, time, urllib.parse

OUT = os.path.expanduser("~/Desktop/Square Off Photos")
UA = "SquareOffPartyGame/1.0 (personal party trivia)"


def L(s):
    out = []
    for line in s.strip().splitlines():
        a, _, t = line.strip().partition("=")
        if a: out.append((a.strip(), (t or a).strip()))
    return out


SPEC = {
 "Minecraft": ("minecraft.wiki", "/api.php", L("""
Creeper
Zombie
Skeleton
Spider
Enderman
Ender Dragon
Wither
Ghast
Blaze
Slime
Villager
Iron Golem
Pig
Cow
Chicken
Sheep
Wolf
Axolotl
Bee
Piglin
Warden
Allay
Mooshroom
Strider
Shulker
Phantom
Witch
Llama
Panda
Fox
Diamond
Diamond Sword
Diamond Pickaxe
TNT
Crafting Table
Furnace
Chest
Bed=Red Bed
Torch
Redstone Dust
Ender Pearl
Golden Apple=Golden Apple
Cake
Elytra
Totem of Undying
Minecart
Bow
Shield
Spawner=Monster Spawner
Beacon
Enchanting Table
Anvil
Jukebox
Grass Block
Obsidian
""")),
 "General Science": ("en.wikipedia.org", "/w/api.php", L("""
Microscope=Optical microscope
Telescope=Refracting telescope
Test tube
Beaker=Beaker (laboratory equipment)
Bunsen burner
DNA=Nucleic acid double helix
Magnet=Horseshoe magnet
Prism=Dispersive prism
Petri dish
Thermometer
Periodic table
Saturn
Mars
Jupiter
The Moon=Moon
Comet
Galaxy=Spiral galaxy
Neuron
Red blood cells=Red blood cell
Tornado
Lightning
Rainbow
Quartz crystal=Quartz
Fossil=Ammonite
Human skeleton
Light bulb=Incandescent light bulb
Battery=Battery (electricity)
Solar panel
Volcano
Glacier
Stalactites=Stalactite
Bacteria=Bacteria
Circuit board=Printed circuit board
Stethoscope
Pendulum
Compass
Meteorite
Aurora=Aurora
Erlenmeyer flask
Wind turbine
Solar eclipse
""")),
 "Girl Pop Singers": ("en.wikipedia.org", "/w/api.php", L("""
Taylor Swift
Beyoncé
Rihanna
Ariana Grande
Lady Gaga
Katy Perry
Billie Eilish
Olivia Rodrigo
Dua Lipa
Selena Gomez
Miley Cyrus
Sabrina Carpenter
Chappell Roan
Adele
Britney Spears
Christina Aguilera
Madonna=Madonna
Shakira
Jennifer Lopez
Doja Cat
Lizzo
SZA
Demi Lovato
Kelly Clarkson
Pink=Pink (singer)
Gwen Stefani
Avril Lavigne
Nicki Minaj
Cardi B
Camila Cabello
Halsey=Halsey (singer)
Meghan Trainor
Lorde
Charli XCX
Tate McRae
Gracie Abrams
Mariah Carey
Whitney Houston
Cher
Kesha
Ava Max
Bebe Rexha
""")),
}


def get(url):
    for k in range(4):
        r = subprocess.run(["curl", "-sSfL", "--max-time", "40", "--retry", "5", "--retry-max-time", "120", "-A", UA, url], capture_output=True)
        if r.returncode == 0: return r.stdout
        time.sleep(20 * (k + 1))
    raise IOError(r.stderr.decode(errors="ignore")[:100])


def batch(host, path, titles):
    res = {}
    for i in range(0, len(titles), 40):
        q = json.loads(get(f"https://{host}{path}?" + urllib.parse.urlencode(dict(action="query", titles="|".join(titles[i:i+40]), redirects=1,
            prop="pageimages|pageprops", piprop="thumbnail", pithumbsize=800, pilicense="any", ppprop="disambiguation", format="json", formatversion="2"))))["query"]
        back = {}
        for n in q.get("normalized", []): back[n["to"]] = n["from"]
        for r in q.get("redirects", []): back[r["to"]] = back.get(r["from"], r["from"])
        for pg in q.get("pages", []):
            if pg.get("missing") or "disambiguation" in pg.get("pageprops", {}): continue
            src = (pg.get("thumbnail") or {}).get("source")
            if src: res[back.get(pg["title"], pg["title"])] = src
        time.sleep(2)
    return res


def safe(n): return re.sub(r'[\\/:*?"<>|]', "", n).strip()


for cat, (host, path, items) in SPEC.items():
    d = os.path.join(OUT, cat); os.makedirs(d, exist_ok=True)
    have = {os.path.splitext(f)[0] for f in os.listdir(d)}
    todo = [(a, t) for a, t in items if safe(a) not in have]
    try: urls = batch(host, path, [t for _, t in todo])
    except Exception as e: print("lookup failed", cat, e, flush=True); continue
    miss = []
    for a, t in todo:
        u = urls.get(t)
        if not u: miss.append(a); continue
        try:
            ext = os.path.splitext(urllib.parse.urlparse(u).path)[1].lower()
            ext = ext if ext in (".jpg", ".jpeg", ".png", ".gif", ".webp") else ".jpg"
            open(os.path.join(d, safe(a) + ext), "wb").write(get(u))
        except Exception: miss.append(a)
        time.sleep(1.5 if "wikipedia" in host else 0.4)
    print(f"{cat}: {len(os.listdir(d))} saved, missing: {', '.join(miss) or 'none'}", flush=True)
