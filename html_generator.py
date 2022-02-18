import jinja2
import datetime
import os

def generate_html(posts):
    templates_path = "./web/templates"
    output_path = "./output"

    # load template
    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(templates_path))
    template = jinja_env.get_template('layout.html')

    # generate html
    html_text = template.render(posts)

    # create output folder if it doesnt exist
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # get current time
    current_datetime = datetime.datetime.now().strftime("%H-%M_%d.%m.%Y_%S")
    file_name = f'posts_{current_datetime}.html'

    # output to file
    with open(f'{output_path}/{file_name}', 'wb') as f:
        f.write(html_text.encode('utf-8'))

    return file_name


if __name__ == "__main__":
    posts = {'posts':
             [{'group_id': 23423,
               'post_url':
                 'https://m.facebook.com/groups/2786770884931764/permalink/3096863857255797/',
               'time': datetime.datetime(2021, 12, 14, 18, 36),
               'text': 'post1',
               'link': 'https://finupp.meitavdash.co.il/p/junior?fbclid=IwAR1DfTiQXZBpUIznK683RYcWcE-ZzPkuAY2FXPihZJGRLs_ySaqrSEvbtak'},
                 {'group_id': 23423,
                  'post_url': 'https://m.facebook.com/groups/2786770884931764/permalink/3096197307322452/',
                  'time': datetime.datetime(2021, 12, 13, 19, 46, 24),
                  'text': 'post2', 'link': None},
                 {'group_id': 23423,
                  'post_url': None,
                  'time': datetime.datetime(2021, 12, 13, 19, 46, 24), 'text': None, 'link': None},
                 {'group_id': 23423,
                  'post_url': 'https://m.facebook.com/groups/2786770884931764/permalink/3122447658030750/',
                  'time': datetime.datetime(2022, 1, 19, 15, 27, 59),
                  'text': 'post4', 'link': 'https://www.fibonatix.com/?fbclid=IwAR3Gf86NpTULxvIWQb3hG8ZGVZ_hZXvaRIZBc0UjwSiyGeuERip3qPqE8jA'}
              ]
             }

    generate_html(posts)
