import pygame
import random
import sys

# Inizializzazione Pygame
pygame.init()

# Dimensioni Schermo e Colori
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 150, 255)

# Frequenza di aggiornamento
clock = pygame.time.Clock()
FPS = 60

# --- CLASSI DEL GIOCO ---

class Player:
    def __init__(self):
        self.width = 50
        self.height = 20
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 50
        self.speed = 5
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.bullet = None

    def move(self, dx):
        self.x += dx
        # Mantieni il giocatore nello schermo
        if self.x < 0: self.x = 0
        if self.x > WIDTH - self.width: self.x = WIDTH - self.width
        self.rect.x = self.x

    def draw(self, surface):
        pygame.draw.rect(surface, GREEN, self.rect)

    def shoot(self):
        if self.bullet is None:
            self.bullet = Bullet(self.x + self.width // 2 - 2, self.y, -10, GREEN)

class Alien:
    def __init__(self, x, y, score_value):
        self.width = 30
        self.height = 20
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.score_value = score_value

    def update_pos(self):
        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self, surface):
        pygame.draw.rect(surface, RED, self.rect)

class Bullet:
    def __init__(self, x, y, speed, color):
        self.width = 4
        self.height = 15
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.speed = speed
        self.color = color

    def move(self):
        self.rect.y += self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

class Barrier:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 15, 15)

    def draw(self, surface):
        pygame.draw.rect(surface, BLUE, self.rect)

# --- FUNZIONI DI GESTIONE ---

def create_aliens():
    aliens = []
    rows = 5
    cols = 11
    for r in range(rows):
        for c in range(cols):
            x = 50 + c * 50
            y = 50 + r * 40
            # Punteggio maggiore per le file più in alto
            score_value = 30 if r < 1 else (20 if r < 3 else 10)
            aliens.append(Alien(x, y, score_value))
    return aliens

def create_barriers():
    barriers = []
    # 4 blocchi di barriere
    for i in range(4):
        start_x = 100 + i * 180
        start_y = HEIGHT - 150
        # Creazione di un blocco di barriere distruttibili
        for row in range(4):
            for col in range(5):
                barriers.append(Barrier(start_x + col * 15, start_y + row * 15))
    return barriers

# --- LOOP PRINCIPALE ---

def main():
    player = Player()
    aliens = create_aliens()
    barriers = create_barriers()
    alien_bullets = []
    
    alien_speed = 1.0
    alien_direction = 1 # 1 = destra, -1 = sinistra
    
    score = 0
    lives = 3
    font = pygame.font.SysFont(None, 36)
    
    game_over = False
    victory = False

    running = True
    while running:
        clock.tick(FPS)
        screen.fill(BLACK)

        # 1. GESTIONE EVENTI
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over and not victory:
                    player.shoot()

        keys = pygame.key.get_pressed()
        if not game_over and not victory:
            if keys[pygame.K_LEFT]:
                player.move(-player.speed)
            if keys[pygame.K_RIGHT]:
                player.move(player.speed)

        if not game_over and not victory:
            # 2. AGGIORNAMENTO POSIZIONI
            
            # Movimento proiettile giocatore
            if player.bullet:
                player.bullet.move()
                if player.bullet.rect.y < 0:
                    player.bullet = None

            # Movimento proiettili alieni
            for b in alien_bullets[:]:
                b.move()
                if b.rect.y > HEIGHT:
                    alien_bullets.remove(b)

            # Movimento Alieni
            move_down = False
            for alien in aliens:
                alien.x += alien_speed * alien_direction
                alien.update_pos()
                if alien.x >= WIDTH - alien.width or alien.x <= 0:
                    move_down = True
            
            if move_down:
                alien_direction *= -1
                for alien in aliens:
                    alien.x += alien_speed * alien_direction # Corregge il bordo
                    alien.y += 20
                    alien.update_pos()
                    # Condizione di sconfitta: alieni toccano il fondo
                    if alien.y >= player.y:
                        game_over = True

            # Gli alieni sparano casualmente
            if len(aliens) > 0 and random.randint(1, 60) == 1:
                shooter = random.choice(aliens)
                alien_bullets.append(Bullet(shooter.x + shooter.width//2, shooter.y + shooter.height, 5, WHITE))

            # 3. GESTIONE COLLISIONI
            
            # Proiettile giocatore vs Alieni
            if player.bullet:
                for alien in aliens[:]:
                    if player.bullet and player.bullet.rect.colliderect(alien.rect):
                        score += alien.score_value
                        aliens.remove(alien)
                        player.bullet = None
                        # Aumenta la velocità (dinamica descritta nel MD)
                        alien_speed += 0.05
                        break
            
            # Proiettile giocatore vs Barriere
            if player.bullet:
                for bar in barriers[:]:
                    if player.bullet and player.bullet.rect.colliderect(bar.rect):
                        barriers.remove(bar)
                        player.bullet = None
                        break

            # Proiettili alieni vs Giocatore e Barriere
            for b in alien_bullets[:]:
                if b.rect.colliderect(player.rect):
                    lives -= 1
                    alien_bullets.remove(b)
                    if lives <= 0:
                        game_over = True
                    else:
                        # Breve "pausa" simulata ricreando i proiettili alieni
                        alien_bullets.clear()
                        break
                
                for bar in barriers[:]:
                    if b in alien_bullets and b.rect.colliderect(bar.rect):
                        barriers.remove(bar)
                        alien_bullets.remove(b)
                        break

            # Controllo Vittoria (ondata finita)
            if len(aliens) == 0:
                victory = True

        # 4. RENDERING GRAFICO
        player.draw(screen)
        if player.bullet:
            player.bullet.draw(screen)
        for alien in aliens:
            alien.draw(screen)
        for b in alien_bullets:
            b.draw(screen)
        for bar in barriers:
            bar.draw(screen)

        # UI: Punteggio e Vite
        score_text = font.render(f"Punteggio: {score}", True, WHITE)
        lives_text = font.render(f"Vite: {lives}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (WIDTH - 100, 10))

        # Messaggi di fine partita
        if game_over:
            go_text = font.render("GAME OVER", True, RED)
            screen.blit(go_text, (WIDTH//2 - 70, HEIGHT//2))
        elif victory:
            win_text = font.render("VITTORIA! Ondata completata.", True, GREEN)
            screen.blit(win_text, (WIDTH//2 - 150, HEIGHT//2))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()