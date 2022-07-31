import imp
import json
from nis import cat
from urllib import response
from django.http import HttpResponse
import requests
from bs4 import BeautifulSoup
from .utils import get_text
import craigslist_scrapper.url_config as url_config


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def get_data_ids(tag):
    tag = str(tag)
    try:
        split_tag = tag.split("data-ids=")[1]
        unforformatter_data_ids = split_tag.split(" ")[0][3:-1]
        data_ids = unforformatter_data_ids.split(",")
        return data_ids
    except:
        return ''


def get_posting(request):
    
    query = request.GET.get('query')
    posting_page = requests.get(
        url_config.CRAIGSLIST_SEARCH,
        params={
            'query' : query
        }
    )
    posting_list = []
    soup = BeautifulSoup(posting_page.content, "html.parser")
    results = soup.find(id="search-results", class_="rows")
    posting_elements = results.find_all("li", class_="result-row")
    for item in posting_elements:
        price = item.find("span", class_="result-price")
        title = item.find("a", class_="result-title hdrlnk") 
        location = item.find("span", class_="result-hood") 
        gallery= item.find("a", class_="result-image gallery")
        data_ids = get_data_ids(gallery)
        images = [url_config.NO_IMAGE]
        if len(data_ids) > 0:
            images.pop()
            for data_id in data_ids:
                image = url_config.CRAIGSLIST_IMAGES + data_id + '_300x300.jpg'
                images.append(image)
        posting_list.append({
            'title' : get_text(title),
            'price' : get_text(price),
            'location' : get_text(location),
            'images' : images
        })
    return HttpResponse(json.dumps(posting_list))

def get_search_suggestion(request):
    query = request.GET.get('search_term')
    