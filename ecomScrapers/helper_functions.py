

def try_extract(obj:dict,field:str,default):
    try:
        return obj[field]
    except KeyError or TypeError:
        return default