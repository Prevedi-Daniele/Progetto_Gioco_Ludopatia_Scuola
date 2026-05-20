import pygame
import random
import sys
import os

LARGHEZZA_SCHERMO = 800
ALTEZZA_SCHERMO = 600
FPS = 60

NERO = (0, 0, 0)
BIANCO = (255, 255, 255)
VERDE = (0, 255, 0)
ROSSO = (255, 0, 0)
CIANO = (0, 255, 255)
GIALLO = (255, 255, 0)
ARANCIONE = (255, 165, 0)

NUMERO_COLONNE_ALIENI = 11
NUMERO_RIGHE_ALIENI = 5
SPAZIO_ORIZZONTALE_ALIENI = 60
SPAZIO_VERTICALE_ALIENI = 50
POSIZIONE_INIZIALE_X_ALIENI = 80
POSIZIONE_INIZIALE_Y_ALIENI = 80

NUMERO_BARRIERE = 4
LARGHEZZA_BARRIERA = 70
ALTEZZA_BARRIERA = 50
DIMENSIONE_BLOCCO_BARRIERA = 7  # pixel per singolo blocchetto
POSIZIONE_Y_BARRIERE = ALTEZZA_SCHERMO - 130

VELOCITA_GIOCATORE = 5
VELOCITA_PROIETTILE_GIOCATORE = 8
VELOCITA_PROIETTILE_ALIENO = 4
PIXEL_DISCESA_ALIENI = 18
VELOCITA_BASE_ALIENI = 0.8

VELOCITA_UFO = 2
POSIZIONE_Y_UFO = 40
INTERVALLO_COMPARSA_UFO = (15, 30)  # secondi fra un'apparizione e l'altra

# Percorso della cartella degli sprite (relativo al file .py)
CARTELLA_SPRITE = os.path.join(os.path.dirname(__file__), "assets", "sprites")



def carica_sprite(nome_file, larghezza=None, altezza=None):
    percorso_completo = os.path.join(CARTELLA_SPRITE, nome_file)
    immagine = pygame.image.load(percorso_completo).convert_alpha()

    if (larghezza == None) == False and (altezza == None) == False:
        immagine = pygame.transform.scale(immagine, (larghezza, altezza))
    return immagine



class Giocatore(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = carica_sprite("giocatore.png", larghezza=52, altezza=32)
        self.rect = self.image.get_rect()
        self.rect.centerx = LARGHEZZA_SCHERMO // 2
        self.rect.bottom = ALTEZZA_SCHERMO - 20
        self.vite = 3
        self.punteggio = 0
        self.sta_morendo = False
        self.timer_respawn = 0


    def aggiorna(self, tasti_premuti):
        # Gestisci la pausa post-morte con effetto lampeggio
        if self.sta_morendo == True:
            self.timer_respawn = self.timer_respawn - 1
            if self.timer_respawn <= 0:
                self.sta_morendo = False
            return

        if tasti_premuti[pygame.K_LEFT] == True and self.rect.left > 0:
            self.rect.x = self.rect.x - VELOCITA_GIOCATORE

        if tasti_premuti[pygame.K_RIGHT] == True and self.rect.right < LARGHEZZA_SCHERMO:
            self.rect.x = self.rect.x + VELOCITA_GIOCATORE


    def subisce_colpo(self):
        self.vite = self.vite - 1
        self.sta_morendo = True
        self.timer_respawn = FPS * 1



class Proiettile(pygame.sprite.Sprite):
    def __init__(self, posizione_x, posizione_y, velocita_verticale, colore=BIANCO):
        super().__init__()
        self.image = pygame.Surface((3, 14), pygame.SRCALPHA)
        self.image.fill(colore)
        self.rect = self.image.get_rect(centerx=posizione_x, top=posizione_y)
        self.velocita_verticale = velocita_verticale


    def aggiorna(self):
        self.rect.y = self.rect.y + self.velocita_verticale

        if self.rect.bottom < 0 or self.rect.top > ALTEZZA_SCHERMO:
            self.kill()



# Ogni tipo di alieno ha due frame per l'animazione (A e B)
CONFIGURAZIONE_TIPI_ALIENI = {
    # indice_riga: (nome_sprite_frame_a, nome_sprite_frame_b, larghezza, altezza, punti)
    0: ("alieno_polpo_a.png", "alieno_polpo_b.png", 44, 32, 30),
    1: ("alieno_granchio_a.png", "alieno_granchio_b.png", 40, 32, 20),
    2: ("alieno_granchio_a.png", "alieno_granchio_b.png", 40, 32, 20),
    3: ("alieno_calamaro_a.png", "alieno_calamaro_b.png", 40, 32, 10),
    4: ("alieno_calamaro_a.png", "alieno_calamaro_b.png", 40, 32, 10),
}



class Alieno(pygame.sprite.Sprite):
    # Contatore globale condiviso per sincronizzare l'animazione di tutta la formazione
    contatore_frame_animazione = 0

    def __init__(self, indice_riga, indice_colonna):
        super().__init__()
        nome_frame_a, nome_frame_b, larghezza, altezza, punti = CONFIGURAZIONE_TIPI_ALIENI[indice_riga]
        self.immagine_frame_a = carica_sprite(nome_frame_a, larghezza=larghezza, altezza=altezza)
        self.immagine_frame_b = carica_sprite(nome_frame_b, larghezza=larghezza, altezza=altezza)
        self.image = self.immagine_frame_a
        self.rect = self.image.get_rect()
        self.indice_riga = indice_riga
        self.indice_colonna = indice_colonna
        self.punti = punti


    def posiziona(self, posizione_x, posizione_y):
        self.rect.topleft = (posizione_x, posizione_y)


    def aggiorna_frame(self):
        if Alieno.contatore_frame_animazione % 2 == 0:
            self.image = self.immagine_frame_a
        else:
            self.image = self.immagine_frame_b



class BloccoBarriera(pygame.sprite.Sprite):
    def __init__(self, posizione_x, posizione_y):
        super().__init__()
        self.punti_salute = 3
        self.image = pygame.Surface((DIMENSIONE_BLOCCO_BARRIERA, DIMENSIONE_BLOCCO_BARRIERA))
        self._ridisegna()
        self.rect = self.image.get_rect(topleft=(posizione_x, posizione_y))


    def _ridisegna(self):
        colori_per_livello_salute = [VERDE, GIALLO, ARANCIONE]
        self.image.fill(colori_per_livello_salute[self.punti_salute - 1])


    def subisce_colpo(self):
        self.punti_salute = self.punti_salute - 1

        if self.punti_salute <= 0:
            self.kill()
        else:
            self._ridisegna()



class Ufo(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = carica_sprite("ufo.png", larghezza=56, altezza=24)
        self.rect = self.image.get_rect()
        self.direzione_movimento = random.choice([-1, 1])

        if self.direzione_movimento == 1:
            self.rect.right = 0
        else:
            self.rect.left = LARGHEZZA_SCHERMO

        self.rect.y = POSIZIONE_Y_UFO


    def aggiorna(self):
        self.rect.x = self.rect.x + VELOCITA_UFO * self.direzione_movimento

        if self.rect.right < 0 or self.rect.left > LARGHEZZA_SCHERMO:
            self.kill()



class Esplosione(pygame.sprite.Sprite):
    def __init__(self, centro_x, centro_y):
        super().__init__()
        self.image = carica_sprite("esplosione.png", larghezza=36, altezza=28)
        self.rect = self.image.get_rect(center=(centro_x, centro_y))
        self.frame_rimanenti = 25


    def aggiorna(self):
        self.frame_rimanenti = self.frame_rimanenti - 1
        
        if self.frame_rimanenti <= 0:
            self.kill()



class Gioco:
    def __init__(self):
        pygame.init()
        self.schermo = pygame.display.set_mode((LARGHEZZA_SCHERMO, ALTEZZA_SCHERMO))
        pygame.display.set_caption("Space Invaders")
        self.orologio = pygame.time.Clock()
        self.carattere_grande = pygame.font.SysFont("monospace", 36, bold=True)
        self.carattere_piccolo = pygame.font.SysFont("monospace", 20)
        self.stato_gioco = "menu"  # stati possibili: menu | gioco | gameover
        self._inizializza_partita()


    def _inizializza_partita(self):
        self.numero_ondata = 1

        self.gruppo_tutti_sprite = pygame.sprite.Group()
        self.gruppo_alieni = pygame.sprite.Group()
        self.gruppo_barriere = pygame.sprite.Group()
        self.gruppo_proiettili_giocatore = pygame.sprite.Group()
        self.gruppo_proiettili_alieni = pygame.sprite.Group()
        self.gruppo_ufo = pygame.sprite.Group()
        self.gruppo_esplosioni = pygame.sprite.Group()

        Alieno.contatore_frame_animazione = 0

        self.giocatore = Giocatore()
        self.gruppo_tutti_sprite.add(self.giocatore)

        self._genera_alieni()
        self._genera_barriere()

        self.direzione_movimento_alieni = 1  # +1 = destra, -1 = sinistra
        self.timer_movimento_alieni = 0
        self.frame_tra_ogni_movimento = 40  # frame tra uno step e il successivo
        self.timer_animazione_alieni = 0  # per cambiare frame alieno ogni N step

        self.timer_sparo_alieni = 0
        self.frame_tra_ogni_sparo_alieno = FPS * 1  # circa 1 sparo al secondo

        self.timer_comparsa_ufo = FPS * random.randint(*INTERVALLO_COMPARSA_UFO)


    def _genera_alieni(self):
        indice_riga = 0
        
        while indice_riga < NUMERO_RIGHE_ALIENI:
            indice_colonna = 0
            
            while indice_colonna < NUMERO_COLONNE_ALIENI:
                alieno = Alieno(indice_riga, indice_colonna)
                posizione_x = POSIZIONE_INIZIALE_X_ALIENI + indice_colonna * SPAZIO_ORIZZONTALE_ALIENI
                posizione_y = POSIZIONE_INIZIALE_Y_ALIENI + indice_riga * SPAZIO_VERTICALE_ALIENI + (self.numero_ondata - 1) * 10
                posizione_y = max(posizione_y, POSIZIONE_INIZIALE_Y_ALIENI)
                alieno.posiziona(posizione_x, posizione_y)
                self.gruppo_alieni.add(alieno)
                self.gruppo_tutti_sprite.add(alieno)
                indice_colonna = indice_colonna + 1
            
            indice_riga = indice_riga + 1


    def _genera_barriere(self):
        distanza_tra_barriere = LARGHEZZA_SCHERMO // (NUMERO_BARRIERE + 1)
        indice_barriera = 0

        while indice_barriera < NUMERO_BARRIERE:
            origine_x_barriera = distanza_tra_barriere * (indice_barriera + 1) - LARGHEZZA_BARRIERA // 2
            numero_righe_blocchi = ALTEZZA_BARRIERA // DIMENSIONE_BLOCCO_BARRIERA
            numero_colonne_blocchi = LARGHEZZA_BARRIERA // DIMENSIONE_BLOCCO_BARRIERA
            indice_riga_blocco = 0

            while indice_riga_blocco < numero_righe_blocchi:
                indice_colonna_blocco = 0

                while indice_colonna_blocco < numero_colonne_blocchi:
                    # Taglia gli angoli superiori per dare una forma ad arco
                    angolo_superiore = indice_riga_blocco == 0 and (indice_colonna_blocco < 2 or indice_colonna_blocco >= numero_colonne_blocchi - 2)

                    if angolo_superiore == True:
                        indice_colonna_blocco = indice_colonna_blocco + 1
                        continue

                    blocco = BloccoBarriera(
                        origine_x_barriera + indice_colonna_blocco * DIMENSIONE_BLOCCO_BARRIERA,
                        POSIZIONE_Y_BARRIERE + indice_riga_blocco * DIMENSIONE_BLOCCO_BARRIERA
                    )

                    self.gruppo_barriere.add(blocco)
                    self.gruppo_tutti_sprite.add(blocco)
                    indice_colonna_blocco = indice_colonna_blocco + 1

                indice_riga_blocco = indice_riga_blocco + 1

            indice_barriera = indice_barriera + 1


    def _calcola_velocita_alieni(self):
        numero_totale_alieni = NUMERO_COLONNE_ALIENI * NUMERO_RIGHE_ALIENI
        numero_alieni_vivi = len(self.gruppo_alieni)
        rapporto_alieni_rimasti = numero_alieni_vivi / numero_totale_alieni
        velocita_corrente = VELOCITA_BASE_ALIENI + (1 - rapporto_alieni_rimasti) * 3.0
        velocita_corrente = velocita_corrente * (1 + (self.numero_ondata - 1) * 0.15)
        return velocita_corrente


    def _muovi_alieni(self):
        if len(self.gruppo_alieni) == 0:
            return

        self.timer_movimento_alieni = self.timer_movimento_alieni + 1
        frame_necessari_per_movimento = max(5, int(self.frame_tra_ogni_movimento / self._calcola_velocita_alieni()))

        if self.timer_movimento_alieni < frame_necessari_per_movimento:
            return

        self.timer_movimento_alieni = 0

        Alieno.contatore_frame_animazione = Alieno.contatore_frame_animazione + 1
        for alieno in self.gruppo_alieni:
            alieno.aggiorna_frame()

        pixel_da_spostare = 8 * self.direzione_movimento_alieni

        bordo_raggiunto = False
        for alieno in self.gruppo_alieni:
            ha_raggiunto_bordo_destro = self.direzione_movimento_alieni == 1 and alieno.rect.right + pixel_da_spostare > LARGHEZZA_SCHERMO - 10
            ha_raggiunto_bordo_sinistro = self.direzione_movimento_alieni == -1 and alieno.rect.left + pixel_da_spostare < 10

            if ha_raggiunto_bordo_destro == True or ha_raggiunto_bordo_sinistro == True:
                bordo_raggiunto = True
                break

        if bordo_raggiunto == True:
            for alieno in self.gruppo_alieni:
                alieno.rect.y = alieno.rect.y + PIXEL_DISCESA_ALIENI
            self.direzione_movimento_alieni = self.direzione_movimento_alieni * -1
        else:
            for alieno in self.gruppo_alieni:
                alieno.rect.x = alieno.rect.x + pixel_da_spostare


    def _gestisci_sparo_alieni(self):
        if len(self.gruppo_alieni) == 0:
            return
        
        self.timer_sparo_alieni = self.timer_sparo_alieni + 1
        frame_necessari_per_sparo = max(20, self.frame_tra_ogni_sparo_alieno - self.numero_ondata * 5)
        
        if self.timer_sparo_alieni < frame_necessari_per_sparo:
            return
        
        self.timer_sparo_alieni = 0

        alieno_piu_basso_per_colonna = {}
        for alieno in self.gruppo_alieni:
            colonna_non_presente = (alieno.indice_colonna in alieno_piu_basso_per_colonna) == False
            alieno_piu_in_basso = alieno_piu_basso_per_colonna.get(alieno.indice_colonna)

            if colonna_non_presente == True or alieno.rect.bottom > alieno_piu_in_basso.rect.bottom:
                alieno_piu_basso_per_colonna[alieno.indice_colonna] = alieno

        alieno_sparatore = random.choice(list(alieno_piu_basso_per_colonna.values()))
        proiettile_alieno = Proiettile(alieno_sparatore.rect.centerx, alieno_sparatore.rect.bottom, VELOCITA_PROIETTILE_ALIENO, ROSSO)
        self.gruppo_proiettili_alieni.add(proiettile_alieno)
        self.gruppo_tutti_sprite.add(proiettile_alieno)


    def _gestisci_comparsa_ufo(self):
        self.timer_comparsa_ufo = self.timer_comparsa_ufo - 1
        ufo_assente = len(self.gruppo_ufo) == 0
        
        if self.timer_comparsa_ufo <= 0 and ufo_assente == True:
            nuovo_ufo = Ufo()
            self.gruppo_ufo.add(nuovo_ufo)
            self.gruppo_tutti_sprite.add(nuovo_ufo)
            self.timer_comparsa_ufo = FPS * random.randint(*INTERVALLO_COMPARSA_UFO)


    def _controlla_collisioni(self):
        alieni_colpiti = pygame.sprite.groupcollide(self.gruppo_alieni, self.gruppo_proiettili_giocatore, True, True)
        
        for alieno_colpito in alieni_colpiti:
            self.giocatore.punteggio = self.giocatore.punteggio + alieno_colpito.punti
            esplosione = Esplosione(alieno_colpito.rect.centerx, alieno_colpito.rect.centery)
            self.gruppo_esplosioni.add(esplosione)
            self.gruppo_tutti_sprite.add(esplosione)

        ufo_colpiti = pygame.sprite.groupcollide(self.gruppo_ufo, self.gruppo_proiettili_giocatore, True, True)
        for ufo_colpito in ufo_colpiti:
            punti_bonus = random.choice([50, 100, 150, 200, 300])
            self.giocatore.punteggio = self.giocatore.punteggio + punti_bonus
            esplosione = Esplosione(ufo_colpito.rect.centerx, ufo_colpito.rect.centery)
            self.gruppo_esplosioni.add(esplosione)
            self.gruppo_tutti_sprite.add(esplosione)

        for proiettile in list(self.gruppo_proiettili_giocatore):
            blocchi_colpiti = pygame.sprite.spritecollide(proiettile, self.gruppo_barriere, False)
            for blocco_colpito in blocchi_colpiti:
                blocco_colpito.subisce_colpo()

        if self.giocatore.sta_morendo == False:
            proiettili_che_hanno_colpito = pygame.sprite.spritecollide(
                self.giocatore, self.gruppo_proiettili_alieni, True)
            if len(proiettili_che_hanno_colpito) > 0:
                esplosione = Esplosione(self.giocatore.rect.centerx, self.giocatore.rect.centery)
                self.gruppo_esplosioni.add(esplosione)
                self.gruppo_tutti_sprite.add(esplosione)
                self.giocatore.subisce_colpo()

        for proiettile in list(self.gruppo_proiettili_alieni):
            blocchi_colpiti = pygame.sprite.spritecollide(proiettile, self.gruppo_barriere, False)
            for blocco_colpito in blocchi_colpiti:
                blocco_colpito.subisce_colpo()
            if len(blocchi_colpiti) > 0:
                proiettile.kill()

        pygame.sprite.groupcollide(self.gruppo_barriere, self.gruppo_alieni, True, False)


    def _controlla_vittoria_sconfitta(self):
        if self.giocatore.vite <= 0:
            self.stato_gioco = "gameover"
            return

        for alieno in self.gruppo_alieni:
            if alieno.rect.bottom >= ALTEZZA_SCHERMO - 60:
                self.stato_gioco = "gameover"
                return

        if len(self.gruppo_alieni) == 0:
            self.numero_ondata = self.numero_ondata + 1
            self._inizia_prossima_ondata()


    def _inizia_prossima_ondata(self):
        for sprite in list(self.gruppo_tutti_sprite):
            if isinstance(sprite, (Proiettile, Alieno, BloccoBarriera, Ufo, Esplosione)):
                sprite.kill()
        
        self.gruppo_ufo.empty()
        self.gruppo_barriere.empty()
        self.gruppo_esplosioni.empty()
        self.gruppo_proiettili_giocatore.empty()
        self.gruppo_proiettili_alieni.empty()
        Alieno.contatore_frame_animazione = 0
        self._genera_alieni()
        self._genera_barriere()
        self.timer_movimento_alieni = 0
        self.timer_sparo_alieni = 0
        self.timer_comparsa_ufo = FPS * random.randint(*INTERVALLO_COMPARSA_UFO)


    def _disegna_hud(self):
        testo_punteggio = self.carattere_piccolo.render(f"PUNTEGGIO: {self.giocatore.punteggio}", True, BIANCO)
        testo_vite = self.carattere_piccolo.render(f"VITE: {self.giocatore.vite}", True, VERDE)
        testo_ondata = self.carattere_piccolo.render(f"ONDATA: {self.numero_ondata}", True, GIALLO)
        
        self.schermo.blit(testo_punteggio, (10, 10))
        self.schermo.blit(testo_vite, (LARGHEZZA_SCHERMO // 2 - 50, 10))
        self.schermo.blit(testo_ondata, (LARGHEZZA_SCHERMO - 140, 10))

        pygame.draw.line(self.schermo, VERDE, (0, 35), (LARGHEZZA_SCHERMO, 35), 1)
        pygame.draw.line(self.schermo, VERDE, (0, ALTEZZA_SCHERMO - 10), (LARGHEZZA_SCHERMO, ALTEZZA_SCHERMO - 10), 1)


    def _disegna_schermata_menu(self):
        self.schermo.fill(NERO)
        
        testo_titolo = self.carattere_grande.render("SPACE INVADERS", True, VERDE)
        testo_istruzione_avvio = self.carattere_piccolo.render("Premi INVIO per iniziare", True, BIANCO)
        testo_controlli = self.carattere_piccolo.render("← → per muoversi  |  SPAZIO per sparare", True, CIANO)
        
        self.schermo.blit(testo_titolo, testo_titolo.get_rect(center=(LARGHEZZA_SCHERMO // 2, ALTEZZA_SCHERMO // 2 - 60)))
        self.schermo.blit(testo_istruzione_avvio, testo_istruzione_avvio.get_rect(center=(LARGHEZZA_SCHERMO // 2, ALTEZZA_SCHERMO // 2 + 20)))
        self.schermo.blit(testo_controlli, testo_controlli.get_rect(center=(LARGHEZZA_SCHERMO // 2, ALTEZZA_SCHERMO // 2 + 60)))


    def _disegna_schermata_gameover(self):
        self.schermo.fill(NERO)
        
        testo_gameover = self.carattere_grande.render("GAME OVER", True, ROSSO)
        testo_punteggio_finale = self.carattere_piccolo.render(f"Punteggio finale: {self.giocatore.punteggio}", True, BIANCO)
        testo_istruzione_riavvio = self.carattere_piccolo.render("Premi INVIO per ricominciare", True, CIANO)
        
        self.schermo.blit(testo_gameover, testo_gameover.get_rect(center=(LARGHEZZA_SCHERMO // 2, ALTEZZA_SCHERMO // 2 - 60)))
        self.schermo.blit(testo_punteggio_finale, testo_punteggio_finale.get_rect(center=(LARGHEZZA_SCHERMO // 2, ALTEZZA_SCHERMO // 2)))
        self.schermo.blit(testo_istruzione_riavvio, testo_istruzione_riavvio.get_rect(center=(LARGHEZZA_SCHERMO // 2, ALTEZZA_SCHERMO // 2 + 60)))


    def avvia(self):
        while True:
            self.orologio.tick(FPS)
            tasti_premuti = pygame.key.get_pressed()

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if evento.type == pygame.KEYDOWN:
                    if self.stato_gioco == "menu" and evento.key == pygame.K_RETURN:
                        self.stato_gioco = "gioco"

                    elif self.stato_gioco == "gameover" and evento.key == pygame.K_RETURN:
                        self._inizializza_partita()
                        self.stato_gioco = "gioco"

                    elif self.stato_gioco == "gioco":
                        if evento.key == pygame.K_SPACE:
                            nessun_proiettile_attivo = len(self.gruppo_proiettili_giocatore) == 0
                            if self.giocatore.sta_morendo == False and nessun_proiettile_attivo == True:
                                nuovo_proiettile = Proiettile(self.giocatore.rect.centerx, self.giocatore.rect.top, -VELOCITA_PROIETTILE_GIOCATORE, BIANCO)
                                self.gruppo_proiettili_giocatore.add(nuovo_proiettile)
                                self.gruppo_tutti_sprite.add(nuovo_proiettile)

            if self.stato_gioco == "gioco":
                self.giocatore.aggiorna(tasti_premuti)

                for proiettile in list(self.gruppo_proiettili_giocatore):
                    proiettile.aggiorna()

                for proiettile in list(self.gruppo_proiettili_alieni):
                    proiettile.aggiorna()

                for ufo in list(self.gruppo_ufo):
                    ufo.aggiorna()

                for esplosione in list(self.gruppo_esplosioni):
                    esplosione.aggiorna()

                self._muovi_alieni()
                self._gestisci_sparo_alieni()
                self._gestisci_comparsa_ufo()
                self._controlla_collisioni()
                self._controlla_vittoria_sconfitta()

            self.schermo.fill(NERO)

            if self.stato_gioco == "menu":
                self._disegna_schermata_menu()

            elif self.stato_gioco == "gameover":
                self._disegna_schermata_gameover()

            elif self.stato_gioco == "gioco":
                self.gruppo_tutti_sprite.draw(self.schermo)
                self._disegna_hud()

                if self.giocatore.sta_morendo == True:
                    if (self.giocatore.timer_respawn // 5) % 2 == 0:
                        self.schermo.blit(self.giocatore.image, self.giocatore.rect)

            pygame.display.flip()


if __name__ == "__main__":
    Gioco().avvia()