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

if __name__ == "__main__":
    print(parse_weight("5 kg + 500 g + 500 g"))