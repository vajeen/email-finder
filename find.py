import requests
from bs4 import BeautifulSoup
import re
import time
from duckduckgo_search import DDGS
from urllib.parse import urljoin


def duckduckgo_search(query):
    results = DDGS().text(query, region='eu-eu', safesearch='on', timelimit='y', max_results=50)
    links = [result['href'] for result in results]
    filtered_links = []
    for link in links:
        if not 'youtube' in link:
            filtered_links.append(link)
        if len(filtered_links) == 10:
            break
    return filtered_links


def find_emails_in_page(url):
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        email_regex = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'

        text_with_linebreaks = soup.get_text(separator='\n')
        emails = set(re.findall(email_regex, text_with_linebreaks))

        contact_links = []
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            if 'contact' in href:
                contact_url = urljoin(url, link['href'])
                contact_links.append(contact_url)

        # Scrape each contact page for emails
        for contact_url in contact_links:
            try:
                contact_response = requests.get(contact_url, headers=headers, timeout=10)
                contact_soup = BeautifulSoup(contact_response.text, 'html.parser')

                contact_text_with_linebreaks = contact_soup.get_text(separator='\n')
                emails.update(re.findall(email_regex, contact_text_with_linebreaks))
            except requests.RequestException:
                continue

        # Clean up
        cleaned_emails = {email.strip() for email in emails}

        return cleaned_emails
    except requests.RequestException:
        return set()


def find_emails_for_company(company_name):
    search_results = duckduckgo_search(company_name)
    print("Links:")
    for i in search_results:
        print(i)
    print("")

    emails_found = set()
    for url in search_results:
        print(url)
        email_list = find_emails_in_page(url)
        emails_found.update(email_list)
        if email_list:
            print("  Email")
            for i in email_list:
                print(f"  {i}")
            print("")
        else:
            print("  Not found")
            print("")
        time.sleep(1)
    return list(emails_found)


def main():
    company_name = input("Enter the company name: ")
    emails = find_emails_for_company(company_name.replace(" ","+"))
    if emails:
        print("All emails")
        for i in emails:
            print(i)


if __name__ == "__main__":
    main()
