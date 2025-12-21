#!/bin/bash

echo "🔧 REINSTALLAZIONE FORZATA GOOGLE ADS API"
echo "=========================================="
echo ""

# Verifica venv
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ Virtual environment NON attivo!"
    exit 1
fi

echo "✅ Virtual environment attivo: $VIRTUAL_ENV"
echo ""

# 1. Disinstalla completamente
echo "1️⃣  Disinstallazione completa..."
echo "-----------------------------------"
pip uninstall -y google-ads google-api-core googleapis-common-protos 2>/dev/null
echo "   ✅ Pacchetti rimossi"
echo ""

# 2. Pulisci cache pip
echo "2️⃣  Pulizia cache pip..."
echo "-----------------------------------"
pip cache purge
echo "   ✅ Cache pulita"
echo ""

# 3. Aggiorna pip
echo "3️⃣  Aggiornamento pip..."
echo "-----------------------------------"
pip install --upgrade pip
echo ""

# 4. Reinstalla google-ads
echo "4️⃣  Reinstallazione google-ads 24.1.0..."
echo "-----------------------------------"
pip install --no-cache-dir google-ads==24.1.0
echo ""

# 5. Verifica installazione
echo "5️⃣  Verifica installazione..."
echo "-----------------------------------"

python3 << 'PYEOF'
import sys
import os

try:
    # Trova dove è installato
    import google.ads.googleads
    base_path = os.path.dirname(google.ads.googleads.__file__)
    
    print(f"   📂 Path installazione:")
    print(f"      {base_path}")
    print()
    
    # Lista versioni API
    items = os.listdir(base_path)
    versions = [d for d in items if d.startswith('v') and os.path.isdir(os.path.join(base_path, d))]
    versions.sort()
    
    print(f"   📊 Versioni API trovate: {len(versions)}")
    for v in versions:
        marker = "👉" if v == versions[-1] else "  "
        print(f"      {marker} {v}")
    
    if versions:
        latest = versions[-1]
        print()
        print(f"   🎯 Ultima versione: {latest}")
        
        # Verifica v18
        if latest == 'v18':
            print("   ✅ API v18 disponibile!")
            sys.exit(0)
        else:
            print(f"   ⚠️  Versione: {latest} (dovrebbe essere v18)")
            print()
            print("   🔍 Debug info:")
            
            # Controlla se v18 esiste ma non viene rilevato
            v18_path = os.path.join(base_path, 'v18')
            if os.path.exists(v18_path):
                print(f"      v18 esiste ma non viene listato")
                print(f"      Path: {v18_path}")
            else:
                print(f"      v18 non esiste in {base_path}")
            
            sys.exit(1)
    else:
        print("   ❌ Nessuna versione API trovata!")
        sys.exit(1)
        
except Exception as e:
    print(f"   ❌ Errore: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ INSTALLAZIONE OK!"
    echo "=========================================="
    echo ""
    echo "🧪 Test connessione:"
    echo "   python test_google_ads_credentials.py"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "⚠️  PROBLEMA PERSISTENTE"
    echo "=========================================="
    echo ""
    echo "La versione 24.1.0 dovrebbe avere v18,"
    echo "ma nel tuo caso ha solo v17."
    echo ""
    echo "Possibili cause:"
    echo "1. Download corrotto da PyPI"
    echo "2. Problema nella build del pacchetto"
    echo "3. Incompatibilità con macOS/Python version"
    echo ""
    echo "🔧 SOLUZIONI ALTERNATIVE:"
    echo ""
    echo "Opzione A: Prova versione diversa"
    echo "   pip install google-ads==23.1.0"
    echo ""
    echo "Opzione B: Installa da GitHub"
    echo "   pip install git+https://github.com/googleads/google-ads-python.git@v24.1.0"
    echo ""
    echo "Opzione C: Controlla info pacchetto"
    echo "   pip show google-ads"
    echo "   pip check"
    echo ""
fi
