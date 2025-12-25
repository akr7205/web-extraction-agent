"""Web crawler for discovering and extracting from all pages of a website."""
import logging
import time
from typing import List, Set, Dict, Any, Optional
from urllib.parse import urljoin, urlparse, urlunparse
from collections import deque
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class WebCrawler:
    """Crawl a website to discover all accessible pages."""
    
    def __init__(
        self,
        max_pages: int = 50,
        max_depth: int = 3,
        same_domain_only: bool = True,
        respect_robots: bool = True,
        delay_between_requests: float = 0.5,
        timeout: int = 10,
        user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ):
        """
        Initialize web crawler.
        
        Args:
            max_pages: Maximum number of pages to crawl
            max_depth: Maximum depth to crawl from starting URL
            same_domain_only: Only crawl pages on the same domain
            respect_robots: Whether to respect robots.txt (basic implementation)
            delay_between_requests: Delay in seconds between requests
            timeout: Request timeout in seconds
            user_agent: User agent string
        """
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.same_domain_only = same_domain_only
        self.respect_robots = respect_robots
        self.delay_between_requests = delay_between_requests
        self.timeout = timeout
        self.user_agent = user_agent
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        })
        
        self.visited_urls: Set[str] = set()
        self.disallowed_paths: Set[str] = set()
    
    def normalize_url(self, url: str) -> str:
        """
        Normalize URL for consistent comparison.
        
        Args:
            url: URL to normalize
            
        Returns:
            Normalized URL
        """
        parsed = urlparse(url)
        # Remove fragment, normalize path
        normalized = urlunparse((
            parsed.scheme,
            parsed.netloc.lower(),
            parsed.path.rstrip('/') if parsed.path != '/' else '/',
            parsed.params,
            parsed.query,
            ''  # Remove fragment
        ))
        return normalized
    
    def is_same_domain(self, url1: str, url2: str) -> bool:
        """
        Check if two URLs are from the same domain.
        
        Args:
            url1: First URL
            url2: Second URL
            
        Returns:
            True if same domain
        """
        domain1 = urlparse(url1).netloc.lower()
        domain2 = urlparse(url2).netloc.lower()
        return domain1 == domain2
    
    def is_valid_url(self, url: str, base_domain: str) -> bool:
        """
        Check if URL should be crawled.
        
        Args:
            url: URL to check
            base_domain: Base domain for comparison
            
        Returns:
            True if URL should be crawled
        """
        parsed = urlparse(url)
        
        # Must have scheme and netloc
        if not parsed.scheme or not parsed.netloc:
            return False
        
        # Must be http or https
        if parsed.scheme not in ['http', 'https']:
            return False
        
        # Check same domain if required
        if self.same_domain_only and not self.is_same_domain(url, base_domain):
            return False
        
        # Skip common non-content URLs
        skip_extensions = {
            '.pdf', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico',
            '.css', '.js', '.zip', '.tar', '.gz', '.mp4', '.mp3',
            '.xml', '.json', '.csv', '.txt', '.doc', '.docx', '.xls', '.xlsx'
        }
        
        path_lower = parsed.path.lower()
        if any(path_lower.endswith(ext) for ext in skip_extensions):
            return False
        
        # Skip common non-content paths
        skip_patterns = ['/cdn-cgi/', '/wp-admin/', '/wp-content/', '/wp-includes/']
        if any(pattern in parsed.path for pattern in skip_patterns):
            return False
        
        return True
    
    def fetch_robots_txt(self, base_url: str) -> None:
        """
        Fetch and parse robots.txt to identify disallowed paths.
        
        Args:
            base_url: Base URL of the website
        """
        if not self.respect_robots:
            return
        
        try:
            robots_url = urljoin(base_url, '/robots.txt')
            response = self.session.get(robots_url, timeout=self.timeout)
            
            if response.status_code == 200:
                # Parse robots.txt with User-agent awareness
                lines = response.text.split('\n')
                current_user_agent = None
                applies_to_us = False
                
                for line in lines:
                    line = line.strip()
                    
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Check for User-agent directive
                    if line.lower().startswith('user-agent:'):
                        agent = line.split(':', 1)[1].strip().lower()
                        current_user_agent = agent
                        # Check if this section applies to our user agent
                        # '*' means all agents, or match our user agent string
                        our_agent = self.user_agent.lower()
                        applies_to_us = (agent == '*' or agent in our_agent or our_agent.startswith(agent))
                    
                    # Only process Disallow if it applies to our user agent
                    elif line.lower().startswith('disallow:') and applies_to_us:
                        path = line.split(':', 1)[1].strip()
                        if path:
                            self.disallowed_paths.add(path)
                
                logger.info(f"Found {len(self.disallowed_paths)} disallowed paths in robots.txt for our user agent")
        except Exception as e:
            logger.debug(f"Could not fetch robots.txt: {e}")
    
    def is_allowed_by_robots(self, url: str) -> bool:
        """
        Check if URL is allowed by robots.txt.
        
        Args:
            url: URL to check
            
        Returns:
            True if allowed
        """
        if not self.respect_robots or not self.disallowed_paths:
            return True
        
        parsed = urlparse(url)
        path = parsed.path
        
        # If path is empty, default to /
        if not path:
            path = '/'
        
        for disallowed in self.disallowed_paths:
            # Handle wildcard patterns
            if disallowed.endswith('*'):
                # Wildcard at end - check if path starts with prefix
                prefix = disallowed[:-1]
                if path.startswith(prefix):
                    return False
            elif disallowed.endswith('/*'):
                # Directory wildcard - check if path is under this directory
                prefix = disallowed[:-2]
                if path == prefix or path.startswith(prefix + '/'):
                    return False
            else:
                # Exact match or prefix match
                if path == disallowed or path.startswith(disallowed):
                    return False
        
        return True
    
    def discover_sitemap_urls(self, base_url: str) -> List[str]:
        """
        Try to discover URLs from sitemap.xml.
        
        Args:
            base_url: Base URL of the website
            
        Returns:
            List of discovered URLs
        """
        urls = []
        sitemap_locations = ['/sitemap.xml', '/sitemap_index.xml', '/sitemap-index.xml']
        
        for location in sitemap_locations:
            try:
                sitemap_url = urljoin(base_url, location)
                response = self.session.get(sitemap_url, timeout=self.timeout)
                
                if response.status_code == 200:
                    try:
                        root = ET.fromstring(response.content)
                        # Handle different sitemap namespaces
                        namespaces = {
                            'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9',
                            '': 'http://www.sitemaps.org/schemas/sitemap/0.9'
                        }
                        
                        # Look for <loc> tags
                        for loc in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                            if loc.text:
                                urls.append(loc.text.strip())
                        
                        # Also try without namespace
                        for loc in root.findall('.//loc'):
                            if loc.text and loc.text.strip() not in urls:
                                urls.append(loc.text.strip())
                        
                        if urls:
                            logger.info(f"Found {len(urls)} URLs in sitemap at {sitemap_url}")
                            break
                    except ET.ParseError as e:
                        logger.debug(f"Could not parse sitemap XML: {e}")
            except Exception as e:
                logger.debug(f"Could not fetch sitemap from {location}: {e}")
        
        return urls
    
    def extract_links(self, html: str, base_url: str) -> List[str]:
        """
        Extract all links from HTML content.
        
        Args:
            html: HTML content
            base_url: Base URL for resolving relative links
            
        Returns:
            List of absolute URLs
        """
        links = []
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href'].strip()
                if not href or href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:'):
                    continue
                
                # Convert to absolute URL
                absolute_url = urljoin(base_url, href)
                links.append(absolute_url)
        
        except Exception as e:
            logger.warning(f"Error extracting links: {e}")
        
        return links
    
    def crawl(self, start_url: str) -> List[Dict[str, Any]]:
        """
        Crawl website starting from the given URL.
        
        Args:
            start_url: Starting URL to crawl from
            
        Returns:
            List of dictionaries with 'url', 'html', 'depth', 'title'
        """
        start_time = time.time()
        start_url = self.normalize_url(start_url)
        base_domain = start_url
        
        logger.info(f"Starting crawl from {start_url}")
        logger.info(f"Max pages: {self.max_pages}, Max depth: {self.max_depth}")
        
        # Fetch robots.txt
        self.fetch_robots_txt(start_url)
        
        # Try to get URLs from sitemap first
        sitemap_urls = self.discover_sitemap_urls(start_url)
        
        # Initialize queue with start URL and sitemap URLs
        queue = deque([(start_url, 0)])  # (url, depth)
        
        # Add sitemap URLs with depth 1
        for url in sitemap_urls[:self.max_pages]:
            normalized = self.normalize_url(url)
            if self.is_valid_url(normalized, base_domain):
                queue.append((normalized, 1))
        
        results = []
        
        while queue and len(results) < self.max_pages:
            url, depth = queue.popleft()
            
            # Skip if already visited
            if url in self.visited_urls:
                continue
            
            # Skip if exceeds max depth
            if depth > self.max_depth:
                continue
            
            # Skip if not allowed by robots.txt
            if not self.is_allowed_by_robots(url):
                logger.debug(f"Skipping {url} (disallowed by robots.txt)")
                continue
            
            # Mark as visited
            self.visited_urls.add(url)
            
            try:
                # Add delay between requests
                if results:  # Don't delay the first request
                    time.sleep(self.delay_between_requests)
                
                logger.info(f"Crawling [{len(results)+1}/{self.max_pages}] depth={depth}: {url}")
                
                # Add Referer header for requests after the first one
                request_headers = {}
                if results:  # Add referer for non-first requests
                    request_headers['Referer'] = results[-1]['url']
                
                response = self.session.get(url, timeout=self.timeout, allow_redirects=True, headers=request_headers)
                
                logger.info(f"Response status: {response.status_code}, Content-Type: {response.headers.get('Content-Type', 'N/A')}, Content-Length: {len(response.text)} bytes")
                
                # Only process HTML content
                content_type = response.headers.get('Content-Type', '').lower()
                if 'text/html' not in content_type:
                    logger.warning(f"Skipping non-HTML content: {content_type} for {url}")
                    continue
                
                if response.status_code == 200:
                    html = response.text
                    
                    if not html or len(html) < 100:
                        logger.warning(f"Empty or very small HTML response ({len(html)} bytes) for {url}")
                        continue
                    
                    logger.info(f"✓ Successfully fetched HTML ({len(html)} bytes) from {url}")
                    
                    # Extract title
                    title = "Untitled"
                    try:
                        soup = BeautifulSoup(html, 'lxml')
                        title_tag = soup.find('title')
                        if title_tag:
                            title = title_tag.get_text().strip()
                    except:
                        pass
                    
                    # Add to results
                    results.append({
                        'url': url,
                        'html': html,
                        'depth': depth,
                        'title': title,
                        'status_code': response.status_code
                    })
                    
                    # Extract and queue new links if not at max depth
                    if depth < self.max_depth and len(results) < self.max_pages:
                        links = self.extract_links(html, url)
                        
                        for link in links:
                            normalized_link = self.normalize_url(link)
                            
                            if (normalized_link not in self.visited_urls and
                                self.is_valid_url(normalized_link, base_domain)):
                                queue.append((normalized_link, depth + 1))
                else:
                    logger.warning(f"Got status {response.status_code} for {url}")
                    logger.warning(f"Response headers: {dict(response.headers)}")
                    logger.warning(f"Response text preview: {response.text[:500] if response.text else 'Empty'}")
            
            except requests.exceptions.RequestException as e:
                logger.warning(f"Failed to fetch {url}: {e}")
            except Exception as e:
                logger.error(f"Error processing {url}: {e}")
        
        elapsed = time.time() - start_time
        logger.info(f"Crawl completed: {len(results)} pages in {elapsed:.2f}s")
        
        return results
    
    def crawl_urls_only(self, start_url: str) -> List[str]:
        """
        Discover URLs without fetching full content.
        
        Args:
            start_url: Starting URL
            
        Returns:
            List of discovered URLs
        """
        results = self.crawl(start_url)
        return [r['url'] for r in results]
