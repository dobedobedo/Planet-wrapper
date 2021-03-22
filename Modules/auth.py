# -*- coding: utf-8 -*-
"""
Created on Tue Apr 10 11:08:07 2018

@author: o0331
"""

from planet import api
from threading import Thread
import queue
import gc
from time import sleep
import sys
from . import prompt_widget
from .__init__ import _Items_assets

def ValidateAccount():
    API_KEY = api.auth.find_api_key()
    if API_KEY == None:
        API_KEY = prompt_widget.AuthInputBox()
        api.utils.write_planet_json({'key': API_KEY})

    return API_KEY

class InitialiseAssetsThread(Thread):
    def __init__(self, _Items_assets, daemon=True):
        super().__init__()
        
        self.Items = list(_Items_assets.keys())
        self.max_message_length = len(max(self.Items, key=len)) + 31
        self.message = queue.Queue()
        self.message.put('{0:<{width}}'.format('Initialising...', width=self.max_message_length))
        self.progress = queue.Queue()
        self.progress.put(0)
        self.result = queue.Queue()
        self.result.put(None)

    def run(self):
        # Check authentication
        API_KEY = ValidateAccount()

        # Initialisation
        Client = api.ClientV1(API_KEY)

        # Check available items based on assets permissions
        Items_asset = dict()
        _permission_filter = api.filters.permission_filter('assets:download')
        
        for _index, Item in enumerate(self.Items):
            _request = api.filters.build_search_request(_permission_filter, [Item])
            try:
                _result = Client.quick_search(_request)
                _result_json = _result.get()

            except Exception as Other_Errors:
                prompt_widget.ErrorBox('Something went wrong',
                                       '{}\nPlease try again later.'.format(Other_Errors))
                sys.exit(0)
            if self.message.empty():
                self.message.put('{0:<{width}}'.format('Checking the permission of {} ...'.format(Item),
                                                       width=self.max_message_length))
            if self.progress.empty():
                self.progress.put(_index)
            if len(_result_json['features']) > 0:
                # Add available assets to respective items
                Items_asset[Item] = _Items_assets[Item]

            # # Wait for 1 second after each request to avoid exceeding the request limit
            sleep(1)

        if self.result.empty():
            self.result.put(Items_asset)

def main():
    # Check authentication
    API_KEY = ValidateAccount()

    # This function is for the abort command of progress bar
    def do_nothing():
        pass
    
    # Disable automatic garbage collect to avoid crashing tkinter
    if gc.isenabled():
        gc.disable()
        
    # Initialise assets list
    task_thread = InitialiseAssetsThread(_Items_assets)
    Avail_Items = prompt_widget.ProgressBar('determinate', task_thread, len(_Items_assets)-1, do_nothing)

    # Clean up
    task_thread = None

    # Temporary enable automatic garbage collect
    if not gc.isenabled():
        gc.enable()

    gc.collect()

    return API_KEY, Avail_Items
