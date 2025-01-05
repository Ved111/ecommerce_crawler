import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class ProductURLCrawler:
    def __init__(self, domains, max_depth=2):
        self.domains = domains
        self.max_depth = max_depth
        self.results = {domain: [] for domain in domains}
        self.visited = {domain: set() for domain in domains}

    def is_product_url(self, url):
        # Enhanced pattern matching for product URLs
        return any(keyword in url.lower() for keyword in ["product", "item", "detail", "shop"])

    async def fetch(self, session, url):
        """Fetch content from a URL."""
        print(f"Fetching URL: {url}")
        try:
            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    print(f"Failed to fetch {url} with status code {response.status}")
                    return None
                return await response.text()
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    async def crawl(self, domain, url, depth, session):
        """Recursively crawl the website for product URLs."""
        if depth > self.max_depth or url in self.visited[domain]:
            return

        # Mark the URL as visited
        self.visited[domain].add(url)

        # Fetch the page content
        html = await self.fetch(session, url)
        if not html:
            return

        soup = BeautifulSoup(html, 'html.parser')

        # Process all links on the page
        for link in soup.find_all("a", href=True):
            full_url = urljoin(url, link["href"])
            parsed_url = urlparse(full_url)
            # Skip external links (e.g., links pointing to other domains)
            if parsed_url.netloc and parsed_url.netloc != urlparse(domain).netloc:
                continue

            # Normalize the URL and check if it's a product URL
            normalized_url = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path
            if self.is_product_url(normalized_url):
                print(f"Found product URL: {normalized_url}")
                self.results[domain].append(normalized_url)

            # Recurse to the next level of depth
            await self.crawl(domain, normalized_url, depth + 1, session)

    async def start_crawling(self):
        """Start the crawling process for each domain."""
        print("Starting crawl for domains:", self.domains)
        async with aiohttp.ClientSession() as session:
            tasks = []
            for domain in self.domains:
                tasks.append(self.crawl(domain, domain, 0, session))

            # Run all crawl tasks concurrently
            await asyncio.gather(*tasks)
        print("Crawl completed. Results:", self.results)
        return self.results
