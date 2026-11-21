"""Download one photo per answer for Square Off photo categories from Wikipedia / Wikimedia Commons."""
import json, os, re, sys, time, urllib.parse, urllib.request

HTML = sys.argv[1]
OUT = sys.argv[2]
UA = "SquareOffPartyGame/1.0 (personal party trivia; python-urllib)"

CATS = {  # category id -> folder name
    "actors": "Actors", "athletes": "Athletes", "mammals": "Mammals", "produce": "Fruits & Veggies",
    "ocean": "Ocean Animals", "kitchen": "Kitchen Items", "disney": "Disney Characters",
    "logos": "Logos", "stinky": "Things That Smell Bad",
}
OVR = {
    "mammals": {"Seal": "Pinniped", "Cow": "Cattle", "Mouse": "House mouse", "Pig": "Domestic pig", "Fox": "Red fox",
                "Panda": "Giant panda", "Rhino": "Rhinoceros", "Hippo": "Hippopotamus", "Bat": "Bat", "Bear": "Brown bear",
                "Monkey": "Rhesus macaque", "Whale": "Humpback whale", "Deer": "White-tailed deer", "Rabbit": "European rabbit"},
    "produce": {"Orange": "Orange (fruit)", "Corn": "Maize", "Peanuts": "Peanut", "Grapes": "Grape", "Cherries": "Cherry",
                "Blueberries": "Blueberry", "Apple": "Apple", "Olive": "Olive", "Lemon": "Lemon", "Kiwi": "Kiwifruit"},
    "ocean": {"Whale": "Humpback whale", "Pufferfish": "Tetraodontidae", "Crab": "Crab", "Seal": "Harbor seal",
              "Squid": "Squid", "Shark": "Great white shark", "Salmon": "Atlantic salmon", "Eel": "Moray eel"},
    "kitchen": {"Plate": "Plate (dishware)", "Sponge": "Sponge (tool)", "Microwave": "Microwave oven", "Ladle": "Ladle (spoon)",
                "Baking sheet": "Sheet pan", "Oven mitt": "Oven glove", "Kitchen timer": "Egg timer",
                "Salt shaker": "Salt and pepper shakers", "Paper towels": "Paper towel", "Knife": "Kitchen knife",
                "Bowl": "Bowl", "Jar": "Jar", "Mug": "Mug"},
    "logos": {"Apple": "Apple Inc.", "Nike": "Nike, Inc.", "Target": "Target Corporation", "Puma": "Puma (brand)",
              "Shell": "Shell plc", "Amazon": "Amazon (company)", "Disney": "The Walt Disney Company",
              "Ralph Lauren": "Ralph Lauren Corporation", "MGM": "Metro-Goldwyn-Mayer", "Paramount": "Paramount Pictures",
              "Olympics": "Olympic symbols", "Twitter": "Twitter", "Ferrari": "Ferrari", "NBC": "NBC"},
    "stinky": {"Skunk": "Striped skunk", "Garbage": "Waste", "Rotten eggs": "Rotten egg", "Stinky cheese": "Limburger",
               "Manure": "Manure", "Durian": "Durian", "Asparagus": "Asparagus", "Litter box": "Litter box",
               "Corpse flower": "Amorphophallus titanum", "Sulfur": "Sulfur", "Porta-potty": "Portable toilet",
               "Dumpster": "Dumpster", "Sewer": "Sanitary sewer", "Toilet": "Toilet", "Onions": "Onion",
               "Diaper": "Diaper", "Cigarette smoke": "Tobacco smoke", "Spoiled milk": "Soured milk", "Moldy bread": "Mold"},
}
SEARCH_SUFFIX = {"disney": " Disney character"}


def get(url):
    import subprocess
    r = subprocess.run(["curl", "-sSfL", "--max-time", "40", "--retry", "7", "--retry-max-time", "240", "-A", UA, url], capture_output=True)
    if r.returncode != 0:
        raise IOError(r.stderr.decode(errors="ignore").strip()[:120])
    return r.stdout


def api(host, **params):
    params.update(format="json", formatversion="2")
    return json.loads(get(f"https://{host}/w/api.php?" + urllib.parse.urlencode(params)))


def answers(html, cid):
    m = re.search(r"\{id:'%s'.*?items:P\(`(.*?)`\)" % cid, html, re.S)
    seen, out = set(), []
    for line in m.group(1).strip().splitlines():
        if "|" in line:
            a = line.split("|", 1)[1].strip()
            if a and a not in seen:
                seen.add(a); out.append(a)
    return out


def wiki_thumb(title):
    d = api("en.wikipedia.org", action="query", titles=title, redirects=1, prop="pageimages|pageprops",
            piprop="thumbnail", pithumbsize=960, pilicense="any", ppprop="disambiguation")
    for p in d["query"].get("pages", []):
        if p.get("missing") or "disambiguation" in p.get("pageprops", {}):
            return None
        return (p.get("thumbnail") or {}).get("source")


def wiki_search_thumb(q):
    d = api("en.wikipedia.org", action="query", generator="search", gsrsearch=q, gsrlimit=3,
            prop="pageimages", piprop="thumbnail", pithumbsize=960, pilicense="any")
    pages = sorted(d.get("query", {}).get("pages", []), key=lambda p: p.get("index", 99))
    for p in pages:
        if p.get("thumbnail"):
            return p["thumbnail"]["source"]


def commons_thumb(q):
    d = api("commons.wikimedia.org", action="query", generator="search", gsrsearch=q + " filetype:bitmap",
            gsrnamespace=6, gsrlimit=3, prop="imageinfo", iiprop="url", iiurlwidth=960)
    pages = sorted(d.get("query", {}).get("pages", []), key=lambda p: p.get("index", 99))
    for p in pages:
        ii = (p.get("imageinfo") or [{}])[0]
        if ii.get("thumburl"):
            return ii["thumburl"]


def safe(name):
    return re.sub(r'[\\/:*?"<>|]', "", name).strip()


def wiki_batch(titles):
    res = {}
    for i in range(0, len(titles), 40):
        chunk = titles[i:i + 40]
        d = api("en.wikipedia.org", action="query", titles="|".join(chunk), redirects=1, prop="pageimages|pageprops",
                piprop="thumbnail", pithumbsize=960, pilicense="any", ppprop="disambiguation")
        q = d["query"]
        back = {}
        for n in q.get("normalized", []): back[n["to"]] = n["from"]
        for r in q.get("redirects", []): back[r["to"]] = back.get(r["from"], r["from"])
        for p in q.get("pages", []):
            orig = back.get(p["title"], p["title"])
            if p.get("missing") or "disambiguation" in p.get("pageprops", {}):
                continue
            src = (p.get("thumbnail") or {}).get("source")
            if src: res[orig] = src
        time.sleep(1.5)
    return res


html = open(HTML, encoding="utf-8").read()
report = {}
for cid, folder in CATS.items():
    d = os.path.join(OUT, folder)
    os.makedirs(d, exist_ok=True)
    missing = []
    ans = answers(html, cid)
    have = {os.path.splitext(f)[0] for f in os.listdir(d)}
    todo = [a for a in ans if safe(a) not in have]
    batch = {} if cid in SEARCH_SUFFIX else wiki_batch([OVR.get(cid, {}).get(a, a) for a in todo])
    for a in todo:
        url = None
        try:
            if cid in SEARCH_SUFFIX:
                url = wiki_search_thumb(a + SEARCH_SUFFIX[cid])
            else:
                url = batch.get(OVR.get(cid, {}).get(a, a))
            if not url:
                url = commons_thumb(a)
            if url:
                data = get(url)
                ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower()
                ext = ext if ext in (".jpg", ".jpeg", ".png", ".gif", ".webp") else ".jpg"
                with open(os.path.join(d, safe(a) + ext), "wb") as f:
                    f.write(data)
            else:
                missing.append(a)
        except Exception as e:
            missing.append(f"{a} ({type(e).__name__})")
        time.sleep(1.2)
    report[folder] = missing
    n = len([f for f in os.listdir(d) if not f.startswith(".")])
    print(f"{folder}: {n} saved, missing: {', '.join(missing) or 'none'}", flush=True)
