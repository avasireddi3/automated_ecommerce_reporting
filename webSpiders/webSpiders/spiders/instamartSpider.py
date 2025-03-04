import scrapy
from bs4 import BeautifulSoup
from scrapy_playwright.page import PageMethod


class InstamartSpider(scrapy.Spider):
    name = "instamartSpider"
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"

    def start_requests(self):
        yield scrapy.Request('https://www.swiggy.com/instamart/search?custom_back=true&query=idli+rava',
        meta= dict(
        playwright = True,
        playwright_include_page = True,
        playwright_page_methods = [
            PageMethod("wait_for_selector", "div[class='sc-aXZVg gPfbij']"),
            PageMethod("click","div[class='sc-aXZVg gPfbij']"),
            PageMethod("wait_for_timeout", 100),
            # execute the scroll script
            PageMethod("evaluate",
                       "for (let i = 0; i < 8; i++) setTimeout(() => window.scrollTo(0, document.body.scrollHeight), i * 2000);"),
            # wait for 30 seconds
            PageMethod("wait_for_timeout", 15000)
            ]
        ))

    async def parse(self, response):
        soup = BeautifulSoup(response.text,'lxml')
        with open("test_html.txt","w") as f:
            f.write(soup.prettify())