"""
AGENTE B2: ANALYZER (Multi-Provider)
Analizza metriche con AI (Gemini o Claude) e propone azioni di ottimizzazione
"""

import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

from database.database import get_db_session
from database.models import CampaignMetric, Alert, ProposedAction
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


# ============================================================================
# ABSTRACT BASE CLASS PER AI PROVIDERS
# ============================================================================

class AIProvider(ABC):
    """Classe base per provider AI"""
    
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 4000) -> str:
        """Genera risposta dall'AI"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Ritorna nome del provider"""
        pass


# ============================================================================
# GEMINI PROVIDER (Google AI Studio - GRATUITO!)
# ============================================================================

class GeminiProvider(AIProvider):
    """Provider per Google Gemini (gratuito)"""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        """
        Inizializza Gemini
        
        Args:
            api_key: API key da Google AI Studio
            model: Modello da usare (gemini-1.5-flash Ã¨ gratuito e veloce)
        """
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model)
            self.model_name = model
            logger.info(f"✅ Gemini API inizializzato (model: {model})")
        except ImportError:
            logger.error("❌ google-generativeai non installato. Installa con: pip install google-generativeai")
            raise
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione Gemini: {e}")
            raise
    
    def generate(self, prompt: str, max_tokens: int = 4000) -> str:
        """
        Genera risposta con Gemini
        
        Args:
            prompt: Prompt per l'AI
            max_tokens: Numero massimo di token
        
        Returns:
            Risposta dell'AI
        """
        try:
            # Gemini configuration
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": max_tokens,
            }
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"❌ Errore chiamata Gemini API: {e}")
            raise
    
    def get_provider_name(self) -> str:
        return f"Gemini ({self.model_name})"


# ============================================================================
# CLAUDE PROVIDER (Anthropic)
# ============================================================================

class ClaudeProvider(AIProvider):
    """Provider per Anthropic Claude"""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        """
        Inizializza Claude
        
        Args:
            api_key: API key Anthropic
            model: Modello da usare
        """
        try:
            import anthropic
            
            self.client = anthropic.Anthropic(api_key=api_key)
            self.model_name = model
            logger.info(f"✅ Claude API inizializzato (model: {model})")
        except ImportError:
            logger.error("❌ anthropic non installato. Installa con: pip install anthropic")
            raise
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione Claude: {e}")
            raise
    
    def generate(self, prompt: str, max_tokens: int = 4000) -> str:
        """
        Genera risposta con Claude
        
        Args:
            prompt: Prompt per l'AI
            max_tokens: Numero massimo di token
        
        Returns:
            Risposta dell'AI
        """
        try:
            message = self.client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return message.content[0].text
            
        except Exception as e:
            logger.error(f"❌ Errore chiamata Claude API: {e}")
            raise
    
    def get_provider_name(self) -> str:
        return f"Claude ({self.model_name})"
    
# ============================================================================
# OPENAI PROVIDER
# ============================================================================

class OpenAIProvider(AIProvider):
    """Provider per OpenAI"""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
            self.model_name = model
            logger.info(f"✅ OpenAI API inizializzato (model: {model})")
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione OpenAI: {e}")
            raise
    
    def generate(self, prompt: str, max_tokens: int = 4000) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert Google Ads optimizer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=max_tokens,
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"❌ Errore chiamata OpenAI API: {e}")
            raise
    
    def get_provider_name(self) -> str:
        return f"OpenAI ({self.model_name})"


# ============================================================================
# CAMPAIGN ANALYZER (Multi-Provider)
# ============================================================================

class CampaignAnalyzer:
    """Analyzer per campagne Google Ads con AI multi-provider"""
    
    def __init__(self, provider: Optional[str] = None):
        """
        Inizializza l'analyzer
        
        Args:
            provider: 'gemini' o 'claude' (se None, usa settings.AI_PROVIDER)
        """
        provider = provider or getattr(settings, 'AI_PROVIDER', 'gemini')
        
        # Inizializza provider appropriato
        if provider.lower() == 'gemini':
            api_key = getattr(settings, 'GEMINI_API_KEY', None)
            model = getattr(settings, 'GEMINI_MODEL', 'gemini-1.5-flash')
            
            if not api_key:
                raise ValueError("GEMINI_API_KEY non trovata in settings")
            
            self.ai_provider = GeminiProvider(api_key, model)
            
        elif provider.lower() == 'claude':
            api_key = getattr(settings, 'ANTHROPIC_API_KEY', None)
            model = getattr(settings, 'ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')
            
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY non trovata in settings")
            
            self.ai_provider = ClaudeProvider(api_key, model)

        elif provider.lower() == 'openai':
            api_key = getattr(settings, 'OPENAI_API_KEY', None)
            model = getattr(settings, 'OPENAI_MODEL', 'gpt-4-turbo-preview')
            
            if not api_key:
                raise ValueError("OPENAI_API_KEY non trovata in settings")
            
            self.ai_provider = OpenAIProvider(api_key, model)
        
        else:
            raise ValueError(f"Provider '{provider}' non supportato. Usa 'gemini' o 'claude' o 'openai'")
        
        logger.info(f"🤖 Analyzer inizializzato con provider: {self.ai_provider.get_provider_name()}")
    
    def get_campaign_history(
        self,
        campaign_id: int,
        days: int = 14  # Aumentato da 7 a 14 giorni
    ) -> List[Dict[str, Any]]:
        """
        Ottiene lo storico di una campagna con statistiche aggregate
        
        Args:
            campaign_id: ID campagna
            days: Numero di giorni di storico (default: 14)
        
        Returns:
            Lista di metriche storiche ordinate per data
        """
        with get_db_session() as db:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            metrics = db.query(CampaignMetric).filter(
                CampaignMetric.campaign_id == campaign_id,
                CampaignMetric.timestamp >= cutoff_date
            ).order_by(CampaignMetric.timestamp.desc()).all()
            
            return [m.to_dict() for m in metrics]
    
    def calculate_performance_stats(
        self,
        history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calcola statistiche aggregate sullo storico
        
        Args:
            history: Lista metriche storiche
            
        Returns:
            Dizionario con statistiche aggregate
        """
        if not history:
            return {}
        
        import numpy as np
        from datetime import datetime
        
        # Converti in array per calcoli
        costs = [h['cost'] for h in history if h['cost'] > 0]
        ctrs = [h['ctr'] for h in history if h['ctr'] > 0]
        cpcs = [h['cpc'] for h in history if h['cpc'] > 0]
        roass = [h['roas'] for h in history if h['roas'] > 0]
        conversions = [h['conversions'] for h in history]
        
        # Statistiche aggregate
        stats = {
            'total_days': len(history),
            'avg_daily_cost': np.mean(costs) if costs else 0,
            'avg_ctr': np.mean(ctrs) if ctrs else 0,
            'avg_cpc': np.mean(cpcs) if cpcs else 0,
            'avg_roas': np.mean(roass) if roass else 0,
            'total_conversions': sum(conversions),
            'days_with_conversions': sum(1 for c in conversions if c > 0),
            'best_roas': max(roass) if roass else 0,
            'worst_roas': min(roass) if roass else 0,
        }
        
        # Analisi per giorno della settimana
        weekend_metrics = []
        weekday_metrics = []
        
        for h in history:
            # Estrai giorno settimana dal timestamp
            ts = h.get('timestamp')
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            
            weekday = ts.weekday()  # 0=Monday, 6=Sunday
            
            if weekday >= 5:  # Sabato o Domenica
                weekend_metrics.append(h)
            else:
                weekday_metrics.append(h)
        
        # Medie weekend vs weekday
        if weekend_metrics:
            stats['weekend_avg_roas'] = np.mean([m['roas'] for m in weekend_metrics if m['roas'] > 0]) if any(m['roas'] > 0 for m in weekend_metrics) else 0
            stats['weekend_avg_conversions'] = np.mean([m['conversions'] for m in weekend_metrics])
        
        if weekday_metrics:
            stats['weekday_avg_roas'] = np.mean([m['roas'] for m in weekday_metrics if m['roas'] > 0]) if any(m['roas'] > 0 for m in weekday_metrics) else 0
            stats['weekday_avg_conversions'] = np.mean([m['conversions'] for m in weekday_metrics])
        
        return stats
    
    def get_recent_alerts(
        self,
        campaign_id: int,
        days: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Ottiene alert recenti per una campagna
        
        Args:
            campaign_id: ID campagna
            days: Numero di giorni
        
        Returns:
            Lista di alert
        """
        with get_db_session() as db:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            alerts = db.query(Alert).filter(
                Alert.campaign_id == campaign_id,
                Alert.created_at >= cutoff_date,
                Alert.resolved == False
            ).order_by(Alert.created_at.desc()).all()
            
            return [a.to_dict() for a in alerts]
    
    def build_analysis_prompt(
        self,
        campaign: Dict[str, Any],
        history: List[Dict[str, Any]],
        alerts: List[Dict[str, Any]]
    ) -> str:
        """
        Costruisce il prompt per l'AI con analisi storica avanzata
        
        Args:
            campaign: Metriche attuali campagna
            history: Storico metriche (14 giorni)
            alerts: Alert attivi
        
        Returns:
            Prompt formattato con contesto storico completo
        """
        from datetime import datetime
        
        # Giorno corrente
        today = datetime.now()
        day_name = ['LunedÃ¬', 'MartedÃ¬', 'MercoledÃ¬', 'GiovedÃ¬', 'VenerdÃ¬', 'Sabato', 'Domenica'][today.weekday()]
        is_weekend = today.weekday() >= 5
        
        # Calcola statistiche aggregate
        stats = self.calculate_performance_stats(history) if history else {}
        
        # Analisi trend dettagliata
        trend_analysis = ""
        if len(history) >= 2:
            latest = history[0]
            yesterday = history[1] if len(history) > 1 else latest
            week_ago = history[6] if len(history) > 6 else history[-1]
            
            # Trend giornaliero (oggi vs ieri)
            daily_ctr_change = ((latest['ctr'] - yesterday['ctr']) / yesterday['ctr'] * 100) if yesterday.get('ctr', 0) > 0 else 0
            daily_roas_change = ((latest['roas'] - yesterday['roas']) / yesterday['roas'] * 100) if yesterday.get('roas', 0) > 0 else 0
            daily_conv_change = latest.get('conversions', 0) - yesterday.get('conversions', 0)
            
            # Trend settimanale
            weekly_ctr_change = ((latest['ctr'] - week_ago['ctr']) / week_ago['ctr'] * 100) if week_ago.get('ctr', 0) > 0 else 0
            weekly_cpc_change = ((latest['cpc'] - week_ago['cpc']) / week_ago['cpc'] * 100) if week_ago.get('cpc', 0) > 0 else 0
            weekly_roas_change = ((latest['roas'] - week_ago['roas']) / week_ago['roas'] * 100) if week_ago.get('roas', 0) > 0 else 0
            
            trend_analysis = f"""
CONTESTO TEMPORALE:
- Oggi: {day_name} {'(Weekend - performance tipicamente diversa)' if is_weekend else '(Giorno feriale)'}
- Ora analisi: {today.strftime('%H:%M')} (dati parziali se prima serata)

TREND GIORNALIERO (Oggi vs Ieri):
- CTR: {daily_ctr_change:+.1f}% (da {yesterday['ctr']:.2f}% a {latest['ctr']:.2f}%)
- ROAS: {daily_roas_change:+.1f}% (da {yesterday['roas']:.2f} a {latest['roas']:.2f})
- Conversioni: {daily_conv_change:+.0f} (da {yesterday.get('conversions', 0):.0f} a {latest.get('conversions', 0):.0f})

TREND SETTIMANALE (Ultimi 7 giorni):
- CTR: {weekly_ctr_change:+.1f}% (da {week_ago['ctr']:.2f}% a {latest['ctr']:.2f}%)
- CPC: {weekly_cpc_change:+.1f}% (da â‚¬{week_ago['cpc']:.2f} a â‚¬{latest['cpc']:.2f})
- ROAS: {weekly_roas_change:+.1f}% (da {week_ago['roas']:.2f} a {latest['roas']:.2f})

PERFORMANCE STORICA (Ultimi 14 giorni):
- Media CTR: {stats.get('avg_ctr', 0):.2f}%
- Media CPC: â‚¬{stats.get('avg_cpc', 0):.2f}
- Media ROAS: {stats.get('avg_roas', 0):.2f}
- Conversioni totali: {stats.get('total_conversions', 0):.0f}
- Giorni con conversioni: {stats.get('days_with_conversions', 0)}/{stats.get('total_days', 0)}
- ROAS migliore: {stats.get('best_roas', 0):.2f}
- ROAS peggiore: {stats.get('worst_roas', 0):.2f}
"""
            # Aggiungi confronto weekend vs weekday se disponibile
            if 'weekend_avg_roas' in stats and 'weekday_avg_roas' in stats:
                trend_analysis += f"""
PATTERN WEEKEND vs GIORNI FERIALI:
- ROAS Weekend: {stats.get('weekend_avg_roas', 0):.2f} (media)
- ROAS Feriali: {stats.get('weekday_avg_roas', 0):.2f} (media)
- Conversioni Weekend: {stats.get('weekend_avg_conversions', 0):.1f} (media/giorno)
- Conversioni Feriali: {stats.get('weekday_avg_conversions', 0):.1f} (media/giorno)
"""
        
        # Formatta alert
        alerts_text = ""
        if alerts:
            alerts_text = "ALERT ATTIVI:\n"
            for alert in alerts:
                alerts_text += f"- [{alert['severity']}] {alert['message']}\n"
        
        # Prompt completo migliorato
        prompt = f"""Sei un esperto di ottimizzazione Google Ads con 10+ anni di esperienza in affiliate marketing e performance marketing.

Analizza questa campagna considerando il CONTESTO STORICO COMPLETO e proponi azioni concrete.

IMPORTANTE: 
- NON basarti solo sui dati di oggi
- Considera i TREND degli ultimi 14 giorni
- Tieni conto del giorno della settimana (performance weekend vs feriali)
- Valuta se una performance bassa oggi Ã¨ un'anomalia o un trend negativo

CAMPAGNA: {campaign.get('campaign_name', 'N/A')}
ID: {campaign.get('campaign_id', 'N/A')}
Status: {campaign.get('status', 'N/A')}

METRICHE OGGI:
========================================
Budget: â‚¬{campaign.get('budget', 0):.2f}
Spesa: â‚¬{campaign.get('cost', 0):.2f}
CTR: {campaign.get('ctr', 0):.2f}%
CPC: â‚¬{campaign.get('cpc', 0):.2f}
ROAS: {campaign.get('roas', 0):.2f}
Conversioni: {campaign.get('conversions', 0):.1f}
Clicks: {campaign.get('clicks', 0):,}
Impressions: {campaign.get('impressions', 0):,}

{trend_analysis}

{alerts_text}

TARGET OBIETTIVI:
- CTR minimo: {settings.TARGET_CTR_MIN}%
- CPC massimo: â‚¬{settings.TARGET_CPC_MAX}
- ROAS minimo: {settings.TARGET_ROAS_MIN}

ISTRUZIONI:
1. Analizza la performance considerando il CONTESTO STORICO
2. Se oggi performa male ma lo storico Ã¨ buono, NON proporre azioni drastiche
3. Se il trend Ã¨ negativo per piÃ¹ giorni, proponi azioni correttive
4. Considera pattern weekend vs feriali nelle tue raccomandazioni
5. Proponi 3-7 azioni concrete e specifiche

ESEMPI:
- Se ROAS oggi = 0 ma media 14gg = 2.5 â†’ NON pausare, Ã¨ anomalia temporanea
- Se ROAS in calo costante da 7 giorni â†’ Azione correttiva urgente
- Se Ã¨ LunedÃ¬ e performance bassa ma weekend era ottimo â†’ Considera stagionalitÃ 

Per ogni azione, fornisci OBBLIGATORIAMENTE questo formato JSON:
{{
  "actions": [
    {{
      "action_type": "INCREASE_BUDGET",
      "priority": "HIGH",
      "target": {{"new_budget_micros": 50000000}},
      "reason": "Performance costantemente sopra target negli ultimi 14 giorni",
      "expected_impact": "Aumento conversioni del 30% mantenendo ROAS sopra 2.0",
      "confidence": 85,
      "current_value": "€30.00",
      "proposed_value": "€50.00"
    }},
    {{
      "action_type": "INCREASE_BID",
      "priority": "MEDIUM",
      "target": {{"keyword_id": "456", "new_bid_micros": 2500000, "current_bid_micros": 1500000}},
      "reason": "Keyword ad alte performance con CTR del 5% e ROAS 3.5",
      "expected_impact": "Aumento impressioni del 40% per keyword top performer",
      "confidence": 75,
      "current_value": "€1.50",
      "proposed_value": "€2.50"
    }},
    {{
      "action_type": "DECREASE_BUDGET",
      "priority": "LOW",
      "target": {{"new_budget_micros": 15000000}},
      "reason": "ROAS sotto target da 7 giorni consecutivi",
      "expected_impact": "Riduzione spesa del 25% su campagna non performante",
      "confidence": 80,
      "current_value": "€20.00",
      "proposed_value": "€15.00"
    }}
  ],
  "summary": "Sintesi che considera contesto storico e trend, non solo snapshot di oggi"
}}

TIPI DI AZIONI DISPONIBILI E FORMATO TARGET:

1. INCREASE_BUDGET / DECREASE_BUDGET:
   target: {{"new_budget_micros": <importo in micros>}}
   current_value: "€XX.XX"
   proposed_value: "€YY.YY"

2. INCREASE_BID / DECREASE_BID / REDUCE_BID:
   target: {{"keyword_id": "123", "new_bid_micros": <bid in micros>, "current_bid_micros": <bid attuale in micros>}}
   current_value: "€XX.XX"
   proposed_value: "€YY.YY"

3. PAUSE_KEYWORD / PAUSE_AD:
   target: {{"keyword_id": "123"}} o {{"ad_id": "456"}}

4. ADD_NEGATIVE_KEYWORD:
   target: {{"keyword_text": "parola negativa"}}

IMPORTANTE: 
- 1 Euro = 1,000,000 micros
- Includi SEMPRE current_value e proposed_value per budget e bid changes
- Includi SEMPRE new_budget_micros (non new_budget)
- Includi SEMPRE new_bid_micros e current_bid_micros per bid changes

PRIORITÃ€: HIGH, MEDIUM, LOW
CONFIDENCE: 0-100 (percentuale di fiducia nell'azione)

RISPONDI SOLO CON IL JSON, NIENT'ALTRO."""

        return prompt
    
    def analyze_campaign(
        self,
        campaign_id: int,
        days_history: int = 7
    ) -> Dict[str, Any]:
        """
        Analizza una campagna e propone azioni
        
        Args:
            campaign_id: ID campagna da analizzare
            days_history: Giorni di storico da considerare
        
        Returns:
            Risultato analisi con azioni proposte
        """
        logger.info(f"🔍 Inizio analisi campagna {campaign_id}")
        
        # Ottieni dati campagna
        with get_db_session() as db:
            latest_metric = db.query(CampaignMetric).filter(
                CampaignMetric.campaign_id == campaign_id
            ).order_by(CampaignMetric.timestamp.desc()).first()
            
            if not latest_metric:
                logger.warning(f"âš Â Ã¯Â¸Â  Nessuna metrica trovata per campagna {campaign_id}")
                return {
                    'campaign_id': campaign_id,
                    'actions': [],
                    'error': 'No metrics found'
                }
            
            campaign = latest_metric.to_dict()
        
        # Ottieni storico e alert
        history = self.get_campaign_history(campaign_id, days_history)
        alerts = self.get_recent_alerts(campaign_id)
        
        # Costruisci prompt
        prompt = self.build_analysis_prompt(campaign, history, alerts)        # Chiama AI con sistema di retry
        logger.info(f"🤖 Chiamata {self.ai_provider.get_provider_name()}...")
        
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                response_text = self.ai_provider.generate(prompt, max_tokens=4000)
                
                # Debug logging: mostra risposta completa
                logger.debug(f"ðŸ“ Risposta AI (tentativo {attempt+1}):\n{response_text}")
                
                # Parse risposta JSON
                actions_data = self.parse_ai_response(response_text)
                
                # Salva azioni in database
                saved_actions = self.save_proposed_actions(
                    campaign_id,
                    campaign['campaign_name'],  # ✅ Add campaign_name
                    actions_data['actions'],
                    actions_data.get('summary', '')
                )
                
                logger.info(f"✅ Analisi completata: {len(saved_actions)} azioni proposte")
                
                return {
                    'campaign_id': campaign_id,
                    'campaign_name': campaign['campaign_name'],
                    'actions': saved_actions,
                    'summary': actions_data.get('summary', ''),
                    'provider': self.ai_provider.get_provider_name()
                }
                
            except ValueError as e:
                # Errore di parsing JSON - riprova
                last_error = e
                if attempt < max_retries - 1:
                    logger.warning(f"❌ Tentativo {attempt+1}/{max_retries} fallito (JSON parsing): {e}")
                    logger.warning(f"🔍„ Riprovo...")
                    continue
                else:
                    logger.error(f"❌ Tutti i {max_retries} tentativi falliti")
                    break
                    
            except Exception as e:
                # Altro errore - non riprovare
                last_error = e
                logger.error(f"❌ Errore non recuperabile: {e}")
                break
        
        # Se arriviamo qui, tutti i tentativi sono falliti
        campaign_name = campaign.get('campaign_name', f'Campaign {campaign_id}') if 'campaign' in locals() else f'Campaign {campaign_id}'
        return {
            'campaign_id': campaign_id,
            'campaign_name': campaign_name,
            'actions': [],
            'error': str(last_error) if last_error else 'Unknown error'
        }
    
    def parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse risposta AI (gestisce sia JSON puro che con markdown)
        
        Args:
            response_text: Testo risposta AI
        
        Returns:
            Dizionario parsed
        """
        # Log risposta originale (primi 200 caratteri)
        logger.debug(f"🔍 Parsing risposta (preview): {response_text[:200]}...")
        
        # Rimuovi markdown code blocks se presenti
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*', '', response_text)
        response_text = response_text.strip()
        
        # Trova solo il JSON se ci sono altri testi
        # Cerca tra { } piÃ¹ esterni
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(0)
            logger.debug(f"âœ‚ï¸ Estratto JSON puro (length: {len(response_text)} chars)")
        
        try:
            data = json.loads(response_text)
            
            # Valida struttura
            if 'actions' not in data:
                raise ValueError("Risposta AI non contiene 'actions'")
            
            logger.debug(f"✅ JSON parsed con successo: {len(data.get('actions', []))} azioni")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Errore parsing JSON: {e}")
            logger.error(f"ðŸ“„ Risposta completa ({len(response_text)} chars):\n{response_text}")
            
            # Mostra area dell'errore
            if hasattr(e, 'pos'):
                start = max(0, e.pos - 50)
                end = min(len(response_text), e.pos + 50)
                error_context = response_text[start:end]
                logger.error(f"🔍 Contesto errore (pos {e.pos}):\n...{error_context}...")
            
            raise ValueError(f"Risposta AI non Ã¨ JSON valido: {e}")
    
    def save_proposed_actions(
        self,
        campaign_id: int,
        campaign_name: str,  # ✅ Add this parameter
        actions: List[Dict[str, Any]],
        ai_summary: str
    ) -> List[Dict[str, Any]]:
        """
        Salva azioni proposte nel database
        
        Args:
            campaign_id: ID campagna
            campaign_name: Nome campagna
            actions: Lista azioni da salvare
            ai_summary: Summary dell'AI
        
        Returns:
            Lista azioni salvate
        """
        saved_actions = []
        
        with get_db_session() as db:
            for action_data in actions:
                # Converti confidence da 0-100 a 0-1 se necessario
                confidence = action_data.get('confidence', 50)
                if confidence > 1:  # Se Ã¨ in formato 0-100
                    confidence = confidence / 100.0
                
                action = ProposedAction(
                    campaign_id=campaign_id,
                    campaign_name=campaign_name,
                    action_type=action_data['action_type'],
                    priority=action_data.get('priority', 'MEDIUM'),
                    target=action_data.get('target', {}),
                    reason=action_data.get('reason', ''),
                    expected_impact=action_data.get('expected_impact', ''),
                    confidence=confidence,
                    current_value=action_data.get('current_value'),  # ✅ Add this
                    proposed_value=action_data.get('proposed_value'),  # ✅ Add this
                    ai_summary=ai_summary,
                    status='PENDING'
                )
                
                db.add(action)
                db.flush()  # Per ottenere l'ID
                
                saved_actions.append({
                    'id': action.id,
                    'action_type': action.action_type,
                    'priority': action.priority,
                    'reason': action.reason,
                    'expected_impact': action.expected_impact,
                    'confidence': action.confidence
                })
            
            db.commit()
        
        return saved_actions
    
    def analyze_all_campaigns(self) -> List[Dict[str, Any]]:
        """
        Analizza tutte le campagne con alert attivi
        
        Returns:
            Lista risultati analisi
        """
        logger.info("🔍 Analisi tutte le campagne con alert...")
        
        # Ottieni campagne con alert non risolti
        with get_db_session() as db:
            campaigns_with_alerts = db.query(Alert.campaign_id).filter(
                Alert.resolved == False
            ).distinct().all()
            
            campaign_ids = [c[0] for c in campaigns_with_alerts]
        
        if not campaign_ids:
            logger.info("✅ Nessuna campagna con alert attivi")
            return []
        
        logger.info(f"📊 Trovate {len(campaign_ids)} campagne da analizzare")
        
        results = []
        for campaign_id in campaign_ids:
            result = self.analyze_campaign(campaign_id)
            results.append(result)
        
        return results


# ============================================================================
# CLI - Esecuzione da terminale
# ============================================================================

if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyzer Agent - Analizza campagne con AI')
    parser.add_argument('campaign_id', type=int, nargs='?', help='ID campagna da analizzare (opzionale)')
    parser.add_argument('--all', action='store_true', help='Analizza tutte le campagne con alert')
    parser.add_argument('--provider', choices=['gemini', 'claude'], help='Provider AI da usare')
    parser.add_argument('--days', type=int, default=7, help='Giorni di storico (default: 7)')
    
    args = parser.parse_args()
    
    try:
        # Inizializza analyzer
        analyzer = CampaignAnalyzer(provider=args.provider)
        
        if args.all:
            # Analizza tutte
            results = analyzer.analyze_all_campaigns()
            
            print("\n" + "="*60)
            print(f"📊 ANALISI COMPLETATA - {len(results)} campagne")
            print("="*60)
            
            for result in results:
                campaign_name = result.get('campaign_name', f"Campaign {result['campaign_id']}")
                print(f"\nðŸŽ¯ {campaign_name} (ID: {result['campaign_id']})")
                print(f"   Provider: {result.get('provider', 'N/A')}")
                print(f"   Azioni proposte: {len(result['actions'])}")
                
                if result.get('summary'):
                    print(f"   Summary: {result['summary']}")
                
                for action in result['actions']:
                    print(f"   âž¤ [{action['priority']}] {action['action_type']}")
                    print(f"     {action['reason']}")

                # Mostra errore se presente
                if result.get('error'):
                    print(f"   ❌  Errore: {result['error']}")
        
        elif args.campaign_id:
            # Analizza singola campagna
            result = analyzer.analyze_campaign(args.campaign_id, args.days)
            
            print("\n" + "="*60)
            print(f"📊 ANALISI CAMPAGNA {result['campaign_id']}")
            print("="*60)
            print(f"Provider: {result.get('provider', 'N/A')}")
            print(f"\nAzioni proposte: {len(result['actions'])}")
            
            if result.get('summary'):
                print(f"\nSummary:\n{result['summary']}")
            
            print("\nAzioni:")
            for i, action in enumerate(result['actions'], 1):
                print(f"\n{i}. [{action['priority']}] {action['action_type']}")
                print(f"   Motivo: {action['reason']}")
                print(f"   Impatto atteso: {action['expected_impact']}")
                print(f"   Confidence: {action['confidence']}%")
        
        else:
            parser.print_help()
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"❌ Errore: {e}")
        sys.exit(1)