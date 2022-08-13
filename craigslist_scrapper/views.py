import imp
import json
from nis import cat
from urllib import response
from django.http import HttpResponse
import requests
from bs4 import BeautifulSoup
from .utils import get_text
import craigslist_scrapper.url_config as url_config
from django.views.decorators.csrf import csrf_exempt


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


@csrf_exempt 
def get_postings(request):
    query = request.GET.get('query')
    postings = get_all_postings(query)
    return HttpResponse(json.dumps(postings))
    
def get_all_postings(query):
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
        data_pid = item['data-pid']
        price = item.find("span", class_="result-price")
        title = item.find("a", class_="result-title hdrlnk") 
        post_url = title['href']
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
            'images' : images,
            'post_url' : post_url,
            'data_pid' : data_pid
        })
    return posting_list

def get_search_suggestion(request):
    search_term = request.GET.get('search_term')
    suggestions = requests.get(
        url_config.CRAIGSLIST_SUGGESTIONS,
        params={
            'type' : 'search',
            'term' : search_term,
            'cat' : 'sss'
        }
    )
    return HttpResponse(suggestions.text)


#Post method
@csrf_exempt 
def get_post(request):
    data_pid = request.GET.get('data_pid')
    postings = get_all_postings(data_pid)
    post = {}

    if len(postings) == 0:
        return HttpResponse('post not found', status=404)
    for card in postings:
        if card['data_pid'] == data_pid:
            post = card
    
    post_page = requests.get(post['post_url'])   
    soup = BeautifulSoup(post_page.content, "html.parser")
    print(soup)
    post_body = soup.find_all("section", class_="body")[0]
    description = post_body.find("section", id="postingbody")
    time_stamps = post_body.find_all("time", class_="date timeago")
    post['description'] = get_text(description)
    post['posted_time'] = time_stamps[0]['datetime']
    if len(time_stamps) > 1:
        post['updated_time'] = time_stamps[1]['datetime']
    return HttpResponse(json.dumps(post))