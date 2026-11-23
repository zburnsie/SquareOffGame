"""Harry Potter character headshots from the Harry Potter fandom wiki, into a review folder."""
import json, os, re, subprocess, sys, time, urllib.parse

OUT = os.path.expanduser("~/Desktop/Square Off Photos/_candidates/Harry Potter Characters")
UA = "SquareOffPartyGame/1.0 (personal party trivia)"
API = "https://harrypotter.fandom.com/api.php"
# answer = wiki page title
ITEMS = {
 "Lord Voldemort": "Tom Riddle", "Dobby": "Dobby", "Cedric Diggory": "Cedric Diggory", "Cho Chang": "Cho Chang",
 "Argus Filch": "Argus Filch", "Dudley Dursley": "Dudley Dursley", "Vernon Dursley": "Vernon Dursley",
 "Petunia Dursley": "Petunia Dursley", "Gilderoy Lockhart": "Gilderoy Lockhart", "Lucius Malfoy": "Lucius Malfoy",
 "Narcissa Malfoy": "Narcissa Malfoy", "Mad-Eye Moody": "Alastor Moody", "Moaning Myrtle": "Myrtle Warren",
 "Molly Weasley": "Molly Weasley", "Arthur Weasley": "Arthur Weasley", "Percy Weasley": "Percy Weasley",
 "Bill Weasley": "William Weasley", "Nymphadora Tonks": "Nymphadora Tonks", "Peter Pettigrew": "Peter Pettigrew",
 "Quirinus Quirrell": "Quirinus Quirrell", "Gellert Grindelwald": "Gellert Grindelwald", "Hedwig": "Hedwig",
 "Kreacher": "Kreacher", "Horace Slughorn": "Horace Slughorn", "Sybill Trelawney": "Sybill Trelawney",
 "Filius Flitwick": "Filius Flitwick", "Pomona Sprout": "Pomona Sprout", "Cornelius Fudge": "Cornelius Fudge",
 "Viktor Krum": "Viktor Krum", "Fleur Delacour": "Fleur Delacour", "Griphook": "Griphook",
 "Lavender Brown": "Lavender Brown", "Seamus Finnigan": "Seamus Finnigan", "Dean Thomas": "Dean Thomas",
 "Kingsley Shacklebolt": "Kingsley Shacklebolt", "Fenrir Greyback": "Fenrir Greyback", "Rita Skeeter": "Rita Skeeter",
 "Aberforth Dumbledore": "Aberforth Dumbledore", "Lily Potter": "Lily J. Potter", "James Potter": "James Potter I",
 "Buckbeak": "Buckbeak", "Fawkes": "Fawkes", "Crookshanks": "Crookshanks", "Scabbers": "Scabbers",
 "Nearly Headless Nick": "Nicholas de Mimsy-Porpington", "Madam Pomfrey": "Poppy Pomfrey", "Madam Hooch": "Rolanda Hooch",
 "Oliver Wood": "Oliver Wood", "Crabbe and Goyle": "Vincent Crabbe", "Aragog": "Aragog", "Fluffy": "Fluffy",
 "Nagini": "Nagini", "Dementor": "Dementor", "Mrs. Norris": "Mrs Norris", "Olympe Maxime": "Olympe Maxime",
}
only = set(sys.argv[1:])

def get(url):
    r = subprocess.run(["curl", "-sSfL", "--max-time", "40", "--retry", "5", "-A", UA, url], capture_output=True)
    if r.returncode: raise IOError(r.stderr.decode(errors="ignore")[:100])
    return r.stdout

os.makedirs(OUT, exist_ok=True)
todo = {a: t for a, t in ITEMS.items() if not only or a in only}
titles = list(todo.values()); urls = {}
for i in range(0, len(titles), 40):
    q = json.loads(get(API + "?" + urllib.parse.urlencode(dict(action="query", titles="|".join(titles[i:i+40]), redirects=1,
        prop="pageimages", piprop="thumbnail", pithumbsize=800, format="json", formatversion="2"))))["query"]
    back = {n["to"]: n["from"] for n in q.get("normalized", [])}
    for r in q.get("redirects", []): back[r["to"]] = back.get(r["from"], r["from"])
    for pg in q.get("pages", []):
        src = (pg.get("thumbnail") or {}).get("source")
        if src: urls[back.get(pg["title"], pg["title"])] = src
miss = []
for a, t in todo.items():
    u = urls.get(t)
    if not u: miss.append(a); continue
    ext = os.path.splitext(urllib.parse.urlparse(u).path.split("/revision")[0])[1].lower()
    ext = ext if ext in (".jpg", ".jpeg", ".png", ".webp", ".gif") else ".jpg"
    try: open(os.path.join(OUT, re.sub(r'[\\/:*?"<>|]', "", a) + ext), "wb").write(get(u))
    except Exception: miss.append(a)
    time.sleep(0.3)
print(len(os.listdir(OUT)), "saved; missing:", ", ".join(miss) or "none")
