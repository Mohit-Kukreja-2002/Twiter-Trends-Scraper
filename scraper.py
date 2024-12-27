from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import os
from dotenv import load_dotenv
import random
import requests
import time
from bs4 import BeautifulSoup
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

class TwitterScraper:
    def __init__(self):
        self.username = os.getenv('TWITTER_USERNAME')
        self.password = os.getenv('TWITTER_PASSWORD')
        self.proxymesh_username = os.getenv('PROXYMESH_USERNAME')
        self.proxymesh_password = os.getenv('PROXYMESH_PASSWORD')

    def get_proxy(self):
        try:
            # Get proxy settings from env
            max_retries = int(os.getenv('PROXY_MAX_RETRIES', 3))
            timeout = int(os.getenv('PROXY_TIMEOUT', 30))
            min_uptime = float(os.getenv('PROXY_MIN_UPTIME', 95))
            max_latency = int(os.getenv('PROXY_MAX_LATENCY', 500))
            
            # Try Bright Data first
            bright_proxy = self.get_bright_data_proxy()
            if bright_proxy:
                return bright_proxy
            
            # Fallback to Scrape.do
            scrape_do_proxy = self.get_scrape_do_proxy()
            if scrape_do_proxy:
                return scrape_do_proxy
            
            return None
            
        except Exception as e:
            print(f"Error setting up proxy: {str(e)}")
            return None

    def get_bright_data_proxy(self):
        try:
            username = os.getenv('BRIGHT_DATA_USERNAME')
            password = os.getenv('BRIGHT_DATA_PASSWORD')
            host = os.getenv('BRIGHT_DATA_HOST')
            port = os.getenv('BRIGHT_DATA_PORT')
            
            if not all([username, password, host, port]):
                return None
            
            proxy_url = f"http://{username}:{password}@{host}:{port}"
            
            # Test the proxy
            response = requests.get(
                'http://httpbin.org/ip',
                proxies={'http': proxy_url, 'https': proxy_url},
                timeout=int(os.getenv('PROXY_TIMEOUT', 30)),
                verify=False
            )
            
            if response.status_code == 200:
                print(f"Using Bright Data proxy")
                return proxy_url
            
        except Exception as e:
            print(f"Bright Data proxy failed: {str(e)}")
        return None

    def get_scrape_do_proxy(self):
        try:
            api_key = os.getenv('SCRAPE_DO_API_KEY')
            if not api_key:
                return None
            
            proxy_url = f"http://{api_key}@proxy.scrape.do:8080"
            
            # Test the proxy
            response = requests.get(
                'http://httpbin.org/ip',
                proxies={'http': proxy_url, 'https': proxy_url},
                timeout=int(os.getenv('PROXY_TIMEOUT', 30)),
                verify=False
            )
            
            if response.status_code == 200:
                print(f"Using Scrape.do proxy")
                return proxy_url
            
        except Exception as e:
            print(f"Scrape.do proxy failed: {str(e)}")
        return None

    def get_url_through_scrape_do(self, url):
        """Helper method to get URLs through Scrape.do API"""
        api_url = f"http://api.scrape.do?token={self.api_key}&url={url}"
        response = requests.get(api_url)
        return response.text

    def setup_driver(self):
        chrome_options = webdriver.ChromeOptions()
        
        # Essential Chrome Options
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Remove or comment out these lines to see the browser
        # chrome_options.add_argument('--headless=new')
        # chrome_options.add_argument('--disable-javascript')
        # chrome_options.add_argument('--disable-gpu')
        # chrome_options.add_argument('--disable-extensions')
        # chrome_options.add_argument('--disable-infobars')
        # chrome_options.add_argument('--block-new-web-contents')
        
        # Remove performance preferences that might affect visibility
        # chrome_options.add_experimental_option('prefs', {
        #     'profile.default_content_setting_values': {
        #         'images': 2,
        #         'javascript': 2,
        #         'cookies': 2,
        #         'plugins': 2,
        #         'popups': 2
        #     },
        #     'disk-cache-size': 4096
        # })
        
        # Get proxy
        proxy = self.get_proxy()
        proxy_used = "Direct Connection"
        
        if proxy:
            print(f"Using proxy: {proxy}")
            chrome_options.add_argument(f'--proxy-server={proxy}')
            proxy_used = proxy.split('://')[1] if '://' in proxy else proxy
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Set timeouts
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        
        return driver, proxy_used

    def login_twitter(self, driver):
        try:
            print("Logging in to Twitter...")
            driver.get('https://x.com/login')
            time.sleep(3)  # Wait for page load
            
            print("Entering username...")
            username_field = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "text"))
            )
            username_field.send_keys(self.username)
            time.sleep(1)
            
            print("Clicking next...")
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']"))
            )
            next_button.click()
            time.sleep(2)
            
            print("Entering password...")
            password_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            password_field.send_keys(self.password)
            time.sleep(1)
            
            print("Clicking login button...")
            login_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Log in']"))
            )
            login_button.click()
            time.sleep(5)  # Wait for login to complete
            
            print("Login successful")
            return True
            
        except Exception as e:
            print(f"Login failed: {str(e)}")
            if driver:
                driver.save_screenshot("login_error.png")
            return False

    def get_trending_topics_with_login(self):
        driver = None
        try:
            # Get driver and proxy info
            driver, proxy_used = self.setup_driver()
            
            # First login
            if not self.login_twitter(driver):
                raise Exception("Failed to login")
            
            # Then get trending topics
            print("Navigating to explore page...")
            driver.get('https://x.com/explore')
            
            print("Waiting for trending section...")
            trend_items = WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-testid='trend']"))
            )
            
            trends = []
            for item in trend_items:
                try:
                    # Get all text elements within the trend
                    all_spans = item.find_elements(By.CSS_SELECTOR, "span")
                    
                    # Find the actual trend text (usually the largest text that's not metadata)
                    for span in all_spans:
                        text = span.text.strip()
                        # Skip metadata text
                        if (text and 
                            not text.startswith("Trending") and 
                            not text.endswith("Trending") and
                            not text.startswith("·") and
                            not "K Tweets" in text and
                            not "M Tweets" in text):
                            trends.append(text)
                            print(f"Found trend: {text}")
                            break
                    
                    if len(trends) >= 5:  # Stop after getting 5 trends
                        break
                        
                except Exception as e:
                    print(f"Error getting trend text: {str(e)}")
                    continue
            
            # Fill remaining slots if needed
            while len(trends) < 5:
                trends.append("N/A")
            
            return {
                'trends': trends[:5],
                'timestamp': datetime.now(),
                'proxy_ip': proxy_used
            }
            
        except Exception as e:
            print(f"Error in get_trending_topics: {str(e)}")
            if driver:
                driver.save_screenshot("error.png")
            raise
            
        finally:
            if driver:
                driver.quit() 