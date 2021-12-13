# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 11:35:46 2018

@author: uqytu1
"""

# Define the available functions
__all__ = ['auth', 'Planet_Search', 'Planet_Request', 'Planet_Download']

# Define Item ans assets for downloadable planet images
# This is the complete list
__Items_assets = {'PSScene': ['ortho_analytic_4b', 'ortho_analytic_8b', 'ortho_analytic_8b_sr', 'ortho_analytic_8b_xml', 
                              'ortho_analytic_4b_sr', 'ortho_analytic_4b_xml', 'basic_analytic_4b', 'basic_analytic_8b', 
                              'basic_analytic_8b_xml', 'basic_analytic_4b_rpc', 'basic_analytic_4b_xml', 
                              'basic_udm2', 'ortho_udm2', 'ortho_visual'], 
                  'PSScene3Band': ['analytic', 'analytic_dn', 'analytic_dn_xml', 'analytic_xml',
                                   'basic_analytic', 'basic_analytic_dn', 'basic_analytic_dn_rpc',
                                   'basic_analytic_dn_xml', 'basic_analytic_rpc', 'basic_analytic_xml',
                                   'basic_udm', 'basic_udm2', 'udm', 'udm2',
                                   'visual', 'visual_xml'],
                  'PSScene4Band': ['analytic', 'analytic_dn', 'analytic_dn_xml', 'analytic_sr', 'analytic_xml',
                                   'basic_analytic', 'basic_analytic_dn', 'basic_analytic_dn_nitf',
                                   'basic_analytic_dn_rpc', 'basic_analytic_dn_rpc_nitf',
                                   'basic_analytic_dn_xml', 'basic_analytic_dn_xml_nitf	',
                                   'basic_analytic_nitf', 'basic_analytic_rpc', 'basic_analytic_rpc_nitf',
                                   'basic_analytic_xml', 'basic_analytic_xml_nitf',
                                   'basic_udm', 'basic_udm2', 'udm', 'udm2'],
                  'PSOrthoTile': ['analytic', 'analytic_5b', 'analytic_5b_xml',
                                  'analytic_dn', 'analytic_dn_xml', 'analytic_sr', 'analytic_xml',
                                  'visual', 'visual_xml', 'udm', 'udm2'],
                  'REScene': ['basic_analytic_b1', 'basic_analytic_b1_nitf', 'basic_analytic_b2', 'basic_analytic_b2_nitf',
                              'basic_analytic_b3', 'basic_analytic_b3_nitf', 'basic_analytic_b4', 'basic_analytic_b4_nitf',
                              'basic_analytic_b5', 'basic_analytic_b5_nitf', 'basic_analytic_xml', 'basic_analytic_xml_nitf',
                              'basic_analytic_sci', 'basic_analytic_rpc', 'basic_udm', 'browse'],
                  'REOrthoTile': ['analytic', 'analytic_sr', 'analytic_xml',
                                  'udm', 'visual', 'visual_xml'],
                  'SkySatScene': ['basic_analytic', 'basic_analytic_dn', 'basic_analytic_dn_rpc', 'basic_analytic_rpc',
                                  'basic_analytic_udm', 'basic_analytic_udm2', 'basic_l1a_panchromatic_dn', 'basic_l1a_panchromatic_dn_rpc',
                                  'basic_panchromatic', 'basic_panchromatic_dn', 'basic_panchromatic_dn_rpc',
                                  'basic_panchromatic_rpc', 'basic_panchromatic_udm2',
                                  'ortho_analytic', 'ortho_analytic_sr', 'ortho_analytic_dn', 'ortho_analytic_udm', 'ortho_analytic_udm2',
                                  'ortho_panchromatic', 'ortho_panchromatic_dn', 'ortho_panchromatic_udm', 'ortho_panchromatic_udm2',
                                  'ortho_pansharpened', 'ortho_pansharpened_udm', 'ortho_pansharpened_udm2', 'ortho_visual'],
                  'SkySatCollect': ['basic_l1a_all_frames', 'ortho_analytic', 'ortho_analytic_sr', 'ortho_analytic_dn',
                                    'ortho_analytic_udm', 'ortho_analytic_udm2',
                                    'ortho_panchromatic', 'ortho_panchromatic_dn', 'ortho_panchromatic_udm', 'ortho_panchromatic_udm2',
                                    'ortho_pansharpened', 'ortho_pansharpened_udm', 'ortho_pansharpened_udm2', 'ortho_visual'],
                  'SkySatVideo': ['video_file', 'video_frames', 'video_metadata'],
                  'Landsat8L1G': ['analytic_b1', 'analytic_b2', 'analytic_b3', 'analytic_b4', 'analytic_b5', 'analytic_b6',
                                  'analytic_b7', 'analytic_b8', 'analytic_b9', 'analytic_b10', 'analytic_b11',
                                  'analytic_bqa', 'metadata_txt', 'visual'],
                  'Sentinel2L1C': ['analytic_b1', 'analytic_b2', 'analytic_b3', 'analytic_b4', 'analytic_b5', 'analytic_b6',
                                   'analytic_b7', 'analytic_b8', 'analytic_b8a', 'analytic_b9', 'analytic_b10', 'analytic_b11', 'analytic_b12',
                                   'metadata_aux', 'visual']}

# These are the product bundle names used for order API
_Items_assets = {'PSScene': ['analytic_udm2', 'analytic_8b_udm2', 'visual', 'basic_analytic_udm2', 
                              'basic_analytic_8b_udm2', 'analytic_sr_udm2', 'analytic_8b_sr_udm2'], 
                 'PSScene3Band': ['analytic', 'visual', 'uncalibrated_dn', 'basic_analytic', 
                                  'basic_uncalibrated_dn'],
                 'PSScene4Band': ['analytic', 'analytic_udm2', 'uncalibrated_dn', 'uncalibrated_dn_udm2', 
                                  'basic_analytic', 'basic_analytic_udm2', 'basic_uncalibrated_dn', 'basic_uncalibrated_dn_udm2', 
                                  'analytic_sr', 'analytic_sr_udm2', 'basic_uncalibrated_dn_nitf', 'basic_uncalibrated_dn_nitf_udm2', 
                                  'basic_analytic_nitf', 'basic_analytic_nitf_udm2'],
                 'PSOrthoTile': ['analytic', 'analytic_udm2', 'analytic_5b', 'analytic_5b_udm2', 
                                 'visual', 'uncalibrated_dn', 'uncalibrated_dn_udm2', 'analytic_sr', 
                                 'analytic_sr_udm2'],
                 'REScene': ['basic_analytic', 'basic_analytic_nitf'],
                 'REOrthoTile': ['analytic', 'visual', 'analytic_sr'],
                 'SkySatScene': ['analytic', 'analytic_udm2', 'visual', 'uncalibrated_dn', 
                                 'uncalibrated_dn_udm2', 'basic_analytic', 'basic_analytic_udm2', 'basic_uncalibrated_dn', 
                                 'basic_uncalibrated_dn_udm2', 'analytic_sr', 'analytic_sr_udm2', 'basic_panchromatic', 
                                 'basic_panchromatic_dn', 'panchromatic', 'panchromatic_dn', 'panchromatic_dn_udm2', 
                                 'pansharpened', 'pansharpened_udm2', 'basic_l1a_dn'],
                 'SkySatCollect': ['analytic', 'analytic_udm2', 'visual', 'uncalibrated_dn', 
                                   'uncalibrated_dn_udm2', 'analytic_sr', 'analytic_sr_udm2', 'panchromatic', 
                                   'panchromatic_dn', 'panchromatic_dn_udm2', 'pansharpened', 'pansharpened_udm2', 
                                   'basic_l1a_dn'],
                 'SkySatVideo': ['video_file', 'video_frames', 'video_metadata'],
                 'Landsat8L1G': ['analytic', 'visual'],
                 'Sentinel2L1C': ['analytic', 'visual']}

# Define the planet URLs
_planet_url =  {'data': 'https://api.planet.com/data/v1',
                'order': 'https://api.planet.com/compute/ops/orders/v2'}

# Define the support input AOI format
_AOI_filetype = [('Shapefile', ['*.shp', '*.SHP', '*.Shp']), 
                 ('GeoJSON', ['*.geojson', '*.GEOJSON', '*.json', '*.JSON']),
                 ('Keyhole Markup Language', ['*.kml', '*.KML']), 
                 ('GeoPackage', ['*.gpkg', '*.GPKG'])]

# Define the filter options
_filter_properties = {'Date': {'type': 'Date',
                               'field_name': 'acquired'},
                     'Area Coverage': {'type': 'Range',
                                       'field_name': None,
                                       'min': 0,
                                       'max': 100},
                     'Cloud Cover': {'type': 'Range',
                                     'field_name': 'cloud_cover',
                                     'min': 0,
                                     'max': 100,
                                     'scale': 100},
                     'Ground Sample Distance': {'type': 'Range',
                                                'field_name': 'gsd',
                                                'min': 0.1,
                                                'max': 30},
                     'Off-nadir Angle': {'type': 'Range',
                                         'field_name': 'view_angle',
                                         'min': -60,
                                         'max': 60},
                     'Sun Azimuth': {'type': 'Range',
                                     'field_name': 'sun_azimuth',
                                     'min': 0,
                                     'max': 360},
                     'Sun Elevation': {'type': 'Range',
                                       'field_name': 'sun_elevation',
                                       'min': -90,
                                       'max': 90},
                     'Ground Control': {'type': 'Bool',
                                        'field_name': 'ground_control'}}
