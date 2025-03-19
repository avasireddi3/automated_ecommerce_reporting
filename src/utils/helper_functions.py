from selenium_driverless import webdriver
from selenium_driverless.scripts.network_interceptor import NetworkInterceptor, InterceptedRequest
from alive_progress import alive_bar
from config import unknown_bar


def try_extract(obj:dict,field:str,default):
    """try clause for extracting a field from response.json"""
    try:
        return obj[field]
    except KeyError or TypeError:
        return default

def parse_weight(quantity:str)->int:
    """parse_weight from string for blinkit responses"""
    try:
        (weight,unit) = quantity.split()
        if unit=="g":
            return int(weight)
        elif unit=="kg":
            return int(weight)*1000
    except ValueError:
        return 0

async def get_auth(url:str,api_term:str,request_method:str)->dict:
    """getting fresh headers for a search session"""
    auth = {}
    async def on_request(data: InterceptedRequest) -> None:
        """setting global variable auth with intercepted network request"""
        if api_term in data.request.url and data.request.method == request_method:
            nonlocal auth
            try:
                auth = data.request.headers
            except KeyError:
                print("no auth header found in request")
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")  # Important for Docker
    options.add_argument("--disable-gpu")
    options.headless = True
    async with webdriver.Chrome(options=options) as driver:
        async with NetworkInterceptor(driver,on_request=on_request):
            await driver.get(url)
            await driver.sleep(0.5)
    return auth

if __name__ == "__main__":
    print(parse_weight("5 kg + 500 g + 500 g"))