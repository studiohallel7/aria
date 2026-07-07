"""
Web Tools - Web browsing and search capabilities.
Includes search, page fetching, and link extraction.
"""

import requests
from typing import Optional, List, Dict, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re


class WebTools:
    """Web browsing and search tools for the agent."""
    
    def __init__(self, user_agent: str = "AutonomousAgent/1.0"):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })
    
    def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search the web using a search engine.
        Note: This is a placeholder - in production, integrate with Google/Bing API.
        """
        # Placeholder implementation
        # In production, use: Google Custom Search API, Bing Search API, or similar
        return [
            {
                "title": f"Result {i+1} for '{query}'",
                "url": f"https://example.com/result{i}",
                "snippet": f"This is a sample search result for query: {query}",
            }
            for i in range(num_results)
        ]
    
    def fetch_page(self, url: str, timeout: int = 10) -> Optional[str]:
        """Fetch the text content of a web page."""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            # Parse HTML and extract text
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(['script', 'style', 'header', 'footer', 'nav']):
                script.decompose()
            
            # Get text
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text[:10000]  # Limit to 10k chars
            
        except Exception as e:
            return None
    
    def extract_links(self, url: str, timeout: int = 10) -> List[str]:
        """Extract all links from a web page."""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            links = []
            parsed_url = urlparse(url)
            base_domain = parsed_url.netloc
            
            for anchor in soup.find_all('a', href=True):
                href = anchor['href'].strip()
                
                # Skip javascript, mailto, etc.
                if href.startswith(('javascript:', 'mailto:', '#')):
                    continue
                
                # Convert relative URLs to absolute
                full_url = urljoin(url, href)
                
                # Only include links from the same domain (optional)
                links.append(full_url)
            
            return list(set(links))  # Remove duplicates
            
        except Exception as e:
            return []
    
    def get_page_metadata(self, url: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
        """Get metadata from a web page (title, description, etc.)."""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            metadata = {
                'url': url,
                'title': '',
                'description': '',
                'author': '',
                'keywords': [],
            }
            
            # Extract title
            title_tag = soup.find('title')
            if title_tag:
                metadata['title'] = title_tag.get_text(strip=True)
            
            # Extract meta description
            desc_tag = soup.find('meta', attrs={'name': 'description'})
            if desc_tag and desc_tag.get('content'):
                metadata['description'] = desc_tag['content']
            
            # Extract author
            author_tag = soup.find('meta', attrs={'name': 'author'})
            if author_tag and author_tag.get('content'):
                metadata['author'] = author_tag['content']
            
            # Extract keywords
            keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
            if keywords_tag and keywords_tag.get('content'):
                metadata['keywords'] = [k.strip() for k in keywords_tag['content'].split(',')]
            
            return metadata
            
        except Exception as e:
            return None
    
    def is_valid_url(self, url: str) -> bool:
        """Check if a URL is valid."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False


# Global instance
_web_tools: Optional[WebTools] = None


def get_web_tools() -> WebTools:
    """Get or create the global web tools instance."""
    global _web_tools
    if _web_tools is None:
        _web_tools = WebTools()
    return _web_tools