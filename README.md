# Sapphirine Spire

Full-colour Python 3 neon ring-hop arcade for ElbowOS.

A gem rides spinning elliptical gates. Leap when the copper gap lines up and climb the spire. Misses break the streak.

This is an original arcade. It is not a Nintendo ROM, not an emulator, and it does not use trademarked characters.

## Play

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 sapphirine_spire.py --play
```

A / D or arrows orbit. Space or W hops. R restarts. Esc quits.

## Record a 9:16 reel

```bash
python3 sapphirine_spire.py --record
```

Headless autoplay writes a 15 second 1080x1920 H.264 MP4 (yuv420p, CRF 20, +faststart).

- Featured account: https://x.com/ElbowOS
- Drive reel: https://drive.google.com/file/d/1dwZc7qNlS6ugawVe1NCjnlAQ6icw0-1p/view
