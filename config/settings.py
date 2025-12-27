"""
Configurazioni centralizzate del sistema
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configurazioni applicazione"""
    
    # ================================
    # DATABASE
    # ================================
    DATABASE_URL: str = "postgresql://localhost/google_ads_automation"
    
    # ================================
    # SUPABASE (per token dinamici)
    # ================================
    SUPABASE_URL: Optional[str] = None
    SUPABASE_SERVICE_KEY: Optional[str] = None
    
    # ================================
    # GOOGLE ADS API - OAuth2 Credentials
    # ================================
    GOOGLE_ADS_DEVELOPER_TOKEN: Optional[str] = None
    GOOGLE_ADS_CLIENT_ID: Optional[str] = None
    GOOGLE_ADS_CLIENT_SECRET: Optional[str] = None
    GOOGLE_ADS_CUSTOMER_ID: str = ""
    
    # ================================
    # AI PROVIDER
    # ================================
    AI_PROVIDER: str = "openai"  # 'gemini' o 'claude' o 'openai'
    
    # Gemini (Google AI Studio - GRATUITO)
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash"
    
    # Claude (Anthropic - A PAGAMENTO)
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"

    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    # ================================
    # API SERVER
    # ================================
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = False
    
    # ================================
    # LOGGING
    # ================================
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    LOG_MAX_BYTES: int = 10485760  # 10MB
    LOG_BACKUP_COUNT: int = 5
    
    # ================================
    # SCHEDULER
    # ================================
    MONITOR_INTERVAL_HOURS: int = 6
    ANALYZER_AUTO_RUN: bool = True
    
    # ================================
    # TARGET PERFORMANCE THRESHOLDS
    # ================================
    TARGET_CTR_MIN: float = 2.0
    TARGET_CPC_MAX: float = 0.60
    TARGET_ROAS_MIN: float = 1.5
    TARGET_OPTIMIZATION_SCORE_MIN: float = 60.0
    
    # ================================
    # TELEGRAM NOTIFICATIONS (OPTIONAL)
    # ================================
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"
    
    def validate_ai_provider(self) -> bool:
        """Valida che il provider AI sia configurato correttamente"""
        if self.AI_PROVIDER.lower() == 'gemini':
            if not self.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY non configurata in .env")
            return True
        
        elif self.AI_PROVIDER.lower() == 'claude':
            if not self.ANTHROPIC_API_KEY:
                raise ValueError("ANTHROPIC_API_KEY non configurata in .env")
            return True
        
        elif self.AI_PROVIDER.lower() == 'openai':
            if not self.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY non configurata in .env")
            return True
        
        else:
            raise ValueError(f"AI_PROVIDER '{self.AI_PROVIDER}' non valido. Usa 'gemini', 'claude' o 'openai'")
    
    def validate_google_ads(self) -> bool:
        """Valida configurazione Google Ads OAuth2"""
        missing = []
        
        if not self.GOOGLE_ADS_DEVELOPER_TOKEN:
            missing.append("GOOGLE_ADS_DEVELOPER_TOKEN")
        if not self.GOOGLE_ADS_CLIENT_ID:
            missing.append("GOOGLE_ADS_CLIENT_ID")
        if not self.GOOGLE_ADS_CLIENT_SECRET:
            missing.append("GOOGLE_ADS_CLIENT_SECRET")
        
        if missing:
            raise ValueError(f"Credenziali Google Ads OAuth2 mancanti: {', '.join(missing)}")
        
        return True
    
    def validate_supabase(self) -> bool:
        """Valida configurazione Supabase"""
        missing = []
        
        if not self.SUPABASE_URL:
            missing.append("SUPABASE_URL")
        if not self.SUPABASE_SERVICE_KEY:
            missing.append("SUPABASE_SERVICE_KEY")
        
        if missing:
            raise ValueError(f"Credenziali Supabase mancanti: {', '.join(missing)}")
        
        return True
    
    def get_ai_provider_info(self) -> dict:
        """Ritorna info sul provider AI configurato"""
        provider = self.AI_PROVIDER.lower()
        
        if provider == 'gemini':
            return {
                'name': 'Google Gemini',
                'model': self.GEMINI_MODEL,
                'cost': 'GRATUITO',
                'configured': bool(self.GEMINI_API_KEY)
            }
        elif provider == 'claude':
            return {
                'name': 'Anthropic Claude',
                'model': self.ANTHROPIC_MODEL,
                'cost': 'A PAGAMENTO',
                'configured': bool(self.ANTHROPIC_API_KEY)
            }
        elif provider == 'openai':
            return {
                'name': 'OpenAI',
                'model': self.OPENAI_MODEL,
                'cost': 'A PAGAMENTO',
                'configured': bool(self.OPENAI_API_KEY)
            }
        else:
            return {
                'name': 'Unknown',
                'model': 'N/A',
                'cost': 'N/A',
                'configured': False
            }
    
    def get_telegram_info(self) -> dict:
        """Ritorna info su configurazione Telegram"""
        return {
            'enabled': bool(self.TELEGRAM_BOT_TOKEN and self.TELEGRAM_CHAT_ID),
            'bot_configured': bool(self.TELEGRAM_BOT_TOKEN),
            'chat_configured': bool(self.TELEGRAM_CHAT_ID)
        }


# Istanza globale settings
settings = Settings()


# ================================
# TEST CONFIGURATION
# ================================

if __name__ == "__main__":
    print("="*60)
    print("CONFIGURAZIONE SISTEMA")
    print("="*60)
    print()
    
    # Database
    print("DATABASE")
    print(f"   URL: {settings.DATABASE_URL}")
    print()
    
    # Supabase
    print("SUPABASE (Token Storage)")
    try:
        settings.validate_supabase()
        print(f"   URL: {settings.SUPABASE_URL}")
        print(f"   Status: OK")
    except ValueError as e:
        print(f"   Status: {e}")
    print()
    
    # Google Ads OAuth2
    print("GOOGLE ADS OAUTH2")
    print(f"   Developer Token: {'***' + settings.GOOGLE_ADS_DEVELOPER_TOKEN[-10:] if settings.GOOGLE_ADS_DEVELOPER_TOKEN else 'NON CONFIGURATO'}")
    print(f"   Client ID: {'***' + settings.GOOGLE_ADS_CLIENT_ID[-20:] if settings.GOOGLE_ADS_CLIENT_ID else 'NON CONFIGURATO'}")
    print(f"   Client Secret: {'***' if settings.GOOGLE_ADS_CLIENT_SECRET else 'NON CONFIGURATO'}")
    
    try:
        settings.validate_google_ads()
        print(f"   OAuth2 Status: OK")
    except ValueError as e:
        print(f"   OAuth2 Status: {e}")
    print()
    
    # AI Provider
    print("AI PROVIDER")
    ai_info = settings.get_ai_provider_info()
    print(f"   Provider: {ai_info['name']}")
    print(f"   Model: {ai_info['model']}")
    print(f"   Cost: {ai_info['cost']}")
    print(f"   Configured: {'OK' if ai_info['configured'] else 'NO'}")
    
    try:
        settings.validate_ai_provider()
        print(f"   Status: OK")
    except ValueError as e:
        print(f"   Status: {e}")
    print()
    
    # Scheduler
    print("SCHEDULER")
    print(f"   Interval: {settings.MONITOR_INTERVAL_HOURS}h")
    print(f"   Auto Analyzer: {'SI' if settings.ANALYZER_AUTO_RUN else 'NO'}")
    print()
    
    # Targets
    print("TARGETS")
    print(f"   CTR min: {settings.TARGET_CTR_MIN}%")
    print(f"   CPC max: EUR{settings.TARGET_CPC_MAX}")
    print(f"   ROAS min: {settings.TARGET_ROAS_MIN}")
    print(f"   Opt. Score min: {settings.TARGET_OPTIMIZATION_SCORE_MIN}")
    print()
    
    # API
    print("API SERVER")
    print(f"   Host: {settings.API_HOST}")
    print(f"   Port: {settings.API_PORT}")
    print(f"   Auto-reload: {'SI' if settings.API_RELOAD else 'NO'}")
    print()
    
    # Telegram
    print("TELEGRAM NOTIFICATIONS")
    telegram_info = settings.get_telegram_info()
    if telegram_info['enabled']:
        print(f"   Status: Abilitato")
        print(f"   Bot Token: {settings.TELEGRAM_BOT_TOKEN[:20]}...")
        print(f"   Chat ID: {settings.TELEGRAM_CHAT_ID}")
    else:
        print(f"   Status: Disabilitato (opzionale)")
        if not telegram_info['bot_configured']:
            print(f"   Bot Token: Non configurato")
        if not telegram_info['chat_configured']:
            print(f"   Chat ID: Non configurato")
    print()
    
    print("="*60)
    
    # Check errors
    errors = []
    
    try:
        settings.validate_supabase()
    except ValueError as e:
        errors.append(f"Supabase: {e}")
    
    try:
        settings.validate_google_ads()
    except ValueError as e:
        errors.append(f"Google Ads: {e}")
    
    try:
        settings.validate_ai_provider()
    except ValueError as e:
        errors.append(f"AI Provider: {e}")
    
    if errors:
        print()
        print("ERRORI CRITICI:")
        for error in errors:
            print(f"   - {error}")
        print()
        print("Configura .env prima di avviare il sistema")
        print()
        exit(1)
    
    print()
    print("Configurazione completa! Sistema pronto.")
    print()