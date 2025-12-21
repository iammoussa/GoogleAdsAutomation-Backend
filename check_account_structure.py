#!/usr/bin/env python3
"""
Verifica se hai un Manager Account (MCC) con sub-accounts
"""

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

print("="*60)
print("🔍 VERIFICA STRUTTURA ACCOUNT GOOGLE ADS")
print("="*60)
print()

try:
    # Carica client
    print("📋 Caricamento credenziali...")
    client = GoogleAdsClient.load_from_storage("google-ads.yaml")
    
    # Leggi login_customer_id dal yaml
    with open("google-ads.yaml", "r") as f:
        import yaml
        config = yaml.safe_load(f)
        login_customer_id = config.get('login_customer_id')
    
    print(f"✅ Login Customer ID: {login_customer_id}")
    print()
    
    # Prova a ottenere info account principale
    print("1️⃣  Verifico account principale...")
    ga_service = client.get_service("GoogleAdsService")
    
    query_main = """
        SELECT 
            customer.id,
            customer.descriptive_name,
            customer.manager
        FROM customer
        LIMIT 1
    """
    
    try:
        response = ga_service.search(
            customer_id=login_customer_id,
            query=query_main
        )
        
        for row in response:
            is_manager = row.customer.manager
            print(f"   Account ID: {row.customer.id}")
            print(f"   Nome: {row.customer.descriptive_name}")
            print(f"   Manager Account (MCC): {'✅ SI' if is_manager else '❌ NO'}")
            print()
            
            if is_manager:
                # È un Manager Account, cerca sub-accounts
                print("2️⃣  Ricerca sub-accounts...")
                print()
                
                query_subs = """
                    SELECT
                        customer_client.id,
                        customer_client.descriptive_name,
                        customer_client.status,
                        customer_client.manager
                    FROM customer_client
                    WHERE customer_client.status = 'ENABLED'
                """
                
                try:
                    response_subs = ga_service.search(
                        customer_id=login_customer_id,
                        query=query_subs
                    )
                    
                    sub_accounts = []
                    for sub_row in response_subs:
                        sub_accounts.append({
                            'id': sub_row.customer_client.id,
                            'name': sub_row.customer_client.descriptive_name,
                            'is_manager': sub_row.customer_client.manager
                        })
                    
                    if sub_accounts:
                        print(f"   ✅ Trovati {len(sub_accounts)} sub-account(s):")
                        print()
                        for i, acc in enumerate(sub_accounts, 1):
                            manager_badge = "🏢 MCC" if acc['is_manager'] else "📊 Account"
                            print(f"   {i}. [{manager_badge}] {acc['name']}")
                            print(f"      ID: {acc['id']}")
                            print()
                        
                        print("="*60)
                        print("💡 IMPORTANTE PER MONITOR")
                        print("="*60)
                        print()
                        print("Hai un Manager Account con sub-accounts.")
                        print("Per estrarre dati, devi specificare quale account usare:")
                        print()
                        print("Opzione A: Usa uno specifico sub-account")
                        print("  1. Scegli un ID dalla lista sopra")
                        print("  2. Modifica .env:")
                        print(f"     GOOGLE_ADS_CUSTOMER_ID={sub_accounts[0]['id']}")
                        print()
                        print("Opzione B: Itera su tutti i sub-accounts")
                        print("  1. Il monitor può essere modificato per iterare")
                        print("  2. Estrae dati da tutti gli account automaticamente")
                        print()
                        
                    else:
                        print("   ⚠️  Nessun sub-account trovato")
                        print("   Questo MCC non gestisce altri account")
                        print()
                        
                except GoogleAdsException as ex:
                    print(f"   ❌ Errore ricerca sub-accounts: {ex}")
                    
            else:
                # Account singolo, non manager
                print("2️⃣  Account singolo (non Manager)")
                print()
                print("   ✅ Questo è un account standard Google Ads")
                print("   ✅ Puoi usarlo direttamente nel monitor")
                print()
                print("   Configurazione attuale:")
                print(f"   GOOGLE_ADS_CUSTOMER_ID={login_customer_id}")
                print()
            
            break
        
        print("="*60)
        print("✅ VERIFICA COMPLETATA")
        print("="*60)
        
    except GoogleAdsException as ex:
        print(f"❌ Errore Google Ads:")
        print()
        for error in ex.failure.errors:
            print(f"   Error code: {error.error_code}")
            print(f"   Message: {error.message}")
            print()
            
            if "DEVELOPER_TOKEN_NOT_APPROVED" in str(error.error_code):
                print("   ⚠️  Developer Token non ancora approvato")
                print("   Controlla: https://ads.google.com/aw/apicenter")
                
            elif "CUSTOMER_NOT_FOUND" in str(error.error_code):
                print("   ⚠️  Customer ID non trovato")
                print(f"   Verifica che {login_customer_id} sia corretto")
                
            elif "AUTHENTICATION_ERROR" in str(error.error_code):
                print("   ⚠️  Errore autenticazione")
                print("   Rigenera refresh token con: python generate_refresh_token.py")

except Exception as e:
    print(f"❌ Errore: {e}")
    print()
    print("Verifica:")
    print("1. File google-ads.yaml presente e corretto")
    print("2. Libreria google-ads installata: pip install google-ads")
    print("3. Credenziali valide")
