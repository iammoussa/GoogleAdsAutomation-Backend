#!/bin/bash

# Script per avviare i vari componenti del sistema
# Usage: ./start.sh [component]

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Attiva venv
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment non trovato. Esegui ./setup.sh prima"
    exit 1
fi

COMPONENT=${1:-help}

case $COMPONENT in
    api)
        print_info "Avvio API Server..."
        python api/main.py
        ;;
    
    scheduler)
        print_info "Avvio Scheduler..."
        python agents/scheduler.py
        ;;
    
    monitor)
        print_info "Esecuzione Monitor (once)..."
        python agents/scheduler.py --monitor-only
        ;;
    
    analyzer)
        print_info "Esecuzione Analyzer (once)..."
        python agents/scheduler.py --analyze-only
        ;;
    
    executor)
        print_info "Esecuzione Executor (dry-run)..."
        python agents/scheduler.py --execute-only --dry-run
        ;;
    
    executor-real)
        echo "⚠️  ATTENZIONE: Esecuzione REALE - applicherà modifiche a Google Ads!"
        read -p "Sei sicuro? (scrivi 'YES' per confermare): " CONFIRM
        if [ "$CONFIRM" = "YES" ]; then
            print_info "Esecuzione Executor (REALE)..."
            python agents/scheduler.py --execute-only
        else
            echo "❌ Annullato"
        fi
        ;;
    
    all)
        print_info "Avvio completo (API + Scheduler)..."
        
        # Avvia API in background
        python api/main.py &
        API_PID=$!
        print_success "API avviata (PID: $API_PID)"
        
        # Avvia Scheduler
        python agents/scheduler.py
        
        # Cleanup on exit
        kill $API_PID 2>/dev/null || true
        ;;
    
    dev)
        print_info "Modalità DEVELOPMENT..."
        print_info "API con auto-reload + Monitor ogni 1h"
        
        # Override settings per dev
        export API_RELOAD=true
        export MONITOR_INTERVAL_HOURS=1
        export LOG_LEVEL=DEBUG
        
        ./start.sh all
        ;;
    
    test)
        print_info "Esecuzione test suite..."
        pytest tests/ -v
        ;;
    
    help|*)
        echo "=================================="
        echo "🚀 GOOGLE ADS AUTOMATION - START"
        echo "=================================="
        echo ""
        echo "Usage: ./start.sh [component]"
        echo ""
        echo "Components disponibili:"
        echo "  api            - Avvia solo API server"
        echo "  scheduler      - Avvia solo Scheduler (monitoring automatico)"
        echo "  monitor        - Esegui Monitor una volta"
        echo "  analyzer       - Esegui Analyzer una volta"
        echo "  executor       - Esegui Executor in DRY-RUN"
        echo "  executor-real  - Esegui Executor REALE (applica modifiche)"
        echo "  all            - Avvia API + Scheduler insieme"
        echo "  dev            - Modalità development (auto-reload)"
        echo "  test           - Esegui test suite"
        echo "  help           - Mostra questo messaggio"
        echo ""
        echo "Esempi:"
        echo "  ./start.sh api              # Solo API"
        echo "  ./start.sh scheduler        # Solo scheduler"
        echo "  ./start.sh all              # Sistema completo"
        echo "  ./start.sh dev              # Development mode"
        echo ""
        ;;
esac
