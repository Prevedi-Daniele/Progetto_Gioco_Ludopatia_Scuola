# Space Invaders in Python (Pygame)

Benvenuto in questo clone del classicissimo arcade **Space Invaders**, sviluppato interamente in Python utilizzando la libreria **Pygame**. Il codice è strutturato ad oggetti ed è pronto per essere eseguito, a patto di avere gli asset grafici corretti nella cartella di gioco.

---

## 🎮 Come Giocare e Controlli

Il gioco si apre con una schermata di menu. L'obiettivo è distruggere tutte le cinque righe di alieni prima che raggiungano la terra o prima di esaurire le vite a disposizione.

* **INVIO (`ENTER`)**: Inizia la partita dal menu principale o ricomincia dopo un Game Over / Vittoria.
* **FRECCIA SINISTRA (`←`)**: Muove la navicella del giocatore verso sinistra.
* **FRECCIA DESTRA (`→`)**: Muove la navicella del giocatore verso destra.
* **BARRA SPAZIATRICE (`SPACE`)**: Spara un proiettile. *Nota: puoi sparare un solo proiettile alla volta; devi attendere che colpisca un bersaglio o esca dallo schermo prima di poterne sparare un altro.*

---

## 🛠️ Struttura del Codice

Il file `space_invaders.py` è organizzato in classi distinte per gestire la programmazione orientata agli oggetti (OOP) tipica dello sviluppo di videogiochi 2D:

### 1. Classi di Gioco (Elementi Principali)

* **`Gioco`**: Il motore principale. Gestisce il ciclo di gioco (Game Loop), l'inizializzazione di Pygame, il controllo della logica di collisione, il calcolo della velocità degli alieni e il disegno delle schermate (Menu, Gioco, Vittoria, Game Over).
* **`Giocatore`**: Gestisce la navicella guidata dall'utente, il movimento entro i bordi dello schermo, il punteggio, il sistema delle 3 vite e l'effetto di lampeggiamento durante il respawn (immunità temporanea).
* **`Alieno`**: Rappresenta il singolo nemico. Il comportamento varia in base alla riga in cui viene generato (punteggio e sprite diversi).

### 2. Classi di Supporto

* **`Proiettile`**: Gestisce i proiettili (sia del giocatore che degli alieni), controllando il loro movimento verticale e la loro rimozione automatica una volta superati i limiti dello schermo.
* **`BloccoBarriera`**: I singoli pixel/blocchi che compongono i 4 scudi protettivi a fondo schermo. Vengono distrutti progressivamente quando colpiti da proiettili o alieni.
* **`Esplosione`**: Un effetto visivo temporaneo (della durata di 25 frame) che appare quando un alieno o il giocatore vengono distrutti.

---

## ⚙️ Meccaniche di Gioco Avanzate

* **Difficoltà Dinamica**: Gli alieni si muovono più velocemente man mano che il loro numero diminuisce. La velocità viene calcolata dinamicamente tramite la funzione `_calcola_velocita_alieni()`.
* **IA di Sparo Nemico**: Gli alieni non sparano a caso da dietro le quinte. Il sistema calcola quale sia l'alieno posizionato più in basso per ogni colonna (`_gestisci_sparo_alieni()`) e seleziona uno di essi per fare fuoco, evitando che i proiettili si colpiscano tra loro.
* **Distruzione delle Barriere**:
* I proiettili del giocatore *attraversano* le barriere distruggendo solo i blocchi che toccano.
* I proiettili nemici *si fermano* al primo impatto distruggendo il blocco.
* Il contatto diretto tra un alieno e la barriera dissolve istantaneamente i blocchi colpiti.



---

## 📁 Requisiti di Sistema e Asset

Per far funzionare il gioco, devi installare Pygame e configurare le immagini.

### Pre-requisiti

Assicurati di avere installato Python e la libreria Pygame:

```bash
pip install pygame

```

### Struttura delle Cartelle

Il codice si aspetta di trovare le immagini (sprite) all'interno di una cartella chiamata `assets/sprites`, posizionata nella stessa directory del file `.py`:

```text
📂 Il_Tuo_Progetto/
 ┣ 📄 space_invaders.py
 ┗ 📂 assets/
   ┗ 📂 sprites/
     ┣ 🖼️ giocatore.png
     ┣ 🖼️ alieno_polpo_a.png
     ┣ 🖼️ alieno_granchio_a.png
     ┣ 🖼️ alieno_calamaro_a.png
     ┗ 🖼️ esplosione.png

```

> **Nota sui Colori e Punteggi:** Il gioco assegna 30 punti per la riga più in alto (Polpo), 20 punti per le righe centrali (Granchio) e 10 punti per le righe inferiori (Calamaro).