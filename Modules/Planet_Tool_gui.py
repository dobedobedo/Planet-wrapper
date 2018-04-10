#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 10:10:05 2018

@author: uqytu1
"""

import os
import sys
import subprocess
import json
from . import Geo_tool
from . import prompt_widget
from . import auth

def main(Items, Items_asset):
    
    # Try to see whether there is a valid account init
    if not auth.ValidateAccount():
        prompt_widget.AuthInputBox()
    
    # Ask user select items and assets for download
    selected_items = prompt_widget.CheckBox(Items, 'item')
    selected_assets = dict()
    for selected_item in selected_items:
        selected_assets[selected_item] = prompt_widget.CheckBox(
                Items_asset[selected_item], 'asset', selected_item)
    
    # Ask user input and output file names
    AOI_filetype = [('Shapefile', ['*.shp', '*.SHP', '*.Shp']), 
                     ('GeoJSON', ['*.geojson', '*.GEOJSON', '*.json', '*.JSON'])]
    AOI = prompt_widget.AskOpenFile('Choose a file containing the area of interest', 
                                    AOI_filetype)
    
    ext = os.path.splitext(AOI)[1]
        
    # Create GeoJSON object based on extension
    # Close application if no input file with extension is selected
    try:
        if 'shp' in ext or 'SHP' in ext or 'Shp' in ext:
                    
        # Create GeoJSON AOI Feature Collection from shapefile
            AOI_geojson = Geo_tool.CreateGeojsonFC(AOI)
            
        else:
        
        # Load GeoJSON for geojson extension
            AOI_geojson = Geo_tool.LoadGeoJSON(AOI)
            
    except FileNotFoundError:
        prompt_widget.InfoBox('Abort', 'No geometry is detected')
        sys.exit(0)
        
    # Detect geometry types in GeoJSON object
    AOI_types = set()
    for feature in AOI_geojson['features']:
        AOI_types.add(feature['geometry']['type'])
    if 'Polygon' in AOI_types or 'Multipolygon' in AOI_types:
        if prompt_widget.User_Confirm(
                'Polygon detected', 'Do you want to filter images with cover percentage?') == 'yes':
            MinCover, MaxCover = prompt_widget.AreaCover_inputBox()
            
    StartDate, EndDate = prompt_widget.DateInputBox()
    
    MinCloud, MaxCloud = prompt_widget.CloudCover_inputBox()
    
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
            Search_Arg[7:7] = ['--asset-type', asset]
        
        search = subprocess.run(Search_Arg, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            search.check_returncode()
            Search_Result.append(json.loads(search.stdout.decode()))
            
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
    
        except subprocess.CalledProcessError:
            prompt_widget.ErrorBox(
                    'Error', 'Search Failed for {}: {}'.format(
                            selected_item, search.stderr.decode()))
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
        
        User_confirm = prompt_widget.User_Confirm('Found images', '\n'.join(Search_Info))
        if User_confirm == 'yes':
            outdir = prompt_widget.AskDirectory('Select the folder to save images')
            
            prompt_widget.InfoBox('Start', 'Start downloading.\nWill prompt users when download finish.')
    # Loop for downloading every images for each item-type
            for item, ID in [
                    (item['properties']['item_type'], 
                     item['id']) for Search in Search_Result for item in Search['features']]:
                        
                Download_Arg = ['planet', 'data', 'download', 
                                '--item-type', item, '--string-in', 'id', ID, 
                                '--dest', outdir]
                for asset in selected_assets[item]:
                    Download_Arg[7:7] = ['--asset-type', asset]
                    Result = subprocess.run(Download_Arg, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                try:
                    Result.check_returncode()
                    
                except subprocess.CalledProcessError:
                    prompt_widget.ErrorBox('Error', 'Download Failed for {}: {}'.format(ID, Result.stderr.decode()))
                    
            prompt_widget.InfoBox('Success', 'Images are downloaded')
    else:
        prompt_widget.InfoBox('No image is found', '\n'.join(Search_Info))
   
