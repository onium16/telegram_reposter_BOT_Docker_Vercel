#!/usr/bin/python3
# -*- coding: utf-8 -*-

from random import randint
from DuckduckGo_parser import DuckDuckGoImageParcer
from saver_for_parcer import Save_to_DB_or_FILE
import db_worker as db_worker
import ast


def get_variables(id_user):
    db=db_worker.DBworker()
    result_variables = db.check_settings_user(id_user)
    if result_variables != None:
        ID, NUMBER, LIST_FOR_SEARCH, GROUP_CHANNEL, TIMESCRIPT = result_variables
        # data type casting:
        ID = int(ID)
        NUMBER = int(NUMBER)
        LIST_FOR_SEARCH = ast.literal_eval(LIST_FOR_SEARCH)
    else:
        None
    return ID, NUMBER, LIST_FOR_SEARCH, GROUP_CHANNEL, TIMESCRIPT


class RequestData():  # random keyword from LIST_FOR_SEARCH param
    '''The class contains a method 'GET_KEYWORD' that receives a list of string data, 
       and using the random library, receives a random element of the list. 
       In this case KEYWORD'''
    def get_keyword(self, listForSearch):
        keyword = listForSearch[randint(0, len(listForSearch)-1)]
        return keyword



if __name__ == '__main__':

    def main_to_save_new_links(id_user):
        ID, NUMBER, LIST_FOR_SEARCH, GROUP_CHANNEL, TIMESCRIPT = get_variables(id_user)
       
        print(
                'ID: ', ID, 
                'NUMBER: ', NUMBER, 
                'LIST_FOR_SEARCH: ', LIST_FOR_SEARCH, 
                'GROUP_CHANNEL: ', GROUP_CHANNEL, 
                'TIMESCRIPT: ',TIMESCRIPT
            )
        keyword = RequestData.get_keyword(RequestData, LIST_FOR_SEARCH)
        print('keyword:',  keyword)
        Duck_parsing = DuckDuckGoImageParcer()
        save_link = Save_to_DB_or_FILE()
    #//////////////////////////////// SaveToDB with check files and links
        save_link.save_to_db(
            id_user = 1,  # default ID for check write own number
            number = NUMBER, 
            list_for_search = LIST_FOR_SEARCH, 
            keyword = keyword,
            group_channel = GROUP_CHANNEL, 
            timescript = TIMESCRIPT, 
            parcer = Duck_parsing.parcingimage)

        main_to_save_new_links(1)
        # pass
