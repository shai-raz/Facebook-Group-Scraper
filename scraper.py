import threading
import datetime
from time import sleep
from facebook_scraper import get_posts
from PyQt5.QtCore import *


class GroupsScraper(QObject, threading.Thread):
    # this signal will indicate when the scraping in complete
    scrape_complete_sig = pyqtSignal(dict)

    def __init__(self, email, password, groups_id):
        threading.Thread.__init__(self)
        QObject.__init__(self)
        self.email = email
        self.password = password
        self.groups_id = groups_id

    def get_fake_groups_posts(self):
        fake_result = {
            2786770884931764: [
                {'post_url':
                 'https://m.facebook.com/groups/2786770884931764/permalink/3096863857255797/',
                 'time': datetime.datetime(2021, 12, 14, 18, 36),
                 'text': 'post1',
                 'link': 'https://finupp.meitavdash.co.il/p/junior?fbclid=IwAR1DfTiQXZBpUIznK683RYcWcE-ZzPkuAY2FXPihZJGRLs_ySaqrSEvbtak'},
                {'post_url': 'https://m.facebook.com/groups/2786770884931764/permalink/3096197307322452/',
                 'time': datetime.datetime(2021, 12, 13, 19, 46, 24),
                 'text': 'post2', 'link': None},
                {'post_url': None,
                    'time': datetime.datetime(2021, 12, 13, 19, 46, 24), 'text': None, 'link': None},
                {'post_url': 'https://m.facebook.com/groups/2786770884931764/permalink/3122447658030750/',
                 'time': datetime.datetime(2022, 1, 19, 15, 27, 59),
                 'text': 'post4', 'link': 'https://www.fibonatix.com/?fbclid=IwAR3Gf86NpTULxvIWQb3hG8ZGVZ_hZXvaRIZBc0UjwSiyGeuERip3qPqE8jA'}
            ]
        }

        sleep(2)
        return fake_result

    # returns: dictionary of group_id: list of posts
    def get_groups_posts(self):
        return self.get_fake_groups_posts()

        result = {}

        for group_id in self.groups_id:
            result[group_id] = []
            for post in get_posts(group=group_id,
                                  credentials=(self.email, self.password),
                                  pages=1):
                result[group_id].append({
                    "post_url": post['post_url'],
                    "time": post['time'],
                    "text": post['text'],
                    "link": post['link'],
                })

        return result

    def run(self):
        # emit a signal that scraping is done
        self.scrape_complete_sig.emit(self.get_groups_posts())
