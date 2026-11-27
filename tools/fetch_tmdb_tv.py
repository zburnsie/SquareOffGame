"""Textless TV posters (falls back to textless stills) for 2000s kids shows. Based on fetch_tmdb.py: textless movie posters from TMDB's public site (posters tagged 'No Language' usually have no title text).
Lines are `Title (Year)`. Saves the top textless poster to ~/Desktop/Square Off Photos/_candidates/<Category>/<Title>.jpg"""
import os, re, subprocess, sys, time, urllib.parse

OUT = os.path.expanduser("~/Desktop/Square Off Photos/_candidates")
UA = "Mozilla/5.0 (Macintosh) SquareOffPartyGame/1.0"
SPEC = {
 "2000s Kids Shows": """
SpongeBob SquarePants (1999)
The Fairly OddParents (2001)
The Adventures of Jimmy Neutron, Boy Genius (2002)
Danny Phantom (2004)
Kim Possible (2002)
Lizzie McGuire (2001)
That's So Raven (2003)
Hannah Montana (2006)
The Suite Life of Zack & Cody (2005)
Drake & Josh (2004)
iCarly (2007)
Zoey 101 (2005)
Avatar: The Last Airbender (2005)
Phineas and Ferb (2007)
Dora the Explorer (2000)
Go, Diego, Go! (2005)
The Backyardigans (2004)
Little Einsteins (2005)
Mickey Mouse Clubhouse (2006)
Wizards of Waverly Place (2007)
Even Stevens (2000)
Sonny with a Chance (2009)
Ned's Declassified School Survival Guide (2004)
The Amanda Show (1999)
All Grown Up! (2003)
As Told by Ginger (2000)
Codename: Kids Next Door (2002)
Foster's Home for Imaginary Friends (2004)
The Grim Adventures of Billy & Mandy (2001)
Ed, Edd n Eddy (1999)
Teen Titans (2003)
Ben 10 (2005)
Johnny Test (2005)
Totally Spies! (2001)
The Proud Family (2001)
American Dragon: Jake Long (2005)
Lilo & Stitch: The Series (2003)
Teenage Mutant Ninja Turtles (2003)
Yu-Gi-Oh! (2000)
Dragon Tales (1999)
Clifford the Big Red Dog (2000)
Caillou (1997)
Max & Ruby (2002)
Wonder Pets! (2006)
Bob the Builder (1998)
LazyTown (2004)
Cyberchase (2002)
Handy Manny (2006)
Super Why! (2007)
WordGirl (2007)
Sid the Science Kid (2008)
Yo Gabba Gabba! (2007)
Chowder (2007)
The Mighty B! (2008)
My Life as a Teenage Robot (2003)
Invader Zim (2001)
Rocket Power (1999)
Hey Arnold! (1996)
Jonas (2009)
Unfabulous (2004)
Dexter's Laboratory (1996)
The Powerpuff Girls (1998)
Arthur (1996)
Blue's Clues (1996)
Rugrats (1991)
""",
}
def get(url):
    for k in range(3):
        r = subprocess.run(["curl", "-sSfL", "--max-time", "40", "--retry", "3", "-A", UA, url], capture_output=True)
        if r.returncode == 0: return r.stdout
        time.sleep(5 * (k + 1))
    raise IOError(r.stderr.decode(errors="ignore")[:100])

safe = lambda n: re.sub(r'[\\/:*?"<>|]', "", n).strip()
only = set(sys.argv[1:]); log = []
for cat, txt in SPEC.items():
    if only and cat not in only: continue
    d = os.path.join(OUT, cat); os.makedirs(d, exist_ok=True)
    have = {os.path.splitext(f)[0] for f in os.listdir(d)}
    miss = []
    for line in dict.fromkeys(l.strip() for l in txt.strip().splitlines() if l.strip()):
        m = re.match(r"(.+) \((\d{4})\)$", line); title, year = m.group(1), m.group(2)
        if safe(title) in have: continue
        try:
            html = get("https://www.themoviedb.org/search/tv?" + urllib.parse.urlencode({"query": title})).decode()
            mid = re.search(r'href="/tv/(\d+[^"/?]*)"', html)
            if not mid: miss.append(line + " [not found]"); continue
            page = get(f"https://www.themoviedb.org/tv/{mid.group(1)}/images/posters?image_language=xx").decode()
            ids = re.findall(r't/p/w220_and_h330_face/([A-Za-z0-9]+\.jpg)', page)
            if not ids:
                page = get(f"https://www.themoviedb.org/tv/{mid.group(1)}/images/backdrops?image_language=xx").decode()
                ids = re.findall(r't/p/w500_and_h282_face/([A-Za-z0-9]+\.jpg)', page)
                if ids: log.append(f"{line}: used a still (no textless poster)")
            if not ids: miss.append(line + " [no textless image]"); continue
            open(os.path.join(d, safe(title) + ".jpg"), "wb").write(get("https://media.themoviedb.org/t/p/w780/" + ids[0]))
            log.append(f"{line} -> {mid.group(1)}")
        except Exception as e: miss.append(f"{line} [{e}]")
        time.sleep(2.5)
    print(f"{cat}: {len(os.listdir(d))} saved; missing: {'; '.join(miss) or 'none'}", flush=True)
print("\n".join(log))
