'''command line interface for running this package'''

import os

from demoSentinel.appLogging.appLogging import enableLogging
from demoSentinel.argParsing.argParsing import getArguments
from demoSentinel.dataRequesting.makeRequest import findProducts, downloadProducts, makeRasters, addNDVIBand, createCumulativeNdviRaster

#turn on logging
log = enableLogging()

def main():
    '''drive the package'''
    

    #get the command line input

    #get the __dict__ attribute of the returned argparse.Namespace object
    commandLineArgs = vars(getArguments(argList=None))

    for platformName in ['Sentinel-2']:
        api, availableProducts = findProducts(username=commandLineArgs['api_username'],
                                        password=commandLineArgs['api_password'],
                                        platformName=platformName,
                                        dateStart=commandLineArgs['date_start'],
                                        dateStop=commandLineArgs['date_stop'],
                                        coordinate=eval(commandLineArgs['point_coord']))
        
        # organize the api response
        gdf = api.to_geodataframe(availableProducts)
        
        # download the products
        log.info('downloading products')
        downloadProducts(api,gdf['uuid'],basePath=commandLineArgs['base_path'])

        pathsS2 = []
        # create a geotiff for each group of downloaded products
        for path in gdf['identifier'].values:
            subdir = [ dir[0] for dir in os.walk(os.path.join(commandLineArgs['base_path'],path+'.SAFE')) if 'R60m' in dir[0] ]
            outPath = makeRasters(subdir[0])
            pathsS2.append(outPath)
        # add ndvi band to geotiffs
        for path in pathsS2:
            addNDVIBand(pathToGeoTiff=path)
        # create a cumulative ndvi raster
        createCumulativeNdviRaster(paths=pathsS2,basePath=commandLineArgs['base_path'])



if __name__ == '__main__':
    main()