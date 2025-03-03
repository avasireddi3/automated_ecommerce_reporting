import re

import scrapy
from bs4 import BeautifulSoup
from scrapy_playwright.page import PageMethod

class DemoSpider(scrapy.Spider):
    name = "demoSpider"
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"

    def start_requests(self):
        yield scrapy.Request('https://www.zeptonow.com/search?query=idli+rava',
        meta= dict(
        playwright = True,
        playwright_include_page = True,
        ))

    async def parse(self, response):
        soup = BeautifulSoup(response.text,'lxml')
        products = soup.find_all("a",attrs={"class":"!my-0 relative z-0 my-3 rounded-t-xl rounded-b-md group"})
        prettyHTML = soup.prettify()

        # with open("test_html.txt","w") as f:
        #     f.write(prettyHTML)
        for product in products:
            name = product.findChild("h5",attrs={"class":"font-subtitle text-lg tracking-wider line-clamp-2 !text-base !font-semibold !h-9 !tracking-normal px-1.5"}).text
            quantity = product.findChild("h5",attrs={"class":re.compile("font-subtitle text-lg tracking-wider line-clamp-1 mt-1 !text-sm !font-normal*")}).text
            try:
                display_price = product.findChild("h4", attrs={"class": "font-heading text-lg tracking-wide line-clamp-1 !font-semibold !text-md !leading-4 !m-0 mb-0.5 py-0.5"}).text
            except:
                display_price = None
            try:
                original_price = product.findChild("p", attrs={"class": "font-body text-xs line-clamp-1 !m-0 ml-1 !text-3xs text-skin-primary-void/40 line-through sm:!text-2xs"}).text
            except:
                original_price = None

            yield {"name":name,
                   "quantity":quantity,
                   "display_price":display_price,
                   "original_price":original_price}
