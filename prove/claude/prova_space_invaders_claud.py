import pygame
import random
import sys

# ── Costanti ────────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 800, 600
FPS = 60

BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
GREEN  = (0,   255, 0)
RED    = (255, 0,   0)
CYAN   = (0,   255, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (180, 0,   255)

ALIEN_COLS  = 11
ALIEN_ROWS  = 5
ALIEN_X_GAP = 60
ALIEN_Y_GAP = 50
ALIEN_START_X = 80
ALIEN_START_Y = 80

BARRIER_COUNT   = 4
BARRIER_W       = 70
BARRIER_H       = 50
BARRIER_BLOCK   = 7          # pixel per ogni blocchetto
BARRIER_Y       = SCREEN_H - 130

PLAYER_SPEED    = 5
BULLET_SPEED    = 8
ALIEN_BULLET_SPEED = 4
ALIEN_DROP      = 18
ALIEN_BASE_SPEED = 0.8       # pixel per frame a piena formazione

UFO_SPEED       = 2
UFO_Y           = 40
UFO_INTERVAL    = (15, 30)   # secondi fra apparizioni


# ── Sprite del giocatore (pixel art 13×8) ───────────────────────────────────
PLAYER_SPRITE = [
    "      X      ",
    "     XXX     ",
    "     XXX     ",
    " XXXXXXXXXXX ",
    "XXXXXXXXXXXXX",
    "XXXXXXXXXXXXX",
    "XX  XXXXX  XX",
    "X    XXX    X",
]

# ── Sprite alieni per riga (pixel art 11×8) ──────────────────────────────────
ALIEN_SPRITES = {
    0: (PURPLE, [          # riga 0 – octopus
        " XXXX  XXXX ",
        "XXXXXXXXXXXX",
        "XX  XXXXXX  ",
        "XXXXXXXXXXXX",
        "  XXXXXXXX  ",
        "   X    X   ",
        "  X  XX  X  ",
        " X        X ",
    ]),
    1: (CYAN, [            # righe 1-2 – crab
        "  X     X  ",
        "   X   X   ",
        "  XXXXXXX  ",
        " XX XXX XX ",
        " XXXXXXXXX ",
        " X XXXXX X ",
        " X       X ",
        "  X     X  ",
    ]),
    2: (CYAN, [
        "  X     X  ",
        "   X   X   ",
        "  XXXXXXX  ",
        " XX XXX XX ",
        " XXXXXXXXX ",
        " X XXXXX X ",
        " X       X ",
        "  X     X  ",
    ]),
    3: (GREEN, [           # righe 3-4 – squid
        "   XXXXX   ",
        " XXXXXXXXX ",
        "XXXXXXXXXXX",
        "XXX     XXX",
        "XXXXXXXXXXX",
        "  XX   XX  ",
        " X  X X  X ",
        "X   X X   X",
    ]),
    4: (GREEN, [
        "   XXXXX   ",
        " XXXXXXXXX ",
        "XXXXXXXXXXX",
        "XXX     XXX",
        "XXXXXXXXXXX",
        "  XX   XX  ",
        " X  X X  X ",
        "X   X X   X",
    ]),
}

ALIEN_POINTS = {0: 30, 1: 20, 2: 20, 3: 10, 4: 10}


def make_surf_from_sprite(lines, color, scale=2):
    """Crea una Surface pygame da una lista di stringhe."""
    h = len(lines)
    w = max(len(l) for l in lines)
    surf = pygame.Surface((w * scale, h * scale), pygame.SRCALPHA)
    for y, row in enumerate(lines):
        for x, ch in enumerate(row):
            if ch == 'X':
                pygame.draw.rect(surf, color,
                                 (x * scale, y * scale, scale, scale))
    return surf


# ── Classi ──────────────────────────────────────────────────────────────────

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = make_surf_from_sprite(PLAYER_SPRITE, GREEN, scale=3)
        self.rect  = self.image.get_rect()
        self.rect.centerx = SCREEN_W // 2
        self.rect.bottom   = SCREEN_H - 20
        self.lives  = 3
        self.score  = 0
        self.dead   = False
        self.respawn_timer = 0

    def update(self, keys):
        if self.dead:
            self.respawn_timer -= 1
            if self.respawn_timer <= 0:
                self.dead = False
            return
        if keys[pygame.K_LEFT]  and self.rect.left  > 0:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_W:
            self.rect.x += PLAYER_SPEED

    def hit(self):
        self.lives -= 1
        self.dead  = True
        self.respawn_timer = FPS * 1   # 1 secondo di pausa


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, dy, color=WHITE):
        super().__init__()
        self.image = pygame.Surface((3, 12))
        self.image.fill(color)
        self.rect  = self.image.get_rect(centerx=x, top=y)
        self.dy    = dy

    def update(self):
        self.rect.y += self.dy
        if self.rect.bottom < 0 or self.rect.top > SCREEN_H:
            self.kill()


class Alien(pygame.sprite.Sprite):
    def __init__(self, row, col):
        super().__init__()
        color, lines = ALIEN_SPRITES[row]
        self.image = make_surf_from_sprite(lines, color, scale=2)
        self.rect  = self.image.get_rect()
        self.row   = row
        self.col   = col
        self.points = ALIEN_POINTS[row]

    def place(self, x, y):
        self.rect.topleft = (x, y)


class BarrierBlock(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.health = 3
        self.image  = pygame.Surface((BARRIER_BLOCK, BARRIER_BLOCK))
        self._redraw()
        self.rect   = self.image.get_rect(topleft=(x, y))

    def _redraw(self):
        colors = [GREEN, YELLOW, ORANGE]
        self.image.fill(colors[self.health - 1])

    def hit(self):
        self.health -= 1
        if self.health <= 0:
            self.kill()
        else:
            self._redraw()


class UFO(pygame.sprite.Sprite):
    UFO_SPRITE = [
        "    XXXXXX    ",
        "  XXXXXXXXXX  ",
        " XXXXXXXXXXXX ",
        "XX  XX  XX  XX",
        "XXXXXXXXXXXXXX",
        "  XXX  XXX    ",
    ]

    def __init__(self):
        super().__init__()
        self.image = make_surf_from_sprite(self.UFO_SPRITE, RED, scale=2)
        self.rect  = self.image.get_rect()
        self.direction = random.choice([-1, 1])
        if self.direction == 1:
            self.rect.right = 0
        else:
            self.rect.left  = SCREEN_W
        self.rect.y = UFO_Y

    def update(self):
        self.rect.x += UFO_SPEED * self.direction
        if self.rect.right < 0 or self.rect.left > SCREEN_W:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, cx, cy, color=WHITE):
        super().__init__()
        self.image  = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (10, 10), 10)
        self.rect   = self.image.get_rect(center=(cx, cy))
        self.timer  = 20

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.kill()


# ── Logica principale del gioco ─────────────────────────────────────────────

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Space Invaders")
        self.clock  = pygame.time.Clock()
        self.font_big   = pygame.font.SysFont("monospace", 36, bold=True)
        self.font_small = pygame.font.SysFont("monospace", 20)
        self.state  = "menu"   # menu | playing | gameover | win
        self._init_game()

    def _init_game(self):
        self.wave   = 1
        self.all_sprites    = pygame.sprite.Group()
        self.aliens         = pygame.sprite.Group()
        self.barriers       = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.alien_bullets  = pygame.sprite.Group()
        self.ufo_group      = pygame.sprite.Group()
        self.explosions     = pygame.sprite.Group()

        self.player = Player()
        self.all_sprites.add(self.player)

        self._spawn_aliens()
        self._spawn_barriers()

        # Movimento alieni
        self.alien_dir     = 1        # +1 = destra, -1 = sinistra
        self.alien_step_x  = 0.0
        self.alien_move_timer = 0
        self.alien_move_interval = 40  # frame fra uno step e il successivo

        # Sparo alieni
        self.alien_shoot_timer = 0
        self.alien_shoot_interval = FPS * 1  # ogni ~1 secondo uno sparo

        # UFO
        self.ufo_timer    = FPS * random.randint(*UFO_INTERVAL)
        self.ufo_spawned  = False

    def _spawn_aliens(self):
        for row in range(ALIEN_ROWS):
            for col in range(ALIEN_COLS):
                a = Alien(row, col)
                x = ALIEN_START_X + col * ALIEN_X_GAP
                y = ALIEN_START_Y + row * ALIEN_Y_GAP + (self.wave - 1) * 10
                y = max(y, ALIEN_START_Y)
                a.place(x, y)
                self.aliens.add(a)
                self.all_sprites.add(a)

    def _spawn_barriers(self):
        spacing = SCREEN_W // (BARRIER_COUNT + 1)
        for i in range(BARRIER_COUNT):
            bx = spacing * (i + 1) - BARRIER_W // 2
            for row in range(BARRIER_H // BARRIER_BLOCK):
                for col in range(BARRIER_W // BARRIER_BLOCK):
                    # Rimuovi gli angoli per forma ad arco
                    if row == 0 and (col < 2 or col >= BARRIER_W // BARRIER_BLOCK - 2):
                        continue
                    b = BarrierBlock(bx + col * BARRIER_BLOCK,
                                     BARRIER_Y + row * BARRIER_BLOCK)
                    self.barriers.add(b)
                    self.all_sprites.add(b)

    def _alien_speed(self):
        """Più alieni muoiono, più veloci diventano."""
        total   = ALIEN_COLS * ALIEN_ROWS
        alive   = len(self.aliens)
        ratio   = alive / total          # 1 → tutti vivi, ~0 → quasi tutti morti
        speed   = ALIEN_BASE_SPEED + (1 - ratio) * 3.0
        speed  *= 1 + (self.wave - 1) * 0.15
        return speed

    def _move_aliens(self):
        if not self.aliens:
            return
        self.alien_move_timer += 1
        interval = max(5, int(self.alien_move_interval / self._alien_speed()))
        if self.alien_move_timer < interval:
            return
        self.alien_move_timer = 0

        step = 8 * self.alien_dir
        # Controlla se qualcuno tocca il bordo
        hit_edge = False
        for a in self.aliens:
            if (self.alien_dir == 1  and a.rect.right  + step > SCREEN_W - 10) or \
               (self.alien_dir == -1 and a.rect.left   + step < 10):
                hit_edge = True
                break

        if hit_edge:
            for a in self.aliens:
                a.rect.y += ALIEN_DROP
            self.alien_dir *= -1
        else:
            for a in self.aliens:
                a.rect.x += step

    def _alien_shoot(self):
        if not self.aliens:
            return
        self.alien_shoot_timer += 1
        interval = max(20, self.alien_shoot_interval - self.wave * 5)
        if self.alien_shoot_timer < interval:
            return
        self.alien_shoot_timer = 0

        # Scegli un alieno a caso dalla colonna più bassa
        cols = {}
        for a in self.aliens:
            if a.col not in cols or a.rect.bottom > cols[a.col].rect.bottom:
                cols[a.col] = a
        shooter = random.choice(list(cols.values()))
        b = Bullet(shooter.rect.centerx, shooter.rect.bottom,
                   ALIEN_BULLET_SPEED, RED)
        self.alien_bullets.add(b)
        self.all_sprites.add(b)

    def _ufo_logic(self):
        self.ufo_timer -= 1
        if self.ufo_timer <= 0 and not self.ufo_group:
            ufo = UFO()
            self.ufo_group.add(ufo)
            self.all_sprites.add(ufo)
            self.ufo_timer = FPS * random.randint(*UFO_INTERVAL)

    def _check_collisions(self):
        # Proiettile giocatore ↔ alieni
        hits = pygame.sprite.groupcollide(
            self.aliens, self.player_bullets, True, True)
        for alien, bullets in hits.items():
            self.player.score += alien.points
            exp = Explosion(alien.rect.centerx, alien.rect.centery, GREEN)
            self.explosions.add(exp)
            self.all_sprites.add(exp)

        # Proiettile giocatore ↔ UFO
        ufo_hits = pygame.sprite.groupcollide(
            self.ufo_group, self.player_bullets, True, True)
        for ufo, _ in ufo_hits.items():
            bonus = random.choice([50, 100, 150, 200, 300])
            self.player.score += bonus
            exp = Explosion(ufo.rect.centerx, ufo.rect.centery, RED)
            self.explosions.add(exp)
            self.all_sprites.add(exp)

        # Proiettile alieno ↔ giocatore
        if not self.player.dead:
            hits = pygame.sprite.spritecollide(
                self.player, self.alien_bullets, True)
            if hits:
                exp = Explosion(self.player.rect.centerx,
                                self.player.rect.centery, WHITE)
                self.explosions.add(exp)
                self.all_sprites.add(exp)
                self.player.hit()

        # Proiettili ↔ barriere
        pygame.sprite.groupcollide(
            self.barriers, self.player_bullets, False, True,
            collided=lambda b, _: (b.hit(), True)[1])
        pygame.sprite.groupcollide(
            self.barriers, self.alien_bullets, False, True,
            collided=lambda b, _: (b.hit(), True)[1])

        # Alieni ↔ barriere (le distruggono al contatto)
        pygame.sprite.groupcollide(
            self.barriers, self.aliens, True, False)

    def _check_win_lose(self):
        if self.player.lives <= 0:
            self.state = "gameover"
            return
        # Alieni arrivati in fondo
        for a in self.aliens:
            if a.rect.bottom >= SCREEN_H - 60:
                self.state = "gameover"
                return
        # Tutti gli alieni distrutti
        if not self.aliens:
            self.wave += 1
            self._next_wave()

    def _next_wave(self):
        # Pulisci proiettili e rifai formazione + barriere
        self.player_bullets.empty()
        self.alien_bullets.empty()
        for g in (self.all_sprites,):
            for s in list(g):
                if isinstance(s, (Bullet, Alien, BarrierBlock, UFO, Explosion)):
                    s.kill()
        self.ufo_group.empty()
        self.barriers.empty()
        self.explosions.empty()
        self._spawn_aliens()
        self._spawn_barriers()
        self.alien_move_timer = 0
        self.alien_shoot_timer = 0
        self.ufo_timer = FPS * random.randint(*UFO_INTERVAL)

    def _draw_hud(self):
        score_surf = self.font_small.render(
            f"SCORE: {self.player.score}", True, WHITE)
        lives_surf = self.font_small.render(
            f"LIVES: {self.player.lives}", True, GREEN)
        wave_surf  = self.font_small.render(
            f"WAVE: {self.wave}", True, YELLOW)
        self.screen.blit(score_surf, (10, 10))
        self.screen.blit(lives_surf, (SCREEN_W // 2 - 50, 10))
        self.screen.blit(wave_surf,  (SCREEN_W - 130, 10))
        # Linea orizzontale separatrice
        pygame.draw.line(self.screen, GREEN, (0, 35), (SCREEN_W, 35), 1)
        pygame.draw.line(self.screen, GREEN,
                         (0, SCREEN_H - 10), (SCREEN_W, SCREEN_H - 10), 1)

    def _draw_menu(self):
        self.screen.fill(BLACK)
        title = self.font_big.render("SPACE INVADERS", True, GREEN)
        sub   = self.font_small.render("Premi INVIO per iniziare", True, WHITE)
        ctrl  = self.font_small.render("← → per muoversi  |  SPAZIO per sparare", True, CYAN)
        self.screen.blit(title, title.get_rect(center=(SCREEN_W//2, SCREEN_H//2 - 60)))
        self.screen.blit(sub,   sub.get_rect(center=(SCREEN_W//2, SCREEN_H//2 + 20)))
        self.screen.blit(ctrl,  ctrl.get_rect(center=(SCREEN_W//2, SCREEN_H//2 + 60)))

    def _draw_gameover(self):
        self.screen.fill(BLACK)
        go   = self.font_big.render("GAME OVER", True, RED)
        sc   = self.font_small.render(
            f"Punteggio finale: {self.player.score}", True, WHITE)
        again = self.font_small.render("Premi INVIO per ricominciare", True, CYAN)
        self.screen.blit(go,    go.get_rect(center=(SCREEN_W//2, SCREEN_H//2 - 60)))
        self.screen.blit(sc,    sc.get_rect(center=(SCREEN_W//2, SCREEN_H//2)))
        self.screen.blit(again, again.get_rect(center=(SCREEN_W//2, SCREEN_H//2 + 60)))

    # ── Loop principale ──────────────────────────────────────────────────────

    def run(self):
        player_can_shoot = True

        while True:
            self.clock.tick(FPS)
            keys = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if self.state == "menu" and event.key == pygame.K_RETURN:
                        self.state = "playing"

                    elif self.state == "gameover" and event.key == pygame.K_RETURN:
                        self._init_game()
                        self.state = "playing"

                    elif self.state == "playing":
                        if event.key == pygame.K_SPACE and player_can_shoot:
                            if not self.player.dead and \
                               len(self.player_bullets) == 0:
                                b = Bullet(self.player.rect.centerx,
                                           self.player.rect.top,
                                           -BULLET_SPEED, WHITE)
                                self.player_bullets.add(b)
                                self.all_sprites.add(b)

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        player_can_shoot = True

            # ── Aggiornamento ────────────────────────────────────────────────
            if self.state == "playing":
                self.player.update(keys)
                self.player_bullets.update()
                self.alien_bullets.update()
                self.ufo_group.update()
                self.explosions.update()

                self._move_aliens()
                self._alien_shoot()
                self._ufo_logic()
                self._check_collisions()
                self._check_win_lose()

            # ── Rendering ────────────────────────────────────────────────────
            self.screen.fill(BLACK)

            if self.state == "menu":
                self._draw_menu()

            elif self.state == "gameover":
                self._draw_gameover()

            elif self.state == "playing":
                self.all_sprites.draw(self.screen)
                self._draw_hud()

                # Flash del giocatore quando morto
                if self.player.dead:
                    if (self.player.respawn_timer // 5) % 2 == 0:
                        self.screen.blit(self.player.image, self.player.rect)

            pygame.display.flip()


if __name__ == "__main__":
    Game().run()
