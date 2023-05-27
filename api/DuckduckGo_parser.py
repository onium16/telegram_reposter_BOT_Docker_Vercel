import re
import time
import requests

from urllib import request
import json

class DuckDuckGoImageParcer: 
    '''Parcer images base on duckduckgo.com searching system.'''

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "X-Requested-With": "XMLHttpRequest",
    }
    
    def __init__(self) -> None:
        pass

    def parcingimage(self, keyword, number_links, count_response_links):
        '''
        keyword - keyword for searching\n
        number_links - amount of links to return, default = 99\n
        count_response_links - the number of responses given by duckduckgo is 100 (return only 99) per page. 
        This parameter is responsible for requesting the next batch of responses.\n
        '''

        links_for_save = []

        params = {
            'q': keyword,
            'iar': 'images',
            'iax': 'images',
            'ia': 'images',
        }
        
        response = requests.get('https://duckduckgo.com/', 
                                headers=self.headers, 
                                params=params)
        print(response.url)
        text_clear = response.text
        vqd = re.findall(r'vqd=(.+),safe_ddg', text_clear)
        if vqd:
            vqd_value = vqd[0][1:-1]
            print(vqd_value, ' - vqd_value')
        else:
            print("Не удалось извлечь значение VQD")
            return
        time.sleep(2)

        params_json = {
            'l': 'wt-wt', # wt-wt
            'o': 'json', # json
            'q': keyword,
            'vqd': vqd_value,
            'p': 1,
            's': count_response_links,
        }

        response = requests.get ('https://duckduckgo.com/i.js', 
                                 headers=self.headers, 
                                 params=params_json)
        url = response.url
        print(url)
        data = None

        try:
            req = request.Request(url, headers=self.headers)
            response = request.urlopen(req)
           
            data = json.loads(response.read().decode())
            # print(data)
        except:
            return '[ERROR]: Parsing failed!!! Check DuckDuckGoImageParcer.'

        for link in data['results']:
            links_for_save.append(link['image'])

        print(len(links_for_save), '- number of found links to process')
        # print(links_for_save, '- links to process')
        return links_for_save

if __name__ == '__main__':
    pass