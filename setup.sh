#!/bin/bash

# Script di setup migliorato per Google Ads Automation
# Usage: ./setup-improved.sh

set -e  # Exit on error

echo "=================================="
echo "🚀 GOOGLE ADS AUTOMATION - SETUP"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

print_step() {
    echo -e "${BLUE}$1${NC}"
}

# 1. Verifica Python
print_step "1️⃣  Verifica Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION installato"
    
    # Verifica versione minima (3.10+)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
        print_error "Python 3.10+ richiesto. Hai Python $PYTHON_VERSION"
        exit 1
    fi
else
    print_error "Python 3 non trovato. Installa Python 3.10+"
    echo "Mac: brew install python@3.10"
    echo "Linux: sudo apt install python3.10"
    exit 1
fi

# 2. Verifica PostgreSQL
echo ""
print_step "2️⃣  Verifica PostgreSQL..."
if command -v psql &> /dev/null; then
    POSTGRES_VERSION=$(psql --version | cut -d' ' -f3)
    print_success "PostgreSQL $POSTGRES_VERSION installato"
else
    print_error "PostgreSQL non trovato"
    print_info "Mac: brew install postgresql@15"
    print_info "      brew services start postgresql@15"
    print_info "Linux: sudo apt install postgresql postgresql-contrib"
    print_info "       sudo systemctl start postgresql"
    exit 1
fi

# 3. Crea virtual environment
echo ""
print_step "3️⃣  Creazione virtual environment..."
if [ -d "venv" ]; then
    print_info "Virtual environment già esistente"
    read -p "Vuoi ricrearlo? (y/N): " RECREATE_VENV
    if [ "$RECREATE_VENV" = "y" ] || [ "$RECREATE_VENV" = "Y" ]; then
        rm -rf venv
        python3 -m venv venv
        print_success "Virtual environment ricreato"
    fi
else
    python3 -m venv venv
    print_success "Virtual environment creato"
fi

# 4. Attiva venv e installa dipendenze
echo ""
print_step "4️⃣  Installazione dipendenze Python..."
print_info "Attivazione virtual environment..."

# Attiva venv
source venv/bin/activate

# Verifica che siamo in venv
if [ -z "$VIRTUAL_ENV" ]; then
    print_error "Impossibile attivare virtual environment"
    exit 1
fi

print_success "Virtual environment attivo: $VIRTUAL_ENV"

# Upgrade pip
print_info "Upgrade pip..."
pip install --upgrade pip --quiet

# Installa dipendenze
print_info "Installazione dipendenze (potrebbe richiedere qualche minuto)..."
if pip install -r requirements.txt --quiet; then
    print_success "Dipendenze installate"
else
    print_error "Errore installazione dipendenze"
    print_info "Prova manualmente: source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# 5. Setup database
echo ""
print_step "5️⃣  Setup database..."
read -p "Nome database (default: google_ads_automation): " DB_NAME
DB_NAME=${DB_NAME:-google_ads_automation}

# Verifica se database esiste
if psql -lqt 2>/dev/null | cut -d \| -f 1 | grep -qw $DB_NAME; then
    print_info "Database '$DB_NAME' già esistente"
    read -p "Vuoi ricrearlo? ATTENZIONE: Perderai tutti i dati! (y/N): " RECREATE
    if [ "$RECREATE" = "y" ] || [ "$RECREATE" = "Y" ]; then
        dropdb $DB_NAME 2>/dev/null || true
        createdb $DB_NAME
        print_success "Database ricreato"
    fi
else
    if createdb $DB_NAME 2>/dev/null; then
        print_success "Database '$DB_NAME' creato"
    else
        print_error "Errore creazione database"
        print_info "Se PostgreSQL richiede password, configura ~/.pgpass"
        print_info "O esegui manualmente: createdb google_ads_automation"
        exit 1
    fi
fi

# Esegui schema
print_info "Applicazione schema database..."
if psql $DB_NAME < database/schema.sql > /dev/null 2>&1; then
    print_success "Schema database applicato"
else
    print_error "Errore applicazione schema"
    print_info "Verifica connessione PostgreSQL"
    exit 1
fi

# 6. Setup file configurazione
echo ""
print_step "6️⃣  Setup file configurazione..."

# .env
if [ ! -f ".env" ]; then
    if [ -f "_env" ]; then
        cp _env .env
    elif [ -f ".env.example" ]; then
        cp .env.example .env
    elif [ -f "_env.example" ]; then
        cp _env.example .env
    else
        print_error "Template .env non trovato"
        exit 1
    fi
    print_success ".env creato da template"
    print_info "⚠️  IMPORTANTE: Modifica .env con le tue credenziali!"
else
    print_info ".env già esistente"
fi

# google-ads.yaml
if [ ! -f "google-ads.yaml" ]; then
    if [ -f "google-ads_yaml.example" ]; then
        cp google-ads_yaml.example google-ads.yaml
    elif [ -f "google-ads.yaml.example" ]; then
        cp google-ads.yaml.example google-ads.yaml
    else
        print_error "Template google-ads.yaml non trovato"
        exit 1
    fi
    print_success "google-ads.yaml creato da template"
    print_info "⚠️  IMPORTANTE: Modifica google-ads.yaml con le tue credenziali Google Ads!"
else
    print_info "google-ads.yaml già esistente"
fi

# 7. Crea cartelle necessarie
echo ""
print_step "7️⃣  Creazione cartelle..."
mkdir -p logs
mkdir -p tmp
mkdir -p backups
print_success "Cartelle create"

# 8. Crea file __init__.py se mancano
echo ""
print_step "8️⃣  Verifica struttura moduli Python..."
for dir in agents api api/routes utils tests config database; do
    if [ -d "$dir" ] && [ ! -f "$dir/__init__.py" ]; then
        touch "$dir/__init__.py"
        print_info "Creato $dir/__init__.py"
    fi
done
print_success "Struttura moduli verificata"

# 9. Test configurazione
echo ""
print_step "9️⃣  Test configurazione..."
print_info "Test import moduli..."

if python -c "from config.settings import settings; print('✅ settings.py OK')" 2>/dev/null; then
    print_success "Config module OK"
else
    print_error "Errore import settings"
    print_info "Verifica che .env contenga tutte le variabili necessarie"
fi

if python -c "from database.database import get_db_session; print('✅ database.py OK')" 2>/dev/null; then
    print_success "Database module OK"
else
    print_error "Errore import database"
    print_info "Verifica DATABASE_URL in .env"
fi

# 10. Completamento
echo ""
echo "=================================="
echo "✅ SETUP COMPLETATO!"
echo "=================================="
echo ""
echo "📋 PROSSIMI PASSI:"
echo ""
echo "1. 🔑 Configura le credenziali:"
echo "   nano .env                    # Aggiungi API keys"
echo "   nano google-ads.yaml         # Aggiungi credenziali Google Ads"
echo ""
echo "2. 🔍 Verifica che il venv sia attivo:"
echo "   source venv/bin/activate     # Se non vedi (venv) nel prompt"
echo ""
echo "3. 🧪 Test connessione Google Ads:"
echo "   python agents/monitor.py"
echo ""
echo "4. 🤖 Test Analyzer con AI:"
echo "   python agents/analyzer.py --all"
echo ""
echo "5. 🚀 Avvia sistema:"
echo "   ./start.sh all               # API + Scheduler"
echo "   # oppure"
echo "   ./start.sh api               # Solo API"
echo "   ./start.sh scheduler         # Solo Scheduler"
echo ""
echo "📚 Documentazione:"
echo "   - README.md          # Documentazione completa"
echo "   - QUICKSTART.md      # Guida rapida"
echo ""
echo "⚠️  RICORDA: Attiva sempre venv prima di lavorare:"
echo "   source venv/bin/activate"
echo ""
