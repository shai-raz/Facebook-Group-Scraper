# imoprt beautifulsoup
from bs4 import BeautifulSoup
import requests



def get_group_name(group_id):
    BASE_GROUP_URL = "https://www.facebook.com/groups/"

    group_url = BASE_GROUP_URL + str(group_id)

    # load group page
    group_page = BeautifulSoup(requests.get(group_url).text, 'html.parser')

    # get group name
    group_name = group_page.find('title').text.split('|')[0].strip()

    return group_name