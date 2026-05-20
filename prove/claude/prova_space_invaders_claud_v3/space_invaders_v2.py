import pygame
import random
import sys
import os

# ── Costanti globali ─────────────────────────────────────────────────────────
LARGHEZZA_SCHERMO = 800
ALTEZZA_SCHERMO = 600
FPS = 60

NERO = (0,   0,   0)
BIANCO = (255, 255, 255)
VERDE = (0,   255, 0)
ROSSO = (255, 0,   0)
CIANO = (0,   255, 255)
GIALLO = (255, 255, 0)
ARANCIONE = (255, 165, 0)

# Griglia alieni
COLONNE_ALIENI = 11
RIGHE_ALIENI = 5
SPAZIO_X_ALIENI = 60
SPAZIO_Y_ALIENI = 50
INIZIO_X_ALIENI = 80
INIZIO_Y_ALIENI = 80

# Barriere
NUMERO_BARRIERE = 4
LARGHEZZA_BARRIERA = 70
ALTEZZA_BARRIERA = 50
DIMENSIONE_BLOCCO = 7  # pixel per singolo blocchetto
Y_BARRIERA = ALTEZZA_SCHERMO - 130

# Velocità
VELOCITA_GIOCATORE = 5
VELOCITA_PROIETTILE = 8
VELOCITA_PROIETTILE_ALIENO = 4
DISCESA_ALIENI = 18
VELOCITA_BASE_ALIENI = 0.8

# UFO
VELOCITA_UFO = 2
Y_UFO = 40
INTERVALLO_UFO = (15, 30)  # secondi fra un'apparizione e l'altra

# Percorso della cartella degli sprite (relativo al file .py)
CARTELLA_SPRITE = os.path.join(os.path.dirname(__file__), "assets", "sprites")


# ── Funzione di caricamento sprite ───────────────────────────────────────────
def carica_sprite(nome_file, larghezza=None, altezza=None):
    # Carica un PNG con trasparenza e lo scala se richiesto
    percorso = os.path.join(CARTELLA_SPRITE, nome_file)
    immagine = pygame.image.load(percorso).convert_alpha()
    if larghezza and altezza:
        immagine = pygame.transform.scale(immagine, (larghezza, altezza))
    return immagine


# ── Classe Giocatore ─────────────────────────────────────────────────────────
class Giocatore(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Carica lo sprite PNG del giocatore
        self.image = carica_sprite("giocatore.png", larghezza=52, altezza=32)
        self.rect = self.image.get_rect()
        self.rect.centerx = LARGHEZZA_SCHERMO // 2
        self.rect.bottom = ALTEZZA_SCHERMO - 20
        self.vite = 3
        self.punteggio = 0
        self.morto = False
        self.timer_respawn = 0

    def aggiorna(self, tasti):
        # Gestisci la pausa post-morte con effetto lampeggio
        if self.morto:
            self.timer_respawn -= 1
            if self.timer_respawn <= 0:
                self.morto = False
            return
        # Movimento orizzontale entro i bordi dello schermo
        if tasti[pygame.K_LEFT]  and self.rect.left  > 0:
            self.rect.x -= VELOCITA_GIOCATORE
        if tasti[pygame.K_RIGHT] and self.rect.right < LARGHEZZA_SCHERMO:
            self.rect.x += VELOCITA_GIOCATORE

    def subisce_colpo(self):
        # Decrementa le vite e attiva il timer di respawn
        self.vite         -= 1
        self.morto = True
        self.timer_respawn = FPS * 1  # 1 secondo di pausa


# ── Classe Proiettile ────────────────────────────────────────────────────────
class Proiettile(pygame.sprite.Sprite):
    def __init__(self, x, y, velocita_y, colore=BIANCO):
        super().__init__()
        # Il proiettile è un semplice rettangolo colorato
        self.image = pygame.Surface((3, 14), pygame.SRCALPHA)
        self.image.fill(colore)
        self.rect = self.image.get_rect(centerx=x, top=y)
        self.velocita_y = velocita_y

    def aggiorna(self):
        self.rect.y += self.velocita_y
        # Rimuovi il proiettile se esce dallo schermo
        if self.rect.bottom < 0 or self.rect.top > ALTEZZA_SCHERMO:
            self.kill()


# ── Classe Alieno ────────────────────────────────────────────────────────────
# Ogni tipo di alieno ha due frame per l'animazione (A e B)
TIPI_ALIENI = {
    # riga: (nome_sprite_A, nome_sprite_B, larghezza, altezza, punti)
    0: ("alieno_polpo_a.png",    "alieno_polpo_b.png",    44, 32, 30),
    1: ("alieno_granchio_a.png", "alieno_granchio_b.png", 40, 32, 20),
    2: ("alieno_granchio_a.png", "alieno_granchio_b.png", 40, 32, 20),
    3: ("alieno_calamaro_a.png", "alieno_calamaro_b.png", 40, 32, 10),
    4: ("alieno_calamaro_a.png", "alieno_calamaro_b.png", 40, 32, 10),
}

class Alieno(pygame.sprite.Sprite):
    # Timer globale condiviso per sincronizzare l'animazione di tutta la formazione
    frame_animazione = 0

    def __init__(self, riga, colonna):
        super().__init__()
        nome_a, nome_b, larg, alt, punti = TIPI_ALIENI[riga]
        # Carica entrambi i frame di animazione
        self.frame_a = carica_sprite(nome_a, larghezza=larg, altezza=alt)
        self.frame_b = carica_sprite(nome_b, larghezza=larg, altezza=alt)
        self.image = self.frame_a
        self.rect = self.image.get_rect()
        self.riga = riga
        self.colonna = colonna
        self.punti = punti

    def posiziona(self, x, y):
        self.rect.topleft = (x, y)

    def aggiorna_frame(self):
        # Alterna tra i due frame in base al timer globale
        if Alieno.frame_animazione % 2 == 0:
            self.image = self.frame_a
        else:
            self.image = self.frame_b


# ── Classe BloccoBarriera ────────────────────────────────────────────────────
class BloccoBarriera(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.salute = 3
        self.image = pygame.Surface((DIMENSIONE_BLOCCO, DIMENSIONE_BLOCCO))
        self._ridisegna()
        self.rect = self.image.get_rect(topleft=(x, y))

    def _ridisegna(self):
        # Verde = integro, Giallo = danneggiato, Arancione = quasi distrutto
        colori = [VERDE, GIALLO, ARANCIONE]
        self.image.fill(colori[self.salute - 1])

    def subisce_colpo(self):
        self.salute -= 1
        if self.salute <= 0:
            self.kill()
        else:
            self._ridisegna()


# ── Classe Ufo ───────────────────────────────────────────────────────────────
class Ufo(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Carica lo sprite PNG dell'UFO
        self.image = carica_sprite("ufo.png", larghezza=56, altezza=24)
        self.rect = self.image.get_rect()
        self.direzione = random.choice([-1, 1])
        # Posizione iniziale: entra da sinistra o da destra
        if self.direzione == 1:
            self.rect.right = 0
        else:
            self.rect.left = LARGHEZZA_SCHERMO
        self.rect.y = Y_UFO

    def aggiorna(self):
        self.rect.x += VELOCITA_UFO * self.direzione
        # Rimuovi quando esce dall'altro lato
        if self.rect.right < 0 or self.rect.left > LARGHEZZA_SCHERMO:
            self.kill()


# ── Classe Esplosione ────────────────────────────────────────────────────────
class Esplosione(pygame.sprite.Sprite):
    def __init__(self, cx, cy):
        super().__init__()
        # Carica lo sprite PNG dell'esplosione
        self.image = carica_sprite("esplosione.png", larghezza=36, altezza=28)
        self.rect = self.image.get_rect(center=(cx, cy))
        self.timer = 25  # frame di durata visibile

    def aggiorna(self):
        self.timer -= 1
        if self.timer <= 0:
            self.kill()


# ── Classe principale Gioco ──────────────────────────────────────────────────
class Gioco:
    def __init__(self):
        pygame.init()
        self.schermo = pygame.display.set_mode((LARGHEZZA_SCHERMO, ALTEZZA_SCHERMO))
        pygame.display.set_caption("Space Invaders")
        self.orologio = pygame.time.Clock()
        self.carattere_grande = pygame.font.SysFont("monospace", 36, bold=True)
        self.carattere_piccolo = pygame.font.SysFont("monospace", 20)
        self.stato = "menu"  # stati possibili: menu | gioco | gameover
        self._inizializza_partita()

    def _inizializza_partita(self):
        self.ondata = 1

        # Gruppi sprite
        self.tutti_sprite = pygame.sprite.Group()
        self.gruppo_alieni = pygame.sprite.Group()
        self.gruppo_barriere = pygame.sprite.Group()
        self.proiettili_giocatore = pygame.sprite.Group()
        self.proiettili_alieni = pygame.sprite.Group()
        self.gruppo_ufo = pygame.sprite.Group()
        self.gruppo_esplosioni = pygame.sprite.Group()

        # Resetta il frame di animazione degli alieni
        Alieno.frame_animazione = 0

        # Crea il giocatore e aggiungilo ai gruppi
        self.giocatore = Giocatore()
        self.tutti_sprite.add(self.giocatore)

        self._genera_alieni()
        self._genera_barriere()

        # Stato del movimento degli alieni
        self.direzione_alieni = 1  # +1 = destra, -1 = sinistra
        self.timer_movimento = 0
        self.intervallo_movimento = 40  # frame tra uno step e il successivo
        self.timer_animazione = 0  # per cambiare frame alieno ogni N step

        # Stato dello sparo degli alieni
        self.timer_sparo_alieni = 0
        self.intervallo_sparo_alieni = FPS * 1  # circa 1 sparo al secondo

        # Stato UFO
        self.timer_ufo = FPS * random.randint(*INTERVALLO_UFO)

    def _genera_alieni(self):
        # Popola la griglia: RIGHE_ALIENI righe × COLONNE_ALIENI colonne
        riga = 0
        while riga < RIGHE_ALIENI:
            colonna = 0
            while colonna < COLONNE_ALIENI:
                alieno = Alieno(riga, colonna)
                x = INIZIO_X_ALIENI + colonna * SPAZIO_X_ALIENI
                y = INIZIO_Y_ALIENI + riga * SPAZIO_Y_ALIENI + (self.ondata - 1) * 10
                y = max(y, INIZIO_Y_ALIENI)
                alieno.posiziona(x, y)
                self.gruppo_alieni.add(alieno)
                self.tutti_sprite.add(alieno)
                colonna += 1
            riga += 1

    def _genera_barriere(self):
        # Distribuisce NUMERO_BARRIERE barriere uniformemente sullo schermo
        distanza = LARGHEZZA_SCHERMO // (NUMERO_BARRIERE + 1)
        i = 0
        while i < NUMERO_BARRIERE:
            bx = distanza * (i + 1) - LARGHEZZA_BARRIERA // 2
            righe_blocco = ALTEZZA_BARRIERA   // DIMENSIONE_BLOCCO
            colonne_blocco = LARGHEZZA_BARRIERA // DIMENSIONE_BLOCCO
            riga = 0
            while riga < righe_blocco:
                colonna = 0
                while colonna < colonne_blocco:
                    # Taglia gli angoli superiori per dare una forma ad arco
                    if riga == 0 and (colonna < 2 or colonna >= colonne_blocco - 2):
                        colonna += 1
                        continue
                    blocco = BloccoBarriera(
                        bx + colonna * DIMENSIONE_BLOCCO,
                        Y_BARRIERA + riga * DIMENSIONE_BLOCCO
                    )
                    self.gruppo_barriere.add(blocco)
                    self.tutti_sprite.add(blocco)
                    colonna += 1
                riga += 1
            i += 1

    def _velocita_alieni(self):
        # Più alieni vengono eliminati, più la formazione accelera
        totale = COLONNE_ALIENI * RIGHE_ALIENI
        vivi = len(self.gruppo_alieni)
        rapporto = vivi / totale
        velocita = VELOCITA_BASE_ALIENI + (1 - rapporto) * 3.0
        velocita *= 1 + (self.ondata - 1) * 0.15
        return velocita

    def _muovi_alieni(self):
        if not self.gruppo_alieni:
            return
        self.timer_movimento += 1
        intervallo = max(5, int(self.intervallo_movimento / self._velocita_alieni()))
        if self.timer_movimento < intervallo:
            return
        self.timer_movimento = 0

        # Cambia frame di animazione ad ogni step di movimento
        Alieno.frame_animazione += 1
        for alieno in self.gruppo_alieni:
            alieno.aggiorna_frame()

        passo = 8 * self.direzione_alieni
        # Verifica se la formazione ha raggiunto un bordo dello schermo
        bordo_raggiunto = False
        for alieno in self.gruppo_alieni:
            if (self.direzione_alieni ==  1 and alieno.rect.right + passo > LARGHEZZA_SCHERMO - 10) or \
               (self.direzione_alieni == -1 and alieno.rect.left  + passo < 10):
                bordo_raggiunto = True
                break

        if bordo_raggiunto:
            # Scende di una riga e inverte la direzione
            for alieno in self.gruppo_alieni:
                alieno.rect.y += DISCESA_ALIENI
            self.direzione_alieni *= -1
        else:
            for alieno in self.gruppo_alieni:
                alieno.rect.x += passo

    def _sparo_alieni(self):
        if not self.gruppo_alieni:
            return
        self.timer_sparo_alieni += 1
        intervallo = max(20, self.intervallo_sparo_alieni - self.ondata * 5)
        if self.timer_sparo_alieni < intervallo:
            return
        self.timer_sparo_alieni = 0

        # Seleziona lo sparatore: l'alieno più in basso per ogni colonna visibile
        colonne = {}
        for alieno in self.gruppo_alieni:
            if alieno.colonna not in colonne or alieno.rect.bottom > colonne[alieno.colonna].rect.bottom:
                colonne[alieno.colonna] = alieno
        sparatore = random.choice(list(colonne.values()))
        proiettile = Proiettile(sparatore.rect.centerx, sparatore.rect.bottom,
                                VELOCITA_PROIETTILE_ALIENO, ROSSO)
        self.proiettili_alieni.add(proiettile)
        self.tutti_sprite.add(proiettile)

    def _logica_ufo(self):
        self.timer_ufo -= 1
        if self.timer_ufo <= 0 and not self.gruppo_ufo:
            ufo = Ufo()
            self.gruppo_ufo.add(ufo)
            self.tutti_sprite.add(ufo)
            self.timer_ufo = FPS * random.randint(*INTERVALLO_UFO)

    def _controlla_collisioni(self):
        # ── Proiettile giocatore ↔ alieni ────────────────────────────────────
        colpiti = pygame.sprite.groupcollide(
            self.gruppo_alieni, self.proiettili_giocatore, True, True)
        for alieno in colpiti:
            self.giocatore.punteggio += alieno.punti
            esp = Esplosione(alieno.rect.centerx, alieno.rect.centery)
            self.gruppo_esplosioni.add(esp)
            self.tutti_sprite.add(esp)

        # ── Proiettile giocatore ↔ UFO ────────────────────────────────────────
        colpiti_ufo = pygame.sprite.groupcollide(
            self.gruppo_ufo, self.proiettili_giocatore, True, True)
        for ufo in colpiti_ufo:
            bonus = random.choice([50, 100, 150, 200, 300])
            self.giocatore.punteggio += bonus
            esp = Esplosione(ufo.rect.centerx, ufo.rect.centery)
            self.gruppo_esplosioni.add(esp)
            self.tutti_sprite.add(esp)

        # ── Proiettile giocatore ↔ barriere ──────────────────────────────────
        # MECCANICA CORRETTA: il proiettile danneggia la barriera ma NON si ferma,
        # così il giocatore può colpire gli alieni anche sparando attraverso le barriere.
        for proiettile in list(self.proiettili_giocatore):
            blocchi_colpiti = pygame.sprite.spritecollide(
                proiettile, self.gruppo_barriere, False)
            for blocco in blocchi_colpiti:
                blocco.subisce_colpo()
            # Il proiettile continua la sua traiettoria verso l'alto

        # ── Proiettile alieno ↔ giocatore ────────────────────────────────────
        if not self.giocatore.morto:
            colpi_ricevuti = pygame.sprite.spritecollide(
                self.giocatore, self.proiettili_alieni, True)
            if colpi_ricevuti:
                esp = Esplosione(self.giocatore.rect.centerx,
                                 self.giocatore.rect.centery)
                self.gruppo_esplosioni.add(esp)
                self.tutti_sprite.add(esp)
                self.giocatore.subisce_colpo()

        # ── Proiettile alieno ↔ barriere ─────────────────────────────────────
        # I proiettili alieni si fermano sulle barriere (comportamento classico)
        for proiettile in list(self.proiettili_alieni):
            blocchi_colpiti = pygame.sprite.spritecollide(
                proiettile, self.gruppo_barriere, False)
            for blocco in blocchi_colpiti:
                blocco.subisce_colpo()
            if blocchi_colpiti:
                proiettile.kill()

        # ── Alieni ↔ barriere (distruzione al contatto diretto) ──────────────
        pygame.sprite.groupcollide(self.gruppo_barriere, self.gruppo_alieni, True, False)

    def _controlla_vittoria_sconfitta(self):
        # Sconfitta: vite esaurite
        if self.giocatore.vite <= 0:
            self.stato = "gameover"
            return
        # Sconfitta: un alieno ha raggiunto il fondo dello schermo
        for alieno in self.gruppo_alieni:
            if alieno.rect.bottom >= ALTEZZA_SCHERMO - 60:
                self.stato = "gameover"
                return
        # Ondata completata: tutti gli alieni eliminati
        if not self.gruppo_alieni:
            self.ondata += 1
            self._prossima_ondata()

    def _prossima_ondata(self):
        # Rimuove tutti gli sprite temporanei e rigenera alieni e barriere
        for sprite in list(self.tutti_sprite):
            if isinstance(sprite, (Proiettile, Alieno, BloccoBarriera, Ufo, Esplosione)):
                sprite.kill()
        self.gruppo_ufo.empty()
        self.gruppo_barriere.empty()
        self.gruppo_esplosioni.empty()
        self.proiettili_giocatore.empty()
        self.proiettili_alieni.empty()
        Alieno.frame_animazione = 0
        self._genera_alieni()
        self._genera_barriere()
        self.timer_movimento = 0
        self.timer_sparo_alieni = 0
        self.timer_ufo = FPS * random.randint(*INTERVALLO_UFO)

    def _disegna_hud(self):
        # Mostra punteggio, vite e numero ondata nella barra superiore
        testo_punteggio = self.carattere_piccolo.render(
            f"PUNTEGGIO: {self.giocatore.punteggio}", True, BIANCO)
        testo_vite = self.carattere_piccolo.render(
            f"VITE: {self.giocatore.vite}", True, VERDE)
        testo_ondata = self.carattere_piccolo.render(
            f"ONDATA: {self.ondata}", True, GIALLO)
        self.schermo.blit(testo_punteggio, (10, 10))
        self.schermo.blit(testo_vite,     (LARGHEZZA_SCHERMO // 2 - 50, 10))
        self.schermo.blit(testo_ondata,   (LARGHEZZA_SCHERMO - 140, 10))
        # Linee di confine dell'area di gioco
        pygame.draw.line(self.schermo, VERDE,
                         (0, 35), (LARGHEZZA_SCHERMO, 35), 1)
        pygame.draw.line(self.schermo, VERDE,
                         (0, ALTEZZA_SCHERMO - 10), (LARGHEZZA_SCHERMO, ALTEZZA_SCHERMO - 10), 1)

    def _disegna_menu(self):
        self.schermo.fill(NERO)
        titolo = self.carattere_grande.render("SPACE INVADERS", True, VERDE)
        sottotitolo = self.carattere_piccolo.render("Premi INVIO per iniziare", True, BIANCO)
        controlli = self.carattere_piccolo.render(
            "← → per muoversi  |  SPAZIO per sparare", True, CIANO)
        self.schermo.blit(titolo,
            titolo.get_rect(center=(LARGHEZZA_SCHERMO // 2, ALTEZZA_SCHERMO // 2 - 60)))
        self.schermo.blit(sottotitolo,
            sottotitolo.get_rect(center=(LARGHEZZA_SCHERMO // 2, ALTEZZA_SCHERMO // 2 + 20)))
        self.schermo.blit(controlli,
            controlli.get_rect(center=(LARGHEZZA_SCHERMO // 2, ALTEZZA_SCHERMO // 2 + 60)))

    def _disegna_gameover(self):
        self.schermo.fill(NERO)
        testo_go = self.carattere_grande.render("GAME OVER", True, ROSSO)
        testo_punteggio = self.carattere_piccolo.render(
            f"Punteggio finale: {self.giocatore.punteggio}", True, BIANCO)
        testo_ricomincia = self.carattere_piccolo.render(
            "Premi INVIO per ricominciare", True, CIANO)
        self.schermo.blit(testo_go,
            testo_go.get_rect(center=(LARGHEZZA_SCHERMO // 2, ALTEZZA_SCHERMO // 2 - 60)))
        self.schermo.blit(testo_punteggio,
            testo_punteggio.get_rect(center=(LARGHEZZA_SCHERMO // 2, ALTEZZA_SCHERMO // 2)))
        self.schermo.blit(testo_ricomincia,
            testo_ricomincia.get_rect(center=(LARGHEZZA_SCHERMO // 2, ALTEZZA_SCHERMO // 2 + 60)))

    # ── Loop principale ──────────────────────────────────────────────────────
    def avvia(self):
        while True:
            self.orologio.tick(FPS)
            tasti = pygame.key.get_pressed()

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if evento.type == pygame.KEYDOWN:
                    if self.stato == "menu" and evento.key == pygame.K_RETURN:
                        self.stato = "gioco"

                    elif self.stato == "gameover" and evento.key == pygame.K_RETURN:
                        self._inizializza_partita()
                        self.stato = "gioco"

                    elif self.stato == "gioco":
                        if evento.key == pygame.K_SPACE:
                            # Un solo proiettile attivo alla volta per il giocatore
                            if not self.giocatore.morto and len(self.proiettili_giocatore) == 0:
                                proiettile = Proiettile(
                                    self.giocatore.rect.centerx,
                                    self.giocatore.rect.top,
                                    -VELOCITA_PROIETTILE,
                                    BIANCO
                                )
                                self.proiettili_giocatore.add(proiettile)
                                self.tutti_sprite.add(proiettile)

            # ── Aggiornamento logica di gioco ────────────────────────────────
            if self.stato == "gioco":
                self.giocatore.aggiorna(tasti)

                # Aggiorna proiettili del giocatore
                for p in list(self.proiettili_giocatore):
                    p.aggiorna()

                # Aggiorna proiettili degli alieni
                for p in list(self.proiettili_alieni):
                    p.aggiorna()

                # Aggiorna UFO
                for u in list(self.gruppo_ufo):
                    u.aggiorna()

                # Aggiorna esplosioni
                for e in list(self.gruppo_esplosioni):
                    e.aggiorna()

                self._muovi_alieni()
                self._sparo_alieni()
                self._logica_ufo()
                self._controlla_collisioni()
                self._controlla_vittoria_sconfitta()

            # ── Rendering ────────────────────────────────────────────────────
            self.schermo.fill(NERO)

            if self.stato == "menu":
                self._disegna_menu()

            elif self.stato == "gameover":
                self._disegna_gameover()

            elif self.stato == "gioco":
                self.tutti_sprite.draw(self.schermo)
                self._disegna_hud()
                # Effetto lampeggio del giocatore durante il respawn
                if self.giocatore.morto:
                    if (self.giocatore.timer_respawn // 5) % 2 == 0:
                        self.schermo.blit(self.giocatore.image, self.giocatore.rect)

            pygame.display.flip()


if __name__ == "__main__":
    Gioco().avvia()