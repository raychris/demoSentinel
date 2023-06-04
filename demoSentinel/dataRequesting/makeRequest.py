'''module for making data requests'''

import requests
import http
import datetime
from sentinelsat import SentinelAPI, geojson_to_wkt, make_path_filter
import os
from osgeo import gdal, osr
import numpy

from demoSentinel.geospatialOps.makeGeometry import makeGeoJsonPoint
from demoSentinel.appLogging.appLogging import enableLogging
log = enableLogging()

def findProducts(username,password,coordinate,platformName,dateStart,dateStop,maxNumberResults=10):
    '''http request for the data
    
    Parameters
    ----------
    coordinate : tuple
        tuple in form of (longitude, latitude)
    platformName : str
        either Sentinel-1 or Sentinel-2
    dataStart : str
        yyyy-MM-ddThh:mm:ss.SSSZ (ISO8601 format)
    dateStop : str
        yyyy-MM-ddThh:mm:ss.SSSZ (ISO8601 format)

    Notes
    -----
    https://sentinelsat.readthedocs.io
    
    '''

    apiUrl = 'https://apihub.copernicus.eu/apihub'

    try:
        # authenticate to api
        api = SentinelAPI(username,password,apiUrl)
        # build point geometry for seach
        point = makeGeoJsonPoint(longitude=coordinate[0],latitude=coordinate[1])
        # query the api
        availableProducts = api.query(area=geojson_to_wkt(point),
                                        date=(dateStart,dateStop),
                                        area_relation='Intersects',
                                        limit=maxNumberResults,
                                        platformname=platformName,
                                        cloudcoverpercentage=(0,10),
                                        producttype='S2MSI2A')
        return api,availableProducts

    except Exception as e:
        log.warning('The http request failed to reach the endpoint.\nAn unexpected error occurred.')
        log.warning(e)

def downloadProducts(api,idList,basePath):
    '''download products
    
    Parameter
    ---------
    api : object
        SentinelApi object
    availableProducts : dictionary
        dictionary of available products from the api
    basePath : str
        location for output

    
    
    '''

    pathFilterb4 = make_path_filter("*B04*60m*")
    pathFilterb8 = make_path_filter("*B8A*60m*")
    pathFilterSCL = make_path_filter('*SCL*60m*')
    for id in idList:
        api.download(id,basePath,nodefilter=pathFilterb4)
        api.download(id,basePath,nodefilter=pathFilterb8)
        api.download(id,basePath,nodefilter=pathFilterSCL)

def makeRasters(pathToData):
    '''use datasets to make a multiband raster'''
    geoTransform = None
    rowsCount = None
    columnsCount = None
    dataType = None
    srs = osr.SpatialReference()
    # all in wgs 84
    srs.ImportFromEPSG(4326)
    # make a geotiff
    driver = gdal.GetDriverByName('Gtiff')
    outPath = None
    for i,file in enumerate(os.listdir(pathToData)):
        filepath = os.path.join(pathToData,file)
        ds = gdal.Open(filepath)
        band = ds.GetRasterBand(1)
        # put b04 in outband 1, b8a in 2, scl in 3
        if 'B04' in file:
            outBand = 1
        elif 'B8A' in file:
            outBand = 2
        elif 'SCL' in file:
            outBand = 3
        elif 'tif' in file:
            continue
        else:
            log.warning('Found an unexpected file')
            exit('Exiting')
        # first time through get details for output
        if i == 0:
            outPath = os.path.join(pathToData,file.split('_')[0]+'_'+file.split('_')[1]+'.tif')
            geoTransform = ds.GetGeoTransform()
            rowsCount = ds.RasterYSize
            columnsCount = ds.RasterXSize
            dataType = band.DataType
            outFile = driver.Create(outPath,xsize=columnsCount,ysize=rowsCount,bands=4,eType=gdal.GDT_Float32)
            outFile.SetGeoTransform(geoTransform)
            outFile.SetProjection(srs.ExportToWkt())
            outFile = None
        outFile = gdal.Open(outPath,gdal.GA_Update)
        log.info('Adding {} to {}'.format(filepath,outPath))
        outFile.GetRasterBand(outBand).WriteArray(band.ReadAsArray())
        outFile.FlushCache()
        outFile = None
        ds = None
    log.info('Finished writing {}'.format(outPath))
    return outPath

def addNDVIBand(pathToGeoTiff):
    '''Add NDVI band to Sentinel-2 geotiffs (with SCL mask to only include SCL 4-7 inclusive)
    
    Parameters
    ----------
    pathToGeoTiff : str
        path to geotiff with Sentinel-2 channels 4 and 8


    Notes
    -----
    https://custom-scripts.sentinel-hub.com/custom-scripts/sentinel-2/ndvi/
    NDVI =(b8-b4)/(b8+b4)

    
    
    '''

    inRaster = gdal.Open(pathToGeoTiff,gdal.GA_Update)
    b4 = inRaster.GetRasterBand(1).ReadAsArray()
    b8 = inRaster.GetRasterBand(2).ReadAsArray()
    scl = inRaster.GetRasterBand(3).ReadAsArray()
    ndvi = (b8-b4)/(b4+b8)
    # use scl to set ndvi elements to 10000 if scl is outside of 4-7
    # label keepers 1 and others 0
    sclMask = numpy.where((scl<4) | (scl>7),0,1)
    # indices of others
    zeroIndices = numpy.where(sclMask==0)
    # set elements of ndvi to 10000 at zeroIndices locations
    ndvi[zeroIndices] = 10000
    # add ndvi to inRaster
    inRaster.GetRasterBand(4).WriteArray(ndvi)
    inRaster.FlushCache()
    inRaster = None

def createCumulativeNdviRaster(paths,basePath):
    '''Create a single band raster with cumulative ndvi.
    define cumulative ndvi as a running sum of ndvi for each pixel at each time step

    Parameters
    ----------
    paths : list
        list of paths to geotiffs with calculated ndvi bands
    basePath : str
        place to send output
    
    '''

    ndviArrays = []
    outPath = os.path.join(basePath,'cumulativeNDVI.tif')
    for i,path in enumerate(paths):
        inRaster = gdal.Open(path)
        ndviBand = inRaster.GetRasterBand(4).ReadAsArray()
        ndviArrays.append(ndviBand)
        # first time through get details for output
        if i == 0:
            srs = osr.SpatialReference()
            # all in wgs 84
            srs.ImportFromEPSG(4326)
            # make a geotiff
            driver = gdal.GetDriverByName('Gtiff')
            geoTransform = inRaster.GetGeoTransform()
            rowsCount = inRaster.RasterYSize
            columnsCount = inRaster.RasterXSize
            outFile = driver.Create(outPath,xsize=columnsCount,ysize=rowsCount,bands=1,eType=gdal.GDT_Float32)
            outFile.SetGeoTransform(geoTransform)
            outFile.SetProjection(srs.ExportToWkt())
            outFile = None
    
    cumulativeNdvi = None
    for i,ndvi in enumerate(ndviArrays):
        if i == 0:
            cumulativeNdvi = ndvi
        else:
            cumulativeNdvi = cumulativeNdvi + ndvi
        # sort out where a pixel was masked and adjust sums
        # keep mask value at 10000
        cumulativeNdvi = numpy.where(cumulativeNdvi>10000, cumulativeNdvi-10000,cumulativeNdvi)
    # account for some negative values
    cumulativeNdvi = numpy.where((cumulativeNdvi>9000) & (cumulativeNdvi!=10000), cumulativeNdvi-10000,cumulativeNdvi)
    log.info('Writing cumulative NDVI file to {}'.format(outPath))

    outRaster = gdal.Open(outPath,gdal.GA_Update)
    # add cumulativeNdvi to outRaster
    outBand = outRaster.GetRasterBand(1)
    outBand.WriteArray(cumulativeNdvi)
    outBand.SetNoDataValue(10000)
    outRaster.FlushCache()
    outRaster = None




