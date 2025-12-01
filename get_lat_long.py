from bs4 import BeautifulSoup
import requests


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
} 

siteid= "0040211092001" 
page_to_scrape =requests.get(f"https://www.unetgrid.com/sitecatalog/catalogmanager?doaction=servlet&jobtype=SiteCatalogDetail&siteid={siteid}",
                             headers=headers)
soup = BeautifulSoup(page_to_scrape.content, 'html.parser') 
quotes = soup.find_all('td',attrs={'width':'20%'})
title = soup.find_all('th', attrs={'width':'20%'})

address= soup.find_all('td', attrs={'width':'10%'})

siteid_i = quotes[0].text.strip()
latitude = quotes[3].text.strip()
longitude = quotes[4].text.strip()

house_number = address[11].text.strip()
street_name = address[13].text.strip()
street_code = address[14].text.strip()
city = address[17].text.strip()
province = address[18].text.strip()
full_Address = house_number + " " + street_name + " " + street_code + " " + city + " " + province

print("Site ID:", siteid_i)
print("Latitude:", latitude)
print("Longitude:", longitude)
print("Full Address:", full_Address)


