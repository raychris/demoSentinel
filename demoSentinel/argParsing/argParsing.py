'''Command line interface argument handling'''

import argparse
import textwrap    

def getArguments(argList):
    '''Get arguments from the command line interface and return parsed arguments'''
    description = textwrap.dedent('''\
                                       A python package that performs the following tasks
​
                                       1) access to ESA ShiHub database (requires signin up to ESA ShiHub)
                                       2) download of Sentinel-1 (GRD) images acquired between date_start and date_stop that instersect with point_coord
                                       3) download of Sentinel-2 images acquired between date_start and date_stop that instersect with point_coord
                                       4) group the downloladed images into sub-series of perfectly spatially superimposable images
                                       5) compute cumulative NDVI for each Sentinel-2 sub-series
                                       6) compute the temporal mean of backscattering values for each Sentinel-1 sub-series''')

    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    addArguments(parser, argList)
    return parser.parse_args()

def addArguments(parser, argList):
    '''Define how arguments available to the command line interface should be parsed'''
    parser.add_argument('--date_start',
                        help='iso-format date, 2023-05-27T00:00:00.000Z')
    parser.add_argument('--date_stop',
                        help='iso-format date, 2023-05-27T00:00:00.000Z')
    parser.add_argument('--point_coord',
                        help='lat-long point, (longitude, latitude)')
    parser.add_argument('--api_username',
                        help='api username')
    parser.add_argument('--api_password',
                        help='api password')
    parser.add_argument('--base_path',
                        help='base path for output (downloaded files, intermediate files)')