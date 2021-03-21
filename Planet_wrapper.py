#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 12:06:17 2018

@author: uqytu1
"""
from Modules import auth, Planet_Search, Planet_Request, Planet_Download

if __name__ == '__main__':
    # Authentication
    API_KEY, Avail_Items = auth.main()

    # Search
    planet_request, selected_assets, AOI_geojson, CoverageRange = Planet_Search.main(Avail_Items)
            
    # Get the requested results
    planet_result = Planet_Request.main(API_KEY, planet_request, AOI_geojson, CoverageRange)

    # Create order and download
    Planet_Download.main(API_KEY, planet_result, selected_assets)
