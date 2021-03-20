# Planet-wrapper
A Python wrapper of Planet API to search and download images
# Dependencies  
This tool needs the following dependencies:  
- planet  
- gdal   
   
# Prerequisite  
The planet API needs the user's API key to access the service. Three authentication methods are provided:  
1. export your API Key to environmental variable PL_API_KEY  
2. save your API key to a JSON file called _.planet.json'_ in the user profile directory, which has the content `{"key": "YOUR_API_KEY"}`  
3. If none of the above two methods was done, the application will prompt the user to use either email or API key for authentication. This process only needs to be done for one time.  
  
For more information about planet API key, refer to https://support.planet.com/hc/en-us/articles/212318178-What-is-my-API-key-  
# Usage  
1. Execute the script. The tool will prompt the user to select the search item types and asset types. For more details regarding the codename, refer to https://www.planet.com/docs/spec-sheets/.  
2. An AOI is a must for this application. Three formats are supported at the moment: **Shapefile (\*.shp)**, **GeoJSON (\*.geojson; \*.json)**, and **KML (\*.kml)**. It can contains multiple _points_, _polygons_, and _features_.  
3. The application will prompt the users for filter options. You can choose multiple filters, and it will prompt for search range later. If no filter is selected, it will automatically search for the latest six months images that touch the AOI.  
4. It will report the search results. If it finds any, it will prompt the user for delivery options. Refer to https://developers.planet.com/docs/orders/delivery/ for more information.  
  
This application supports both GUI and CLI. If a display environment is not found, it will convert to CLI mode automatically.  
