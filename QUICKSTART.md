# ⚡ QUICKSTART GUIDE

Inizia in 5 minuti! 🚀

---

## 🎯 Setup Veloce

### 1. Clone & Setup
```bash
git clone <repo-url>
cd google-ads-automation

# Setup automatico
chmod +x setup.sh
./setup.sh
```

Lo script:
- ✅ Verifica Python e PostgreSQL
- ✅ Crea virtual environment
- ✅ Installa dipendenze
- ✅ Crea database
- ✅ Genera file configurazione

---

### 2. Configura Credenziali

**Google Ads API:**
```bash
nano google-ads.yaml
```
Inserisci:
- Developer Token
- Client ID & Secret
- Refresh Token
- Customer ID

**Claude API:**
```bash
nano .env
```
Inserisci:
```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
GOOGLE_ADS_CUSTOMER_ID=1234567890
```

---

### 3. Test Connessione
```bash
# Test Google Ads
python agents/monitor.py

# Output atteso:
# ✅ Trovate 3 campagne
# ⚠️  Rilevati 2 alert
```

---

### 4. Prima Analisi AI
```bash
# Analizza tutte le campagne
python agents/analyzer.py --all

# Output atteso:
# 🤖 Chiamata Claude API...
# ✅ 5 azioni proposte
```

---

### 5. Avvia Sistema

**Opzione A - Sistema Completo:**
```bash
./start.sh all
```

**Opzione B - Solo API (per dashboard):**
```bash
./start.sh api
```

**Opzione C - Solo Scheduler (monitoring automatico):**
```bash
./start.sh scheduler
```

---

## 🎮 Comandi Utili
```bash
# Makefile commands
make setup          # Setup completo
make run-all        # Avvia tutto
make monitor        # Monitor once
make analyzer       # Analyzer once
make logs           # Vedi logs live
make test           # Test suite

# Direct commands
./start.sh monitor        # Solo monitor
./start.sh analyzer       # Solo analyzer
./start.sh executor       # Executor (dry-run)
./start.sh dev            # Development mode
```

---

## 📊 API Endpoints

API disponibile su `http://localhost:8000`

**Campagne:**
- `GET /api/campaigns/` - Lista campagne
- `GET /api/campaigns/{id}` - Dettagli campagna
- `GET /api/campaigns/{id}/history` - Storico metriche

**Azioni:**
- `GET /api/actions/pending` - Azioni da approvare
- `POST /api/actions/{id}/approve` - Approva azione
- `POST /api/actions/execute` - Esegui azioni

**Docs:**
- `http://localhost:8000/docs` - Swagger UI
- `http://localhost:8000/redoc` - ReDoc

---

## 🐳 Docker Quick Start
```bash
# Build & Start
docker-compose up -d

# Logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## 🔥 Workflow Tipo
```bash
# 1. Setup iniziale (1x)
./setup.sh

# 2. Configura credenziali
nano .env
nano google-ads.yaml

# 3. Test
python agents/monitor.py

# 4. Avvia sistema
./start.sh all

# 5. Dashboard Flutter si connette a localhost:8000

# 6. Monitor gira ogni 6h automaticamente
# 7. Tu approvi azioni da dashboard
# 8. Executor applica modifiche
```

---

## ❓ Problemi Comuni

**"Google Ads API failed"**
→ Verifica customer ID in `.env`

**"Claude API timeout"**
→ Verifica API key in `.env`

**"Database connection refused"**
→ Verifica PostgreSQL: `pg_isready`

**"No campaigns found"**
→ Verifica customer ID corretto

---

## 📚 Prossimi Step

1. ✅ Setup completo
2. ✅ Test monitor
3. ✅ Test analyzer
4. 📱 Connetti Dashboard Flutter
5. 🚀 Deploy in produzione

Leggi **README.md** per documentazione completa!
