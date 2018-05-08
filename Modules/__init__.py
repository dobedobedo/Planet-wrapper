#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 11:35:46 2018

@author: uqytu1
"""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

from future import standard_library
standard_library.install_aliases()
__all__ = ['Planet_Tool_gui', 'Planet_Tool_cli']

# Define Item ans assets for downloadable planet images 
Items = ['PSScene3Band', 'PSScene4Band', 'PSOrthoTile', 
         'REScene', 'REOrthoTile', 'SkySatScene', 
         'Landsat8L1G', 'Sentinel2L1C']

Items_asset = {
    'PSScene3Band':[
        'analytic', 'analytic_dn', 'analytic_xml', 'analytic_dn_xml', 
        'visual', 'visual_xml', 
        'basic_analytic_dn', 'basic_analytic_dn_xml', 'basic_analytic', 'basic_analytic_xml', 
        'basic_analytic_rpc', 'basic_analytic_dn_rpc', 'basic_udm', 'udm'], 
    'PSScene4Band':[
        'analytic', 'analytic_sr', 'analytic_dn', 'analytic_xml', 'analytic_dn_xml', 
        'basic_analytic', 'basic_analytic_dn', 'basic_analytic_xml', 'basic_analytic_dn_xml', 
        'basic_analytic_nitf', 'basic_analytic_dn_nitf', 'basic_analytic_xml_nitf', 'basic_analytic_dn_xml_nitf', 
        'basic_analytic_rpc', 'basic_analytic_dn_rpc', 'basic_analytic_rpc_nitf', 'basic_analytic_dn_rpc_nitf', 
        'basic_udm', 'udm'], 
    'PSOrthoTile':[
        'analytic', 'analytic_dn', 'analytic_xml', 'analytic_dn_xml', 
        'visual', 'visual_xml', 'udm'], 
    'REScene':[
        'basic_analytic_b1', 'basic_analytic_b2', 'basic_analytic_b3', 'basic_analytic_b4', 'basic_analytic_b5', 
        'basic_analytic_b1_nitf', 'basic_analytic_b2_nitf', 'basic_analytic_b3_nitf', 'basic_analytic_b4_nitf', 
        'basic_analytic_b5_nitf', 'basic_analytic_xml', 'basic_analytic_xml_nitf', 'basic_analytic_sci', 
        'browse', 'basic_analytic_rpc', 'basic_udm'], 
    'REOrthoTile':[
        'analytic', 'analytic_xml', 'visual', 'visual_xml', 'udm'], 
    'SkySatScene':[
        'ortho_visual', 'ortho_analytic_dn', 'ortho_analytic_udm', 'ortho_pansharpened', 
        'ortho_pansharpened_udm', 'ortho_panchromatic_dn', 'ortho_panchromatic_udm', 
        'basic_analytic_dn', 'basic_analytic_dn_rpc', 'basic_panchromatic_dn', 
        'basic_panchromatic_dn_rpc', 'basic_udm'], 
    'Landsat8L1G':[
        'analytic_b1', 'analytic_b2', 'analytic_b3', 'analytic_b4', 'analytic_b5', 'analytic_b6', 
        'analytic_b7', 'analytic_b8', 'analytic_b9', 'analytic_b10', 'analytic_b11', 'analytic_bqa', 
        'metadata_txt'], 
    'Sentinel2L1C':[
        'analytic_b1', 'analytic_b2', 'analytic_b3', 'analytic_b4', 'analytic_b5', 
        'analytic_b6', 'analytic_b7', 'analytic_b8', 'analytic_b8a', 'analytic_b9', 
        'analytic_b10', 'analytic_b11', 'analytic_b12', 'visual', 'metadata_aux']}
