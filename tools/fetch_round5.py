"""Round 5: NBA Players, NFL Players (Wikipedia), Gilmore Girls Characters, MCU Characters (fan wikis).
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
 "NBA Players": (WP, L("""
LeBron James
Stephen Curry
Kevin Durant
Giannis Antetokounmpo
Nikola Jokić
Luka Dončić
Joel Embiid
Jayson Tatum
Jaylen Brown
Anthony Edwards
Shai Gilgeous-Alexander
Victor Wembanyama
Ja Morant
Devin Booker
Damian Lillard
Kawhi Leonard
Paul George
James Harden
Kyrie Irving
Jimmy Butler
Bam Adebayo
Anthony Davis
Donovan Mitchell
Trae Young
Zion Williamson
De'Aaron Fox
Domantas Sabonis
Tyrese Haliburton
Jalen Brunson
Karl-Anthony Towns
Rudy Gobert
Chris Paul
Russell Westbrook
Klay Thompson
Draymond Green
Paolo Banchero
Chet Holmgren
Cade Cunningham
LaMelo Ball
Tyrese Maxey
Pascal Siakam
DeMar DeRozan
Zach LaVine
Brandon Ingram
Jamal Murray
Kristaps Porziņģis
Jrue Holiday
Derrick White=Derrick White (basketball)
Mikal Bridges
Alperen Şengün
Scottie Barnes
Franz Wagner
Evan Mobley
Darius Garland
Lauri Markkanen
Jalen Williams
Fred VanVleet
Julius Randle
Aaron Gordon
Michael Porter Jr.
Austin Reaves
Al Horford
Brook Lopez
Andrew Wiggins
Cooper Flagg
Kyle Lowry
Michael Jordan
Kobe Bryant
Shaquille O'Neal
Magic Johnson
Larry Bird
Tim Duncan
Dirk Nowitzki
Dwyane Wade
Allen Iverson
Kevin Garnett
Hakeem Olajuwon
Charles Barkley
Dennis Rodman
Yao Ming
Vince Carter
Carmelo Anthony
Dwight Howard
Steve Nash
Kareem Abdul-Jabbar
Scottie Pippen
Tony Parker
Pau Gasol
Manu Ginóbili
Derrick Rose
Blake Griffin
Paul Pierce
""")),
 "NFL Players": (WP, L("""
Patrick Mahomes
Travis Kelce
Josh Allen=Josh Allen (quarterback)
Lamar Jackson
Joe Burrow
Jalen Hurts
Justin Herbert
Aaron Rodgers
Tom Brady
Peyton Manning
Dak Prescott
C. J. Stroud
Brock Purdy
Jared Goff
Kirk Cousins
Russell Wilson
Matthew Stafford
Jordan Love
Trevor Lawrence
Tua Tagovailoa
Kyler Murray
Caleb Williams
Jayden Daniels
Bo Nix
Baker Mayfield
Christian McCaffrey
Saquon Barkley
Derrick Henry
Josh Jacobs
Jahmyr Gibbs
Bijan Robinson
Jonathan Taylor=Jonathan Taylor (American football)
Tyreek Hill
Justin Jefferson
Ja'Marr Chase
CeeDee Lamb
Davante Adams
Stefon Diggs
A. J. Brown
Amon-Ra St. Brown
Puka Nacua
Cooper Kupp
DK Metcalf
Mike Evans=Mike Evans (wide receiver)
Deebo Samuel
George Kittle
Mark Andrews=Mark Andrews (American football)
T. J. Watt
J. J. Watt
Myles Garrett
Nick Bosa
Aaron Donald
Micah Parsons
Maxx Crosby
Jalen Ramsey
Von Miller
Fred Warner=Fred Warner (American football)
Jason Kelce
Rob Gronkowski
Marshawn Lynch
Odell Beckham Jr.
Calvin Johnson
Drew Brees
Eli Manning
Ray Lewis
Cam Newton
Jerry Rice
Barry Sanders
Emmitt Smith
Deion Sanders
Joe Montana
Brett Favre
Travis Hunter=Travis Hunter (American football)
Shedeur Sanders
Michael Vick
Ben Roethlisberger
Russell Wilson
Adrian Peterson
LaDainian Tomlinson
Julio Jones
Larry Fitzgerald
Antonio Brown
""")),
 "Gilmore Girls Characters": ("https://gilmoregirls.fandom.com/api.php", L("""
Lorelai Gilmore
Rory Gilmore
Luke Danes
Emily Gilmore
Richard Gilmore
Sookie St. James
Lane Kim
Paris Geller
Jess Mariano
Dean Forester
Logan Huntzberger
Kirk Gleason
Michel Gerard
Taylor Doose
Miss Patty
Babette Dell
Christopher Hayden
Mrs. Kim=Mrs. Kim
Jackson Belleville
Zack Van Gerbig
Liz Danes
TJ=T.J.
April Nardini
Max Medina
Jason Stiles
Marty
Doyle McMaster
Madeline Lynn
Louise Grant
Sherry Tinsdale
Trix Gilmore=Lorelai "Trix" Gilmore
Mitchum Huntzberger
Gypsy
Caesar
Brian Fuller
Gil
Paul Anka
Tristin Dugray
Andrew
Shira Huntzberger
Honor Huntzberger
Colin McRea
Finn
Nicole Leahy
Rachel
Anna Nardini
Kyon
Jamie
Francie Jarvis
Headmaster Charleston=Hanlin Charleston
Bootsy
Lindsay Lister
Mia
""")),
 "MCU Characters": ("https://marvelcinematicuniverse.fandom.com/api.php", L("""
Iron Man=Tony Stark
Captain America=Steve Rogers
Thor
Hulk=Bruce Banner
Black Widow=Natasha Romanoff
Hawkeye=Clint Barton
Spider-Man=Peter Parker
Black Panther=T'Challa
Doctor Strange=Stephen Strange
Scarlet Witch=Wanda Maximoff
Vision
Loki
Thanos
Groot
Rocket
Star-Lord=Peter Quill
Gamora
Drax=Drax the Destroyer
Nebula
Mantis
Ant-Man=Scott Lang
Wasp=Hope van Dyne
Captain Marvel=Carol Danvers
Falcon=Sam Wilson
Winter Soldier=Bucky Barnes
War Machine=James Rhodes
Nick Fury
Shuri
Okoye
Killmonger=N'Jadaka
Wong
Valkyrie
Hela
Ultron
Red Skull=Johann Schmidt
Peggy Carter
Pepper Potts
Happy Hogan
Ned Leeds
MJ=Michelle Jones
Shang-Chi
Ms. Marvel=Kamala Khan
Moon Knight=Marc Spector
She-Hulk=Jennifer Walters
Kate Bishop
Yelena Belova
Agatha Harkness
Kang=He Who Remains
Mysterio=Quentin Beck
Vulture=Adrian Toomes
Deadpool=Wade Wilson
Wolverine=James Howlett
Korg
Yondu=Yondu Udonta
Ego
Phil Coulson
Maria Hill
Odin
Heimdall
Ghost=Ava Starr
Abomination=Emil Blonsky
Howard the Duck
Ronan the Accuser
The Collector=Taneleer Tivan
Grandmaster=En Dwi Gast
Ikaris
Thena
Sylvie=Sylvie Laufeydottir
Miss Minutes
""")),
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
