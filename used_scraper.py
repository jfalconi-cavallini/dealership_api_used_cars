import requests
from bs4 import BeautifulSoup
import json
import re

def save_cars_to_file(cars, filename='used_scraped_cars.json'):
    with open(filename, 'w') as f:
        json.dump(cars, f, indent=4)

def parse_price(price_str):
    try:
        return float(price_str.replace('$', '').replace(',', '').strip())
    except:
        return 0.0

def scrape_inventory_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; CarInventoryScraper/1.0)'
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve page: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    cars = []
    seen_links = set()  # avoid duplicates

    # iterate "div.elementor-widget-wrap" blocks
    car_blocks = soup.select('div.elementor-widget-wrap')

    for block in car_blocks:
        # Same selector for the two H2 links inside each block
        a_tags = block.select('h2.elementor-heading-title a')
        if len(a_tags) >= 2:
            year_make = a_tags[0].get_text(strip=True)
            model = a_tags[1].get_text(strip=True)
            link = a_tags[0]['href']

            if link in seen_links:
                continue
            seen_links.add(link)

            # Used SRP starts with "Used "
            if year_make.startswith("Used "):
                year_make = year_make[len("Used "):]

            parts = year_make.split(' ', 1)
            year = parts[0] if len(parts) > 0 else ''
            make = parts[1] if len(parts) > 1 else ''

            # scan the same class of <p> tags inside the block and grab the one that starts with "VIN:"
            vin = ''
            info_ps = block.select('div.elementor-widget-container > p.elementor-heading-title.elementor-size-default')
            if info_ps:
                for p_tag in info_ps:
                    text = p_tag.get_text(strip=True)
                    # On used pages, VIN is one clean line like "VIN: 1C3CDZAB5CN110236"
                    if text.startswith("VIN:"):
                        vin = text.replace("VIN:", "").strip()
                        break

            # If VIN still missing, parse it from the URL (/vehicle/<VIN>/...)
            if not vin:
                m = re.search(r'/vehicle/([A-HJ-NPR-Z0-9]{11,17})/', link, flags=re.I)
                if m:
                    vin = m.group(1)

            # Image handling :tries data-auto5-image, then <img src>
            img_div = block.select_one('div.elementor-image')
            if img_div and img_div.has_attr('data-auto5-image'):
                image_url = img_div['data-auto5-image']
                if image_url.startswith('//'):
                    image_url = 'https:' + image_url
            else:
                img_tag = block.select_one('div.elementor-image img')
                if img_tag:
                    image_url = img_tag.get('src')
                    if image_url and image_url.startswith('//'):
                        image_url = 'https:' + image_url
                else:
                    image_url = None

            # Price
            msrp_price = 0.0
            text_block = block.get_text(" ", strip=True)
            m_price = re.search(r'\$[\d,]+(?:\.\d{2})?', text_block)
            if m_price:
                msrp_price = parse_price(m_price.group(0))

            cars.append({
                'condition': 'Used',
                'year': year,
                'make': make,
                'model': model,
                'vin': vin,
                'link': link,
                'image_url': image_url,
                'price': msrp_price
            })

    return cars

def get_total_pages(url):
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; CarInventoryScraper/1.0)'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve page: {response.status_code}")
        return 1

    soup = BeautifulSoup(response.text, 'html.parser')

    pager_div = soup.find('div', class_='pager-body pager-body-full', attrs={'data-event': 'click_pagination'})

    if not pager_div:
        print("Pagination div not found, assuming 1 page")
        return 1

    page_numbers = []
    for a_tag in pager_div.find_all('a'):
        text = a_tag.get_text(strip=True)
        if text.isdigit():
            page_numbers.append(int(text))

    return max(page_numbers) if page_numbers else 1

def scrape_all_used_cars(base_url):
    total_pages = 10  # get_total_pages(base_url)
    print(f"Total pages found: {total_pages}")

    all_cars = []
    for page_num in range(1, total_pages + 1):
        url = base_url if page_num == 1 else f"{base_url}srp-page-{page_num}/"
        print(f"Scraping page {page_num}: {url}")
        cars = scrape_inventory_page(url)
        all_cars.extend(cars)

    return all_cars

def scrape_and_save():
    """Run the scraper and save results to scraped_cars.json (same filename pattern)"""
    base_url = 'https://www.claycooley.com/inventory/used-vehicles/'
    all_used_cars = scrape_all_used_cars(base_url)
    print(f"Total used cars scraped: {len(all_used_cars)}")
    save_cars_to_file(all_used_cars)
    return all_used_cars

if __name__ == "__main__":
    scrape_and_save()
