import json, os, re, subprocess, time, urllib.parse
OUT = os.path.expanduser("~/Desktop/Square Off Photos"); UA = "SquareOffPartyGame/1.0 (personal party trivia)"
def get(url):
    for k in range(4):
        r = subprocess.run(["curl","-sSfL","--max-time","40","--retry","5","--retry-max-time","120","-A",UA,url], capture_output=True)
        if r.returncode == 0: return r.stdout
        time.sleep(20*(k+1))
    raise IOError("fetch failed")
def commons(q, n=1):
    d = json.loads(get("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(dict(action="query", generator="search", gsrsearch=q+" filetype:bitmap", gsrnamespace=6, gsrlimit=4, prop="imageinfo", iiprop="url", iiurlwidth=960, format="json", formatversion="2"))))
    pages = sorted(d.get("query",{}).get("pages",[]), key=lambda p: p.get("index",99))
    return [p["imageinfo"][0]["thumburl"] for p in pages if p.get("imageinfo") and p["imageinfo"][0].get("thumburl")][:n]
WANT = [("Landmarks","Eiffel Tower","Eiffel Tower Paris view Champ de Mars"),("Landmarks","Burj Khalifa","Burj Khalifa Dubai daytime"),
 ("Landmarks","Forbidden City","Forbidden City Beijing Hall of Supreme Harmony"),("Toys","Lego","Lego bricks pile"),("Toys","Jenga","Jenga tower game wooden blocks"),
 ("Toys","Barbie","Barbie doll toy"),("Toys","Hot Wheels","Hot Wheels die-cast car toy"),("Toys","Furby","Furby toy"),
 ("Makeup","Blush","blush makeup powder compact"),("Makeup","Bronzer","bronzer makeup powder"),("Makeup","Perfume","perfume bottle"),
 ("Makeup","False eyelashes","false eyelashes strip"),("Makeup","Eyelash curler","eyelash curler")]
for cat, ans, q in WANT:
    d = os.path.join(OUT, "_candidates", cat); os.makedirs(d, exist_ok=True)
    try:
        for i, u in enumerate(commons(q, 2)):
            ext = os.path.splitext(urllib.parse.urlparse(u).path)[1].lower() or ".jpg"
            open(os.path.join(d, f"{ans}__{i}{ext}"), "wb").write(get(u)); time.sleep(1.5)
        print("ok", cat, ans, flush=True)
    except Exception as e: print("fail", cat, ans, e, flush=True)
    time.sleep(1.5)
