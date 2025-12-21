import os
from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient

load_dotenv()

print("🔍 Testing Google Ads Token...")
print(f"Developer Token: {os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN')[:10]}...")
print(f"Client ID: {os.getenv('GOOGLE_ADS_CLIENT_ID')}")
print(f"Customer ID: {os.getenv('GOOGLE_ADS_CUSTOMER_ID')}")
print(f"Refresh Token Length: {len(os.getenv('GOOGLE_ADS_REFRESH_TOKEN', ''))}")

try:
    client = GoogleAdsClient.load_from_dict({
        "developer_token": os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN'),
        "client_id": os.getenv('GOOGLE_ADS_CLIENT_ID'),
        "client_secret": os.getenv('GOOGLE_ADS_CLIENT_SECRET'),
        "refresh_token": os.getenv('GOOGLE_ADS_REFRESH_TOKEN'),
        "login_customer_id": os.getenv('GOOGLE_ADS_CUSTOMER_ID'),
    })
    
    # Try a simple API call
    ga_service = client.get_service("GoogleAdsService")
    query = "SELECT customer.id FROM customer LIMIT 1"
    
    response = ga_service.search(
        customer_id=os.getenv('GOOGLE_ADS_CUSTOMER_ID'),
        query=query
    )
    
    print("✅ SUCCESS! Token is valid!")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    print(f"Error type: {type(e).__name__}")