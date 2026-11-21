# Square Off

A party trivia game for the TV. Everyone gets a square and a category. Players duel their neighbors on dueling clocks; the loser's squares go to the winner. Last one standing owns the board.

## Run it

It's a static site with no build step: open `index.html` through any web server, or deploy the folder to Vercel (framework preset: **Other**, no build command, output directory: root).

Locally: `python3 -m http.server` in this folder, then open http://localhost:8000.

## How it's put together

- `index.html` — the whole game (setup, board, duels, scoring).
- `photos/index.json` — the photo categories and their answers; `photos/ph-*.json` — each category's photos as data URIs.
- `states.json`, `countries.json` — outlines for State Capitals and Geography.
- `tools/` — scripts used to download, merge and pack photos (`pack_photos.py` rebuilds `photos/` from a folder of `Category/Answer.jpg` files).

Host controls during a duel: **Space** correct, **P** pass, **S** skip clue, **A** show answer to host, **Esc** pause.
