import requests
from bs4 import BeautifulSoup
import sys
import csv
from urllib.parse import urlparse, urljoin

def extract_urls_from_xml(xml_url):
    """
    Extract all the URLs from the given XML file.
    """
    urls = []
    response = requests.get(xml_url)
    
    if response.status_code != 200:
        print(f"Failed to fetch {xml_url}. HTTP status code: {response.status_code}")
        return urls

    soup = BeautifulSoup(response.content, 'xml')
    
    for link in soup.find_all('xhtml:link', rel="alternate"):
        url = link.get('href')
        if url:
            urls.append(url)
    return urls

def extract_links_from_url(url):
    """
    Extract internal and external links from the given URL.
    """
    internal_links = set()
    external_links = set()
    
    domain = urlparse(url).netloc
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Failed to fetch {url}. HTTP status code: {response.status_code}")
        return internal_links, external_links

    soup = BeautifulSoup(response.content, 'html.parser')
    
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        
        # Exclude links pointing to images
        if href.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp')):
            continue
        
        absolute_url = urljoin(url, href)
        
        if domain in urlparse(absolute_url).netloc:
            internal_links.add(absolute_url)
        else:
            external_links.add(absolute_url)

    return internal_links, external_links

def save_to_csv(urls):
    """
    Visit each URL, check the HTTP response code, extract internal and external links, 
    and save the URLs and response codes to a CSV file.
    """
    with open("URLs.csv", "w", newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["URL", "Response", "Internal Links", "External Links"])
        
        for url in urls:
            try:
                response = requests.get(url)
                print(f"{url} - {response.status_code}")
                
                internal_links, external_links = extract_links_from_url(url)
                
                csvwriter.writerow([
                    url, 
                    response.status_code, 
                    "\n".join(internal_links), 
                    "\n".join(external_links)
                ])
            except requests.RequestException as e:
                print(f"{url} - Error: {e}")
                csvwriter.writerow([url, "Error", "", ""])

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scraper.py <xml_url>")
        sys.exit(1)

    xml_url = sys.argv[1]
    urls = extract_urls_from_xml(xml_url)
    save_to_csv(urls)
