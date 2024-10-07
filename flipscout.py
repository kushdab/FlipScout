import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Amazon Product Advertising API keys (replace with your own)
AMAZON_API_KEY = 'your_amazon_api_key'
AMAZON_API_SECRET = 'your_amazon_secret_key'
AMAZON_ASSOCIATE_TAG = 'your_associate_tag'

# eBay Scraper
def scrape_ebay(min_discount=20):
    url = f"https://www.ebay.com/sch/i.html?_nkw=discount+items&_sop=15"  # Sort by best deals or sales
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.70 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    ebay_items = []
    for item in soup.find_all('li', class_='s-item'):
        title = item.find('h3', class_='s-item__title').get_text(strip=True)
        price = float(item.find('span', class_='s-item__price').get_text(strip=True).replace('$', '').replace(',', ''))
        discount_tag = item.find('span', class_='s-item__discount')
        
        if discount_tag:
            discount_percent = int(discount_tag.get_text(strip=True).replace('%', '').replace('OFF', ''))
            if discount_percent >= min_discount:
                ebay_items.append({'title': title, 'price': price, 'discount': discount_percent})
    
    return ebay_items

# Search Amazon for same items
def search_amazon(item_title):
    search_url = f"https://www.amazon.com/s?k={item_title.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.70 Safari/537.36"
    }
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    amazon_items = []
    for result in soup.find_all('div', class_='s-result-item'):
        title = result.find('span', class_='a-text-normal')
        price_whole = result.find('span', class_='a-price-whole')
        price_fraction = result.find('span', class_='a-price-fraction')
        
        if title and price_whole and price_fraction:
            price = float(price_whole.get_text(strip=True) + price_fraction.get_text(strip=True))
            amazon_items.append({'title': title.get_text(strip=True), 'price': price})
    
    return amazon_items

# Compare eBay and Amazon prices for profit potential
def compare_prices(ebay_items):
    profitable_items = []
    
    for ebay_item in ebay_items:
        amazon_items = search_amazon(ebay_item['title'])
        
        if amazon_items:
            # Compare first matching item on Amazon
            amazon_item = amazon_items[0]
            if amazon_item['price'] > ebay_item['price'] * 1.2:  # 20% margin
                profit = amazon_item['price'] - ebay_item['price']
                profitable_items.append({
                    'ebay_title': ebay_item['title'],
                    'ebay_price': ebay_item['price'],
                    'amazon_price': amazon_item['price'],
                    'profit': profit
                })
    
    return profitable_items

# Main Execution
if __name__ == "__main__":
    ebay_items = scrape_ebay(min_discount=20)
    print("Found items on eBay with 20%+ discount:")
    for item in ebay_items:
        print(f"Title: {item['title']}, Price: ${item['price']}, Discount: {item['discount']}%")

    profitable_items = compare_prices(ebay_items)
    
    print("\nItems that can be sold profitably on Amazon:")
    for item in profitable_items:
        print(f"eBay Title: {item['ebay_title']}, eBay Price: ${item['ebay_price']}, Amazon Price: ${item['amazon_price']}, Profit: ${item['profit']}")
