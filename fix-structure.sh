#!/bin/bash

# Script veloce per fixare la struttura Python
# Usage: chmod +x fix-structure.sh && ./fix-structure.sh

echo "🔧 Fixing Python module structure..."
echo ""

# Crea __init__.py in tutte le directory necessarie
directories=(
    "agents"
    "config"
    "database"
    "utils"
    "api"
    "api/routes"
    "tests"
)

for dir in "${directories[@]}"; do
    if [ -d "$dir" ]; then
        if [ ! -f "$dir/__init__.py" ]; then
            touch "$dir/__init__.py"
            echo "✅ Creato $dir/__init__.py"
        else
            echo "ℹ️  $dir/__init__.py già esistente"
        fi
    else
        echo "⚠️  Directory $dir non trovata (normale se non esiste ancora)"
    fi
done

echo ""
echo "✅ Struttura fixata!"
echo ""
echo "📝 Aggiungi al tuo ~/.zshrc o ~/.bashrc:"
echo ""
echo "# Google Ads Automation"
echo "export PYTHONPATH=\"\${PYTHONPATH}:$PWD\""
echo ""
echo "Oppure esegui prima di ogni comando:"
echo "export PYTHONPATH=\"\${PYTHONPATH}:$(pwd)\""
echo ""
echo "O usa lo script ./run.sh che lo fa automaticamente:"
echo "./run.sh monitor"
echo ""
