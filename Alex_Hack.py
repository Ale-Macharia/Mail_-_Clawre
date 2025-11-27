from bs4 import BeautifulSoup
import requests
import urllib.parse
from collections import deque
import re 

user_url = str(input('[+] Enter Target URL To Scan : '))
urls = deque([user_url])

scraped_urls = set()
emails = set()

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"
}

# improved email regex (captures .co.ke and uppercase TLDs)
email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,10}"

count = 0

try:
    while len(urls):
        count += 1
        if count == 100:
            break

        url = urls.popleft()
        scraped_urls.add(url)

        parts = urllib.parse.urlsplit(url) 
        base_url = "{}://{}".format(parts.scheme, parts.netloc)
        path = url[:url.rfind('/')+1] if '/' in parts.path else url     

        print('[%d] Processing %s ' % (count, url))

        try:
            response = requests.get(url, headers=headers, timeout=5)
        except (requests.exceptions.MissingSchema, 
                requests.exceptions.ConnectionError):
            continue

        # extract emails
        new_emails = set(re.findall(email_pattern, response.text))
        emails.update(new_emails)

        soup = BeautifulSoup(response.text, 'lxml')

        for anchor in soup.find_all('a'):
            link = anchor.get('href', '')

            # ignore empty, JS or mailto links
            if link.startswith("javascript") or link.startswith("#") or link.startswith("mailto"):
                continue

            if link.startswith('/'):
                link = base_url + link
            elif not link.startswith('http'):
                link = path + link

            if link.startswith('http') and link not in scraped_urls and link not in urls:
                urls.append(link)

except KeyboardInterrupt:
    print('[-] Closing !')

print("\n[+] Emails Found:")
for mail in emails:
    print(mail)
