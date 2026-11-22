# Square Off

A party trivia game for the TV. Everyone gets a square and a category. Players duel their neighbors on dueling clocks; the loser's squares go to the winner. Last one standing owns the board.

## Run it

It's a static site with no build step: open `index.html` through any web server, or deploy the folder to Vercel (framework preset: **Other**, no build command, output directory: root).

Locally: `python3 -m http.server` in this folder, then open http://localhost:8000.

## How it's put together

- `index.html` — the whole game (setup, board, duels, scoring).
- `photos/index.json` — the photo categories and their answers; `photos/ph-*.json` — each category's photos as data URIs.
- `states.json` — outlines for State Capitals; `world.json` — world map for Geography (target country highlighted among its neighbors).
- `tools/` — scripts used to download, merge and pack photos (`pack_photos.py` rebuilds `photos/` from a folder of `Category/Answer.jpg` files).

## Phone remote

On the board screen, press **Phone remote** and scan the QR code with the host's phone. The phone shows each clue with its answer and has big **Correct**, **Pass** (−3 seconds and a new clue), **Skip** and **Pause** buttons, plus all the board controls. It connects directly to the TV page through PeerJS, so keep both devices on the same Wi-Fi. The remote works on the deployed site, not inside the Claude preview.

Keyboard controls on the TV during a duel: **Space** correct, **P** pass, **S** skip clue, **A** show answer to host, **M** music on/off, **Esc** pause.

Duel music is an original chiptune loop generated live with the Web Audio API (no audio files). It speeds up when the player on the clock drops under 10 seconds.
