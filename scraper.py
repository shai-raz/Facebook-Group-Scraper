import threading
import datetime
from time import sleep
from facebook_scraper import get_posts
from PyQt5.QtCore import *
from utils import datetime_to_html_str


class GroupsScraper(QObject, threading.Thread):
    # this signal will indicate when the scraping in complete
    scrape_complete_sig = pyqtSignal(dict)
    group_scrapeing_started_sig = pyqtSignal(str)
    group_scrapeing_complete_sig = pyqtSignal(str)

    def __init__(self, email, password, group_ids, keywords, group_id_name_dict, num_of_pages=2):
        threading.Thread.__init__(self)
        QObject.__init__(self)
        self.email = email
        self.password = password
        self.groups_id = group_ids
        self.keywords = keywords
        self.group_id_name_dict = group_id_name_dict
        self.num_of_pages = num_of_pages

    def get_fake_groups_posts(self):
        fake_result = {
            'posts':
            [
                {
                    'group_id': 452297688135230,
                    'group_name': self.group_id_name_dict["452297688135230"],
                    'post_url':
                    'https://m.facebook.com/groups/2786770884931764/permalink/3096863857255797/',
                    'time': datetime_to_html_str(datetime.datetime(2021, 12, 14, 18, 36)),
                    'text': 'post1',
                    'link': 'https://finupp.meitavdash.co.il/p/junior?fbclid=IwAR1DfTiQXZBpUIznK683RYcWcE-ZzPkuAY2FXPihZJGRLs_ySaqrSEvbtak'
                },
                {
                    'group_id': 452297688135230,
                    'group_name': self.group_id_name_dict["452297688135230"],
                    'post_url': 'https://m.facebook.com/groups/2786770884931764/permalink/3096197307322452/',
                    'time': datetime_to_html_str(datetime.datetime(2021, 12, 14, 18, 36)),
                    'text': 'post2',
                    'link': None
                },
                {
                    'group_id': 452297688135230,
                    'group_name': self.group_id_name_dict["452297688135230"],
                    'post_url': None,
                    'time': datetime_to_html_str(datetime.datetime(2021, 12, 14, 18, 36)),
                    'text': None,
                    'link': None
                },
                {
                    'group_id': 452297688135230,
                    'group_name': self.group_id_name_dict["452297688135230"],
                    'post_url': 'https://m.facebook.com/groups/2786770884931764/permalink/3122447658030750/',
                    'time': datetime_to_html_str(datetime.datetime(2021, 12, 14, 18, 36)),
                    'text': 'post4',
                    'link': 'https://www.fibonatix.com/?fbclid=IwAR3Gf86NpTULxvIWQb3hG8ZGVZ_hZXvaRIZBc0UjwSiyGeuERip3qPqE8jA'
                }
            ]
        }

        # sleep(2)
        return fake_result

    def mobile_to_desktop_post_url(self, post_url):
        return post_url.replace('m.facebook', 'www.facebook')

    def create_post_item(self, group_id, post_url, time, text, link, matched_keywords):
        return {
            'group_id': group_id,
            'group_name': self.group_id_name_dict[group_id],
            'post_url': self.mobile_to_desktop_post_url(post_url),
            'time': time,
            'text': text,
            'link': link,
            'keywords': matched_keywords
        }

    # returns: dictionary of group_id: list of posts
    def get_groups_posts(self):
        # return self.get_fake_groups_posts()

        result = {'posts': []}

        for group_id in self.groups_id:
            self.group_scrapeing_started_sig.emit(self.group_id_name_dict[group_id])
            for post in get_posts(group=group_id,
                                  credentials=(self.email, self.password),
                                  pages=self.num_of_pages):
                if post['text'] is None:
                    continue

                if self.keywords:
                    # check if the post contains any of the keywords
                    # this also checks if the keyword appears in the TRANSLATED text
                    # for example if a keyword is "hello" it will match a post having the word "hello" in it
                    matched_keywords = [keyword for keyword in self.keywords if keyword in post['text']]
                else:
                    matched_keywords = []

                if not self.keywords or len(matched_keywords) > 0:
                    post_text = post['original_text'] if 'original_text' in post else post['text']
                    result['posts'].append(
                        self.create_post_item(
                            group_id,
                            post['post_url'],
                            post['time'],
                            post_text,
                            post['link'],
                            matched_keywords
                        )
                    )

            self.group_scrapeing_complete_sig.emit(self.group_id_name_dict[group_id])

        # sort posts by time
        result['posts'] = sorted(result['posts'], key=lambda k: k['time'], reverse=True)

        # change all times to html string
        for post in result['posts']:
            post['time'] = datetime_to_html_str(post['time'])

        return result

    def run(self):
        # emit a signal that scraping is done
        self.scrape_complete_sig.emit(self.get_groups_posts())
