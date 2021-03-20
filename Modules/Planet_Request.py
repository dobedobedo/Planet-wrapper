# -*- coding: utf-8 -*-
"""
Created on Wed Mar  17 10:10:05 2021

@author: uqytu1
"""

import json
from io import StringIO
import sys
from planet import api
from . import Geo_tool, prompt_widget

def main(API_KEY, _request, AOI_geojson, Coverage=None):
    # Set up the client
    Client = api.ClientV1(API_KEY)

    # Request with the search filter
    res = Client.quick_search(_request)

    # Get all the results in a JSON object from the paged response
    File_Object = StringIO()
    res.json_encode(File_Object)
    res_json = json.loads(File_Object.getvalue())

    if Coverage is not None:
        # Loop through every geometry to calculate the coverage
        strip_images = list()
        geoms = AOI_geojson['features']
        for Planet_feature in res_json['features']:
            CoverageResults = list()

            # Loop through every geometry feature
            for geom in geoms:
                CoverageResults = Geo_tool.MeetCoverageRange(json.dumps(geom),
                                                             json.dumps(Planet_feature),
                                                             Coverage[0],
                                                             Coverage[1])
            # If the images don't satisfy the coverage filter, add it into the strip list
            if not any(CoverageResults):
                strip_images.append(Planet_feature)

        # Strip images from the result
        if len(strip_images) > 0:
            for strip_image in strip_images:
                res_json['features'].remove(strip_image)

    # Report and quit the application if there is no result
    if len(res_json['features']) == 0:
        prompt_widget.InfoBox('No result', 'No selected items match the search criterion.')
        sys.exit(0)
    else:
    # Report the result number
        prompt_widget.InfoBox('Search result', 'Found {} matched items.'.format(len(res_json['features'])))

    return res_json
