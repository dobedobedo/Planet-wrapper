# Planet-wrapper
A Python wrapper of Planet API to search and download images
# Dependencies  
This tool needs the following dependencies:  
- planet  
- gdal   
   
# Prerequisite  
The planet API needs the user's API key to access the service. Three authentication methods are provided:  
1. export your API Key to environmental variable PL_API_KEY  
2. save your API key to a JSON file called _.planet.json_ in the user profile directory, which has the content `{"key": "YOUR_API_KEY"}`  
3. If none of the above two methods was done, the application will prompt the user to use either email or API key for authentication. This process only needs to be done for one time and it will create a _.planet.json_ file for you.  
  
For more information about planet API key, refer to https://support.planet.com/hc/en-us/articles/212318178-What-is-my-API-key-  
# Usage  
1. Execute the script. The tool will prompt the user to select the search item types and asset types. For more details regarding the codename, refer to https://developers.planet.com/docs/apis/data/items-assets/.  
2. An AOI is a must for this application. Three formats are supported at the moment: **Shapefile (\*.shp)**, **GeoJSON (\*.geojson; \*.json)**, and **Keyhole Markup Language (\*.kml)**. It can contains multiple _geometries_.  
3. The application will prompt the users for filter options. You can choose multiple filters, and it will prompt for search range later. If no filter is selected, it will automatically search for the latest six months images that touch the AOI.  
4. It will report the search results. If it finds any, it will prompt the user for delivery options. Refer to https://developers.planet.com/docs/orders/delivery/ for more information. If _local drive_ is chosen and **Deliver in a single archive** is not check, the application will create sub-directories under the chosen directory based on the items' acquired date.  
  
This application supports both GUI and CLI. If a display environment is not found, it will convert to CLI mode automatically.  
  
# Known issue  
Sometimes the GUI crashes because of threading issue. If this problem persist, open **Modules/prompt_widget.py** and go to **line 712**, insert a new line then input `raise tk._tkinter.TclError` to force using CLI progressbar.  
