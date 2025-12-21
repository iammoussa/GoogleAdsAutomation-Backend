#!/usr/bin/env python3
"""
Test Google Ads API Credentials
Verifica se le credenziali sono corrette e se il Developer Token è approvato
"""

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import sys

print("="*60)
print("🔍 TEST CREDENZIALI GOOGLE ADS API")
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
        
        print(f"   Developer Token: {config.get('developer_token', 'MISSING')[:10]}...")
        print(f"   Client ID: {config.get('client_id', 'MISSING')[:30]}...")
        print(f"   Login Customer ID: {config.get('login_customer_id', 'MISSING')}")
        print(f"   use_proto_plus: {config.get('use_proto_plus', 'MISSING')}")
    print()
    
    # Test connessione con query semplice
    print("3️⃣  Test connessione con query base...")
    
    customer_id = config.get('login_customer_id')
    
    # Query molto semplice per testare connessione
    query = """
        SELECT 
            customer.id,
            customer.descriptive_name
        FROM customer
        LIMIT 1
    """
    
    ga_service = client.get_service("GoogleAdsService")
    
    try:
        response = ga_service.search(
            customer_id=customer_id,
            query=query
        )
        
        for row in response:
            print(f"   ✅ Connessione OK!")
            print(f"   Account ID: {row.customer.id}")
            print(f"   Account Name: {row.customer.descriptive_name}")
            print()
            break
        
        print("="*60)
        print("✅ TUTTO OK! Google Ads API funzionante")
        print("="*60)
        sys.exit(0)
        
    except GoogleAdsException as ex:
        print(f"   ❌ Errore Google Ads API:")
        print()
        
        for error in ex.failure.errors:
            print(f"   Error code: {error.error_code}")
            print(f"   Message: {error.message}")
            
            # Check per errori comuni
            if "DEVELOPER_TOKEN_NOT_APPROVED" in str(error.error_code):
                print()
                print("   ⚠️  PROBLEMA: Developer Token NON APPROVATO")
                print()
                print("   SOLUZIONE:")
                print("   1. Il token deve essere approvato da Google (24-48h)")
                print("   2. Solo il Manager Account owner può richiedere approvazione")
                print("   3. Vai su: https://ads.google.com/aw/apicenter")
                print()
                
            elif "CUSTOMER_NOT_FOUND" in str(error.error_code):
                print()
                print("   ⚠️  PROBLEMA: Customer ID non trovato")
                print()
                print("   SOLUZIONE:")
                print("   1. Verifica il Customer ID in google-ads.yaml")
                print("   2. Deve essere senza trattini: 7281691195")
                print("   3. Se usi Manager Account, usa l'ID del manager")
                print()
                
            elif "AUTHENTICATION_ERROR" in str(error.error_code):
                print()
                print("   ⚠️  PROBLEMA: Errore autenticazione OAuth2")
                print()
                print("   SOLUZIONE:")
                print("   1. Verifica Client ID, Secret, Refresh Token")
                print("   2. Il Refresh Token potrebbe essere scaduto")
                print("   3. Rigenera il Refresh Token")
                print()
        
        print()
        print("="*60)
        print("❌ TEST FALLITO")
        print("="*60)
        sys.exit(1)

except Exception as e:
    print(f"❌ Errore: {e}")
    print()
    print("Possibili cause:")
    print("1. File google-ads.yaml non trovato o malformato")
    print("2. Credenziali mancanti o errate")
    print("3. Libreria google-ads non installata")
    print()
    sys.exit(1)
