"""
Web Tools - Web browsing and search capabilities.
Includes real search engine integration, page fetching, and link extraction.
Supports DuckDuckGo HTML scraping for free search and optional API integrations.
"""

import requests
from typing import Optional, List, Dict, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, quote_plus
import re
import time


class WebTools:
    """Web browsing and search tools for the agent."""
    
    def __init__(self, user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        })
        self.last_search_time = 0
        self.search_delay = 2  # Seconds between searches to avoid rate limiting
    
    def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search the web using DuckDuckGo HTML interface (free, no API key required).
        Falls back to other methods if needed.
        """
        # Rate limiting
        elapsed = time.time() - self.last_search_time
        if elapsed < self.search_delay:
            time.sleep(self.search_delay - elapsed)
        
        try:
            # DuckDuckGo HTML search
            encoded_query = quote_plus(query)
            search_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            response = self.session.get(search_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            # Extract results from DuckDuckGo HTML
            for result in soup.find_all('a', class_='result__a', limit=num_results):
                title = result.get_text(strip=True)
                url = result.get('href')
                
                # DuckDuckGo uses redirect URLs, extract actual URL
                if url and url.startswith('/l/?uddg='):
                    from urllib.parse import unquote
                    url = unquote(url.split('/l/?uddg=')[1].split('&rutime=')[0])
                
                # Find snippet
                snippet = ""
                snippet_elem = result.find_parent('div', class_='results_main').find('a', class_='result__snippet')
                if snippet_elem:
                    snippet = snippet_elem.get_text(strip=True)
                else:
                    snippet_elem = result.find_next_sibling('a', class_='result__snippet')
                    if snippet_elem:
                        snippet = snippet_elem.get_text(strip=True)
                
                if title and url:
                    results.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet,
                        "source": "duckduckgo"
                    })
            
            # If we got results, update last search time
            if results:
                self.last_search_time = time.time()
                return results
            
        except Exception as e:
            print(f"DuckDuckGo search failed: {e}")
        
        # Fallback: Try Wikipedia for informational queries
        try:
            wiki_results = self._search_wikipedia(query, num_results)
            if wiki_results:
                return wiki_results
        except Exception as e:
            print(f"Wikipedia search failed: {e}")
        
        # Last resort: Return empty with explanation
        return [{
            "title": "Search unavailable",
            "url": "",
            "snippet": f"Web search temporarily unavailable. Query was: {query}",
            "source": "fallback"
        }]
    
    def _search_wikipedia(self, query: str, num_results: int = 3) -> List[Dict[str, Any]]:
        """Search Wikipedia as a fallback."""
        api_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": num_results
        }
        
        # Add proper headers for Wikipedia
        headers = {
            "User-Agent": "AutonomousAgent/1.0 (contact: agent@example.com)",
            "Accept-Language": "en-US,en;q=0.5"
        }
        
        try:
            response = self.session.get(api_url, params=params, timeout=10, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get('query', {}).get('search', []):
                results.append({
                    "title": item['title'],
                    "url": f"https://en.wikipedia.org/wiki/{item['title'].replace(' ', '_')}",
                    "snippet": item.get('snippet', ''),
                    "source": "wikipedia"
                })
            
            return results
        except Exception as e:
            print(f"Wikipedia API error: {e}")
            return []
    
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
    
    def search_news(self, query: str, num_results: int = 3) -> List[Dict[str, Any]]:
        """Search for news articles (uses Google News RSS as fallback)."""
        try:
            # Use Google News RSS feed (no API key required)
            encoded_query = quote_plus(query)
            rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en&gl=US&ceid=US:en"
            
            response = self.session.get(rss_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'xml')
            results = []
            
            for item in soup.find_all('item', limit=num_results):
                title = item.find('title')
                link = item.find('link')
                pub_date = item.find('pubDate')
                
                if title and link:
                    results.append({
                        "title": title.get_text(strip=True),
                        "url": link.get_text(strip=True),
                        "published": pub_date.get_text(strip=True) if pub_date else "",
                        "source": "google_news"
                    })
            
            return results
            
        except Exception as e:
            return [{
                "title": "News search unavailable",
                "url": "",
                "published": "",
                "source": "fallback"
            }]
    
    def get_weather(self, location: str) -> Optional[Dict[str, Any]]:
        """Get weather information using wttr.in (free, no API key)."""
        try:
            encoded_location = quote_plus(location)
            url = f"http://wttr.in/{encoded_location}?format=j1"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            current = data.get('current_condition', [{}])[0]
            
            return {
                "location": location,
                "temperature_c": current.get('temp_C', 'N/A'),
                "temperature_f": current.get('temp_F', 'N/A'),
                "condition": current.get('weatherDesc', [{}])[0].get('value', 'N/A'),
                "humidity": current.get('humidity', 'N/A'),
                "wind_speed": current.get('windspeedKmph', 'N/A'),
                "feels_like": current.get('FeelsLikeC', 'N/A'),
            }
            
        except Exception as e:
            return None


# Global instance
_web_tools: Optional[WebTools] = None


def get_web_tools() -> WebTools:
    """Get or create the global web tools instance."""
    global _web_tools
    if _web_tools is None:
        _web_tools = WebTools()
    return _web_tools