#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import requests
from db_worker import DBworker


class Save_to_DB_or_FILE:
    '''SaveToFolder or SaveToDB with check files and links.\n
        Contains two methods with these functions.'''

    # //////////////////////////////// SaveToDB with check files and links
    def save_to_db(self, id_user, number, list_for_search, keyword, group_channel, timescript, parcer):
        error_links = 0
        added_links = 0
        db = DBworker()
        indent = 0
        count_response_links = 100 # the number of responses given by duckduckgo is 100 per page. this parameter is responsible for requesting the next batch of responses
        link_for_send_telegram = []
        try:
            db.create_db()
            db.create_index_db()
            db.setup_settings(id_user, number, list_for_search, group_channel, timescript)
            print('[INFO] Process writing DB is done.')
            amount_links_in_db = db.check_amount_links(keyword=keyword, id_user=id_user)
            print(amount_links_in_db, ' - amount_links_in_db')

            if amount_links_in_db == 99:
                count_response_links += 100
                indent = 0
            elif amount_links_in_db > 99:
                while amount_links_in_db > 99:
                    count_response_links += 100
                    amount_links_in_db -= 100 
                else:
                    indent = amount_links_in_db
            else: 
                indent = amount_links_in_db

            count_response_links -= 100

            while added_links < number:
                count_response_links += 100
                links = parcer(keyword=keyword,number_links=99,count_response_links=count_response_links)
                for link in links[indent:]:
                    # print(link[indent:], ' - for link in links[indent:] ', len(link[indent:]), ' - len links[indent:] ', number, ' - number')
                    if added_links < number:
                        error_links, added_links, name_added_links = db.add_links_to_db(id_user, keyword, link, error_links, added_links)
                        # print(name_added_links, '- print from saver for parcer')
                        link_for_send_telegram.append(name_added_links[0])    # links_link_for_send_telegram
                        # print('link added to list')
                        time.sleep(0.2)
                    else:
                        break
                # print(added_links, ' - added links to DataBase. ', error_links, ' - amount error_links.')

                indent = 0
                print('Data processing. Wait 3 sec... Thank you')
                time.sleep(3)
                continue
            return link_for_send_telegram
        except requests.exceptions.JSONDecodeError as e:
            print(f'''\n An error occurred processing the JSON response from the server., [ERROR]: ''', e)
        except IndexError as e:
            print('An error has occurred. Maybe nothing new was found according to your request.\n ERROR -', e) 

        db.sort_db_by_column('USERS')
        db.sort_db_by_column('HISTORY_REQUESTS')

        print(f'Saving completed. Found and saved - {added_links} of the requested {number}.')

if __name__ == '__main__':
    # from api.DuckduckGo_parser import DuckDuckGoImageParcer   
    
    # DBworker.create_db(DBworker)
    # DBworker.check_amount_links(DBworker, 1, 'car 4k')
    # DBworker. add_links_to_db(DBworker, 1, 'parcer', "https://stackoverflow.com/questions/16573332/jsondecodeerror-expecting-value-line-1-lur-0", error_links = 0, added_links= 0 )
    # DBworker.setup_settings(DBworker, 1, 20, ['car 4k', 'girl 4k', 'parcer'], '@parcer', "11:22:33")
    # DBworker. check_settings_user(DBworker, '1')
    # Duck_parsing = DuckDuckGoImageParcer()
    # Save_to_DB_or_FILE.save_to_db(Save_to_DB_or_FILE, 1, 10, ['car 4k', 'girl 4k', 'parcer'], 'car 4k', '@parcer', "11:22:33", parcer=Duck_parsing.parcingimage)
    pass