# FastAPI Banking API

Questa applicazione FastAPI simula un sistema bancario con autenticazione, gestione degli account e trasferimenti di fondi tra utenti.

## **Installazione**

Questa applicazione utilizza **Poetry** per la gestione delle dipendenze. Assicurati di avere Poetry installato prima di procedere.

### **1. Clona il repository**
```sh
git clone <rpoetryepository_url>
cd <repository_name>
```

### **2. Installa le dipendenze**
```sh
poetry install
```

### **3. Avvia l'applicazione**
```sh
poetry run uvicorn fastapi_webserver.entrypoint:app --host 127.0.0.1 --port 8000 --reload
```
L'API sarà disponibile su `http://127.0.0.1:8000`.

---

## **Endpoints principali**

### **Autenticazione**
- **POST /token** → Ottiene un token di accesso con username e password

### **Gestione utenti**
- **GET /retrive_user/{access_token}** → Recupera username associato a un token
- **GET /account/{username}** → Mostra i dettagli dell'account di un utente

### **Transazioni**
- **POST /transfer** → Trasferisce fondi tra utenti

---

## **Testing**
L'applicazione include test automatici con **pytest**.
I test vengono eseguiti usando un immagine Docker.

### **Eseguire i test**
```sh
docker compose up
```

---

## **Autore**
Sviluppato da Antonio Cervelione.