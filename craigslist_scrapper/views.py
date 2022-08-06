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
from django.core.mail import send_mail



rooms_list = {}


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def get_data_ids(gallery):
    try:
        unforformatter_data_ids = gallery.get('data-ids')
        data_ids = unforformatter_data_ids.split(",")
        return data_ids
    except:
        return []

is_loopinf = False

@csrf_exempt
def get_posting(request):
    global is_loopinf
    global rooms_list
    rooms = get_rooms()
    new_rooms = []
    if(is_loopinf == False):
        is_loopinf = True
        for room in rooms:
            if room not in rooms_list.keys():
                new_room = rooms[room]
                new_rooms.append({
                    'title' : new_room['title'],
                    'location' : new_room['price'],
                    'post_url' : new_room['post_url']
                })
    else:
        return HttpResponse(['is already in loop', json.dumps(rooms)])
    rooms_list = rooms
    if len(new_rooms) > 0:
        print(new_rooms)
        send_mail(
            'New rooms',
            json.dumps(new_rooms),
            'jrv1271663@gmail.com',
            ['jvaz15194@gmail.com'],
            fail_silently=False,
        )
    return HttpResponse(json.dumps(new_rooms))



def get_rooms():
    query = ''
    posting_page = requests.get(
        url_config.ROOM_RENT, 
        params={
            'query' : ''
        }
    )
    posting_list = {}
    soup = BeautifulSoup(posting_page.content, "html.parser")
    results = soup.find(id="search-results", class_="rows")
    posting_elements = results.find_all("li", class_="result-row")
    for item in posting_elements:
        data_pid = item.get('data-pid')
        price = item.find("span", class_="result-price")
        title = item.find("a", class_="result-title hdrlnk") 
        location = item.find("span", class_="result-hood") 
        gallery= item.find("a", class_="result-image gallery")
        data_ids = get_data_ids(gallery)
        post_url = None
        if gallery != None:
            post_url = gallery.get("href")
        images = [url_config.NO_IMAGE]
        if len(data_ids) > 0:
            images.pop()
            for data_id in data_ids:
                image = url_config.CRAIGSLIST_IMAGES + data_id[2:] + '_300x300.jpg'
                images.append(image)
        posting_list[data_pid] = {
            'title' : get_text(title),
            'price' : get_text(price),
            'location' : get_text(location),
            'images' : images,
            'data_pid' : data_pid,
            'post_url' : post_url
        }
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


def get_images_from_post(post_html):
    try:
        split_1 = post_html.split('var imgList = ')
        split_2 = split_1[1].split(';')
        return split_2[0]
    except:
        return []
    print(post_html)


def get_post(request):
    post_url = request.GET.get('post_url')
    post_id = request.GET.get('post_id')
    post_page = requests.get(
        post_url
    )
    soup = BeautifulSoup(post_page.content, "html.parser")
    post_images = get_images_from_post(post_page.text)
    posting_title_section = soup.find("h1", class_="postingtitle")
    title = posting_title_section.find("span", id="titletextonly")
    price = posting_title_section.find("span", class_="price")
    location = posting_title_section.find("small")
    post_data = {
        'images' : get_text(title),
        'price' : get_text(price),
        'location' : get_text(location)
    }
    print(post_data)
    return HttpResponse(post_data)