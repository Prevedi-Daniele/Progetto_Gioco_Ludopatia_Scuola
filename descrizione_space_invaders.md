# Space Invaders

## Descrizione generale

Space Invaders è uno sparatutto arcade bidimensionale ambientato nello spazio.
Il giocatore controlla un piccolo cannone terrestre posto nella parte inferiore dello schermo e deve difendersi da ondate di alieni che avanzano lentamente dall’alto verso il basso.

L’obiettivo è distruggere tutti gli invasori prima che:

* raggiungano il fondo dello schermo;
* colpiscano il giocatore troppe volte.

Il gioco diventa progressivamente più veloce e difficile man mano che il numero di alieni diminuisce.

---

# Grafica e stile visivo

## Stile grafico

Lo stile originale è:

* **pixel art retro**
* grafica molto minimale
* sprite 2D
* sfondo nero fisso
* colori semplici e contrastati

Gli elementi principali sono composti da pochi pixel:

* alieni
* navicella del giocatore
* proiettili
* barriere difensive

L’estetica richiama i cabinati arcade degli anni ’70 e ’80.

---

## Struttura dello schermo

Lo schermo è generalmente suddiviso così:

### Parte alta

Formazione degli alieni:

* disposti in righe e colonne;
* si muovono insieme come un unico blocco.

### Parte centrale

Area di combattimento:

* attraversata dai proiettili;
* contiene le barriere difensive.

### Parte bassa

Zona del giocatore:

* cannone controllato dal giocatore;
* indicatore vite/punteggio.

---

## Elementi grafici principali

### Giocatore

* Piccolo cannone o navicella.
* Movimento solo orizzontale.
* Aspetto simmetrico e semplice.

### Alieni

* Diversi tipi di sprite.
* Ogni riga può avere un alieno differente.
* Animazioni minime a 2 frame.

### Barriere

* Blocchi distruttibili.
* Si deteriorano quando vengono colpiti.

### Proiettili

* Sottili linee verticali luminose.
* Velocità costante.

---

# Meccaniche di gioco

## Movimento del giocatore

Il giocatore:

* può muoversi a sinistra e destra;
* non può salire o scendere;
* può sparare verso l’alto.

Comandi tipici:

* ← → per muoversi
* spazio per sparare

---

## Movimento degli alieni

Gli alieni:

1. si muovono orizzontalmente tutti insieme;
2. quando raggiungono un bordo:

   * scendono di una riga;
   * invertono direzione.

Schema tipico:

```text
→→→
←←←
→→→
```

Ogni discesa li avvicina al giocatore.

---

## Velocità dinamica

Una caratteristica famosa:

* meno alieni rimangono,
* più velocemente si muovono.

Questo crea tensione crescente:

* inizio lento e controllabile;
* finale rapido e caotico.

---

## Sistema di sparo

### Giocatore

Il giocatore può:

* avere un singolo proiettile attivo;
* sparare solo verso l’alto.

Quando il proiettile:

* colpisce un alieno → alieno distrutto;
* colpisce barriera → barriera danneggiata.

---

### Alieni

Gli alieni sparano:

* verso il basso;
* in modo casuale o pseudo-casuale.

I colpi:

* possono colpire il giocatore;
* possono distruggere le barriere.

---

# Regole di gioco

## Obiettivo

Distruggere tutti gli alieni dell’ondata.

Dopo ogni ondata:

* ne inizia una nuova;
* velocità e difficoltà aumentano.

---

## Condizioni di sconfitta

Il giocatore perde se:

* termina le vite;
* gli alieni raggiungono il fondo;
* un alieno collide col giocatore.

---

## Sistema vite

Generalmente:

* 3 vite iniziali;
* perdita di una vita quando colpiti.

Dopo un colpo:

* breve pausa;
* respawn del giocatore.

---

## Punteggio

Ogni alieno vale punti diversi:

* alieni più difficili → più punti.

Spesso:

* alieni superiori valgono di più;
* alieni inferiori valgono meno.

---

# Dinamica dei personaggi

## Giocatore

### Ruolo

Difensore terrestre.

### Dinamica

* movimento rapido ma limitato;
* deve schivare e mirare;
* gameplay basato su riflessi e timing.

---

## Alieni

### Comportamento collettivo

Gli alieni non si muovono individualmente:

* agiscono come una formazione unica.

Questo crea:

* pressione costante;
* avanzata inevitabile.

---

## UFO speciale

Molte versioni includono:

* una nave speciale che attraversa lo schermo in alto.

Caratteristiche:

* appare raramente;
* difficile da colpire;
* assegna molti punti bonus.

---

# Struttura logica del gioco

## Ciclo principale

Il gioco segue un loop continuo:

1. input del giocatore
2. aggiornamento posizioni
3. collisioni
4. rendering grafico
5. aggiornamento punteggio
6. controllo vittoria/sconfitta

---

## Collisioni

Collisioni principali:

* proiettile giocatore ↔ alieni
* proiettile alieni ↔ giocatore
* proiettili ↔ barriere

---

## Gestione ondate

Quando tutti gli alieni sono distrutti:

* nuova formazione;
* velocità aumentata;
* difficoltà crescente.

---

# Sensazione di gameplay

Space Invaders crea:

* tensione crescente;
* ritmo progressivamente accelerato;
* senso di assedio continuo.

Il giocatore alterna:

* precisione;
* schivate rapide;
* gestione del rischio.