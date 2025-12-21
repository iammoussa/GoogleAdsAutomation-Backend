#!/bin/bash

# Script per aggiungere configurazione Gemini al tuo .env esistente
# Usage: chmod +x patch-env-gemini.sh && ./patch-env-gemini.sh

set -e

echo "============================================"
echo "🔧 PATCH .env - Aggiungi Gemini"
echo "============================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_info() { echo -e "${YELLOW}ℹ️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_step() { echo -e "${BLUE}$1${NC}"; }

# Verifica che .env esista
if [ ! -f ".env" ]; then
    print_error ".env non trovato!"
    echo "Crea prima il file .env"
    exit 1
fi

print_success ".env trovato"
echo ""

# Backup .env
print_step "📦 Backup .env..."
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
print_success "Backup creato: .env.backup.*"
echo ""

# Verifica se AI_PROVIDER è già presente
if grep -q "AI_PROVIDER=" .env; then
    print_info "AI_PROVIDER già presente in .env"
    
    # Chiedi se vuole aggiornare
    read -p "Vuoi aggiornare la configurazione AI? (y/N): " UPDATE
    if [ "$UPDATE" != "y" ] && [ "$UPDATE" != "Y" ]; then
        print_info "Operazione annullata"
        exit 0
    fi
    
    # Aggiorna AI_PROVIDER a gemini
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/AI_PROVIDER=.*/AI_PROVIDER=gemini/" .env
    else
        sed -i "s/AI_PROVIDER=.*/AI_PROVIDER=gemini/" .env
    fi
    print_success "AI_PROVIDER aggiornato a 'gemini'"
else
    # Aggiungi nuova sezione AI Provider
    print_step "➕ Aggiungo configurazione AI Provider..."
    
    # Trova dove inserire (dopo ANTHROPIC_API_KEY se esiste, altrimenti dopo GOOGLE_ADS)
    if grep -q "ANTHROPIC_API_KEY=" .env; then
        # Inserisci prima di ANTHROPIC_API_KEY
        cat >> .env.tmp << 'EOF'

# ================================
# AI PROVIDER CONFIGURATION
# ================================
# Scegli: 'gemini' (GRATIS) o 'claude' (a pagamento)
AI_PROVIDER=gemini

# Gemini (Google AI Studio) - GRATUITO
# Ottieni key da: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-1.5-flash

EOF
        
        # Aggiungi ANTHROPIC_MODEL se non presente
        if ! grep -q "ANTHROPIC_MODEL=" .env; then
            echo "ANTHROPIC_MODEL=claude-3-5-sonnet-20241022" >> .env.tmp
        fi
        
        # Inserisci prima di ANTHROPIC_API_KEY
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' '/ANTHROPIC_API_KEY=/r .env.tmp' .env
        else
            sed -i '/ANTHROPIC_API_KEY=/r .env.tmp' .env
        fi
        
        rm .env.tmp
        
    else
        # Aggiungi alla fine della sezione Google Ads
        cat >> .env << 'EOF'

# ================================
# AI PROVIDER CONFIGURATION
# ================================
# Scegli: 'gemini' (GRATIS) o 'claude' (a pagamento)
AI_PROVIDER=gemini

# Gemini (Google AI Studio) - GRATUITO
# Ottieni key da: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-1.5-flash

# Claude (Anthropic) - A PAGAMENTO
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

EOF
    fi
    
    print_success "Configurazione AI Provider aggiunta"
fi

echo ""

# Aggiungi TARGET thresholds se non presenti
if ! grep -q "TARGET_CTR_MIN=" .env; then
    print_step "➕ Aggiungo TARGET thresholds..."
    
    cat >> .env << 'EOF'

# ================================
# TARGET PERFORMANCE THRESHOLDS
# ================================
TARGET_CTR_MIN=2.0
TARGET_CPC_MAX=0.60
TARGET_ROAS_MIN=1.5
TARGET_OPTIMIZATION_SCORE_MIN=60.0

EOF
    print_success "TARGET thresholds aggiunti"
fi

echo ""

# Chiedi Gemini API Key
print_step "🔑 Configurazione Gemini API Key..."
echo ""
echo "📝 Per ottenere la tua API key GRATUITA:"
echo "   1. Vai su: https://aistudio.google.com/app/apikey"
echo "   2. Clicca 'Create API Key'"
echo "   3. Copia la key (inizia con AIza...)"
echo ""

# Mostra key attuale se esiste
CURRENT_KEY=$(grep "GEMINI_API_KEY=" .env | cut -d'=' -f2)
if [ ! -z "$CURRENT_KEY" ] && [ "$CURRENT_KEY" != "your-gemini-api-key-here" ]; then
    print_info "Key attuale: ${CURRENT_KEY:0:15}..."
fi

read -p "Inserisci la tua Gemini API Key (o premi Enter per saltare): " GEMINI_KEY

if [ ! -z "$GEMINI_KEY" ]; then
    # Aggiorna GEMINI_API_KEY
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s|GEMINI_API_KEY=.*|GEMINI_API_KEY=$GEMINI_KEY|" .env
    else
        sed -i "s|GEMINI_API_KEY=.*|GEMINI_API_KEY=$GEMINI_KEY|" .env
    fi
    print_success "GEMINI_API_KEY configurata"
else
    print_info "Configura GEMINI_API_KEY manualmente in .env"
fi

echo ""

# Mostra diff
print_step "📊 Modifiche effettuate:"
echo ""
if command -v diff &> /dev/null; then
    BACKUP_FILE=$(ls -t .env.backup.* | head -1)
    if [ ! -z "$BACKUP_FILE" ]; then
        echo "--- .env (prima)"
        echo "+++ .env (dopo)"
        diff "$BACKUP_FILE" .env || true
    fi
fi

echo ""
echo "============================================"
echo "✅ PATCH COMPLETATO!"
echo "============================================"
echo ""
echo "📋 COSA È STATO FATTO:"
echo "   ✅ Backup creato (.env.backup.*)"
echo "   ✅ AI_PROVIDER=gemini aggiunto"
echo "   ✅ GEMINI_API_KEY configurata"
echo "   ✅ GEMINI_MODEL impostato"
echo "   ✅ TARGET thresholds aggiunti"
echo ""
echo "🔍 VERIFICA IL FILE:"
echo "   cat .env | grep -A 5 'AI_PROVIDER'"
echo ""
echo "📝 SE SERVE MODIFICARE:"
echo "   nano .env"
echo ""
echo "🧪 TEST CONFIGURAZIONE:"
echo "   python config/settings.py"
echo ""
echo "🔙 RIPRISTINARE BACKUP SE SERVE:"
echo "   cp .env.backup.* .env"
echo ""
