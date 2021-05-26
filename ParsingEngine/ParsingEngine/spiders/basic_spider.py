import scrapy
from w3lib.html import remove_tags
from pathlib import Path
from datetime import datetime
import locale
import requests


locale.setlocale(locale.LC_ALL, "ru_RU")


class BasicSpider(scrapy.Spider):
    name = 'basic'
    # allowed_domains = ['https://xn--90adear.xn--p1ai/r/65']
    start_urls = ['https://xn--90adear.xn--p1ai/r/65']

    gibdd_sakhalin_region_news_selector = "body div.folder-homepage div.active"

    regional_news_request_url = f"{start_urls[0][:-5]}/news/regional?perPage=4&page=1&region=65"

    regional_news_request_headers = {
        "authority": "xn--90adear.xn--p1ai",
        "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"90\", \"Google Chrome\";v=\"90\"",
        "x-requested-with": "xmlhttprequest",
        "sec-ch-ua-mobile": "?0",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
        "accept": "*/*",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://xn--90adear.xn--p1ai/r/65/",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    def parse(self, response):
        news_div = response.css(self.gibdd_sakhalin_region_news_selector)

        home_news = list(self.parse_home_news_div(news_div.css("div.home-news")))

        response = requests.get(url=self.regional_news_request_url,
                                headers=self.regional_news_request_headers)

        regional_news = list(self.parse_regional_news_json(response))

        yield dict(home_news=home_news, regional_news=regional_news)

    def parse_home_news_div(self, home_news_div):
        for item in home_news_div.css("div.sl-item"):
            date_div = item.css("div.sl-item-date")
            title_div = item.css("div.sl-item-title")
            text_div = item.css("div.sl-item-text")

            yield {
                "date": date_div.css("::text").get(),
                "title": title_div.css("a.news-popup::text").get(),
                "description": text_div.css("::text").get()
            }

    def parse_regional_news_json(self, regional_news_json_response):
        regional_news_json_response = regional_news_json_response.json()
        regional_news_json_data = regional_news_json_response["data"]

        for item in regional_news_json_data:
            timestamp = item["datetime"]
            item_datetime = datetime.fromtimestamp(timestamp)
            item_date = item_datetime.strftime("%B, %d")
            item_time = item_datetime.strftime("%H:%M")

            clean_description = remove_tags(item["description"])

            yield {
                "date": item_date,
                "time": item_time,
                "region": item["region"]["name"],
                "title": item["title"],
                "description": clean_description
            }


