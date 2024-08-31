# SeeBeyond - Guarda Oltre
SeeBeyond è un progetto, sviluppato a fini educativi, che ha come obiettivo per attenuare le problematiche degli ipovedenti e si pone come obiettivo quello di aiutarle nella loro vita quotidiana, ma con scopo primario quello di riconoscere e calcolare la distanza delle entità che circondano l’utente.
<p align="center">
<img src="https://github.com/user-attachments/assets/19148584-e54c-49b3-a5e1-0ac05b28fde4" alt="image" width="300" height="auto" />
</p>

Il progetto SeeBeyond si compone di un backend e un frontend: \
Repository Backend: https://github.com/Miki-Palmisano/SeeBeyond-AI \
Repository Frontend: https://github.com/Miki-Palmisano/SeeBeyond

## SeeBeyond AI

Sviluppato in Python utilizzando una Rete Neurale di tipo Convoluzionale dedicata al riconoscimento di oggetti e animali. Python è stato scelto come linguaggio principale per la sua flessibilità, facilità di apprendimento e per l’ampia disponibilità di librerie e framework, come TensorFlow e PyTorch. \
\
Una Rete Neurale di tipo Convoluzionale è una rete di neuroni artificiale che è ispirata all’apprendimento visivo animale, cioè che apprende e trova corrispondenze da una sequenza di immagini fornite come input. La scelta di una rete neurale rappresenta un vantaggio significativo, poiché, in particolare le reti neurali Convoluzionali (CNN), sono note per la loro capacità di apprendere da grandi quantità di dati, identificando modelli complessi e svolgendo compiti di classificazione e riconoscimento con un’elevata precisione. \
\
Queste tecnologie offrono la possibilità di elaborare e analizzare immagini, riconoscendo in modo efficiente e accurato oggetti e animali. La flessibilità delle reti neurali consente inoltre di adattarsi a diverse tipologie di dati e di essere ottimizzate per raggiungere livelli sempre maggiori di precisione e affidabilità nel riconoscimento. \
\
In Python, si è scelto di progettare (dunque non implementato) anche un Optical Character Recognition (OCR), tecnologia che consente di convertire immagini di testo stampato o scritto a mano in testo elettronico editabile. L’obiettivo principale di questa scelta è quello di permettere agli utenti con deficit visivi di essere informati su comunicazioni ed eventi che circondano la vita quotidiana, partendo da un cartello stradale o una locandina di un evento fino ad arrivare a dei semplici nomi e prezzi di prodotti acquistabili in un supermercato.

## Implementazione e Test

### Librerie e Modelli

SeeBeyond, in quanto riconoscitore di entità (oggetti o animali), ha avuto bisogno di un Object Detection, che si differenzia da comune Computer Vision dalla possibilità di non solo riconoscere ma anche localizzare l’oggetto nel frame, necessario al calcolo della distanza. Dunque si sono andate valutate le librerie PyTorch e TensorFlow, entrambi framework di Machine Learning open-source. \
\
PyTorch e TensorFlow presentano alcune differenze significative nella gestione della parte di Addestramento: PyTorch utilizza un grafico computazionale dinamico, che consente modifiche durante l’esecuzione, facilitando il debug e la sperimentazione, dunque durante il train si possono modificare parametri di apprendimento in modo da far convergere il grafico. TensorFlow, invece, si basa su un grafico statico, offrendo potenzialmente vantaggi di ottimizzazione durante l’esecuzione e maggiore velocità, a discapito però della garanzia di successo. Inoltre, PyTorch è spesso elogiato per la sua sintassi intuitiva e approccio "Pythonic", rendendo più agevole la scrittura di codice. D’altro canto, TensorFlow ha un ecosistema più ampio e particolarmente forte con l’integrazione di strumenti esterni o di terze parti. \
\
Dopo aver approfondito vantaggi e svantaggi, si è optato per Pytorch in quanto più flessibile e maneggevole rispetto TensorFlow. Per quanto riguarda le tipologie di train di AI, si è ritenuto interessante l’approccio che segue il Trasfered Learning, ovvero acquisire un modello preaddestrato, Faster R-CNN ResNet50 nel caso in questione, e sostituirne il layer di dataset con uno costruito in base alle esigenze progettuali. 

### Dataset

Il dataset iniziale è costituito da due sole classi, "gatto" e "automobile". Lo stesso è stato costruito grazie ad uno script scritto ad hoc che, connettendosi con <a href='https://cocodataset.org/#home'>COCO Dataset</a> presente online (dataset.py), acquisisce Immagini, Label e Boxes al fine di individuare velocemente le entità nei frame, necessari per la fase di train di un modello di Object Detection. Le Label non sono altro che i campi che contengono l’identificativo della classe dell’oggetto, mentre i Boxes sono proprio le figure geometriche che circoscrivono l’oggetto riconosciuto (solitamente vengono utilizzati dei rettangoli).

### Addestramento

La fase di addestramento del modello parte dall’adattamento del dataset di COCO in un formato riconoscibile dal modello Faster R-CNN ResNet50, dove 50 sono i layer che costituiscono il modello stesso. Nel nostro caso, dopo aver convertito il dataset (convertDataset.py) ricavandone il box e assegnando un nosto label (formato da ID e Nome), sostituiamo l’ultimo layer, tecnica chiamata Transfered Learning. \
\
Il train si struttura in epoche, dove per ogni epoca viene analizzato il dataset in toto. Indice di convergenza è il valore di LOSS che indica la perdita 
di apprendimento del modello, obiettivo è quello di minimizzarlo. Dopo numerosi test e dopo aver cambiato i parametri del Learning Rate, Batch Size (numero di immagini analizzate simultaneamente per volta) e Weight Decay (paramentro che regolarizza l’aggiornamento dei pesi del modello in modo tale da non ricadere in Overfitting, cioè l’adattamento eccessivo del modello ai dati di addestramento) abbiamo ottenuto un modello con valore di LOSS del circa 8% che esaudiva le richieste minime del prototipo. \
\
In particolare si è sfruttata l’architettura di Pytorch mediante l’uso di uno Scheduler, algoritmo che in base a dei parametri preimpostati, monitora costantemente l’apprendimento del modello, riducendo il Learning Rate in caso di divergenza dello stesso. Il modello, addestrato sul nostro dataset, è stato poi salvato in un formato ".pth" nativo di PyTorch, il quale consente di essere utilizzato successivamente. Per la fase di riconoscimento quindi si è aggiunto il modello di partenza (Faster R-CNN ResNet50) e si sono impostati i pesi derivati dall’addestramento. Le percentuali risultanti che ha offerto sono apprezzabili in fase prototipale. La dimostrazione del funzionamento del protipo è presente nella figura di seguito.

<p align="center">
<img src="https://github.com/user-attachments/assets/a50787fa-1b62-4f41-91f9-420baacd0e87" alt="image" width="auto" height="300">
</p>

### Calcolo della distanza

Dopo aver ottenuto un modello apprezzabile, si è occupati di riuscire a calcolare la distanza delle entità, usando il criterio della Fotogrammetria, secondo cui, disponendo di due frame contenenti la stessa entità in movimento, si riesce a calcolarne la distanza mediante le formule di base alla trigonometria. In fase prototipale si è usati la webcam del MacBook e la videocamera dell’iPhone, tecnologia disponibile in ambiente Apple che, seppur diverse in specifiche tecniche, hanno restituito risultati accettabili. Di norma si devono disporre di due videocamere identiche. Su ogni frame si è andati dunque a disegnare il Box che circondava l’entità riconosciuta, derivata dalla Object Detection, la tipologia "auto" o "gatto", derivata dall’addestramento, e la distanza, derivata dalla triangolazione.

### Conclusione

Il tempo impiegato per progettare e implementare il sistema non è stato sufficiente a realizzare un prototipo completo in ogni sua parte, dunque nella sua fase prototipale si è scelto di ridurre il numero di classi a due, mostrando però le potenzialità che possono scaturire da quello che è idealmente SeeBeyond.

## Obiettivi Futuri

### Potenziamento dell'AI (prime fasi minime)
Come prima obiettivo futuro c’è sicuramente l’aumento del numero di classi riconosciute dal Software AI, essendo fino ad ora solo due ("Gatto" e "Auto"), andando ad addestrare l’AI stessa in modo da includere quante più entità possibili, ed aumentarne l’affidabilità di riconoscimento. \
\
Ulteriore successiva pubblicazione si concentrerà sull’implementazione dell’OCR, funzionalità dapprima testata usando la libreria Tesseract ma successivamente accantonata in quanto non soddisfava i requisiti minimi. \

### Classificazione degli Ambienti (Upgrade AI)

Funzionalità aggiuntiva di sicurezza è la classificazione degli ambienti, a partire da un ambiente Cittadino fino ad arrivare ad un ambiente Sterrato, in quanto potrebbe tornare utile all’utente saperlo.
In aggiunta a queste si informeranno gli utenti dei punti di pericolosità situati in esse, come:
<ul>
  <li>Scale o buche in ambiente cittadino;</li>
  <li>Ammassi di roccia o parti di strada dismessi in ambiente sterrato;</li>
  <li>Eventuali punti poco chiari (per illuminazione o per mancato ricono- scimento) o sospetti in caso di qualsiasi ambiente.</li>
</ul>

### Gestione Pericolosità e Umore Animali (Upgrade AI)

Un’altra funzionalità interessante è la gestione della pericolosità, momentanea o permanente, degli animali, implementando, qualora un animale fosse classificato come "pericoloso", tecniche per fare in modo di scacciarlo e renderlo inoffensivo. \
\
In un’ulteriore prospettiva futura, si prevede di implementare la capacità di rilevare lo stato emotivo degli animali.


## TERMINI E CONDIZIONI D'USO

<p align="center">
© [SeeBeyond - Guarda Oltre] - [2023/2024] <br>
  <br>
<strong>IL CODICE È FORNITO “COSÌ COM’È” SENZA GARANZIA DI ALCUN TIPO, CONCESSO A TITOLO GRATUITO A QUALSIASI PERSONA E DI UTILIZZARLO SENZA RESTRIZIONI, ESCLUDENDO FINI DI COMMERCIABILITÀ. IN NESSUN CASO GLI AUTORI DEL CODICE SARANNO RESPONSABILI PER QUALSIASI RECLAMO, DANNI O ALTRA RESPONSABILITÀ, DERIVANTI DA O IN CONNESSIONE CON IL CODICE O L’USO.</strong><br>
<br>
L’avviso di copyright sopra riportato e questo avviso di permesso devono essere inclusi in tutte le copie o porzioni sostanziali, citando gli autori del suddetto: <br>
<br>
Ideato e Realizzato da <br>
  <br>
Miki Palmisano - <a href="https://github.com/Miki-Palmisano">Link GitHub</a> <br>
Riccardo Semeraro - <a href="https://github.com/riccardosemeraro">Link GitHub</a> <br>
Davide Verditto - <a href="https://github.com/wDaaV">Link GitHub</a> <br>
<br>
Un gruppo di Studenti del <a href="http://www.poliba.it/">Politecnico di Bari</a> <br>
<br>
Progetto rivolto a persone ipovedenti che necessitano di sostegno e sicurezza per orientarsi in qualsiasi luogo circostante.
</p>



