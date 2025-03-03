import re
import scrapy
from bs4 import BeautifulSoup
from scrapy_playwright.page import PageMethod


class BlinkitSpider(scrapy.Spider):
    name = "blinkitSpider"
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"

    def start_requests(self):
        yield scrapy.Request('https://blinkit.com/s/?q=idli%20rava',
        meta= dict(
        playwright = True,
        playwright_include_page = True,
        playwright_page_methods = [
            PageMethod("wait_for_selector", "input[placeholder='search delivery location']"),
            PageMethod("click", "input[placeholder='search delivery location']"),
            PageMethod("fill","input[placeholder='search delivery location']","Kammana"),
            PageMethod("click", "input[placeholder='search delivery location']"),
            PageMethod("fill", "input[placeholder='search delivery location']", ""),
            PageMethod("click", "input[placeholder='search delivery location']"),
            PageMethod("wait_for_timeout",1000),
            PageMethod("fill", "input[placeholder='search delivery location']", "Kammana"),
            PageMethod("wait_for_timeout", 1000),
            PageMethod("wait_for_selector", "div[class='address-container-v1']"),
            PageMethod("click", "div[class='LocationSearchList__LocationListContainer-sc-93rfr7-0 lcVvPT']"),
            # execute the scroll script
            PageMethod("evaluate",
                       "for (let i = 0; i < 8; i++) setTimeout(() => window.scrollTo(0, document.body.scrollHeight), i * 2000);"),
            # wait for 30 seconds
            PageMethod("wait_for_timeout", 15000)


            ]
        ))

    async def parse(self, response):
        soup = BeautifulSoup(response.text,'lxml')
        prettyHTML = soup.prettify()
        with open("test_html.txt","w") as f:
            f.write(prettyHTML)