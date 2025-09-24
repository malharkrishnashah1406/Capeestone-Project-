import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict, Any
from datetime import datetime
import random
from fake_useragent import UserAgent
from config.config import SCRAPING_CONFIG, SCRAPING_SOURCES

class WebScraper:
    def __init__(self):
        self.rate_limit = SCRAPING_CONFIG["rate_limit"]
        self.timeout = SCRAPING_CONFIG["timeout"]
        self.max_retries = SCRAPING_CONFIG["max_retries"]
        self.ua = UserAgent()

    def get_random_user_agent(self) -> str:
        """Get a random user agent to avoid detection"""
        return self.ua.random

    def make_request(self, url: str) -> requests.Response:
        """Make a request with rate limiting and retries"""
        headers = {
            "User-Agent": self.get_random_user_agent()
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    url,
                    headers=headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                time.sleep(1 / self.rate_limit)  # Rate limiting
                return response
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise e
                time.sleep(2 ** attempt)  # Exponential backoff

    def scrape_government_news(self) -> List[Dict[str, Any]]:
        """Scrape news from government websites"""
        articles = []
        for url in SCRAPING_SOURCES["government"]:
            try:
                response = self.make_request(url)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Example for RBI website
                if "rbi.org.in" in url:
                    news_items = soup.find_all('div', class_='news-item')
                    for item in news_items:
                        title = item.find('h3').text.strip()
                        link = url + item.find('a')['href']
                        date = item.find('span', class_='date').text.strip()
                        
                        articles.append({
                            "title": title,
                            "url": link,
                            "published_at": date,
                            "source": "RBI",
                            "content": self.scrape_article_content(link)
                        })
                
                # Add similar logic for other government websites
                
            except Exception as e:
                print(f"Error scraping {url}: {e}")
        
        return articles

    def scrape_startup_news(self) -> List[Dict[str, Any]]:
        """Scrape news from startup news websites"""
        articles = []
        for url in SCRAPING_SOURCES["startup_news"]:
            try:
                response = self.make_request(url)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Example for Inc42
                if "inc42.com" in url:
                    news_items = soup.find_all('article')
                    for item in news_items:
                        title = item.find('h2').text.strip()
                        link = item.find('a')['href']
                        date = item.find('time')['datetime']
                        
                        articles.append({
                            "title": title,
                            "url": link,
                            "published_at": date,
                            "source": "Inc42",
                            "content": self.scrape_article_content(link)
                        })
                
                # Add similar logic for other startup news websites
                
            except Exception as e:
                print(f"Error scraping {url}: {e}")
        
        return articles

    def scrape_financial_news(self) -> List[Dict[str, Any]]:
        """Scrape news from financial news websites"""
        articles = []
        for url in SCRAPING_SOURCES["financial_news"]:
            try:
                response = self.make_request(url)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Example for MoneyControl
                if "moneycontrol.com" in url:
                    news_items = soup.find_all('li', class_='clearfix')
                    for item in news_items:
                        title = item.find('h2').text.strip()
                        link = item.find('a')['href']
                        date = item.find('span', class_='date').text.strip()
                        
                        articles.append({
                            "title": title,
                            "url": link,
                            "published_at": date,
                            "source": "MoneyControl",
                            "content": self.scrape_article_content(link)
                        })
                
                # Add similar logic for other financial news websites
                
            except Exception as e:
                print(f"Error scraping {url}: {e}")
        
        return articles

    def scrape_article_content(self, url: str) -> str:
        """Scrape the content of a specific article"""
        try:
            response = self.make_request(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Different selectors for different websites
            if "moneycontrol.com" in url:
                content = soup.find('div', class_='article_content')
            elif "inc42.com" in url:
                content = soup.find('div', class_='entry-content')
            else:
                content = soup.find('article') or soup.find('div', class_='content')
            
            return content.get_text(strip=True) if content else ""
        except Exception as e:
            print(f"Error scraping article content from {url}: {e}")
            return ""

    def scrape_all_news(self) -> List[Dict[str, Any]]:
        """Scrape news from all sources"""
        all_articles = []
        
        # Scrape from different sources
        all_articles.extend(self.scrape_government_news())
        all_articles.extend(self.scrape_startup_news())
        all_articles.extend(self.scrape_financial_news())
        
        return all_articles 