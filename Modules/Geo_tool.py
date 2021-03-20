# -*- coding: utf-8 -*-
"""
Created on Wed Apr  4 13:54:30 2018

@author: uqytu1
"""
from osgeo import osr, ogr
import json
from . import prompt_widget

def CreateGeojsonFC(AOI):
    # Open geometry
    shp = ogr.Open(AOI)
    lyr = shp.GetLayer()
    LyrDefn = lyr.GetLayerDefn()

    # Transform coordinate to WGS84 geographic crs
    sourceSR = lyr.GetSpatialRef()
    targetSR = osr.SpatialReference()

    # Set the axis order as the traditional x y z way (for gdal above 3)
    try:
        sourceSR.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
        targetSR.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    except AttributeError:
        pass
    
    targetSR.ImportFromEPSG(4326)
    coordTrans = osr.CoordinateTransformation(sourceSR,targetSR)
    
    # Create feature list for storing GeoJson feature collection
    my_features = list()
    
    # Loop through features
    for feat in lyr:
        geom = feat.GetGeometryRef()
        try:
            geom.Transform(coordTrans)
        except TypeError:
            prompt_widget.InfoBox('No projection found', 
                                  'If the CRS is not EPSG::4326, search result may not be desired.')
            pass

        # Flat geometry to 2D and assign it to the transformed feature
        geom.FlattenTo2D()
        transformed_feat = ogr.Feature(LyrDefn)
        transformed_feat.SetGeometry(geom)

        # Create a feature JSON object and strip 'properties' field as we don't need it
        feature = transformed_feat.ExportToJson()
        feature_json = json.loads(feature)
        feature_json.pop('properties')

        # Add the geometry into feature collections
        my_features.append(feature_json)
    
    # Close shapefile
    lyr = None
    shp = None
    
    # Create a Feature Collection geojson
    FeatureCollections = {'type': 'FeatureCollection', 'features': my_features}
    
    return FeatureCollections

def LoadGeoJSON(AOI):
    # This function can check CRS information in a GeoJSON file
    with open(AOI) as json_data:
        #AOI_geojson = geojson.load(json_data)
        AOI_geojson = json.load(json_data)

    # Show warning if no CRS is detected
    if 'crs' not in AOI_geojson.keys():
        prompt_widget.InfoBox('No projection found', 
                              'If the CRS is not EPSG::4326, search result may not be desired.')

    # Transform coordinate to WGS84 geographic crs and convert it back to geojson
    FeatureCollections = CreateGeojsonFC(json.dumps(AOI_geojson))
    
    return FeatureCollections

def CalculateCoverPercentage(AOI_geom, ImageFrame_geom):
    # Create a list of CoverPercentage in case of multipolygon
    CoverPercentage = list()

    AOI_count = AOI_geom.GetGeometryCount()
    # Loop through geometry for every shapes in case it's multipolygon
    for i in range(AOI_count):
        AOI_shp = AOI_geom.GetGeometryRef(i)

        # If the AOI is not a valid polygon. Skip the calculation
        if not AOI_shp.IsValid() or not ImageFrame_geom.IsValid():
            CoverPercentage.append(None)
            continue

        # Get the areas
        AOI_Area = AOI_shp.GetArea()
        ImageFrame_Area = ImageFrame_geom.GetArea()

        # Use AOI as reference to calculate the coverage if the image frame is larger than AOI
        # Otherwise, the coverage is calculated the other way around
        if ImageFrame_Area >= AOI_Area:
            Reference_Area = AOI_Area
        else:
            Reference_Area = ImageFrame_Area

        # Calculate the intersection percentage
        intersection = AOI_shp.Intersection(ImageFrame_geom)
        Cover_Area = intersection.GetArea()
        CoverPercentage.append(int((Cover_Area/Reference_Area)*100))

    return CoverPercentage

def MeetCoverageRange(AOI_geojson, ImageFrame_geojson, _min, _max):
    # Load data as ogr vectors. The GeoJSON inputs must be string
    AOI = ogr.Open(AOI_geojson)
    AOI_lyr = AOI.GetLayer()

    ImageFrame = ogr.Open(ImageFrame_geojson)
    ImageFrame_lyr = ImageFrame.GetLayer()

    # Get the geometry from Image Frame
    ImageFrame_feat = ImageFrame_lyr.GetNextFeature()
    ImageFrame_geom = ImageFrame_feat.GetGeometryRef()

    # Get the feature from AOI. Only one feature per input.
    AOI_feat = AOI_lyr.GetNextFeature()
    AOI_geom = AOI_feat.GetGeometryRef()

    # Get the list of coverage percentage. Null means to skip that AOI
    Coverage = CalculateCoverPercentage(AOI_geom, ImageFrame_geom)

    CoverageResults = list()
    
    for Result in Coverage:
        # If meet the Area Coverage condition or the AOI is invalid polygon, make the coverage valid
        if Result is None:
            CoverageResults.append(True)
        
        elif (Result >= _min and Result <= _max):
            CoverageResults.append(True)

        # Otherwise, invalid coverage percentage
        else:
            CoverageResults.append(False)

    return CoverageResults
