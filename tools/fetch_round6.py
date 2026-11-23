"""Round 6: more Wikipedia categories. Round 5: NBA Players, NFL Players (Wikipedia), Gilmore Girls Characters, MCU Characters (fan wikis).
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

WPL = lambda txt: (WP, L(txt))
SPEC = {
 "NBA Players": WPL("Anthony Edwards=Anthony Edwards (basketball)"),
 "Dog Breeds": WPL("""
Labrador Retriever
Golden Retriever
German Shepherd
French Bulldog
Bulldog
Poodle
Beagle
Rottweiler
Dachshund
Corgi=Pembroke Welsh Corgi
Yorkshire Terrier
Boxer=Boxer (dog)
Siberian Husky
Great Dane
Pug
Chihuahua=Chihuahua (dog)
Shih Tzu
Border Collie
Australian Shepherd
Dalmatian=Dalmatian (dog)
Doberman=Dobermann
Pomeranian=Pomeranian dog
Bernese Mountain Dog
Saint Bernard=St. Bernard (dog)
Basset Hound
Bloodhound
Greyhound
Whippet
Afghan Hound
Shiba Inu
Akita=Akita (dog)
Chow Chow
Cavalier King Charles Spaniel
Cocker Spaniel=American Cocker Spaniel
Boston Terrier
Maltese=Maltese dog
Bichon Frise
Schnauzer=Miniature Schnauzer
Newfoundland=Newfoundland dog
Old English Sheepdog
Shetland Sheepdog
Weimaraner
Vizsla
Rhodesian Ridgeback
Jack Russell Terrier
Bull Terrier
Pit Bull=American Pit Bull Terrier
Samoyed=Samoyed dog
Alaskan Malamute
Mastiff=English Mastiff
Irish Wolfhound
Shar Pei
Papillon=Papillon dog
Goldendoodle
Bulldog
"""),
 "Flowers": WPL("""
Rose
Tulip
Sunflower=Common sunflower
Daisy=Bellis perennis
Lily=Lilium
Orchid=Orchidaceae
Lavender=Lavandula
Daffodil=Narcissus (plant)
Carnation=Dianthus caryophyllus
Hydrangea
Peony=Paeonia
Lotus=Nelumbo nucifera
Dandelion=Taraxacum
Poppy=Papaver rhoeas
Iris=Iris (plant)
Marigold=Tagetes
Chrysanthemum
Magnolia
Cherry blossom
Hibiscus
Lilac=Syringa vulgaris
Gardenia
Jasmine
Bird of paradise=Strelitzia reginae
Venus flytrap
Water lily=Nymphaeaceae
Morning glory
Pansy
Snapdragon=Antirrhinum
Zinnia
Dahlia
Gerbera
Calla lily=Zantedeschia aethiopica
Tiger lily=Lilium lancifolium
Bluebell=Hyacinthoides non-scripta
Forget-me-not=Myosotis
Foxglove=Digitalis purpurea
Lily of the valley
Hyacinth=Hyacinthus orientalis
Camellia
Azalea
Begonia
Petunia
Gladiolus
Cosmos=Cosmos bipinnatus
Protea=Protea cynaroides
Edelweiss=Leontopodium nivale
Bleeding heart=Lamprocapnos
Sweet pea=Lathyrus odoratus
Wisteria
Bougainvillea
Poinsettia
Corpse flower=Amorphophallus titanum
"""),
 "Musical Instruments": WPL("""
Piano
Acoustic guitar
Electric guitar
Violin
Cello
Double bass
Harp
Trumpet
Trombone
French horn
Tuba
Saxophone
Clarinet
Flute=Western concert flute
Oboe
Bassoon
Piccolo
Drum kit
Snare drum
Xylophone
Timpani
Tambourine
Triangle=Triangle (musical instrument)
Accordion
Harmonica
Banjo
Mandolin
Ukulele
Bagpipes
Sitar
Harpsichord
Pipe organ
Bongo drums=Bongo drum
Cowbell=Cowbell (instrument)
Maracas
Steelpan
Didgeridoo
Theremin
Kazoo
Recorder=Recorder (musical instrument)
Glockenspiel
Cymbal
Synthesizer
Keytar
Bugle
Sousaphone
Gong
Djembe
Castanets
Lute
"""),
 "Human Anatomy": WPL("""
Heart
Brain=Human brain
Lungs=Lung
Liver
Kidney
Stomach
Small intestine
Large intestine
Skull
Spine=Vertebral column
Rib cage
Pelvis
Femur
Eye=Human eye
Ear
Tooth=Human tooth
Tongue
Pancreas
Spleen
Gallbladder
Bladder=Urinary bladder
Thyroid
Esophagus
Trachea
Diaphragm=Thoracic diaphragm
Biceps
Hand
Foot
Larynx
Collarbone=Clavicle
Kneecap=Patella
Shoulder blade=Scapula
Jawbone=Mandible
Sternum
Tibia
Humerus
Appendix=Appendix (anatomy)
Tonsils=Tonsil
Fingernail=Nail (anatomy)
Gluteus maximus
Quadriceps=Quadriceps femoris muscle
Pectoral muscle=Pectoralis major
Abs=Rectus abdominis muscle
Achilles tendon
Cerebellum
Spinal cord
Aorta
"""),
 "Ballroom Dance": WPL("""
Waltz
Viennese Waltz=Viennese waltz
Tango
Argentine Tango=Argentine tango
Foxtrot
Quickstep
Cha-cha=Cha-cha-cha (dance)
Rumba=Ballroom rumba
Samba=Samba (ballroom dance)
Paso Doble=Paso doble
Jive=Jive (dance)
Salsa=Salsa (dance)
Mambo=Mambo (dance)
Swing=Swing (dance)
Lindy Hop
Merengue=Merengue (dance)
Bachata=Bachata (dance)
Bolero=Bolero (dance)
Charleston=Charleston (dance)
Two-Step=Country-western two-step
Polka
Lambada
Hustle=Hustle (dance)
West Coast Swing
Square Dance=Square dance
Minuet
Flamenco
"""),
 "Commercial Mascots": WPL("""
Flo (Progressive)=Flo (Progressive Insurance)
LiMu Emu (Liberty Mutual)=LiMu Emu
GEICO Gecko=Gecko (mascot)
Tony the Tiger
Ronald McDonald
Mr. Clean
Pillsbury Doughboy
Energizer Bunny
Kool-Aid Man
M&M's characters=M&M's spokescandies
Mr. Peanut
Michelin Man=Bibendum
Jolly Green Giant
Aflac Duck
Colonel Sanders
The Burger King=The Burger King
Jake from State Farm
Mayhem (Allstate)=Mayhem (character)
Chester Cheetah
Trix Rabbit
Lucky the Leprechaun
Cap'n Crunch
Snap, Crackle and Pop
Toucan Sam
Count Chocula
Elsie the Cow
Chuck E. Cheese=Chuck E. Cheese (character)
Rich Uncle Pennybags (Monopoly)=Rich Uncle Pennybags
Smokey Bear
McGruff the Crime Dog
Morris the Cat
Spuds MacKenzie
Gerber Baby
Old Spice Guy=The Man Your Man Could Smell Like
The Most Interesting Man in the World
Captain Morgan
Big Boy=Big Boy (mascot)
Taco Bell Chihuahua=Gidget (dog)
Budweiser Clydesdales
Hamburglar
Grimace=Grimace (character)
Sonny the Cuckoo Bird
Charmin Bears
Mr. Monopoly
Little Debbie
Wendy (Wendy's)=Wendy Thomas
Geoffrey the Giraffe
The Noid
Mr. Owl
Duracell Bunny=Duracell Bunny
Chiquita Banana=Miss Chiquita
Planters Mr. Peanut
Tidy Bowl Man
Sonic Drive-In guys
Nipper
Poppin' Fresh
Jack Box
"""),
 "Cartoon Characters": WPL("""
Bugs Bunny
Daffy Duck
Porky Pig
Tweety
Sylvester=Sylvester the Cat
Wile E. Coyote and Road Runner=Wile E. Coyote and the Road Runner
Tom (Tom and Jerry)=Tom Cat
Jerry (Tom and Jerry)=Jerry Mouse
Scooby-Doo=Scooby-Doo (character)
Shaggy=Shaggy Rogers
Fred Flintstone
Barney Rubble
George Jetson
Yogi Bear
Homer Simpson
Bart Simpson
Marge Simpson
Lisa Simpson
SpongeBob SquarePants=SpongeBob SquarePants (character)
Patrick Star
Squidward Tentacles
Mr. Krabs
Plankton=Plankton and Karen
Sandy Cheeks
Peter Griffin
Stewie Griffin
Eric Cartman
Popeye
Olive Oyl
Garfield=Garfield (character)
Snoopy
Charlie Brown
Woody Woodpecker
Pink Panther=The Pink Panther (character)
Dora the Explorer=Dora (character)
Peppa Pig=Peppa Pig (character)
Bluey=Bluey (character)
Tommy Pickles
Johnny Bravo=Johnny Bravo (character)
Dexter (Dexter's Laboratory)=Dexter (Dexter's Laboratory)
Courage the Cowardly Dog=Courage (character)
Rick Sanchez
Morty Smith
Bob Belcher
Hank Hill
Shrek=Shrek (character)
Donkey (Shrek)=Donkey (Shrek)
Puss in Boots=Puss in Boots (Shrek)
Po (Kung Fu Panda)=Po (Kung Fu Panda)
Gru=Gru (Despicable Me)
Minions=Minions (Despicable Me)
Casper=Casper the Friendly Ghost
Betty Boop
Felix the Cat
Arthur=Arthur Read
Clifford the Big Red Dog=Clifford the Big Red Dog (character)
Curious George=Curious George (character)
Powerpuff Girls=The Powerpuff Girls (characters)
Finn and Jake (Adventure Time)=Finn the Human
Aang=Aang
Jimmy Neutron
Timmy Turner
Danny Phantom=Danny Phantom (character)
Ben 10=Ben Tennyson
Steven Universe=Steven Universe (character)
Daria=Daria Morgendorffer
Beavis and Butt-Head=Beavis and Butt-Head (characters)
Marvin the Martian
Pepé Le Pew
Foghorn Leghorn
Speedy Gonzales
Tasmanian Devil=Tasmanian Devil (Looney Tunes)
Elmer Fudd
"""),
 "Pop Stars (more)": WPL("""
Justin Bieber
Ed Sheeran
Bruno Mars
Harry Styles
The Weeknd
Shawn Mendes
Justin Timberlake
Michael Jackson
Elton John
Post Malone
Charlie Puth
Sam Smith
Lewis Capaldi
Nick Jonas
Joe Jonas
Zayn Malik
Niall Horan
Benson Boone
Usher=Usher (musician)
Jason Derulo
Pitbull=Pitbull (rapper)
Ricky Martin
Enrique Iglesias
George Michael
Prince=Prince (musician)
Freddie Mercury
Adam Levine
Lil Nas X
Bad Bunny
Troye Sivan
Conan Gray
Teddy Swims
Lionel Richie
Stevie Wonder
Robbie Williams
Tyla=Tyla (singer)
Raye=Raye (singer)
Jennie=Jennie (singer)
Rosé=Rosé (singer)
Lana Del Rey
Ellie Goulding
Sia=Sia (musician)
Janet Jackson
Celine Dion
Fergie=Fergie (singer)
Paula Abdul
Hilary Duff
Kylie Minogue
Rita Ora
Reneé Rapp
Addison Rae
"""),
 "Famous Athletes (more)": WPL("""
Mike Trout
Mookie Betts
Bryce Harper
Kylian Mbappé
Neymar
David Beckham
Erling Haaland
Megan Rapinoe
Alex Morgan
Mia Hamm
Lewis Hamilton
Max Verstappen
Sidney Crosby
Alexander Ovechkin
Connor McDavid
Naomi Osaka
Coco Gauff
Carlos Alcaraz
Maria Sharapova
Andre Agassi
Rory McIlroy
Scottie Scheffler
Jack Nicklaus
Arnold Palmer
Mike Tyson
Conor McGregor
Ronda Rousey
Sha'Carri Richardson
Noah Lyles
Florence Griffith Joyner
Carl Lewis
Mary Lou Retton
Nadia Comăneci
Sunisa Lee
Gabby Douglas
Apolo Ohno
Chloe Kim
Eileen Gu
Mikaela Shiffrin
Dale Earnhardt Jr.
Danica Patrick
Jeff Gordon
A'ja Wilson
Sue Bird
Diana Taurasi
Paige Bueckers
Kevin Durant
Mia Hamm
Tom Brady
"""),
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
