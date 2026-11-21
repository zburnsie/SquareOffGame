"""Merge the user's photos (preferred) with Wikipedia photos, fix typos, remove duplicate answers and duplicate images."""
import os, re, shutil, sys, unicodedata, json
from PIL import Image

MINE = os.path.expanduser("~/Downloads/The Floor")
WIKI = os.path.expanduser("~/Desktop/Square Off Photos")
OUT = os.path.expanduser("~/Desktop/Square Off Photos Final")

# output category <- (user's folder, wikipedia folder)
CATS = {
    "Actors": ("Actors", "Actors"),
    "Animals": ("Animals", "Mammals"),
    "Disney Characters": ("Disney Characters", "Disney Characters"),
    "Famous Athletes": ("Famous Athletes", "Athletes"),
    "Fruits and Vegetables": ("Fruits and Vegetables", "Fruits & Veggies"),
    "Kitchen Items": ("Kitchen Items", "Kitchen Items"),
    "Logos": ("Logos", "Logos"),
    "Ocean Animals": ("Ocean Animals", "Ocean Animals"),
}
RENAME = {
    "Dwane Johnson (The Rock)": "Dwayne Johnson (The Rock)", "Kristin Bell": "Kristen Bell",
    "Nicholas Cage": "Nicolas Cage", "Robert Downey Jr": "Robert Downey Jr.", "Russel Wilson": "Russell Wilson",
    "Derek Henry": "Derrick Henry", "Nick Wild": "Nick Wilde", "Robinhood": "Robin Hood", "Oven Mit": "Oven Mitt",
    "AUDI": "Audi", "AirBNB": "Airbnb", "BlackBerry": "Blackberry", "Sword Fish": "Swordfish",
    "Puffer fish": "Pufferfish", "Angler Fish": "Anglerfish", "Messi": "Lionel Messi", "Ronaldo": "Cristiano Ronaldo",
    "Otter": "Sea Otter", "Shaquille O’Neal": "Shaquille O'Neal", "Timothee Chalamet": "Timothée Chalamet",
}
# same thing, different names (normalized key -> canonical normalized key)
ALIAS = {"shark": "greatwhiteshark", "whale": "humpbackwhale", "kiwi": "kiwifruit", "ovenmitt": "ovenmitt",
         "fryingpan": "castironskillet"}


def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\(.*?\)", "", s)
    s = re.sub(r"[^a-z0-9]", "", s)
    s = re.sub(r"jr$", "", s)
    s = re.sub(r"(ies)$", "y", s) if len(s) > 5 else s
    s = re.sub(r"(?<!s)s$", "", s) if len(s) > 4 else s
    return ALIAS.get(s, s)


def dhash(path, size=8):
    im = Image.open(path).convert("L").resize((size + 1, size), Image.LANCZOS)
    px = list(im.getdata())
    bits = 0
    for r in range(size):
        for c in range(size):
            bits = (bits << 1) | (px[r * (size + 1) + c] > px[r * (size + 1) + c + 1])
    return bits


def files(d):
    if not os.path.isdir(d):
        return []
    return sorted(f for f in os.listdir(d) if not f.startswith(".") and os.path.isfile(os.path.join(d, f)))


if os.path.exists(OUT):
    shutil.rmtree(OUT)
report = {}
for cat, (mine_dir, wiki_dir) in CATS.items():
    od = os.path.join(OUT, cat)
    os.makedirs(od)
    kept = {}        # norm -> (answer, source)
    hashes = []      # (hash, answer)
    r = {"renamed": [], "dup_name": [], "dup_image": [], "broken": [], "mine": 0, "wiki": 0}
    for src, d in (("mine", os.path.join(MINE, mine_dir)), ("wiki", os.path.join(WIKI, wiki_dir))):
        for f in files(d):
            p = os.path.join(d, f)
            stem, ext = os.path.splitext(f)
            stem = stem.strip()
            ans = RENAME.get(stem, stem) if src == "mine" else stem
            if src == "mine" and ans != stem:
                r["renamed"].append(f"{stem} → {ans}")
            k = norm(ans)
            if k in kept:
                r["dup_name"].append(f"{ans} ({src}) — already have {kept[k][0]} ({kept[k][1]})")
                continue
            try:
                h = dhash(p)
            except Exception as e:
                r["broken"].append(f"{f} ({src})")
                continue
            near = next((a for hh, a in hashes if bin(hh ^ h).count("1") <= 5), None)
            if near:
                r["dup_image"].append(f"{ans} ({src}) looks the same as {near}")
                continue
            hashes.append((h, ans))
            kept[k] = (ans, src)
            shutil.copy2(p, os.path.join(od, ans + ext.lower().replace(".jpeg", ".jpg")))
            r[src] += 1
    report[cat] = r

for cat, r in report.items():
    print(f"\n### {cat}: {r['mine'] + r['wiki']} photos ({r['mine']} yours + {r['wiki']} Wikipedia)")
    for k in ("renamed", "dup_name", "dup_image", "broken"):
        if r[k]:
            print(f"  {k}: " + "; ".join(r[k]))
