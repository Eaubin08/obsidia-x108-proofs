"""
Moltbook Integration Layer
===========================

Intégration avec Moltbook pour publier les transactions X-108 sur le feed public.
Permet la transparence et la visibilité des décisions du Safety Gate.

"An agent should not pay because it can — it should pay only when the action survives time."

Fonctionnalités :
- Publication des résultats de transactions sur Moltbook
- Création d'un feed public transparent
- Statistiques d'utilisation du Safety Gate
"""

import requests
from typing import Dict, Optional
from datetime import datetime
import os
import json

class MoltbookIntegration:
    """
    Gère l'intégration avec Moltbook pour la publication de transactions.
    """
    
    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        """
        Initialize the Moltbook integration.
        
        Args:
            api_key: Moltbook API key
            api_url: Moltbook API endpoint
        """
        self.api_key = api_key or os.getenv('MOLTBOOK_API_KEY', '')
        self.api_url = api_url or os.getenv('MOLTBOOK_API_URL', 'https://api.moltbook.com')
        
        # Mode démo si pas de clé API
        self.demo_mode = not self.api_key
        
        # Stats en mémoire pour le mode démo
        self.demo_posts = []
        self.demo_stats = {
            'total_posts': 0,
            'allowed_posts': 0,
            'blocked_posts': 0
        }
    
    def post_transaction_result(self, transaction: Dict) -> Dict:
        """
        Poste le résultat d'une transaction sur Moltbook.
        
        Args:
            transaction: Dict contenant les détails de la transaction
                - status: 'ALLOW' ou 'BLOCK'
                - amount: Montant en USDC
                - recipient: Destinataire
                - coherence: Score de cohérence (0.0 à 1.0)
                - temporal_passed: Bool, si la contrainte temporelle est passée
                - timestamp: Timestamp de la transaction
                
        Returns:
            Dict avec url du post et status
        """
        # Préparer le payload
        payload = {
            'type': 'agent_payment_validation',
            'status': transaction.get('status', 'UNKNOWN'),
            'amount': transaction.get('amount', 0),
            'recipient': transaction.get('recipient', 'unknown'),
            'coherence_score': transaction.get('coherence', 0.0),
            'temporal_check': transaction.get('temporal_passed', False),
            'timestamp': transaction.get('timestamp', datetime.now().isoformat()),
            'safety_gate': 'X-108',
            'tags': ['#AgenticCommerce', '#X108Safety', '#SafetyGate'],
            'message': self._generate_message(transaction)
        }
        
        if self.demo_mode:
            # Mode démo : simuler la publication
            post_id = len(self.demo_posts) + 1
            demo_url = f"https://moltbook.com/posts/{post_id}"
            
            self.demo_posts.append({
                'id': post_id,
                'url': demo_url,
                'payload': payload,
                'created_at': datetime.now().isoformat()
            })
            
            self.demo_stats['total_posts'] += 1
            if payload['status'] == 'ALLOW':
                self.demo_stats['allowed_posts'] += 1
            else:
                self.demo_stats['blocked_posts'] += 1
            
            return {
                'success': True,
                'url': demo_url,
                'post_id': post_id,
                'mode': 'demo',
                'message': 'Transaction posted to Moltbook (demo mode)'
            }
        
        # Mode production : appeler l'API Moltbook
        try:
            response = requests.post(
                f"{self.api_url}/posts",
                json=payload,
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                timeout=10
            )
            
            if response.status_code == 201:
                data = response.json()
                return {
                    'success': True,
                    'url': data.get('url', ''),
                    'post_id': data.get('id', ''),
                    'mode': 'production',
                    'message': 'Transaction posted to Moltbook successfully'
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'mode': 'production'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'mode': 'production'
            }
    
    def _generate_message(self, transaction: Dict) -> str:
        """
        Génère un message lisible pour Moltbook.
        
        Args:
            transaction: Dict avec les détails de la transaction
            
        Returns:
            String formaté pour Moltbook
        """
        status = transaction.get('status', 'UNKNOWN')
        amount = transaction.get('amount', 0)
        coherence = transaction.get('coherence', 0.0)
        temporal_passed = transaction.get('temporal_passed', False)
        
        if status == 'ALLOW':
            emoji = "✅"
            action = "ALLOWED"
        else:
            emoji = "❌"
            action = "BLOCKED"
        
        message = f"{emoji} X-108 Safety Gate: Payment {action}\n\n"
        message += f"Amount: {amount} USDC\n"
        message += f"Coherence Score: {coherence:.2f}\n"
        message += f"Temporal Check: {'✓ Passed' if temporal_passed else '✗ Failed'}\n\n"
        
        if status == 'ALLOW':
            message += "\"An agent should not pay because it can — it should pay only when the action survives time.\"\n\n"
            message += "This payment survived the mandatory HOLD and passed all safety checks."
        else:
            message += "This payment was blocked by the Safety Gate to prevent premature or incoherent transactions."
        
        return message
    
    def get_feed_url(self) -> str:
        """
        Retourne l'URL du feed public X-108 sur Moltbook.
        
        Returns:
            URL du feed
        """
        if self.demo_mode:
            return "https://moltbook.com/feed/x108-safety-gate (demo)"
        return f"{self.api_url}/feed/x108-safety-gate"
    
    def get_stats(self) -> Dict:
        """
        Récupère les statistiques de publication sur Moltbook.
        
        Returns:
            Dict avec total_posts, allowed_posts, blocked_posts
        """
        if self.demo_mode:
            return self.demo_stats
        
        try:
            response = requests.get(
                f"{self.api_url}/stats/x108-safety-gate",
                headers={'Authorization': f'Bearer {self.api_key}'},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return self.demo_stats
                
        except Exception as e:
            print(f"Warning: Could not fetch Moltbook stats: {e}")
            return self.demo_stats
    
    def get_recent_posts(self, limit: int = 10) -> list:
        """
        Récupère les posts récents sur Moltbook.
        
        Args:
            limit: Nombre de posts à récupérer
            
        Returns:
            Liste de posts
        """
        if self.demo_mode:
            return self.demo_posts[-limit:]
        
        try:
            response = requests.get(
                f"{self.api_url}/posts/x108-safety-gate",
                params={'limit': limit},
                headers={'Authorization': f'Bearer {self.api_key}'},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('posts', [])
            else:
                return []
                
        except Exception as e:
            print(f"Warning: Could not fetch recent posts: {e}")
            return []
    
    def format_post_for_display(self, post_result: Dict) -> str:
        """
        Formate un résultat de post pour l'affichage.
        
        Args:
            post_result: Dict retourné par post_transaction_result()
            
        Returns:
            String formaté pour affichage
        """
        if post_result.get('success'):
            return f"""
📡 **Posted to Moltbook**

**URL:** {post_result['url']}
**Post ID:** {post_result['post_id']}
**Mode:** {post_result['mode']}

This transaction is now visible on the agent internet!

View the public feed: {self.get_feed_url()}
            """
        else:
            return f"""
⚠️ **Moltbook Posting Failed**

**Error:** {post_result.get('error', 'Unknown error')}
**Mode:** {post_result.get('mode', 'unknown')}

The transaction was processed but not published to Moltbook.
            """
    
    def is_connected(self) -> bool:
        """
        Vérifie si l'intégration Moltbook est connectée.
        
        Returns:
            True si connecté, False sinon
        """
        return not self.demo_mode


# Fonction utilitaire pour créer une instance
def create_moltbook_integration() -> MoltbookIntegration:
    """
    Factory function pour créer une instance de MoltbookIntegration.
    """
    return MoltbookIntegration()


# Exemple d'utilisation
if __name__ == "__main__":
    # Test en mode démo
    moltbook = create_moltbook_integration()
    
    print("📡 Moltbook Integration Layer")
    print(f"Mode: {'Demo' if moltbook.demo_mode else 'Production'}")
    print(f"Feed URL: {moltbook.get_feed_url()}")
    print()
    
    # Test de publication d'une transaction autorisée
    print("✅ Test: ALLOWED Transaction")
    allowed_tx = {
        'status': 'ALLOW',
        'amount': 5.0,
        'recipient': 'api_provider',
        'coherence': 0.85,
        'temporal_passed': True,
        'timestamp': datetime.now().isoformat()
    }
    
    result = moltbook.post_transaction_result(allowed_tx)
    print(moltbook.format_post_for_display(result))
    
    # Test de publication d'une transaction bloquée
    print("❌ Test: BLOCKED Transaction")
    blocked_tx = {
        'status': 'BLOCK',
        'amount': 3.0,
        'recipient': 'suspicious_agent',
        'coherence': 0.35,
        'temporal_passed': False,
        'timestamp': datetime.now().isoformat()
    }
    
    result = moltbook.post_transaction_result(blocked_tx)
    print(moltbook.format_post_for_display(result))
    
    # Afficher les statistiques
    print("📊 Moltbook Statistics:")
    stats = moltbook.get_stats()
    print(f"Total Posts: {stats['total_posts']}")
    print(f"Allowed: {stats['allowed_posts']}")
    print(f"Blocked: {stats['blocked_posts']}")
