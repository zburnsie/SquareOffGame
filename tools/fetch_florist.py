"""Florist-style Flowers: top 3 Wikimedia Commons hits per flower, saved as '<Flower>~1.jpg' etc. for picking the best one."""
import json, os, subprocess, sys, time, urllib.parse
OUT = os.path.expanduser("~/Desktop/Square Off Photos/_candidates/Flowers (florist)")
UA = "SquareOffPartyGame/1.0 (personal party trivia)"
FLOWERS = {  # answer: Commons search words
 "Rose": "red roses bouquet", "Tulip": "pink tulips bouquet", "Peony": "pink peony flower close-up", "Ranunculus": "ranunculus flowers bouquet",
 "Hydrangea": "blue hydrangea flower head", "Orchid": "white phalaenopsis orchid flowers", "Lily": "white oriental lily flower Stargazer",
 "Stargazer lily": "stargazer lily flower", "Carnation": "pink carnation flowers", "Gerbera daisy": "gerbera daisy flower", "Sunflower": "sunflowers bouquet vase",
 "Calla lily": "calla lily bouquet", "Chrysanthemum": "chrysanthemum flower close-up", "Dahlia": "dahlia flower close-up", "Anemone": "anemone coronaria flower",
 "Freesia": "freesia flowers", "Lisianthus": "lisianthus eustoma flowers", "Alstroemeria": "alstroemeria flowers", "Baby's breath": "gypsophila baby's breath flowers",
 "Snapdragon": "snapdragon antirrhinum flowers", "Delphinium": "delphinium flowers blue", "Sweet pea": "sweet pea flowers lathyrus odoratus", "Protea": "king protea flower",
 "Iris": "purple iris flower close-up", "Hyacinth": "hyacinth flower purple", "Lavender": "lavender bunch flowers", "Gardenia": "gardenia flower white",
 "Magnolia": "magnolia flower bloom", "Gladiolus": "gladiolus flowers", "Daffodil": "yellow daffodils bunch", "Amaryllis": "red amaryllis hippeastrum flower",
 "Poinsettia": "poinsettia plant red", "Lily of the valley": "lily of the valley flowers convallaria", "Bird of paradise": "bird of paradise flower strelitzia",
 "Camellia": "camellia flower pink", "Garden rose": "garden roses english rose pink", "Daisy": "white daisies bouquet", "Aster": "aster flowers purple",
 "Zinnia": "zinnia flower", "Marigold": "marigold flowers orange", "Cherry blossom": "cherry blossom branch close-up", "Orchid (cymbidium)": "cymbidium orchid flowers",
 "Statice": "statice limonium flowers", "Wax flower": "waxflower chamelaucium", "Hellebore": "hellebore flower", "Cosmos": "cosmos flower pink",
 "Lotus": "lotus flower pink", "Water lily": "water lily flower", "Dianthus": "dianthus flowers", "Eucalyptus": "eucalyptus stems bouquet",
}
def get(url):
    for k in range(4):
        r = subprocess.run(["curl", "-sSfL", "--max-time", "40", "--retry", "4", "--retry-max-time", "90", "-A", UA, url], capture_output=True)
        if r.returncode == 0: return r.stdout
        time.sleep(10 * (k + 1))
    raise IOError(r.stderr.decode(errors="ignore")[:80])
os.makedirs(OUT, exist_ok=True); miss = []
for ans, q in FLOWERS.items():
    if any(f.startswith(ans + "~") for f in os.listdir(OUT)): continue
    try:
        r = json.loads(get("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(dict(action="query", generator="search",
            gsrsearch=q + " filetype:bitmap", gsrnamespace=6, gsrlimit=2, prop="imageinfo", iiprop="url", iiurlwidth=960, format="json", formatversion="2"))))
        pages = sorted(r.get("query", {}).get("pages", []), key=lambda p: p.get("index", 0))
        for i, pg in enumerate(pages, 1):
            u = pg["imageinfo"][0].get("thumburl")
            if not u: continue
            open(os.path.join(OUT, f"{ans}~{i}.jpg"), "wb").write(get(u)); time.sleep(1.2)
        if not pages: miss.append(ans)
    except Exception as e: miss.append(f"{ans} ({e})")
    time.sleep(1)
print("florist done; missing:", ", ".join(miss) or "none")
