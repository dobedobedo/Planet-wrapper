# Planet-wrapper
A Python 3 wrapper of Planet API to search and download images
# Dependencies  
This tool needs the following dependencies:  
- planet  
- gdal  
- geojson  
  
Make sure the location of **planet** binery is in your _$PATH_ variable (which means you can execute **planet** directly without entering to its path).  
# Prerequisite  
The planet API needs user's API key to access the service. To make this tool recognise your API Key, three methods are provided:  
1. export your API Key to environmental variable PL_API_KEY  
2. save your API key to a text file, and modify the PL_API_KEY path in the script  
3. When the above two methods fail, the application will prompt user to enter API Key  
  
For more information about planet API key, refer to https://support.planet.com/hc/en-us/articles/212318178-What-is-my-API-key-  
# Usage  
1. Execute the script, the tool will prompt the user to select search item type and asset type. For more details regarding the codename, refer to https://developers.planet.com/docs/apis/data/items-assets/.  
2. Another prompt window appear to ask user select a file containing the area of interest. Two formats are supported at the moment: **Shapefile (\*.shp)** and **GeoJSON (\*.geojson; \*.json)**. It can contains multiple _points_, _polygons_, and _features_.  
3. The application will detect the geometry type of the input file. If _polygon_ is detected, it will prompt the user whether to set _aera cover percentage_ as a filter criteria. If user selects _yes_, then it will prompt the user set the minimum and maximum area cover percentage (range from 0 to 100)  
4. Next, it will prompt the user to enter the _date range_ (in format yyyy-mm-dd)  
5. Finally, it will prompt the user to enter the _cloud cover range_ (range from 0 to 1)  
  
The application will then start to search based on those criteria. Once the search finishes, it will report the user the number of available images for each item type, then the user can decide whether to download them or not. During the download process, there will be no information appears at the moment (future feature). However, when the download finishes, there will be another prompt window appears to let the user know if the task is successful.  
  
This application can also be run on servers without graphical interface. It will try running gui first anyway then cli. If you prefer command line interface, you need to change the main function behaviour.  
# Future work  
Consider to add a real-time progress report when download. However, I need to figure out how to parse the output.
