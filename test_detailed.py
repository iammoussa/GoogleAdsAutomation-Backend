#!/usr/bin/env python3
"""
Test avanzato Google Ads API - Cattura errori specifici
"""

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import sys

print("="*60)
print("🔍 TEST DETTAGLIATO GOOGLE ADS API")
print("="*60)
print()

try:
    # Carica client
    print("1️⃣  Caricamento credenziali da google-ads.yaml...")
    client = GoogleAdsClient.load_from_storage("google-ads.yaml")
    print("   ✅ Client inizializzato")
    print()
    
    # Leggi configurazione
    print("2️⃣  Verifica configurazione:")
    with open("google-ads.yaml", "r") as f:
        import yaml
        config = yaml.safe_load(f)
        
        dev_token = config.get('developer_token', 'MISSING')
        print(f"   Developer Token: {dev_token[:10]}...")
        print(f"   Client ID: {config.get('client_id', 'MISSING')[:30]}...")
        print(f"   Login Customer ID: {config.get('login_customer_id', 'MISSING')}")
        print(f"   use_proto_plus: {config.get('use_proto_plus', 'MISSING')}")
        
        customer_id = config.get('login_customer_id')
    print()
    
    # Verifica versione API
    print("3️⃣  Verifica versione API...")
    import google.ads.googleads
    import os
    
    base_path = os.path.dirname(google.ads.googleads.__file__)
    versions = [d for d in os.listdir(base_path) if d.startswith('v') and os.path.isdir(os.path.join(base_path, d))]
    versions.sort()
    print(f"   Versioni disponibili: {', '.join(versions)}")
    print(f"   Ultima: {versions[-1]}")
    print()
    
    # Test connessione con gestione errori dettagliata
    print("4️⃣  Test connessione con query base...")
    print()
    
    query = """
        SELECT 
            customer.id,
            customer.descriptive_name
        FROM customer
        LIMIT 1
    """
    
    ga_service = client.get_service("GoogleAdsService")
    
    try:
        print(f"   📡 Invio richiesta a Google Ads API...")
        print(f"   Customer ID: {customer_id}")
        print()
        
        response = ga_service.search(
            customer_id=customer_id,
            query=query
        )
        
        for row in response:
            print(f"   ✅ CONNESSIONE RIUSCITA!")
            print()
            print(f"   Account ID: {row.customer.id}")
            print(f"   Account Name: {row.customer.descriptive_name}")
            print()
            break
        
        print("="*60)
        print("✅ TUTTO OK! Google Ads API funzionante")
        print("="*60)
        print()
        print("🚀 Prossimi passi:")
        print("   python check_account_structure.py")
        print("   python monitor.py")
        sys.exit(0)
        
    except GoogleAdsException as ex:
        print(f"   ❌ Errore Google Ads API")
        print()
        print("   📋 Dettagli errore:")
        print("   " + "="*56)
        
        for error in ex.failure.errors:
            error_code_name = error.error_code._name_
            error_message = error.message
            
            print(f"   Error Code: {error_code_name}")
            print(f"   Message: {error_message}")
            print()
            
            # Analisi errori specifici
            if "DEVELOPER_TOKEN" in error_code_name:
                print("   🎯 CAUSA: Developer Token")
                print("   " + "-"*56)
                print()
                print("   Il tuo Developer Token NON è ancora approvato.")
                print()
                print("   📝 STATUS CHECK:")
                print("   1. Vai su: https://ads.google.com/aw/apicenter")
                print("   2. Cerca 'API Center' nel menu")
                print("   3. Controlla lo status del token:")
                print()
                print("      ⏳ PENDING   → Aspetta email (24-48h)")
                print("      ✅ APPROVED  → Token approvato (strano!)")
                print("      ❌ DENIED    → Devi richiedere di nuovo")
                print()
                print("   💡 NOTA:")
                print("   - Solo Manager Account (MCC) può richiedere token")
                print("   - Devi spiegare l'uso dell'API")
                print("   - Approvazione manuale da Google (non automatica)")
                print()
                
            elif "CUSTOMER" in error_code_name:
                print("   🎯 CAUSA: Customer ID")
                print("   " + "-"*56)
                print()
                print("   Il Customer ID potrebbe essere errato o non accessibile.")
                print()
                print("   ✅ VERIFICA:")
                print(f"   1. Customer ID usato: {customer_id}")
                print("   2. Formato corretto? (senza trattini)")
                print("   3. Hai accesso a questo account?")
                print()
                print("   🔍 COME TROVARE IL CUSTOMER ID CORRETTO:")
                print("   1. Vai su: https://ads.google.com")
                print("   2. Click su icona tools (chiave inglese)")
                print("   3. Settings → Account settings")
                print("   4. Copia il numero (es: 123-456-7890)")
                print("   5. Usa SENZA trattini: 1234567890")
                print()
                
            elif "AUTHENTICATION" in error_code_name:
                print("   🎯 CAUSA: Autenticazione OAuth2")
                print("   " + "-"*56)
                print()
                print("   Il Refresh Token è scaduto o non valido.")
                print()
                print("   🔧 SOLUZIONE:")
                print("   1. Rigenera refresh token:")
                print("      python generate_refresh_token.py")
                print()
                print("   2. Segui le istruzioni del wizard")
                print("   3. Copia il nuovo refresh_token")
                print("   4. Incollalo in google-ads.yaml")
                print()
                
            else:
                print("   🎯 CAUSA: Altro errore")
                print("   " + "-"*56)
                print()
                print(f"   Error code: {error_code_name}")
                print(f"   Message: {error_message}")
                print()
        
        print("   " + "="*56)
        print()
        print("="*60)
        print("❌ TEST FALLITO")
        print("="*60)
        sys.exit(1)

except Exception as e:
    print(f"❌ Errore generico: {e}")
    print()
    
    # Analisi errore generico
    error_str = str(e)
    
    if "501" in error_str or "GRPC target method" in error_str:
        print("🎯 ANALISI ERRORE 501:")
        print("="*60)
        print()
        print("L'errore '501 GRPC target method can't be resolved'")
        print("può avere diverse cause:")
        print()
        print("1️⃣  DEVELOPER TOKEN NON APPROVATO (più probabile)")
        print("   → Controlla: https://ads.google.com/aw/apicenter")
        print("   → Status deve essere 'Approved'")
        print()
        print("2️⃣  use_proto_plus configurazione errata")
        print("   → In google-ads.yaml deve essere: use_proto_plus: True")
        print()
        print("3️⃣  Customer ID formato errato")
        print("   → Deve essere solo numeri: 7281691195")
        print("   → NON: 728-169-1195")
        print()
        print("4️⃣  Problema di rete/firewall")
        print("   → Prova da rete diversa")
        print("   → Verifica che googleads.googleapis.com sia raggiungibile")
        print()
        print("="*60)
        print()
        print("🔍 DEBUG AVANZATO:")
        print("="*60)
        print()
        print("Verifica le tue credenziali:")
        print()
        print("1. Developer Token:")
        with open("google-ads.yaml", "r") as f:
            import yaml
            config = yaml.safe_load(f)
            dev_token = config.get('developer_token', 'MISSING')
            print(f"   Valore: {dev_token[:15]}...")
            print(f"   Lunghezza: {len(dev_token)} caratteri")
            print()
        
        print("2. Test risoluzione DNS:")
        print("   ping googleads.googleapis.com")
        print()
        
        print("3. Controlla status token:")
        print("   https://ads.google.com/aw/apicenter")
        print()
    
    print("Possibili cause:")
    print("1. Developer Token non approvato")
    print("2. File google-ads.yaml malformato")
    print("3. Credenziali mancanti o errate")
    print()
    sys.exit(1)
