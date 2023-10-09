# WELCOME
This package demonstrates the ability to perform the following tasks:

1. access to ESA SciHub database (requires signin up to ESA SciHub)
2. download of Sentinel-1 (GRD) images acquired between date_start and date_stop that instersect with point_coord
3. download of Sentinel-2 images acquired between date_start and date_stop that instersect with point_coord
4. group the downloladed images into sub-series of perfectly spatially superimposable images (INCOMPLETE for Sentinel-1)
5. compute cumulative NDVI for each Sentinel-2 sub-series (See the sampleOutput directory in this repo for examples)
6. compute the temporal mean of backscattering values for each Sentinel-1 sub-series (INCOMPLETE)

# GETTING STARTED
This package is designed to run on a linux operating system.  It was tested on RHEL 8.

## Documentation
Documentation is hosted at https://raychris.github.io/demoSentinel/index.html

## Setting up the environment
After cloning the repository to your machine to /your/local/directory, set two environment variables using bash.

```
export PYTHONPATH=$PYTHONPATH:/your/local/directory># lets python find the package
export LOGDIR=/your/log/directory # log files will go here
```

Next set up your python environment using conda
```
cd /your/local/directory
conda env create -f environment.yml
conda activate fbk
```

## Try it out
```
python /your/local/directory/demoSentinel/demoSentinel/runIt.py \
--date_start 2023-03-01T00:00:00.000Z \
--date_stop 2023-05-29T00:00:00.000Z \
--point_coord (11.1217,46.0748) \
--api_username username \
--api_password password \
--base_path /a/place/to/put/output \
/
```

## Command line help

For help from the command line
```
python /your/local/directory/demoSentinel/demoSentinel/runIt.py --help
```
