#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  4 13:54:30 2018

@author: uqytu1
"""
from osgeo import osr, ogr
import geojson

def CreateGeojsonFC(AOI):
    # Open shapefile
    shp = ogr.Open(AOI)
    lyr = shp.GetLayer()
    
    # Transform coordinate to WGS84 geographic crs
    sourceSR = lyr.GetSpatialRef()
    targetSR = osr.SpatialReference()
    targetSR.ImportFromEPSG(4326)
    coordTrans = osr.CoordinateTransformation(sourceSR,targetSR)
    
    featList = range(lyr.GetFeatureCount())
    
    # Create feature list for storing GeoJson feature collection
    my_features = list()
    
    for FID in featList:
        feat = lyr.GetFeature(FID)
        geom = feat.GetGeometryRef()
        geom.Transform(coordTrans)
        
        if (geom.GetGeometryName() == 'MULTIPOLYGON'):
            count = 0
            multipoly = list()
            for polygon in geom:
                poly = list()
                geomInner = geom.GetGeometryRef(count)
                ring = geomInner.GetGeometryRef(0)
                numpoints = ring.GetPointCount()
                for p in range(numpoints):
                    x, y, z = ring.GetPoint(p)
                    poly.append((x, y))
                multipoly.append((poly, ))
                count += 1
            feature = geojson.Feature(geometry=geojson.MultiPolygon(multipoly))
            my_features.append(feature)
            
        elif (geom.GetGeometryName() == 'POLYGON'):
            ring = geom.GetGeometryRef(0)
            numpoints = ring.GetPointCount()
            poly = list()
            for p in range(numpoints):
                x, y, z = ring.GetPoint(p)
                poly.append((x, y))
            feature = geojson.Feature(geometry=geojson.Polygon([poly]))
            my_features.append(feature)
                
        elif (geom.GetGeometryName() == 'MULTIPOINT'):
            count = 0
            multipoint = list()
            for point in geom:
                geomInner = geom.GetGeometryRef(count)
                numpoints = geomInner.GetPointCount()
                for p in range(numpoints):
                    x, y, z = geomInner.GetPoint(p)
                    multipoint.append((x, y))
                count += 1
            feature = geojson.Feature(geometry=geojson.MultiPoint(multipoint))
            my_features.append(feature)
                
        elif (geom.GetGeometryName() == 'POINT'):
            x, y, z = geom.GetPoint()
            feature = geojson.Feature(geometry=geojson.Point((x, y)))
            my_features.append(feature)
            
        else:
            continue
    
    # Close shapefile
    lyr = None
    shp = None
    
    FeatureCollections = geojson.FeatureCollection(my_features)
    return FeatureCollections

def LoadGeoJSON(AOI):
    with open(AOI) as json_data:
        AOI_geojson = geojson.load(json_data)
    return AOI_geojson

def PolyFromGeoJSON(AOI):
    poly = ogr.CreateGeometryFromJson(str(AOI['geometry']))
    return poly

def CalculateCoverPercentage(AOI_geojson, ImageFrame_geojson):
    AOI = PolyFromGeoJSON(AOI_geojson)
    AOI_Area = AOI.GetArea()
    ImageFrame = PolyFromGeoJSON(ImageFrame_geojson)
    intersection = AOI.Intersection(ImageFrame)
    Cover_Area = intersection.GetArea()
    CoverPercentage = int((Cover_Area/AOI_Area)*100)
    return CoverPercentage
    