# -*- coding: utf-8 -*-
"""
Created on Wed Mar  10 10:10:05 2021

@author: uqytu1
"""

import os
import sys
import json
from . import Geo_tool
from . import prompt_widget
from .__init__ import _AOI_filetype, _filter_properties
from planet import api

def main(Avail_Items):
    # It is suggested to order SkySat download separatedly
    # Ask the user if download SkySat if permitted
    # If yes, then other items will be removed from the option
    skysat_mask = [x.startswith('SkySat') for x in Avail_Items.keys()]
    if any(skysat_mask):
        user_answer = prompt_widget.User_Confirm('SkySat is available',
                                                 ''.join(['It is recommended to download SkySat products separatedly\n',
                                                          'Do you want to download SkySat products?\n',
                                                          'If answer yes, only SkySat products will be available.\n',
                                                          'Otherwise, SkySat products will be removed from choices']))
        if user_answer.lower() == 'yes' or user_answer == 'y':
            Unwanted_Items = [item for index, item in enumerate(Avail_Items.keys()) if not skysat_mask[index]]
        elif user_answer.lower() == 'no' or user_answer == 'n':
            Unwanted_Items = [item for index, item in enumerate(Avail_Items.keys()) if skysat_mask[index]]
        for item in Unwanted_Items:
            Avail_Items.pop(item)
    
    try:
        # Ask the user to select items and assets for download
        selected_items = prompt_widget.CheckBox(list(Avail_Items.keys()), 'Please select desired download item',
                                                'https://developers.planet.com/docs/apis/data/items-assets/', additional_info=True)

    except ValueError:
        # Quit if there is no other items available
        prompt_widget.InfoBox('Abort', 'No available items are detected')
        sys.exit(0)

    selected_assets = dict()
    for selected_item in selected_items:
        selected_assets[selected_item] = prompt_widget.CheckBox(
                Avail_Items[selected_item], 'Please select desired product bundles for {}'.format(selected_item),
                'https://developers.planet.com/docs/orders/product-bundles-reference/', additional_info=True)
    
    # Ask user input and output file names
    AOI = prompt_widget.AskOpenFile('Input a file containing the area of interest', 
                                    _AOI_filetype)
    ext = os.path.splitext(AOI)[1]

    # Create GeoJSON object based on extension
    # Close application if no input file with extension is selected
    try:
        if ext.lower() == '.geojson' or ext.lower() == '.json':
            AOI_geojson = Geo_tool.LoadGeoJSON(AOI)

        else:
            AOI_geojson = Geo_tool.CreateGeojsonFC(AOI)

    except FileNotFoundError:
        prompt_widget.InfoBox('Abort', 'No geometry is detected')
        sys.exit(0)
    
    except AttributeError:
        prompt_widget.InfoBox('Abort', 'No geometry is detected')
        sys.exit(0)
    
    # Detect the geometry type, and add area coverage as a filter option if polygons are detected
    AOI_types = set()
    for feature in AOI_geojson['features']:
        AOI_types.add(feature['geometry']['type'])
        
    _filter_options = list(_filter_properties.keys())
    if 'Polygon' in AOI_types or 'MultiPolygon' in AOI_types:
        pass
    else:
        _filter_options.remove('Area Coverage')

    # Ask the user to select filters. Allow empty input
    selected_filters = prompt_widget.CheckBox(_filter_options, 'Please select search filters', allow_none=True)

    # Create search filters, 
    search_filters = list()

    # Set CoverageRange to None. When return None, then skip coverage calculation in the next phase
    CoverageRange = None
    for _filter in selected_filters:
        filter_type = _filter_properties[_filter]['type']
        _field_name = _filter_properties[_filter]['field_name']

        if filter_type == 'Date':
            StartDate, EndDate = prompt_widget.DateInputBox()
            format_filter = [api.filters.date_range(_field_name, gte=StartDate),
                             api.filters.date_range(_field_name, lte=EndDate)]
            
        if filter_type == 'Range':
            _min = _filter_properties[_filter]['min']
            _max = _filter_properties[_filter]['max']
            MinRange, MaxRange = prompt_widget.RangeInputBox(_filter, _min, _max)
            if 'scale' in _filter_properties[_filter].keys():
                scale = _filter_properties[_filter]['scale']
                MinRange /= scale
                MaxRange /= scale
            if _field_name is None:
                CoverageRange = (MinRange, MaxRange)
                continue
            
            format_filter = [api.filters.range_filter(_field_name, gte=MinRange),
                             api.filters.range_filter(_field_name, lte=MaxRange)]

        if filter_type == 'Bool':
            format_filter = [api.filters.string_filter(_field_name, 'true')]

        search_filters[-1:-1] = format_filter

    or_filter = list()
    # One geometry in and 'AND' filter, and then use 'OR' filter to combine them
    for feature in AOI_geojson['features']:
        and_filter = api.filters.and_filter(api.filters.geom_filter(feature['geometry']), *search_filters)
        or_filter.append(and_filter)
    all_filter = api.filters.or_filter(*or_filter)
    
    request_filter = api.filters.build_search_request(all_filter, selected_items)
    
    return request_filter, selected_assets, AOI_geojson, CoverageRange
        
