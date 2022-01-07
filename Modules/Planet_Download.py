# -*- coding: utf-8 -*-
"""
Created on Thu Mar  18 19:24:05 2021

@author: uqytu1
"""

from threading import Thread
import gc
import queue
from time import sleep
import os
import math
from datetime import datetime
import json
import requests
from requests.auth import HTTPBasicAuth
import sys
from . import prompt_widget
from .__init__ import _planet_url

class OrderThread(Thread):
    def __init__(self, API_KEY, Avail_Items, selected_assets, delivery, daemon=True):
        super().__init__()

        self.auth = HTTPBasicAuth(API_KEY, '')
        self.Avail_Items = Avail_Items
        self.selected_assets = selected_assets
        self.delivery = delivery

        self.order_id = ''
        self.Item_date = None
        self.max_message_length = 60
        self.message = queue.Queue()
        self.message.put('Creating order')
        self.progress = queue.Queue()
        self.progress.put(0)
        self.result = queue.Queue()
        self.result.put(None)

    def run(self):
        # Use order API to download the order
        headers = {'content-type': 'application/json'}

        # Use the current time as the name of the order
        _now = datetime.now()
        order_name = _now.strftime('%Y-%m-%d-%H%M%S')

        # Prepare a products request list
        products = list()
        _index = 0
        products_index = dict()
        for _Item, _assets in self.selected_assets.items():
            products.append({'item_ids': [], 'item_type': _Item, 'product_bundle': ','.join(_assets)})
            products_index[_Item] = _index
            _index += 1
        # Create an database for each item's acquired date
        _Item_date = dict()
        for Item in self.Avail_Items:
            Item_type = Item['properties']['item_type']
            Item_ID = Item['id']
            products[products_index[Item_type]]['item_ids'].append(Item_ID)
            _Item_date[Item_ID] = datetime.strptime(Item['properties']['acquired'][:10], '%Y-%m-%d')

        self.Item_date = _Item_date

        # Create a partial order so that it will skip unavailable asets
        order_request = {'name': order_name, 'order_type': 'partial', 'products': products}

        # Add the delivery condition if there is any
        if len(self.delivery) > 0:
            order_request['delivery'] = self.delivery

        # Thread pipeline
        pipeline = queue.Queue()

        # Create an order
        order_url = _planet_url['order']
        pipeline.put(requests.post(order_url,
                                   data=json.dumps(order_request),
                                   auth=self.auth,
                                   headers=headers))
        
        while not pipeline.empty():
            order_response = pipeline.get()
        
        order_response_json = order_response.json()
        try:
            order_id = order_response_json['id']
            self.order_id = order_id
            if self.message.empty():
                self.message.put('Creating order: {}'.format(order_id))

            # Check the status of the order 1 minute later, and return the response when it's ready for download
            order_status = order_response_json['state']

            sleep(60)
            while order_status not in ['success', 'failed', 'partial', 'cancelled']:
                pipeline.put(requests.get('{}/{}'.format(order_url, order_id), auth=self.auth))
                while not pipeline.empty():
                    order_response = pipeline.get()
                order_response_json = order_response.json()
                order_status = order_response_json['state']
                # Check the status every 5 minutes
                sleep(300)
            if self.result.empty():
                self.result.put(order_response_json)
        # Report the message for any reason cause the order failed
        except Exception as Error:
            prompt_widget.ErrorBox(f'Error: {order_response.status_code}',
                                   f"{order_response_json['general'][0]['message']}\n{order_response_json['field']['Products'][0]['message']}")
            sys.exit(0)
        
    # Cancel the order if the task is aborted.
    def Abort(self):
        order_url = _planet_url['order']
        requests.put('{}/{}'.format(order_url, self.order_id), auth=self.auth)
        prompt_widget.ErrorBox('Abort', 'Order has been cancelled.')
        
class DownloadThread(Thread):
    def __init__(self, API_KEY, Item_date, order_response, output_dir, archive=False, overwrite=False, daemon=True):
        super().__init__()

        self.auth = HTTPBasicAuth(API_KEY, '')
        self.order_response = order_response
        self.Item_date = Item_date
        
        self.downloads = order_response['_links']['results']
        self.output_dir = output_dir
        self.overwrite = overwrite
        self.archive = archive
        
        longest_filename = max([r['name'].split('/')[-1] for r in self.downloads], key=len)
        
        self.max_message_length = max([len(longest_filename), len(order_response['id'])+13]) + 20
        self.message = queue.Queue()
        self.message.put('{:<{width}}'.format('Initialising', width=self.max_message_length))
        self.progress = queue.Queue()
        self.progress.put(0)
        self.result = queue.Queue()
        self.result.put(None)

    def run(self):
        results_urls = [r['location'] for r in self.downloads]
        results_names = [r['name'] for r in self.downloads]
        
        progress_counter = 0
        for url, name in zip(results_urls, results_names):
            filename = name.split('/')[-1]
            if filename == 'manifest.json':
                filename = '{}_manifest.json'.format(self.order_response['id'])
                output_subdir = self.output_dir
            else:
                if not self.archive:
                    # Create subdirectories based on the assets date
                    for Item_ID, date in self.Item_date.items():
                        if filename.startswith(Item_ID):
                            assets_date = date
                            break
                    date_subfolder = assets_date.strftime('%Y-%m-%d')
                    output_subdir = os.path.join(self.output_dir, date_subfolder)
                    
                    if not os.path.exists(output_subdir):
                        os.mkdir(output_subdir)
                    else:
                        # If the existing subdirectory is not writable, create a new one
                        if not os.access(output_subdir, os.X_OK | os.W_OK):
                            suffix = 1
                            output_subdir = '{}_{}'.format(output_subdir, suffix)
                            # This is to prevent creating other existing subdirectory
                            while os.path.exists(output_subdir):
                                suffix += 1
                                output_subdir = '{}_{}'.format(output_subdir.rsplit('_', 1)[0], suffix)
                            os.mkdir(output_subdir)
                else:
                    output_subdir = self.output_dir
                        
            output_file = os.path.join(output_subdir, filename)
            if self.overwrite or not os.path.exists(output_file):
                try:
                    if self.message.empty():
                        self.message.put('{:<{width}}'.format('Downloading {}'.format(filename), width=self.max_message_length))

                    download_response = requests.get(url, allow_redirects=True, auth=self.auth)

                    with open(output_file, 'wb') as f:
                        pipeline = queue.Queue()
                        pipeline.put(download_response.content)
                        while not pipeline.empty():
                            f.write(pipeline.get())
                    f = None

                    gc.collect()
                    
                # Report the message for any reason cause the download failed
                except Exception as Error:
                    prompt_widget.ErrorBox('Something went wrong', Error)
                    sys.exit(0)
            else:
                if self.message.empty():
                    self.message.put('Skipping {:<{width}}'.format(filename, width=self.max_message_length))

            progress_counter += 1
            if self.progress.empty():
                self.progress.put(progress_counter)

            # Wait for 5 second between each request
            sleep(5)

def main(API_KEY, _planet_result, selected_assets):
    # List available Planet items
    Avail_Items = _planet_result['features']

    # Ask the user to select the delivery method
    output_dir, delivery, overwrite = prompt_widget.DeliveryBox()

    # Disable automatic garbage collect to avoid crashing tkinter
    if gc.isenabled():
        gc.disable()
            
    # Create an order. Cancel the order if the task is aborted.
    task_thread = OrderThread(API_KEY, Avail_Items, selected_assets, delivery)
    order_response = prompt_widget.ProgressBar('indeterminate', task_thread, len(Avail_Items)-1, task_thread.Abort)

    # Get the date information to respective items
    Item_date = task_thread.Item_date

    # Clean up
    task_thread = None

    # Temporary enable automatic garbage collect
    if not gc.isenabled():
        gc.enable()

    gc.collect()

    # End the application here if the delivery method is to cloud storage
    delivery_options = delivery.keys()
    if 'amazon_s3' in delivery_options or 'azure_blob_storage' in delivery_options or 'google_cloud_storage' in delivery_options:
        prompt_widget.InfoBox('Done', 'Check your cloud storage for the delivery progress')
        sys.exit(0)

    # Count available assets
    _assets_count = len(order_response['_links']['results'])

    # Do nothing when cancel the download
    def do_nothing():
        pass

    # Disable automatic garbage collection to avoid crashing tkinter
    if gc.isenabled():
        gc.disable()
                    
    # Check if the download is a single archive
    if 'single_archive' in delivery_options:
        task_thread = DownloadThread(API_KEY, Item_date, order_response, output_dir, archive=True, overwrite=overwrite)

    else:
    # Download the assets separatedly
        task_thread = DownloadThread(API_KEY, Item_date, order_response, output_dir, overwrite=overwrite)
        
    prompt_widget.ProgressBar('determinate', task_thread, _assets_count-1, do_nothing)

    # Clean up
    task_thread = None
    gc.collect()
    
