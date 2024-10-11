# requests is module to fetch web pages
# BeautifulSoup is module for parsing html and extracting the links
# urljoin & urlparse ensure the crawler works correctly with both absolute and relative URLs
# time is used for time delay between requests to avoid overwhelming the server
# re for filtering links
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import re


# ==================== WebCrawler class ======================= #
class WebCrawler:
    def __init__(self, base_url, max_depth=3, delay=1):
        self.base_url = base_url  # starting url for the crawl
        self.visited_urls = (
            set()
        )  # set to store urls that have been crawled to avoid repeated requests
        self.max_depth = max_depth  # The maximum depth the crawler should go. This helps in limiting the number of recursive calls.
        self.delay = delay  # Time delay between requests to prevent the crawler from making too many requests too quickly
        self.valid_urls = []  # List of successfully crawled URLs
        self.invalid_urls = []  # List of URLs that failed to load

    def fetch_page(self, url):
        try:  # for the success case
            response = requests.get(
                url, timeout=5
            )  # use get method to fetch the page content within 5 seconds else time out
            response.raise_for_status()  # method to check the status code of the request so that if the status code represent an error the code won't continue executing
            return (
                response.text
            )  # .text returns the content of the web page as a string
        except requests.exceptions.RequestException as e:  # for the fail case
            print(f"Failed to fetch {url}: {e}")
            self.invalid_urls.append(
                url
            )  # insert the invalid url that cause the exeption in the invalid urls list
            return None
    # this function is designed to extract all anchor tags of the fetched page and checks whether they belong to the same domain as the base URL
    def parse_links(self, html, current_url):
        soup = BeautifulSoup(
            html, "html.parser"
        )  # to parse html document or string of html content making it easy to extract specific elements
        links = set()  # set to store the links "anchor <a> tags" , Note that the set data structure is used to avoid duplecates
        for tag in soup.find_all("a", href=True):
            href = tag.get("href")
            href = urljoin(current_url, href)  # Handle relative URLs to join it to the current_url wich is the url of the page wich we get the html content from
            parsed_href = urlparse(href) # This breaks down the URL into its components (scheme, netloc, path, etc.), allowing easy access to different parts of the URL.
            if parsed_href.scheme in ["http", "https"]: # Filter out non-HTTP/HTTPS links and ensure they're not pointing to external domains
                clean_href = (
                    # "http or https"            # "domain name"
                    parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
                )
                # check if the clean_href not already visited and the domain name of it is the same domain name as the base url
                if clean_href not in self.visited_urls and self.is_same_domain(
                    clean_href
                ):
                    links.add(clean_href)
        return links
    
    # function to check if domain name of the url given is the same domain name as the base url
    def is_same_domain(self, url):
        return urlparse(self.base_url).netloc == urlparse(url).netloc
    # The core recursive function. It takes a URL and crawls all links found on the page up to the specified max_depth. At each step
    def crawl(self, url=None, depth=0):
        # check if the depth given to crawl function is not greater than the max depth to stop the recursave calls
        if depth > self.max_depth:
            return
        # check if there is no url given . if so , then we make it the base url as a default value 
        if url is None:
            url = self.base_url
        # check if the url given is already visited or not
        if url in self.visited_urls:
            return
        # if the url and depth pass the previous checks then the crawling starts
        print(f"Crawling: {url} at depth {depth}")
        # calling the fetch page function then check if there is no result returned the function terimenates
        html = self.fetch_page(url)
        if html is None:
            return

        self.visited_urls.add(url)
        self.valid_urls.append(url)
        # calling the parse links function and pass to it the html content and the url
        links = self.parse_links(html, url)

        # Recursive crawling of the fetched links
        for link in links:
            time.sleep(self.delay)  # Delay to avoid overwhelming the server
            self.crawl(link, depth + 1) # crawling for each link to get relative links in deffret layer

    # function to call crawl function and start crawling
    def start_crawl(self):
        print(f"Starting crawl at: {self.base_url}")
        self.crawl()
    # function to return both lists , valid urls and invalid urls
    def get_results(self):
        return {"valid_urls": self.valid_urls, "invalid_urls": self.invalid_urls}



from crawler import WebCrawler



if __name__ == "__main__":
    base_url = "http://www.itsecgames.com"
    crawler = WebCrawler(base_url, max_depth=3, delay=1)
    crawler.start_crawl()
    results = crawler.get_results()

    print("\nValid URLs:")
    for url in results["valid_urls"]:
        print(url)

    print("\nInvalid URLs:")
    for url in results["invalid_urls"]:
        print(url)
