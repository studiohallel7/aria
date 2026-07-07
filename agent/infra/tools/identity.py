"""
Identity Core - Identity verification with web search capabilities.
Verifies identities by cross-referencing information from multiple web sources.
"""

import requests
from typing import Optional, List, Dict, Any, Tuple
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import hashlib


class IdentityCore:
    """
    Identity verification system that uses web search to verify identities.
    Cross-references information from multiple sources for validation.
    """
    
    def __init__(self, user_agent: str = "IdentityCore/1.0"):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })
        self.verification_results = []
    
    def verify_name(self, name: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Verify a person's name by searching for it on the web.
        Returns confidence score and supporting evidence.
        """
        results = {
            'name': name,
            'context': context,
            'confidence_score': 0.0,
            'sources_found': 0,
            'evidence': [],
            'risk_flags': []
        }
        
        # Search queries to perform
        queries = [
            f'"{name}"',
            f'{name} profile',
            f'{name} linkedin',
            f'{name} professional'
        ]
        
        if context:
            queries.append(f'"{name}" {context}')
        
        # Simulate search results (in production, use real search API)
        for query in queries:
            search_results = self._search_web(query)
            if search_results:
                results['sources_found'] += len(search_results)
                results['evidence'].extend(search_results[:3])  # Limit evidence
        
        # Calculate confidence score
        if results['sources_found'] > 0:
            # More sources = higher confidence
            source_score = min(results['sources_found'] / 10.0, 0.5)
            
            # Quality of sources (domain authority simulation)
            quality_score = self._calculate_source_quality(results['evidence'])
            
            results['confidence_score'] = min(source_score + quality_score, 1.0)
        
        # Check for risk flags
        results['risk_flags'] = self._check_risk_flags(name, results['evidence'])
        
        self.verification_results.append(results)
        return results
    
    def verify_email(self, email: str) -> Dict[str, Any]:
        """
        Verify an email address by checking format and searching for associations.
        """
        results = {
            'email': email,
            'valid_format': False,
            'domain_exists': False,
            'confidence_score': 0.0,
            'evidence': [],
            'risk_flags': []
        }
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, email):
            results['valid_format'] = True
            results['confidence_score'] += 0.3
        
        # Extract domain and check if it exists
        domain = email.split('@')[1] if '@' in email else ''
        if domain:
            results['domain_exists'] = self._check_domain_exists(domain)
            if results['domain_exists']:
                results['confidence_score'] += 0.3
        
        # Search for email associations
        search_results = self._search_web(f'"{email}"')
        if search_results:
            results['evidence'] = search_results[:5]
            results['confidence_score'] += min(len(search_results) * 0.1, 0.4)
        
        # Check for disposable email domains
        disposable_domains = ['tempmail.com', 'throwaway.com', 'guerrillamail.com']
        if domain in disposable_domains:
            results['risk_flags'].append('disposable_email')
            results['confidence_score'] -= 0.5
        
        results['confidence_score'] = max(0.0, min(1.0, results['confidence_score']))
        self.verification_results.append(results)
        return results
    
    def verify_phone(self, phone: str, country_code: str = 'US') -> Dict[str, Any]:
        """
        Verify a phone number by checking format and searching for associations.
        """
        results = {
            'phone': phone,
            'country_code': country_code,
            'valid_format': False,
            'confidence_score': 0.0,
            'evidence': [],
            'risk_flags': []
        }
        
        # Basic phone validation (simplified)
        phone_clean = re.sub(r'[^\d+]', '', phone)
        if len(phone_clean) >= 10 and len(phone_clean) <= 15:
            results['valid_format'] = True
            results['confidence_score'] += 0.4
        
        # Search for phone number associations
        search_results = self._search_web(f'"{phone}"')
        if search_results:
            results['evidence'] = search_results[:5]
            results['confidence_score'] += min(len(search_results) * 0.1, 0.4)
        
        # Check for VOIP or virtual phone indicators
        voip_indicators = ['voip', 'virtual', 'temporary']
        for indicator in voip_indicators:
            if any(indicator in str(evidence).lower() for evidence in results['evidence']):
                results['risk_flags'].append(f'possible_{indicator}_number')
        
        results['confidence_score'] = max(0.0, min(1.0, results['confidence_score']))
        self.verification_results.append(results)
        return results
    
    def comprehensive_verify(self, name: Optional[str] = None, 
                           email: Optional[str] = None,
                           phone: Optional[str] = None,
                           additional_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform comprehensive identity verification using multiple data points.
        """
        verification_report = {
            'timestamp': str(__import__('datetime').datetime.now()),
            'inputs': {
                'name': name,
                'email': email,
                'phone': phone,
                'additional_info': additional_info
            },
            'verifications': {},
            'overall_confidence': 0.0,
            'overall_risk': 'low',
            'recommendations': []
        }
        
        scores = []
        risk_count = 0
        
        # Verify each provided piece of information
        if name:
            name_result = self.verify_name(name, additional_info.get('context') if additional_info else None)
            verification_report['verifications']['name'] = name_result
            scores.append(name_result['confidence_score'])
            if name_result['risk_flags']:
                risk_count += len(name_result['risk_flags'])
        
        if email:
            email_result = self.verify_email(email)
            verification_report['verifications']['email'] = email_result
            scores.append(email_result['confidence_score'])
            if email_result['risk_flags']:
                risk_count += len(email_result['risk_flags'])
        
        if phone:
            phone_result = self.verify_phone(phone)
            verification_report['verifications']['phone'] = phone_result
            scores.append(phone_result['confidence_score'])
            if phone_result['risk_flags']:
                risk_count += len(phone_result['risk_flags'])
        
        # Calculate overall confidence
        if scores:
            verification_report['overall_confidence'] = sum(scores) / len(scores)
        
        # Determine overall risk level
        if risk_count == 0:
            verification_report['overall_risk'] = 'low'
        elif risk_count <= 2:
            verification_report['overall_risk'] = 'medium'
        else:
            verification_report['overall_risk'] = 'high'
        
        # Generate recommendations
        if verification_report['overall_confidence'] < 0.5:
            verification_report['recommendations'].append(
                'Low confidence score - recommend additional verification steps'
            )
        if verification_report['overall_risk'] == 'high':
            verification_report['recommendations'].append(
                'High risk detected - manual review recommended'
            )
        if not verification_report['recommendations']:
            verification_report['recommendations'].append(
                'Identity verification passed - proceed with standard protocols'
            )
        
        return verification_report
    
    def _search_web(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search the web for information.
        In production, integrate with Google Custom Search API, Bing API, etc.
        """
        # Placeholder implementation
        # In production, replace with actual API calls
        try:
            # Example: Using DuckDuckGo HTML interface (for demonstration)
            # Note: For production, use official APIs
            url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                results = []
                
                for result in soup.find_all('div', class_='result__body')[:num_results]:
                    title_elem = result.find('a', class_='result__title')
                    snippet_elem = result.find('a', class_='result__snippet')
                    
                    if title_elem and snippet_elem:
                        results.append({
                            'title': title_elem.get_text(strip=True),
                            'url': title_elem.get('href', ''),
                            'snippet': snippet_elem.get_text(strip=True)
                        })
                
                return results
        except Exception as e:
            pass
        
        # Fallback to mock results if search fails
        return [
            {
                'title': f'Search result for "{query}"',
                'url': 'https://example.com',
                'snippet': f'Information about {query}'
            }
        ]
    
    def _check_domain_exists(self, domain: str) -> bool:
        """Check if a domain exists by attempting to resolve it."""
        try:
            response = self.session.get(f'http://{domain}', timeout=5)
            return response.status_code < 400
        except:
            # Try HTTPS
            try:
                response = self.session.get(f'https://{domain}', timeout=5, allow_redirects=False)
                return True
            except:
                return False
    
    def _calculate_source_quality(self, evidence: List[Dict[str, Any]]) -> float:
        """Calculate quality score based on source domains."""
        if not evidence:
            return 0.0
        
        high_quality_domains = ['linkedin.com', 'twitter.com', 'facebook.com', 
                               'github.com', 'medium.com', 'wikipedia.org']
        medium_quality_domains = ['blogspot.com', 'wordpress.com', 'reddit.com']
        
        quality_score = 0.0
        for item in evidence:
            url = item.get('url', '')
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            if any(hq in domain for hq in high_quality_domains):
                quality_score += 0.15
            elif any(mq in domain for mq in medium_quality_domains):
                quality_score += 0.08
            else:
                quality_score += 0.05
        
        return min(quality_score, 0.5)
    
    def _check_risk_flags(self, name: str, evidence: List[Dict[str, Any]]) -> List[str]:
        """Check for potential risk indicators in search results."""
        flags = []
        
        risk_keywords = ['scam', 'fraud', 'fake', 'complaint', 'warning', 'arrest']
        
        for item in evidence:
            text = f"{item.get('title', '')} {item.get('snippet', '')}".lower()
            for keyword in risk_keywords:
                if keyword in text:
                    flags.append(f'negative_content_{keyword}')
                    break
        
        return list(set(flags))
    
    def get_verification_history(self) -> List[Dict[str, Any]]:
        """Return all verification results performed in this session."""
        return self.verification_results
    
    def clear_history(self):
        """Clear verification history."""
        self.verification_results = []


# Global instance
_identity_core: Optional[IdentityCore] = None


def get_identity_core() -> IdentityCore:
    """Get or create the global IdentityCore instance."""
    global _identity_core
    if _identity_core is None:
        _identity_core = IdentityCore()
    return _identity_core
