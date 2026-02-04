import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Set, Dict
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class WebCrawler:
    """Web crawler to extract content from websites."""
    
    def __init__(self, max_pages: int = 100, max_depth: int = 3):
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.visited_urls: Set[str] = set()
        self.pages_data: List[Dict[str, str]] = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def is_valid_url(self, url: str, base_domain: str) -> bool:
        """Check if URL is valid and belongs to the same domain."""
        try:
            parsed = urlparse(url)
            base_parsed = urlparse(base_domain)
            
            # Check if same domain/subdomain
            if parsed.netloc != base_parsed.netloc:
                return False
            
            # Skip non-http(s) schemes
            if parsed.scheme not in ['http', 'https']:
                return False
            
            # Skip common file extensions
            skip_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.zip', '.exe', '.dmg']
            if any(url.lower().endswith(ext) for ext in skip_extensions):
                return False
            
            return True
        except Exception:
            return False
    
    def clean_text(self, soup: BeautifulSoup) -> str:
        """Extract and clean text from HTML."""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract all valid links from a page."""
        links = []
        for link in soup.find_all('a', href=True):
            url = urljoin(base_url, link['href'])
            # Remove fragments
            url = url.split('#')[0]
            if self.is_valid_url(url, base_url):
                links.append(url)
        return list(set(links))
    
    def crawl_page(self, url: str) -> Dict[str, any]:
        """Crawl a single page and extract content."""
        try:
            logger.info(f"Crawling: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.find('title')
            title_text = title.string if title else url
            
            # Extract and clean text
            content = self.clean_text(soup)
            
            # Extract links
            links = self.extract_links(soup, url)
            
            return {
                'url': url,
                'title': title_text,
                'content': content,
                'links': links,
                'success': True
            }
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")
            return {
                'url': url,
                'success': False,
                'error': str(e)
            }
    
    def crawl(self, start_url: str) -> List[Dict[str, str]]:
        """Crawl website starting from the given URL."""
        logger.info(f"Starting crawl from: {start_url}")
        
        # Initialize
        self.visited_urls.clear()
        self.pages_data.clear()
        
        # Queue for BFS crawling
        to_visit = [(start_url, 0)]  # (url, depth)
        
        while to_visit and len(self.visited_urls) < self.max_pages:
            url, depth = to_visit.pop(0)
            
            # Skip if already visited or depth exceeded
            if url in self.visited_urls or depth > self.max_depth:
                continue
            
            # Mark as visited
            self.visited_urls.add(url)
            
            # Crawl the page
            page_data = self.crawl_page(url)
            
            if page_data['success']:
                # Store page data
                self.pages_data.append({
                    'url': page_data['url'],
                    'title': page_data['title'],
                    'content': page_data['content']
                })
                
                # Add new links to queue
                if depth < self.max_depth:
                    for link in page_data['links']:
                        if link not in self.visited_urls:
                            to_visit.append((link, depth + 1))
            
            # Rate limiting
            time.sleep(0.5)
        
        logger.info(f"Crawling complete. Pages crawled: {len(self.pages_data)}")
        return self.pages_data
