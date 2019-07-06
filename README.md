# Sentinel 2 LC1-L2A Automatic Product Downloader

## Introduction:

A program that allows you to automatically download multiple Sentinel LC1/L2A products givin a certain location, time frame and sensing frequency. This program was created to allow for easy gathering of Sentinel 2 data by eliminating the need for manual searching and processing and to allow for the ability to see how specific locations change over time. Each Sentinel 2 LC1/LC2 products are availible in 100 km^2 size which means that A: product sizes can be very large and B: might not cover the entire area of interest. These problems are combated here as this program will download all the products that cover the area of interest, stich them together and then crop out the area that you are intersted in. Meaning that you only have to process the areas that you are interested. This program also prioritises getting the products with the smallest amount of cloud cover.   

## Dependencies:

This program was written in Windows 10 using Python 3.6 anad an Anaconda installation. Python 3.6 can be downloaded [here](https://repo.continuum.io/archive/), I use `Anaconda3-5.2.0-Windows-x86_64.exe`. 

The following python packages are needed and can be install via `PIP`: `sentinelsat, datetime, glob, os, utm, zipfile, numpy, pyproj,  pandas, re, pygeoj`.

The following python packages are also needed and can be downloaded [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/): `rasterio, shapely, gdal`.

Navigate in the terminal to your download location and you can `PIP` install them from there:
 `pip install rasterio-0.24.0-cp27-none-win32.whl`

## Getting Started:

Providing you have all the dependencies installed, running the program should be pretty straight forward and you should only need to change the following variables: 

`Username = "USERNAME"`    
`Password = "PASSWORD"`        

`footprintName = "Donegal" #name of .geojson file `   
`geoJsonFolder = 'D:/Documents/Programming/hello/GEOFiles/`     

`start_date = "2016-6-1"`    
`end_date = "2019-6-10"`     
`frequency = 8`
`productLevel = 'L1C'`

`download_folder = 'E:/Products'`        
`productSize = 650`    

`Username, Password`: this is the username and password that give authentication for the Sentinel servers. Creeate and account [here](https://scihub.copernicus.eu/dhus/#/self-registration). 

`footprintName`: Area of Earth that you are intersted in, you can use [this](http://geojson.io). Select your area of interest with the square or polygon tool, then save, save as .GeoJson. Save it to desired location and update directory location below:    
`geoJsonFolder = 'D:/Documents/Programming/hello/GEOFiles/`     

`start_date = "2016-6-1"`: Enter you start date for the timeperiod you are interested in. YYYY-M-D format.        
`end_date = "2019-6-10"`: Enter the end date for the time period that you are interested in. YYYY-M-D format.     
`frequency = 8`: Frequency that you want to download products for, measured in days. For this example it will download one set of products every 8 days from the start time that was specified before.     
`productLevel = 'L1C'`: Specify L1C or L2A, L1C denotes radiometric measurements from the Top Of Atmosphere whild L2A are Bottom of Atmosphere readings, they are L1C products that have had atmostphereic corrections applied to them.     

`download_folder = 'E:/Products'`: download folder location for products.            
`productSize = 650`: Size of the product, measured in MB and ranging between 0 and approx 1200, this is used to ensure that the product returned has as close to the 100 x 100 km of data. Due to the way that Sentinel scans it might return a product that is very small, hence holding only a few pieces of useful data. The higher this number the more chance that there will be no blank areas in the finished cropped mosaic but will result in having a higher cloud coverage. The smaller it is the lower the cloud coverage percentage will be but the greater the chance the cropped mosaic will have missing data. I have had good results with setting this value to 650.     

## Further Notes:

The quantities of products that this program will download will vary greatly depending on the size of the interest area and the frequency size selected. Theoretically you can create a .geojson file of any size on the Earth and it will download and create a mosaic of the geojson file. Each sentinel product is approximatly 800 MB and it might need several to cover the selected area. Consquently each of the finished cropped mosaics could be several hundred megabytes each. And if you set a large frequency it will have to download the same number of products again for each time period. 

The smaller the sensing period, the greater the cloud coverage percentage will be on the finished cropped mosaic. This is due to Sentinels sensing time, each point on Earth is scanned approximatly once every five days and its down to chance how much cloud there will be then. For optimal results I have found setting the frequency to 30 (once a month) is a good place to start. 

If you download L1C products, the cropped mosaic will have a resolution of 1 pixel is 10m square. If you download L2A products, it will create three mosaics of resolution: 10m, 20, and 60m. Depending on your desired resololution this will allow for easier to manage files. 

## Folder Structure: 

Once the program runs successfully, you will have the following folders and files for example:

Top folder: `2018-6-1 - 2018-7-10_Donegal_30_L2A`, here the star date, end date, area of interest, frequency and product level are listed. 

Inside you will have multiple subfolder for each time period:    
Sub folder: `20180601 - 201806031`    
            `20180631 - 201807030`    
            `20180730 - 201808029`     
            `etc`    
You should have same number of folders for the frequency that you set. 
            
Inside each subfolder you will have `Cropped_Image_Bands`, that will include the finished cropped mosaic, the downloaded zip files and extracted products used to create the cropped mosaic and `Time Period Meta Data` containing metadata about the cropped mosaic. Inside the `Cropped_Image_Bands` folder you will find the resultant cropped mosaics, included in the are each of the images bands files names. The three folders; `R10, R20, R60`, contain the different resolutions of images.     


