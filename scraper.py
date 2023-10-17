import requests
from bs4 import BeautifulSoup
import sys
import csv

def extract_urls_from_xml(xml_url):
    """
    Extract all the URLs from the given XML file that match the specified pattern.
    """
    urls = []
    response = requests.get(xml_url)
    
    # Check if request was successful
    if response.status_code != 200:
        print(f"Failed to fetch {xml_url}. HTTP status code: {response.status_code}")
        return urls

    soup = BeautifulSoup(response.content, 'xml')
    
    # Extract URLs with the given pattern
    for link in soup.find_all('xhtml:link', rel="alternate"):
        url = link.get('href')
        if url:
            urls.append(url)
    return urls

def check_url_response_and_save_to_csv(urls):
    """
    Visit each URL, check the HTTP response code, and save the URLs and response codes to a CSV file.
    """
    with open("URLs.csv", "w", newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["URL", "Response"])  # CSV header

        for url in urls:
            try:
                response = requests.get(url)
                print(f"{url} - {response.status_code}")
                csvwriter.writerow([url, response.status_code])
            except requests.RequestException as e:
                print(f"{url} - Error: {e}")
                csvwriter.writerow([url, "Error"])

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scraper.py <xml_url>")
        sys.exit(1)

    xml_url = sys.argv[1]
    urls = extract_urls_from_xml(xml_url)
    check_url_response_and_save_to_csv(urls)
