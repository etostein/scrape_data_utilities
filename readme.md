README
🚀 Overview

This project collects latitude and longitude data for specific site IDs.
To run the script successfully, you must first add your Work Order (WO) numbers to the site_ids.csv file.

Step 1 — Add WO Numbers to site_ids.csv

Open the file named site_ids.csv

Add your WO / Site IDs into the file

Save it

The script will read this CSV and process all site IDs you provide.

Step 2 — Run the Python Script

Execute the script that collects latitude and longitude:

python get_lat_long.py


This will:

Load the IDs you added in site_ids.csv

Retrieve their coordinates

Output the latitude and longitude values accordingly

Step 3 - Run update_db
make sure script targets the right DB