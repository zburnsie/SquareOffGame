"""Pack ~/Desktop/Square Off Photos Final/<Category>/<Answer>.<ext> into site/photos/index.json + one JSON of data URIs per category."""
import base64, io, json, os, re, sys, unicodedata
from PIL import Image

SRC = os.path.expanduser("~/Desktop/Square Off Photos Final")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "photos")  # the repo's photos/
PROMPTS = {
    "Actors": "Who is this?", "Animals": "Name the animal", "Disney Characters": "Which Disney character?",
    "Famous Athletes": "Who is this?", "Fruits and Vegetables": "Name it", "Kitchen Items": "Name the kitchen item",
    "Logos": "Whose logo is this?", "Ocean Animals": "Name the sea creature", "Pro Sports Logos": "Which team?",
    "Famous Dishes": "Name the dish", "Harry Potter Characters": "Which Harry Potter character?",
    "Arts and Crafts": "Name the craft", "Toys": "Name the toy", "Landmarks": "Name the landmark",
    "Pokémon": "Who's that Pokémon?", "Makeup": "Name the makeup item", "Cereal": "Name the cereal",
    "Minecraft": "Name this Minecraft thing", "General Science": "Name it", "Pop Stars": "Who is this pop star?",
    "NBA Players": "Who is this NBA player?", "NFL Players": "Who is this NFL player?",
    "Gilmore Girls Characters": "Which Gilmore Girls character?", "MCU Characters": "Which Marvel character?",
    "Movie Posters": "Name the movie", "Christmas Movies": "Name the Christmas movie", "Cartoon Characters": "Which cartoon character?",
    "Dog Breeds": "Name the dog breed", "Commercial Mascots": "Name the mascot", "Human Anatomy": "Name the body part",
    "Musical Instruments": "Name the instrument", "Flowers": "Name the flower", "Ballroom Dance": "Name the dance",
}
ORDER = list(PROMPTS)


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return "ph-" + re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def to_data_uri(path):
    im = Image.open(path)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, (255, 255, 255))
        bg.paste(im, mask=im.split()[-1])
        im = bg
    else:
        im = im.convert("RGB")
    im.thumbnail((900, 900), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=80, optimize=True, progressive=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


only = set(sys.argv[1:])  # optionally pack just these categories
os.makedirs(OUT, exist_ok=True)
idx_path = os.path.join(OUT, "index.json")
index = {c["name"]: c for c in json.load(open(idx_path))} if os.path.exists(idx_path) else {}
for cat in sorted(os.listdir(SRC), key=lambda c: (ORDER.index(c) if c in ORDER else 99, c)):
    d = os.path.join(SRC, cat)
    if not os.path.isdir(d) or (only and cat not in only):
        continue
    files = sorted((f for f in os.listdir(d) if not f.startswith(".")), key=lambda f: f.lower())
    answers, uris = [], []
    for f in files:
        try:
            uris.append(to_data_uri(os.path.join(d, f)))
            answers.append(unicodedata.normalize("NFC", os.path.splitext(f)[0]).strip())
        except Exception as e:
            print("  skipped", f, e)
    cid = slug(cat)
    with open(os.path.join(OUT, cid + ".json"), "w") as fh:
        json.dump(uris, fh, separators=(",", ":"))
    index[cat] = {"id": cid, "name": cat, "prompt": PROMPTS.get(cat, "What is this?"), "answers": answers}
    print(f"{cat}: {len(answers)} photos, {os.path.getsize(os.path.join(OUT, cid + '.json')) / 1e6:.1f} MB", flush=True)
ordered = sorted(index.values(), key=lambda c: (ORDER.index(c["name"]) if c["name"] in ORDER else 99, c["name"]))
json.dump(ordered, open(idx_path, "w"), ensure_ascii=False, separators=(",", ":"))
