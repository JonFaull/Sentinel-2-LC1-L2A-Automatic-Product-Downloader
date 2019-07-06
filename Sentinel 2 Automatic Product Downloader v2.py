from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
import datetime
from datetime import date
import rasterio
from rasterio import merge
from rasterio.warp import calculate_default_transform, reproject, Resampling
import glob
import os
import utm
import zipfile
import shapely 
import numpy as np
from shapely.geometry import box, Point
import pyproj
import pandas as pd 
import re
import pygeoj
#from colortools import Color


def download_products(starting_date, ending_date): # Download products, given start and end time and desired search area. 
  
  #Retrieve products for that map
  products = api.query(footprint,
                              date=(starting_date, ending_date), #search between dates
                              #date=('20190201', date(2019, 2, 14)), #search between dates
                              platformname='Sentinel-2',
                              cloudcoverpercentage=(0, 100)) #set cloud coverage percental


  products_df = api.to_dataframe(products) #create pandas data frame of availible products

  
  products_df_sorted = products_df.sort_values(['cloudcoverpercentage', 'ingestiondate'], ascending=[True, True]) #sort by cloud coverage and ingestiondate
  products_df_sorted = products_df_sorted.head(8000)


  lengthDF = len(products_df_sorted.index) #Get the length of the Pandas data frame that has all the products in it. 
  tileids_and_uuids = {} #Create empty dictionary
  
  sensingDate = starting_date + ' - ' + ending_date
  sensingDateSaveLocation = downloadFileLocation + '/' + sensingDate + '/'  
  
  if not os.path.exists(sensingDateSaveLocation): #check to see if save folder exists and creates it if not. 
    os.makedirs(sensingDateSaveLocation)
  
  y = 1
  
  for i in range(lengthDF): #Search through all products in data frame
      product = products_df_sorted.iloc[i]
      
      tileid = product['tileid'] #get tileid from Data frame
      uuid = product['uuid'] #get uuid from Data frame
      ingestiondate = product['ingestiondate']
      
      cloudcover =  product['cloudcoverpercentage']
      
      fileSize = product['size'] #Used to get size, small files only contain small areas of data and are undeisrable, see if statement later, want file sizes about 400 mb. 
      fileSizeString = fileSize.split('.')
      fileSizeInteger = int(fileSizeString[0])
    
      title  = product['title']

      titleRegex = re.compile(r'_\D\d\d\D\D\D_')
      
      tileIdName = titleRegex.search(title)
      tile_id = tileIdName.group()
     
      
      if productLevel == 'L1C':
          LcLevelRegex = re.compile(r'^........1C')
      elif productLevel == 'L2A':
          LcLevelRegex = re.compile(r'^........2A') 
          
      
      if len(str(tile_id)) == 8: #Only look for products that have 5 charecters in them, tiles only have 5.
        if tile_id not in tileids_and_uuids: #see if that tile is allready in the dictionary. 
          if (LcLevelRegex.search(title) and fileSizeInteger > productSize):            
            tileids_and_uuids[tile_id] = uuid #wright that tileid and uuid to dictionary.  
            
          print(y, 'Tile_id:', tile_id, tileid, 'UUID:', uuid, 'Ingestion Date:', ingestiondate, 'cloud coverage:', cloudcover)
          
        y = y + 1
      
  dicLength = len(tileids_and_uuids)
  print("There are:", dicLength, "products to download")
  

  metaDataLocation = sensingDateSaveLocation + '/Time_Period_Meta_Data.csv'
  metaDataFile =  open(metaDataLocation, 'w') #Creates metadata .csv file and deletes any old one. 
  metaDataFile.close() 

  print(tileids_and_uuids)
  print('There are ', len(tileids_and_uuids), 'products to download.')
  
  x = 1
  Tile = 1
  
  for key, value in tileids_and_uuids.items():
    print(x, 'This is the UUID of to download: ', value)
    x = x + 1
    
    
    get_metadata = api.get_product_odata(value, full=True) #Get Metadata of file and writes it to file. 
    metadata_df = api.to_dataframe(get_metadata)
    metadata = pd.DataFrame(data = metadata_df)
    
    
    tileNo = 'Tile ' + str(Tile) + ':' + '\n'
    
    metaDataFile =  open(metaDataLocation, 'a')


    metaDataFile.write(tileNo)

    
    metadata.to_csv(metaDataFile, mode = metadata, index = True, columns = metadata)
    metaDataFile.write('\n')

    print(metadata)
    Tile = Tile + 1 
    
    api.download(value, sensingDateSaveLocation) #Download product

  root = sensingDateSaveLocation
  
  
  for file in os.listdir(root): #extract files
    if file.endswith(".zip"): #find file ending with .zip
      print('Extracting:', file)
      file_location = os.path.join(root, file) #join the folder location with the zip file name
      print(file_location)
      zip_ref = zipfile.ZipFile(file_location, 'r') #read the file location
      zip_ref.extractall(root) #extract
      zip_ref.close()
  
  print("Products for time period have been downloaded.")


def geojsonLocation(geoJson_name, geoJon_location):
    
    footprintLocation = geoJon_location + geoJson_name + '.geojson' #geojson file location
    footprint = geojson_to_wkt(read_geojson(footprintLocation))
    
    return footprintLocation, footprint 
    

def cropped_mosaic(downloadFileLocation, footprintLocation): #For creating a mosaic of each band and cropping to the desired area from geojson file. 

    
    
    
    geojsonFile = pygeoj.load(filepath = footprintLocation) #load the bounds (edge) of geojson file
    
    #geojsonFile = pygeoj.load(filepath='D:/Documents/Programming/hello/GEOFiles/galway.geojson')
    
    print('bounds for Geojson = ', geojsonFile.bbox)



    Geojson_bounds = geojsonFile.bbox 
    print(Geojson_bounds)

    
    
    left = Geojson_bounds[0] #set bounds to variables
    bottom = Geojson_bounds[1]
    right = Geojson_bounds[2]
    top = Geojson_bounds[3]
    
    print('top =',top, 'left =', left, 'bottom =', bottom, 'right =', right)
    
    
    
    print('type = ', type(left))


    u = utm.from_latlon(bottom, left) #convert lat and long bounds to UTM bounds for files. 
    left = u[0]
    bottom = u[1]



    v = utm.from_latlon(top, right)
    right = v[0]
    top = v[1]

    print(u)

    

    folder = downloadFileLocation + '/*'
    projectFolder = glob.glob(folder)
    print(projectFolder)

    for timePeriod in projectFolder:
        print('the time period is', timePeriod)
    
        path = timePeriod


        times = path.split("\\")
        time = times[-1]
    
        BandsFolder = path + '/Cropped_Image_Bands' #location of folder to save images to
    
        if not os.path.exists(BandsFolder): #check to see if save folder exists and creates it if not. creates above folder if not all ready created.
            os.makedirs(BandsFolder)


        files = [] 
        for r, d, f in os.walk(path): #get list of .jp2 files. 
            for file in f:
                if '.jp2' in file:
                    files.append(os.path.join(r, file))
                    print(file)

        print(files)

        if productLevel == 'L1C':
            for i in range(1, 16):
                print(i)

                src_files_to_mosaic = []
        
                if i <= 12: #create search conditions 
                    number = str(i).zfill(2)
                    imageNo = 'B' + number + '.jp2$' 
                    name = time + '_B' + number
                    print(imageNo)
                elif i == 13:
                    imageNo = str('B8A.jp2$') 
                    name = time +'_B8A'
                    print(imageNo)
                elif i == 14:
                    imageNo = str('TCI.jp2$')
                    name = time + '_TCI'
                    print(imageNo)
                elif i == 15:
                    imageNo = str('PVI.jp2$')
                    name = time + '_PVI'
                    print(imageNo)
        
        
                fileRegex = re.compile(imageNo)

                foundFiles = list(filter(fileRegex.findall, files)) #find all files that have same ending, B01.jp2 etc. 
                print('files to create image from:', foundFiles)
                print(len(foundFiles))

        
                src_files_to_mosaic = [] 
                for fp in foundFiles: # open .jp2 images and write to list.  
                    src = rasterio.open(fp)
                    src_files_to_mosaic.append(src)
                    print(src.bounds)
            

                print(src_files_to_mosaic)
                print(len(src_files_to_mosaic))

                bounds = (left, bottom, right, top)
        
                mosaic, out_trans = rasterio.merge.merge(src_files_to_mosaic, bounds = bounds) #Merge rasters, bounds = None or bounds 

                out_meta = src.meta.copy() #Copy the metadata
                crsFile = rasterio.open(foundFiles[0])

                out_meta.update({"driver": "GTiff", # Update the metadata
                                 "height": mosaic.shape[1],
                                 "width": mosaic.shape[2],
                                 "transform": out_trans
                                #"crs": crsFile.crs #"+proj=utm +zone=35 +ellps=GRS80 +units=m +no_defs "
                                }
                                )

                L1Cpath = BandsFolder + '/Level_1C_Data'

                if not os.path.exists(L1Cpath): #check to see if save folder exists and creates it if not. creates above folder if not all ready created.
                    os.makedirs(L1Cpath)
                
                
                saveLocationName = L1Cpath + '/' + name + '.tiff'


                with rasterio.open(saveLocationName, "w", **out_meta) as dest: #Write the mosaic raster to disk
                    dest.write(mosaic)

                print("Cropping Complete")

        elif productLevel == 'L2A':
            
            bandNames = ['AOT_10m','B02_10m','B03_10m','B04_10m','B08_10m','TCI_10m','WVP_10m','AOT_20m','B02_20m','B03_20m','B04_20m','B05_20m','B06_20m',
                        'B07_20m','B11_20m','B12_20m','B8A_20m','SCL_20m','TCI_20m','WVP_20m','AOT_60m','B01_60m','B02_60m','B03_60m','B04_60m','B05_60m','B06_60m','B07_60m','B09_60m','B11_60m','B12_60m','B8A_60m','SCL_60m','TCI_60m','WVP_60m']

            print(len(bandNames))

            bNamePos = 0
            for i in range(1, 36):
                print(i)
                imageNo = bandNames[bNamePos] + str('.jp2')

                name = str(bandNames[bNamePos])
                src_files_to_mosaic = []
        
                        
                fileRegex = re.compile(imageNo)

                foundFiles = list(filter(fileRegex.findall, files)) #find all files that have same ending, B01.jp2 etc. 
                print('files to create image from:', foundFiles)
                print(len(foundFiles))

        
                src_files_to_mosaic = [] 

                for fp in foundFiles: # open .jp2 images and write to list.  
                    src = rasterio.open(fp)
                    src_files_to_mosaic.append(src)
                    print(src.bounds)
            

                print(src_files_to_mosaic)
                print(len(src_files_to_mosaic))

                bounds = (left, bottom, right, top)
        
                mosaic, out_trans = rasterio.merge.merge(src_files_to_mosaic, bounds = bounds) #Merge rasters, bounds = None or bounds 

                out_meta = src.meta.copy() #Copy the metadata
                crsFile = rasterio.open(foundFiles[0])

                out_meta.update({"driver": "GTiff", # Update the metadata
                                 "height": mosaic.shape[1],
                                 "width": mosaic.shape[2],
                                 "transform": out_trans
                                #"crs": crsFile.crs #"+proj=utm +zone=35 +ellps=GRS80 +units=m +no_defs "
                                }
                                )

                R10path = BandsFolder + '/Level_2A_Data/R10m'
                R20path = BandsFolder + '/Level_2A_Data/R20m'
                R60path = BandsFolder + '/Level_2A_Data/R60m'

                if not os.path.exists(R10path): #check to see if save folder exists and creates it if not. creates above folder if not all ready created.
                    os.makedirs(R10path)
                if not os.path.exists(R20path): #check to see if save folder exists and creates it if not. creates above folder if not all ready created.
                    os.makedirs(R20path)
                if not os.path.exists(R60path): #check to see if save folder exists and creates it if not. creates above folder if not all ready created.
                    os.makedirs(R60path)

                if name.endswith('10m'):
                    saveLocationName = R10path + '/' + time + '_' + name + '.tiff'
                elif name.endswith('20m'):
                    saveLocationName = R20path + '/' + time + '_' + name + '.tiff'
                elif name.endswith('60m'):
                    saveLocationName = R60path + '/' + time + '_' + name + '.tiff'

                
                
                #saveLocationName = BandsFolder + '/' + name + '.tiff'








                with rasterio.open(saveLocationName, "w", **out_meta) as dest: #Write the mosaic raster to disk
                    dest.write(mosaic)

                bNamePos = bNamePos + 1

                print("Cropping Complete")

Username = "USERNAME" #enter your SCI-HUB username and password here.
Password = "PASSWORD"

footprintName = "Donegal" #name of .geojson file
geoJsonFolder = 'D:/Documents/Programming/hello/GEOFiles/' #folder where footprintName is located. 

start_date = "2018-6-1" #start date, format: "YYYY-M-D"
end_date = "2018-7-10" #finish data 
download_folder = 'E:/Products' #download folder location
frequency = 30 #frequency (measured in days)
productLevel = 'L2A' #product level, L2A or L1C
productSize = 650 #Size of the product, used to ensure that the returned product has data in them and will not result in blank space. Measured in MB. Recommend to keep at 650.


api = SentinelAPI(Username, Password, 'https://scihub.copernicus.eu/dhus') #username and password for SCIHUB 
footprintLocation, footprint = geojsonLocation(footprintName, geoJsonFolder) #get the footprint area of interest

downloadFileName = start_date + ' - ' + end_date + '_' + footprintName + '_' + str(frequency) + '_' + str(productLevel)
downloadFileLocation = download_folder + '/' + downloadFileName
print(downloadFileLocation)

if not os.path.exists(downloadFileLocation): #check to see if save folder exists and creates it if not. 
    os.makedirs(downloadFileLocation)


print(downloadFileName)

d1 = pd.date_range(start_date, end_date, freq = "1D").strftime("%Y%m%d") #creates the sensing periods given start and finished date and sensing frequency.

print(d1)

start = 0 
end = frequency


x = 1
for i in d1:
  if end <= len(d1):
    start_date = d1[start]
    end_date = d1[end]
    
    print(start)
    print(end)

    start = start + frequency
    end = end + frequency
    
  else:
    start_date = start_date
    end_date = d1[-1]
    break
  
  date = (x, start_date, end_date)
  print(date)
  
  starting_date = ''

  for i in start_date:
    starting_date = starting_date + i
  
  ending_date = ''

  for i in end_date:
    ending_date = ending_date + i

  print(x, starting_date, ending_date)
  x = x + 1

  download_products(starting_date, ending_date)



cropped_mosaic(downloadFileLocation, footprintLocation) #crop the bands into a mosaic with only the area of interest. 



print("Complete")