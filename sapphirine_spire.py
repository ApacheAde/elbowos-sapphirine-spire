#!/usr/bin/env python3
"""Sapphirine Spire — neon ring-hop climber for ElbowOS. Python 3 + pygame.

Ride a gem around spinning elliptical gates. Leap when the copper gap
lines up. A / D or arrows orbit, Space / W hop. --play for a window,
--record for a 15s 9:16 reel (default).
"""
import math, os, random, subprocess, sys

os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get("ELBOWOS_MP4", "/home/workdir/artifacts/SAPPHIRINE_SPIRE_ElbowOS.mp4")
TITLE, HANDLE = "SAPPHIRINE SPIRE", "x.com/ElbowOS"
INK = (4, 14, 18)
TEAL = (18, 72, 78)
COPPER = (232, 122, 54)
SAPP = (64, 224, 196)
GOLD = (255, 214, 120)
MAG = (255, 72, 168)
WHITE = (236, 250, 248)

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.Font(None, 92)
        self.mid = pygame.font.Font(None, 54)
        self.small = pygame.font.Font(None, 40)
        flags = 0 if "--play" in sys.argv else pygame.HIDDEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            pygame.display.quit()
            pygame.display.init()
            self.screen = pygame.display.set_mode((W, H), pygame.HIDDEN)
        pygame.display.set_caption(TITLE)
        self.motes = [(random.randrange(W), random.randrange(H), random.uniform(0.4, 1.6)) for _ in range(70)]
        self.reset()

    def reset(self):
        self.t = 0.0
        self.score = 0
        self.streak = 0
        self.idx = 0
        self.p_ang = 20.0
        self.orbit = 90.0
        self.cool = 0.0
        self.flash = 0.0
        self.trail = []
        self.pops = []
        self.rings = []
        for i in range(8):
            self.rings.append({
                "y": 340 + i * 175,
                "r": 250 + (i % 3) * 28,
                "ang": random.uniform(0, 360),
                "spin": random.choice((-1, 1)) * random.uniform(55, 90),
                "gap": 78,
                "hot": 0.0,
            })

    def hop(self, forced=False):
        ring = self.rings[self.idx]
        diff = abs((self.p_ang - ring["ang"] + 180) % 360 - 180)
        ok = diff < ring["gap"] * 0.42
        if self.cool > 0:
            return
        if ok or forced:
            ring["hot"] = 1.0
            self.idx = (self.idx + 1) % len(self.rings)
            self.streak = self.streak + 1 if ok else 0
            gain = 100 + self.streak * 20 if ok else 10
            self.score += gain
            self.flash = 0.35
            self.cool = 0.22
            x, y = self.pos(self.rings[self.idx])
            self.pops.append([x, y, 1.0, f"+{gain}"])
        else:
            self.streak = 0
            self.score = max(0, self.score - 25)
            self.cool = 0.28
            self.flash = 0.2

    def pos(self, ring):
        a = math.radians(self.p_ang)
        x = W / 2 + math.cos(a) * ring["r"]
        y = ring["y"] + math.sin(a) * ring["r"] * 0.42
        return x, y

    def update(self, dt, do_hop, auto=False):
        self.t += dt
        self.cool = max(0, self.cool - dt)
        self.flash = max(0, self.flash - dt)
        self.p_ang = (self.p_ang + self.orbit * dt) % 360
        for ring in self.rings:
            ring["ang"] = (ring["ang"] + ring["spin"] * dt) % 360
            ring["hot"] = max(0, ring["hot"] - dt * 2.2)
        if auto:
            ring = self.rings[self.idx]
            delta = (ring["ang"] - self.p_ang + 180) % 360 - 180
            self.orbit = max(-220, min(220, delta * 4.5))
            if abs(delta) < ring["gap"] * 0.45 and self.cool <= 0:
                self.hop()
        elif do_hop:
            self.hop()
        self.motes = [(x, (y + sp * 40 * dt) % H, sp) for x, y, sp in self.motes]
        self.pops = [p for p in self.pops if p[2] > 0]
        for p in self.pops:
            p[1] -= 50 * dt
            p[2] -= dt

    def draw_ring(self, ring, focus):
        r = ring["r"]
        rect = pygame.Rect(0, 0, int(r * 2), int(r * 0.84))
        rect.center = (W // 2, ring["y"])
        col = COPPER if focus else SAPP
        if ring["hot"] > 0:
            col = GOLD
        gap = math.radians(ring["gap"])
        start = math.radians(ring["ang"]) + gap / 2
        end = start + math.tau - gap
        pygame.draw.arc(self.screen, (12, 40, 44), rect.inflate(18, 10), 0, math.tau, 10)
        pygame.draw.arc(self.screen, col, rect, start, end, 8 if focus else 5)
        a = math.radians(ring["ang"])
        gx = W / 2 + math.cos(a) * r
        gy = ring["y"] + math.sin(a) * r * 0.42
        pygame.draw.circle(self.screen, MAG, (int(gx), int(gy)), 10)

    def draw(self):
        surf = self.screen
        surf.fill(INK)
        for y in range(0, H, 8):
            shade = 8 + int(18 * y / H)
            pygame.draw.line(surf, (shade, shade + 10, shade + 12), (0, y), (W, y))
        pygame.draw.polygon(surf, (10, 36, 40), [(W // 2, 180), (180, H - 80), (W - 180, H - 80)])
        for x, y, sp in self.motes:
            pygame.draw.circle(surf, (40, 120, 110), (int(x), int(y)), 2)
        for i, ring in enumerate(self.rings):
            self.draw_ring(ring, i == self.idx)
        x, y = self.pos(self.rings[self.idx])
        self.trail.append((x, y))
        self.trail = self.trail[-14:]
        for i, (tx, ty) in enumerate(self.trail):
            pygame.draw.circle(surf, SAPP, (int(tx), int(ty)), 3 + i // 4)
        pygame.draw.circle(surf, (255, 170, 70), (int(x), int(y)), 24)
        pygame.draw.circle(surf, WHITE, (int(x), int(y)), 12)
        for px, py, life, text in self.pops:
            lab = self.small.render(text, True, GOLD)
            lab.set_alpha(int(255 * max(life, 0)))
            surf.blit(lab, lab.get_rect(center=(px, py)))
        banner = self.font.render(TITLE, True, SAPP)
        surf.blit(banner, banner.get_rect(center=(W // 2, 110)))
        sc = self.mid.render(f"SCORE  {self.score}", True, GOLD)
        surf.blit(sc, sc.get_rect(center=(W // 2, 190)))
        st = self.small.render(f"STREAK  {self.streak}", True, WHITE)
        surf.blit(st, st.get_rect(center=(W // 2, 240)))
        handle = self.mid.render(HANDLE, True, COPPER)
        surf.blit(handle, handle.get_rect(center=(W // 2, H - 90)))
        hint = self.small.render("SPACE hop   A/D orbit", True, TEAL)
        surf.blit(hint, hint.get_rect(center=(W // 2, H - 42)))

    def play(self):
        clock = pygame.time.Clock()
        left = right = False
        while True:
            hop = False
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return
                if ev.type == pygame.KEYDOWN:
                    if ev.key in (pygame.K_ESCAPE, pygame.K_q):
                        return
                    if ev.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                        hop = True
                    if ev.key == pygame.K_r:
                        self.reset()
                    left = left or ev.key in (pygame.K_a, pygame.K_LEFT)
                    right = right or ev.key in (pygame.K_d, pygame.K_RIGHT)
                if ev.type == pygame.KEYUP:
                    if ev.key in (pygame.K_a, pygame.K_LEFT):
                        left = False
                    if ev.key in (pygame.K_d, pygame.K_RIGHT):
                        right = False
            self.orbit = -110 if left else 110 if right else 78
            self.update(1 / FPS, hop, auto=False)
            self.draw()
            pygame.display.flip()
            clock.tick(FPS)

    def record(self):
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-an",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
            "-preset", "veryfast", "-movflags", "+faststart", OUT,
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        frames = FPS * SECS
        try:
            for n in range(frames):
                self.orbit = 96 if (n // 45) % 2 == 0 else -70
                self.update(1 / FPS, False, auto=True)
                self.draw()
                proc.stdin.write(pygame.image.tobytes(self.screen, "RGB"))
        finally:
            proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", "ignore")
        rc = proc.wait()
        if rc != 0 or not os.path.isfile(OUT) or os.path.getsize(OUT) < 10000:
            raise SystemExit(f"ffmpeg failed ({rc}):\n{err[-1500:]}")
        print("wrote", OUT, os.path.getsize(OUT), "score", self.score, "streak", self.streak)

def main():
    g = Game()
    if "--play" in sys.argv:
        g.play()
    else:
        g.record()
    pygame.quit()

if __name__ == "__main__":
    main()
