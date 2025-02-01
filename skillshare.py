import requests, json, sys, re, os
import cloudscraper
from slugify import slugify
import ffmpeg

class Skillshare(object):
    def __init__(
        self,
        cookie,
        download_path=os.environ.get('FILE_PATH', './Skillshare'),
        pk='BCpkADawqM2OOcM6njnM7hf9EaK6lIFlqiXB0iWjqGWUQjU7R8965xUvIQNqdQbnDTLz0IAO7E6Ir2rIbXJtFdzrGtitoee0n1XXRliD-RH9A-svuvNW9qgo3Bh34HEZjXjG4Nml4iyz3KqF',
        brightcove_account_id=3695997568001,
    ):
        self.cookie = cookie.strip().strip('"')
        self.download_path = download_path
        self.pk = pk.strip()
        self.brightcove_account_id = brightcove_account_id
        self.pythonversion = 3 if sys.version_info >= (3, 0) else 2

    def is_unicode_string(self, string):
        if (self.pythonversion == 3 and isinstance(string, str)) or (self.pythonversion == 2 and isinstance(string, str)):
            return True

        else:
            return False

    def download_course_by_url(self, url):
        m = re.match(r'https://www.skillshare.com/en/classes/.*?/(\d+)', url)

        if not m:
            raise Exception('Failed to parse class ID from URL')

        self.download_course_by_class_id(m.group(1))

    def download_course_by_class_id(self, class_id):
        data = self.fetch_course_data_by_class_id(class_id=class_id)
        teacher_name = None

        if 'vanity_username' in data['_embedded']['teacher']:
            teacher_name = data['_embedded']['teacher']['vanity_username']

        if not teacher_name:
            teacher_name = data['_embedded']['teacher']['full_name']

        if not teacher_name:
            raise Exception('Failed to read teacher name from data')

        if self.is_unicode_string(teacher_name):
            teacher_name = teacher_name.encode('ascii', 'replace')

        title = data['title']

        if self.is_unicode_string(title):
            title = title.encode('ascii', 'replace')  # ignore any weird char

        base_path = os.path.abspath(
            os.path.join(
                self.download_path,
                slugify(teacher_name),
                slugify(title),
            )
        ).rstrip('/')

        if not os.path.exists(base_path):
            os.makedirs(base_path)

        for s in data['_embedded']['sessions']['_embedded']['sessions']:
            video_id = s['id']

            if not video_id:
                raise Exception('Failed to read video ID from data')

            s_title = s['title']

            if self.is_unicode_string(s_title):
                s_title = s_title.encode('ascii', 'replace')

            file_name = '{} - {}'.format(
                str(s['index'] + 1).zfill(2),
                slugify(s_title),
            )

            self.download_video(
                fpath='{base_path}/{session}.mp4'.format(
                    base_path=base_path,
                    session=file_name,
                ),
                video_id=video_id,
            )

            print('')

    def fetch_course_data_by_class_id(self, class_id):
        url = 'https://api.skillshare.com/classes/{}'.format(class_id)
        scraper = cloudscraper.create_scraper(
            browser={
                'custom': 'Skillshare/4.1.1; Android 5.1.1',
            },
            delay=10
        )

        res = scraper.get(
            url,
            headers={
            'Accept': 'application/vnd.skillshare.class+json;,version=0.8',
            'User-Agent': 'Skillshare/5.3.0; Android 9.0.1',
            'Host': 'api.skillshare.com',
            'Referer': 'https://www.skillshare.com/',
            'cookie': self.cookie,
            }
        )

        if not res.status_code == 200:
            raise Exception('Fetch error, code == {}'.format(res.status_code))

        return res.json()

    def download_video(self, fpath, video_id):
        streams_url = 'https://www.skillshare.com/sessions/{video_id}/stream'.format(
            video_id=video_id,
        )
        
        headers = {
            "cookie": self.cookie,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        }
        
        response = requests.get(streams_url, headers=headers)
        
        print(response.text)

        if response.status_code != 200:
            raise Exception('Failed to fetch video meta')

        dl_url = response.json()['streams'][1]['url']

        print('Downloading {}...'.format(fpath))

        if os.path.exists(fpath):
            print('Video already downloaded, skipping...')
            return

        ffmpeg.input(dl_url).output(fpath, vcodec='libx264', acodec='aac').run()

def splash():

    print(r"""   
                 ____  _    _ _ _     _                          ____  _     
                / ___|| | _(_) | |___| |__   __ _ _ __ ___      |  _ \| |    
                \___ \| |/ / | | / __| '_ \ / _` | '__/ _ \_____| | | | |    
                 ___) |   <| | | \__ \ | | | (_| | | |  __/_____| |_| | |___ 
                |____/|_|\_\_|_|_|___/_| |_|\__,_|_|  \___|     |____/|_____|  
                             _ __ ___  _ _  _ _ _  ___  _ _ 
                            | / /| __>| \ || | | || . || | |
                            |  \ | _> |   || | | ||   |\   /
                            |_\_\|___>|_\_||__/_/ |_|_| |_| 
                    
                    
                        
                     ####### #     # ####### #     #    #     #####  #    # 
                     #     # ##    # #       #     #   # #   #     # #   #  
                     #     # # #   # #       #     #  #   #  #       #  #   
                     #     # #  #  # #####   ####### #     # #       ###    
                     #     # #   # # #       #     # ####### #       #  #   
                     #     # #    ## #       #     # #     # #     # #   #  
                     ####### #     # ####### #     # #     #  #####  #    # 
                                                                                                         
                """)
