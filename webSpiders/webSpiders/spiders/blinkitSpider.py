import json
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
            PageMethod("wait_for_timeout", 100),
            PageMethod("fill","input[placeholder='search delivery location']","Kammanahalli"),
            PageMethod("wait_for_timeout", 100),
            PageMethod("fill", "input[placeholder='search delivery location']", ""),
            PageMethod("wait_for_timeout", 100),
            PageMethod("fill", "input[placeholder='search delivery location']", "Kammanahalli"),
            PageMethod("wait_for_timeout", 100),
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

        # data = soup.find("script",string=re.compile("window.grofers*")).text
        # data = data.split("window.grofers = {};")[1]
        # data = data.split("{",maxsplit=1)[1]
        # data = data.split("};",maxsplit=1)[0]
        # data = dict(data)
        # data = "{" + data + "}"


        products = soup.find_all("div",attrs={"class":"Product__UpdatedContentContainer-sc-11dk8zk-7 bekgjj"})
        for product in products:
            name = product.findChild("div",attrs={"class":"Product__UpdatedTitle-sc-11dk8zk-9 hxWnoO"}).text
            try:
                quantity = product.findChild("span", attrs={"class": "bff_variant_text_only plp-product__quantity--box"}).text
            except:
                try:
                    quantity = product.findChild("div", attrs={"class": "plp-product__quantity--box"}).text
                except:
                    quantity=None
            price_tag = product.findChild("div", attrs={"class": "Product__UpdatedPriceAndAtcContainer-sc-11dk8zk-10 ljxcbQ"})
            prices = []
            for child in price_tag.children:
                for price in child.children:
                    prices.append(price.text)
            display_price = prices[0]
            if "₹" in prices[1]:
                original_price = prices[1]
            else:
                original_price = None
            yield {
                "name":name,
                "quantity":quantity,
                "display_price":display_price,
                "original_price":original_price
            }