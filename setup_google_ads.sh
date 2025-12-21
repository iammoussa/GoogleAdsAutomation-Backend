#!/bin/bash

echo "🔧 SETUP GOOGLE ADS API - DIAGNOSI E FIX"
echo "=========================================="
echo ""

# 1. Verifica virtual environment
echo "1️⃣  Verifica Virtual Environment"
echo "-----------------------------------"
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment ATTIVO"
    echo "   Path: $VIRTUAL_ENV"
else
    echo "❌ Virtual environment NON attivo!"
    echo ""
    echo "🔧 SOLUZIONE:"
    echo "   cd /percorso/google-ads-automation"
    echo "   source venv/bin/activate"
    echo ""
    exit 1
fi

echo ""

# 2. Verifica Python path
echo "2️⃣  Verifica Python Path"
echo "-----------------------------------"
PYTHON_PATH=$(which python)
echo "   Python in uso: $PYTHON_PATH"

if [[ "$PYTHON_PATH" == *"venv"* ]]; then
    echo "   ✅ Python del venv"
else
    echo "   ⚠️  Python NON del venv!"
    echo "   Riattiva il venv: source venv/bin/activate"
fi

echo ""

# 3. Verifica pip path
echo "3️⃣  Verifica Pip Path"
echo "-----------------------------------"
PIP_PATH=$(which pip)
echo "   Pip in uso: $PIP_PATH"

if [[ "$PIP_PATH" == *"venv"* ]]; then
    echo "   ✅ Pip del venv"
else
    echo "   ⚠️  Pip NON del venv!"
fi

echo ""

# 4. Controlla se google-ads è installato
echo "4️⃣  Controlla google-ads installato"
echo "-----------------------------------"
INSTALLED=$(pip list 2>/dev/null | grep -i "^google-ads ")

if [[ -z "$INSTALLED" ]]; then
    echo "   ❌ google-ads NON installato"
    NEED_INSTALL=true
else
    echo "   ✅ Trovato: $INSTALLED"
    
    # Estrai versione
    VERSION=$(echo "$INSTALLED" | awk '{print $2}')
    
    if [[ "$VERSION" == "24."* ]]; then
        echo "   ✅ Versione corretta: $VERSION"
        NEED_INSTALL=false
    else
        echo "   ⚠️  Versione vecchia: $VERSION (serve 24.1.0)"
        NEED_INSTALL=true
    fi
fi

echo ""

# 5. Installa/Aggiorna se necessario
if [ "$NEED_INSTALL" = true ]; then
    echo "5️⃣  Installazione google-ads 24.1.0"
    echo "-----------------------------------"
    
    # Disinstalla se presente
    if [[ -n "$INSTALLED" ]]; then
        echo "   Disinstallo versione vecchia..."
        pip uninstall -y google-ads >/dev/null 2>&1
    fi
    
    echo "   Installo google-ads==24.1.0..."
    pip install google-ads==24.1.0
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "   ✅ Installazione completata!"
    else
        echo ""
        echo "   ❌ Installazione fallita"
        echo ""
        echo "   Prova manualmente:"
        echo "   pip install --upgrade pip"
        echo "   pip install google-ads==24.1.0"
        exit 1
    fi
    
    echo ""
fi

# 6. Verifica finale
echo "6️⃣  Verifica finale"
echo "-----------------------------------"

python3 << 'PYEOF'
import sys

try:
    # Import test
    from google.ads.googleads.client import GoogleAdsClient
    print("   ✅ Import GoogleAdsClient: OK")
    
    # Verifica versioni API
    import os
    import google.ads.googleads
    
    base_path = os.path.dirname(google.ads.googleads.__file__)
    versions = [d for d in os.listdir(base_path) if d.startswith('v') and os.path.isdir(os.path.join(base_path, d))]
    versions.sort()
    
    if versions:
        latest = versions[-1]
        print(f"   ✅ Ultima API: {latest}")
        
        if latest == 'v18':
            print("   ✅ API v18 disponibile (corretta)")
        else:
            print(f"   ⚠️  API {latest} (dovrebbe essere v18)")
            sys.exit(1)
    else:
        print("   ❌ Nessuna versione API trovata")
        sys.exit(1)
        
except Exception as e:
    print(f"   ❌ Errore: {e}")
    sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ TUTTO PRONTO!"
    echo "=========================================="
    echo ""
    echo "🧪 Ora puoi testare la connessione:"
    echo "   python test_google_ads_credentials.py"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "❌ PROBLEMI RILEVATI"
    echo "=========================================="
    echo ""
    echo "Controlla i messaggi sopra per dettagli"
    exit 1
fi
