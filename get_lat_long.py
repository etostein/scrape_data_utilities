from bs4 import BeautifulSoup
import requests
import csv
import time
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
} 

site_ids = []
with open('site_ids.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader)  
    for row in reader:
        #add leading zeros to make sure siteid is 14 characters long
        siteid = row[0].strip().zfill(13)
        site_ids.append(siteid)

print(f"Loaded {len(site_ids)} site IDs: {site_ids}") 

for siteid in site_ids:
    print(f"\nProcessing: '{siteid}' (length: {len(siteid)})") 
    try:
        page_to_scrape =requests.get(f"https://www.unetgrid.com/sitecatalog/catalogmanager?doaction=servlet&jobtype=SiteCatalogDetail&siteid={siteid}",
                                    headers=headers)
        print(f"Status: {page_to_scrape.status_code}") 
        soup = BeautifulSoup(page_to_scrape.content, 'html.parser') 
        quotes = soup.find_all('td',attrs={'width':'20%'})
        title = soup.find_all('th', attrs={'width':'20%'})
        address= soup.find_all('td', attrs={'width':'10%'})

        print(f"Found {len(quotes)} quote fields, {len(address)} address fields")

        siteid_i = quotes[0].text.strip()
        latitude = quotes[3].text.strip()
        longitude = quotes[4].text.strip()

        house_number = address[11].text.strip()
        street_name = address[13].text.strip()
        street_code = address[14].text.strip()
        city = address[17].text.strip()
        province = address[18].text.strip()
        full_Address = house_number + " " + street_name + " " + street_code + " " + city + " " + province


        print(f"Site ID: {siteid_i}, Lat: {latitude}, Long: {longitude}, Address: {full_Address}")

    except Exception as e:
        print(f"✗ Error with {siteid}: {e}")
    time.sleep(0.5)
