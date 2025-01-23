import os
import csv
import time
import requests
import random
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from tkinter import Tk, Label, Button, filedialog, StringVar, ttk

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64)...Chrome/87.0.4280.88 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64)...Chrome/88.0.4324.96 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6)...'
]

def scrape_url(url, image_folder, retry_attempts=3):
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    for _ in range(retry_attempts):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            name_tag = soup.find('div', {'class': 'product-title-container'})
            name = name_tag.find('h1').text.strip() if name_tag and name_tag.find('h1') else "Unknown Name"

            price_tag = soup.find('div', {'class': 'price'})
            if price_tag:
                price_strong = price_tag.find('strong') 
                price = price_strong.text.strip() if price_strong else "Unknown Price"
            else:
                price = "Unknown Price"
            
            image_tag = soup.find('div', {'class': 'id-relative id-h-full id-w-full'})
            image_url = None
            if image_tag:
                image_tag = image_tag.find('img')
                if image_tag and 'src' in image_tag.attrs:
                    image_url = image_tag['src']
                    if image_url.startswith('//'):
                        image_url = 'https:' + image_url
            
            if image_url:
                image_data = requests.get(image_url).content
                image_name = os.path.join(image_folder, os.path.basename(image_url))
                with open(image_name, 'wb') as img_file:
                    img_file.write(image_data)
            else:
                image_name = None

            return {'Name': name, 'Price': price, 'Image': image_name}
        except requests.RequestException as e:
            print(f"Error scraping {url}: {e}")
            time.sleep(random.uniform(1, 5))
    return None


def update_progress_bar(progress_bar, current, total, root):
    progress_bar['value'] = (current / total) * 100
    root.update_idletasks()

def parallel_scrape(urls, image_folder, progress_bar, root):
    results = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_url = {executor.submit(scrape_url, url, image_folder): url for url in urls}
        for i, future in enumerate(future_to_url):
            result = future.result()
            if result:
                results.append(result)
            update_progress_bar(progress_bar, i + 1, len(urls), root)
            print(f"Scraped {i+1}/{len(urls)} URLs.")
    return results

def sequential_scrape(urls, image_folder, progress_bar, root):
    results = []
    for i, url in enumerate(urls):
        result = scrape_url(url, image_folder)
        if result:
            results.append(result)
        update_progress_bar(progress_bar, i + 1, len(urls), root)
        print(f"Scraped {i+1}/{len(urls)} URLs.")
    return results

def save_to_csv(data, output_file):
    keys = ['Name', 'Price', 'Image']
    with open(output_file, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

def main():
    def select_file():
        file_path.set(filedialog.askopenfilename(filetypes=[("Text files", "*.txt")]))

    def start_scraping(parallel):
        input_file = file_path.get()
        if not input_file:
            status_label.config(text="Please select a file.")
            return

        with open(input_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]

        image_folder = os.path.join(os.getcwd(), 'images')
        os.makedirs(image_folder, exist_ok=True)

        start_time = time.time()
        progress_bar['value'] = 0

        if parallel:
            results = parallel_scrape(urls, image_folder, progress_bar, root)
        else:
            results = sequential_scrape(urls, image_folder, progress_bar, root)

        end_time = time.time()

        output_file = os.path.join(os.getcwd(), 'scraped_data.csv')
        save_to_csv(results, output_file)

        status_label.config(text=f"Scraping completed in {end_time - start_time:.2f} seconds. Data saved to scraped_data.csv.")

    def copy_to_file():
        url = "https://www.alibaba.com/product-detail/Wholesale-2022-Qatar-Soccer-Ball-Football_1600786777613.html"
        with open("urls.txt", "w") as file:
            file.write(url)
        status_label.config(text="URL copied to urls.txt.")

    root = Tk()
    root.title("Web Scraper")

    file_path = StringVar()

    Label(root, text="Select a file with URLs:").pack(pady=5)
    Button(root, text="Browse", command=select_file).pack(pady=5)

    Button(root, text="Parallel Scraping", command=lambda: start_scraping(True)).pack(pady=5)
    Button(root, text="Sequential Scraping", command=lambda: start_scraping(False)).pack(pady=5)
    
    Button(root, text="Copy URL to File", command=copy_to_file).pack(pady=5)

    progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
    progress_bar.pack(pady=10)

    status_label = Label(root, text="", fg="green")
    status_label.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
