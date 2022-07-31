from bs4 import BeautifulSoup

# make genric method that returns none if there is an error
def get_text(element):
    if element != None:
        return element.text.strip()
    return None

