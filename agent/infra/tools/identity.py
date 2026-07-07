"""
Identity Core - Identity verification with web search capabilities.
Verifies identities by cross-referencing information from multiple web sources.
"""

import hashlib
import json
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime

from .web import WebTools


@dataclass
class IdentityRecord:
    """Represents an identity record for verification."""
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    username: Optional[str] = None
    social_profiles: List[str] = field(default_factory=list)
    verified_sources: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    last_verified: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class IdentityCore:
    """
    Identity verification system with web search capabilities.
    Cross-references identity information from multiple sources.
    """
    
    def __init__(self, web_tools: Optional[WebTools] = None):
        self.web_tools = web_tools or WebTools()
        self.identity_cache: Dict[str, IdentityRecord] = {}
        self.verification_history: List[Dict[str, Any]] = []
        
    def _hash_identifier(self, identifier: str) -> str:
        """Create a hash of an identifier for caching."""
        return hashlib.sha256(identifier.lower().strip().encode()).hexdigest()[:16]
    
    def verify_name(self, name: str, context: Optional[str] = None) -> IdentityRecord:
        """
        Verify a person's name by searching web sources.
        
        Args:
            name: Full name to verify
            context: Additional context (profession, location, etc.)
            
        Returns:
            IdentityRecord with verification results
        """
        cache_key = self._hash_identifier(f"name:{name}")
        
        # Check cache first
        if cache_key in self.identity_cache:
            cached = self.identity_cache[cache_key]
            if cached.last_verified and \
               (datetime.now() - cached.last_verified).total_seconds() < 3600:
                return cached
        
        # Build search queries
        queries = [name]
        if context:
            queries.append(f"{name} {context}")
            queries.append(f"{name} professional profile")
        
        # Search multiple sources
        all_results = []
        sources_found = set()
        
        for query in queries[:3]:  # Limit queries
            results = self.web_tools.search(query, num_results=5)
            all_results.extend(results)
            for result in results:
                if result.get('source'):
                    sources_found.add(result['source'])
            time.sleep(0.5)  # Rate limiting
        
        # Analyze results
        social_profiles = []
        confidence_factors = []
        
        for result in all_results:
            url = result.get('url', '').lower()
            title = result.get('title', '').lower()
            
            # Check for social media profiles
            if any(domain in url for domain in ['linkedin.com', 'twitter.com', 'github.com', 'facebook.com']):
                social_profiles.append(url)
                confidence_factors.append(0.3)
            
            # Check for professional profiles
            if any(term in title for term in ['profile', 'bio', 'about', 'professional']):
                confidence_factors.append(0.2)
            
            # Check for news mentions
            if 'news' in result.get('source', ''):
                confidence_factors.append(0.15)
        
        # Calculate confidence score
        base_score = min(len(sources_found) * 0.1, 0.3)
        social_score = min(len(set(social_profiles)) * 0.15, 0.4)
        result_score = min(sum(confidence_factors), 0.3)
        confidence_score = base_score + social_score + result_score
        
        record = IdentityRecord(
            name=name,
            social_profiles=list(set(social_profiles))[:5],
            verified_sources=list(sources_found),
            confidence_score=min(confidence_score, 1.0),
            last_verified=datetime.now(),
            metadata={
                'total_results': len(all_results),
                'queries_used': queries,
                'context': context
            }
        )
        
        # Cache the result
        self.identity_cache[cache_key] = record
        
        # Log verification
        self.verification_history.append({
            'timestamp': datetime.now().isoformat(),
            'type': 'name_verification',
            'identifier': name,
            'confidence': record.confidence_score
        })
        
        return record
    
    def verify_email(self, email: str) -> Dict[str, Any]:
        """
        Verify an email address through various checks.
        
        Args:
            email: Email address to verify
            
        Returns:
            Dictionary with verification results
        """
        import re
        
        result = {
            'email': email,
            'valid_format': False,
            'domain_exists': False,
            'disposable': False,
            'confidence': 0.0,
            'details': {}
        }
        
        # Check format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        result['valid_format'] = bool(re.match(email_pattern, email))
        
        if not result['valid_format']:
            return result
        
        # Extract domain
        domain = email.split('@')[1]
        result['details']['domain'] = domain
        
        # Check for disposable email domains
        disposable_domains = [
            'tempmail.com', 'throwaway.com', 'guerrillamail.com',
            'mailinator.com', '10minutemail.com'
        ]
        result['disposable'] = domain.lower() in disposable_domains
        
        # Search for domain reputation
        domain_results = self.web_tools.search(f"{domain} email provider", num_results=3)
        result['domain_exists'] = len(domain_results) > 0
        
        # Calculate confidence
        confidence = 0.0
        if result['valid_format']:
            confidence += 0.3
        if result['domain_exists']:
            confidence += 0.4
        if not result['disposable']:
            confidence += 0.3
        
        result['confidence'] = confidence
        
        return result
    
    def verify_username(self, username: str, platforms: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Verify if a username exists across multiple platforms.
        
        Args:
            username: Username to check
            platforms: List of platforms to check (default: major social networks)
            
        Returns:
            Dictionary with platform availability
        """
        if platforms is None:
            platforms = [
                'github.com', 'twitter.com', 'instagram.com',
                'reddit.com', 'linkedin.com', 'facebook.com'
            ]
        
        results = {
            'username': username,
            'platforms_checked': [],
            'found_on': [],
            'not_found_on': [],
            'profiles': []
        }
        
        for platform in platforms:
            platform_name = platform.split('.')[0]
            results['platforms_checked'].append(platform_name)
            
            # Search for username on platform
            query = f"site:{platform} {username}"
            search_results = self.web_tools.search(query, num_results=2)
            
            found = False
            for result in search_results:
                url = result.get('url', '').lower()
                if username.lower() in url.lower():
                    found = True
                    results['profiles'].append({
                        'platform': platform_name,
                        'url': url,
                        'title': result.get('title', '')
                    })
                    break
            
            if found:
                results['found_on'].append(platform_name)
            else:
                results['not_found_on'].append(platform_name)
        
        results['presence_score'] = len(results['found_on']) / len(platforms) if platforms else 0.0
        
        return result
    
    def cross_reference(self, name: str, email: Optional[str] = None, 
                       username: Optional[str] = None) -> Dict[str, Any]:
        """
        Cross-reference multiple identity attributes.
        
        Args:
            name: Full name
            email: Email address
            username: Username
            
        Returns:
            Comprehensive verification report
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'inputs': {
                'name': name,
                'email': email,
                'username': username
            },
            'verifications': {},
            'overall_confidence': 0.0,
            'flags': [],
            'recommendations': []
        }
        
        # Verify each attribute
        if name:
            name_result = self.verify_name(name)
            report['verifications']['name'] = {
                'confidence': name_result.confidence_score,
                'sources': name_result.verified_sources,
                'social_profiles': name_result.social_profiles
            }
        
        if email:
            email_result = self.verify_email(email)
            report['verifications']['email'] = email_result
        
        if username:
            username_result = self.verify_username(username)
            report['verifications']['username'] = username_result
        
        # Calculate overall confidence
        confidences = []
        for v in report['verifications'].values():
            if isinstance(v, dict) and 'confidence' in v:
                confidences.append(v['confidence'])
        
        if confidences:
            report['overall_confidence'] = sum(confidences) / len(confidences)
        
        # Add flags and recommendations
        if report['overall_confidence'] < 0.3:
            report['flags'].append('low_confidence')
            report['recommendations'].append('Request additional verification documents')
        
        if email and report['verifications'].get('email', {}).get('disposable'):
            report['flags'].append('disposable_email')
            report['recommendations'].append('Email uses disposable domain')
        
        return report
    
    def get_verification_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent verification history."""
        return self.verification_history[-limit:]
    
    def clear_cache(self):
        """Clear the identity cache."""
        self.identity_cache.clear()


# Global instance
_identity_core: Optional[IdentityCore] = None


def get_identity_core() -> IdentityCore:
    """Get or create the global identity core instance."""
    global _identity_core
    if _identity_core is None:
        _identity_core = IdentityCore()
    return _identity_core
