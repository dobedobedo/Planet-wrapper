#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 16:22:30 2018

@author: uqytu1
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from builtins import dict
from builtins import range
from builtins import int
from builtins import str
from builtins import input
from future import standard_library
standard_library.install_aliases()
import os
import subprocess
import json
from datetime import datetime, timedelta
import re
import getpass
from . import Geo_tool
from . import auth

def ParseInputNumbers(selects):
    try:
        selected_index = set()
        for select in selects:
            if '-' in select:
                start, end = select.split('-')
                for i in range(int(start), int(end)+1):
                    selected_index.add(i-1)
                        
            else:
                selected_index.add(int(select)-1)
        return selected_index
    except ValueError:
        print('Can\'t recognise input. Please try again!')
        return False

def main(Items, Items_asset):
    
    print('Welcome! During the process, you can escape the program anytime by pressing Ctrl + C ')

    # Try to see whether there is a valid account init
    if not auth.ValidateAccount():
        while True:
            try:
                email = input('Your planet account: ')
                pwd = getpass.getpass('Your password: ')
                cmd = cmd = ['planet', 'init', '--email', email, '--password', pwd]
                subprocess.check_call(cmd)
                email = None
                pwd = None
                break
            except subprocess.CalledProcessError:
                print('Credential is not correct!')
                continue
    
    # Ask user to select items for download
    print('Input the item numbers you want to download:')
    for index, item in enumerate(Items):
        print('{:>2}: {:<}'.format(index+1, item))
    print('e.g.: "1-3" to select 1 to 3; 1 3 to select 1 and 3')
    
    # Check whether input is valid
    while True:
        selects = input('>>> ').split()
        selected_index = ParseInputNumbers(selects)
        if selected_index:
            break
        else:
            continue
        
    selected_items = list()
    for index in selected_index:
        selected_items.append(Items[index])
        
    # Ask user to select assets for each item
    selected_assets = dict()
    for selected_item in selected_items:
        print('Input the asset numbers you want to download for {}:'.format(selected_item))
        for index, item in enumerate(Items_asset[selected_item]):
            print('{:>2}: {:<}'.format(index+1, item))
        print('e.g.: "1-3" to select 1 to 3; 1 3 to select 1 and 3')
        
    # Check whether input is valid
        while True:
            selects = input('>>> ').split()
            selected_index = ParseInputNumbers(selects)
            if selected_index:
                break
            else:
                continue
        
        selected_assets[selected_item] = list()
        for index in selected_index:
            selected_assets[selected_item].append(Items_asset[selected_item][index])
    
    # Ask user input and output file names
    AOI_filetype = ['.shp', '.geojson', '.json']
    while True:
        AOI = input('Enter the file name containing the area of interest: ')
        try:
            ext = os.path.splitext(AOI)[1]
        except AttributeError:
            print('Invalud input file. Please try again.')
            continue
        
        if os.path.isfile(AOI) and ext.lower() in AOI_filetype:
            break
        else:
            print('Invalud input file. Please try again.')
            continue
        
    # Create GeoJSON object based on extension
    if 'shp' in ext or 'SHP' in ext or 'Shp' in ext:
                
    # Create GeoJSON AOI Feature Collection from shapefile
        AOI_geojson = Geo_tool.CreateGeojsonFC(AOI)
        
    else:
    
    # Load GeoJSON for geojson extension
        AOI_geojson = Geo_tool.LoadGeoJSON(AOI)
        
    # Detect geometry types in GeoJSON object
    AOI_types = set()
    for feature in AOI_geojson['features']:
        AOI_types.add(feature['geometry']['type'])
        
    # Ask the user if area cover percentage is set
    if 'Polygon' in AOI_types or 'Multipolygon' in AOI_types:
        print('Polygon detected. Do you want to filter images with cover percentage?')
        while True:
            User_Confirm = input('(y/n): ')
            if User_Confirm.lower() == 'y' or User_Confirm.lower() == 'yes':
                while True:
                    try:
                        MinCover = int(input('Please enter the minimum cover percentage (0-100): '))
                        MaxCover = int(input('Please enter the maximum cover percentage (0-100): '))
                        if (MaxCover - MinCover) >= 0 and MinCover >= 0 and MaxCover <= 100:
                            MinCover = str(MinCover)
                            MaxCover = str(MaxCover)
                            break
                        else:
                            print('Maximum cover must be larger than minimum cover in range between 0 to 100!')
                            continue
                    except ValueError:
                        print('Can\'t recognise input. Please try again.')
                        continue
            elif User_Confirm.lower() == 'n' or User_Confirm.lower() == 'no':
                break
            else:
                print('Can\'t recognise input. Please try again.')
                continue
    
    # Ask the user to input date range
    while True:
        try:
            SYear, SMonth, SDay = input('Please enter the start date (yyyy-mm-dd): ').split('-')
            float(SYear), float(SMonth), float(SDay)
            StartDate = '-'.join([SYear[0:4], SMonth[0:2].zfill(2), SDay[0:2].zfill(2)])
            
            EYear, EMonth, EDay = input('Please enter the end date (yyyy-mm-dd): ').split('-')
            float(EYear), float(EMonth), float(EDay)
            EndDate = '-'.join([EYear[0:4], EMonth[0:2].zfill(2), EDay[0:2].zfill(2)])
            
            if re.match('^[0-9]{4}-[0-9]{2}-[0-9]{2}$', StartDate) and \
               re.match('^[0-9]{4}-[0-9]{2}-[0-9]{2}$', EndDate):
                       
                time_diff = datetime.strptime(EndDate, '%Y-%m-%d') - datetime.strptime(StartDate, '%Y-%m-%d')
                if time_diff > timedelta(0):
                    break
                else:
                    print('The end date must be later than the start date.')
                    continue
        except ValueError:
            print('Please follow the format yyyy-mm-dd')
            continue
    
    # Ask the user to input cloud cover range
    while True:
        try:
            MinCloud = float(input('Please enter the minimum cloud cover percentage (0-100): '))
            MaxCloud = float(input('Please enter the maximum cloud cover percentage (0-100): '))
            if (MaxCloud - MinCloud) >= 0 and MinCloud >= 0 and MaxCloud <= 100:
                MinCloud = '{:.2f}'.format(MinCloud/100)
                MaxCloud = '{:.2f}'.format(MaxCloud/100)
                break
            else:
                print('Maximum cover must be larger than minimum cover in range between 0 to 100!')
                continue
        except ValueError:
            print('You must input numbers')
            continue
    
    # Loop for all features for each item type
    Search_Result = list()
    Found_image = dict()
    
    for selected_item, feature in [
            (selected_item, feature) for selected_item in selected_items for feature in AOI_geojson['features']]:
        Search_Arg = ['planet', 'data', 'search', 
                      '--item-type', selected_item, 
                      '--range', 'cloud_cover', 'gte', MinCloud, 
                      '--range', 'cloud_cover', 'lte', MaxCloud, 
                      '--date', 'acquired', 'gte', StartDate, 
                      '--date', 'acquired', 'lte', EndDate, 
                      '--geom', str(feature)]
    # Add selected asset types to search arguments
        for asset in selected_assets[selected_item]:
            Search_Arg[5:5] = ['--asset-type', asset]
        
        search = subprocess.Popen(Search_Arg, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = search.communicate()
        if search.returncode == 0:
            Search_Result.append(json.loads(stdout.decode()))
            
    # Use cover area percentage to filter search result
            for index, element in enumerate(Search_Result[-1]['features']):
                try:
                    Min = eval(MinCover)
                    Max = eval(MaxCover)
                    
                    try:
                        Cover_Percentage = Geo_tool.CalculateCoverPercentage(feature, element)
                        if Cover_Percentage <= Min or Cover_Percentage >= Max:
                            del Search_Result[-1]['features'][index]
                        
                    except ZeroDivisionError:
                        continue
                    
                except NameError:
                    break
    
        else:
            print('Search Failed for {}: {}'.format(selected_item, stderr.decode()))
            continue
            
        try:
            Found_image[selected_item] += len(Search_Result[-1]['features'])
    
        except KeyError:
            Found_image[selected_item] = len(Search_Result[-1]['features'])
    
    # Display search stats
    Search_Info = list()
    total = 0
    for item, number in Found_image.items():
        Search_Info.append('{}: {} asset(s) for {} item(s)'.format(item, len(selected_assets[item]), number))
        total += number
        
    if total > 0:
        Search_Info.append('total {} items are found! Do you want to download them?'.format(total))
        
        print('Found images')
        print('\n'.join(Search_Info))
        while True:
            User_Confirm = input('(y/n): ')
            if User_Confirm.lower() == 'y' or User_Confirm.lower() == 'yes':
                outdir = input('Enter the folder location to save images: ')
                if not os.path.isdir(outdir):
                    print('folder doesn\'t exist. Will create one.')
                    os.makedirs(outdir)
                
                print('Start downloading.\nWill prompt users when download finish.')
        # Loop for downloading every images for each item-type
                for item, ID in [
                        (item['properties']['item_type'], 
                         item['id']) for Search in Search_Result for item in Search['features']]:
                            
                    Download_Arg = ['planet', 'data', 'download', 
                                    '--item-type', item, '--string-in', 'id', ID, 
                                    '--dest', outdir]
                    for asset in selected_assets[item]:
                        Download_Arg[5:5] = ['--asset-type', asset]
                    
                    Result = subprocess.Popen(Download_Arg, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, stderr = Result.communicate()
                    if Result.returncode == 0:
                        
                        print(stdout.decode())
                        
                    else:
                        print('Download Failed for {}: {}'.format(ID, stderr))
                        
                print('Images are downloaded')
                break
                
            elif User_Confirm.lower() == 'n' or User_Confirm.lower() == 'no':
                break
            else:
                print('Can\'t recognise input. Please try again.')
                continue
    else:
        print('No image is found')
        print('\n'.join(Search_Info))
