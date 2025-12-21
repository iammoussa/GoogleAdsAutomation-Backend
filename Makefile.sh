# Makefile per comandi comuni

.PHONY: help setup install test run clean

help:
    @echo "=================================="
    @echo "🚀 GOOGLE ADS AUTOMATION"
    @echo "=================================="
    @echo ""
    @echo "Comandi disponibili:"
    @echo "  make setup       - Setup iniziale completo"
    @echo "  make install     - Installa dipendenze"
    @echo "  make test        - Esegui test"
    @echo "  make run-api     - Avvia API server"
    @echo "  make run-scheduler - Avvia scheduler"
    @echo "  make run-all     - Avvia tutto"
    @echo "  make monitor     - Esegui monitor once"
    @echo "  make analyzer    - Esegui analyzer once"
    @echo "  make clean       - Pulisci file temporanei"
    @echo "  make logs        - Mostra logs in real-time"
    @echo ""

setup:
    @chmod +x setup.sh
    @./setup.sh

install:
    @pip install -r requirements.txt

test:
    @pytest tests/ -v --cov=agents --cov=api

run-api:
    @chmod +x start.sh
    @./start.sh api

run-scheduler:
    @chmod +x start.sh
    @./start.sh scheduler

run-all:
    @chmod +x start.sh
    @./start.sh all

dev:
    @chmod +x start.sh
    @./start.sh dev

monitor:
    @chmod +x start.sh
    @./start.sh monitor

analyzer:
    @chmod +x start.sh
    @./start.sh analyzer

executor-dry:
    @chmod +x start.sh
    @./start.sh executor

clean:
    @rm -rf __pycache__ */__pycache__ */*/__pycache__
    @rm -rf .pytest_cache
    @rm -rf htmlcov
    @rm -rf .coverage
    @rm -rf tmp/*
    @rm -rf *.egg-info
    @find . -name "*.pyc" -delete
    @echo "✅ Cleanup completato"

logs:
    @tail -f logs/app.log

logs-errors:
    @tail -f logs/errors.log

db-reset:
    @echo "⚠️  Resetting database..."
    @dropdb google_ads_automation 2>/dev/null || true
    @createdb google_ads_automation
    @psql google_ads_automation < database/schema.sql
    @echo "✅ Database resettato"

db-backup:
    @mkdir -p backups
    @pg_dump google_ads_automation > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
    @echo "✅ Backup creato in backups/"
