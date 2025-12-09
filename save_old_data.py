import csv
import os
import psycopg2
from dotenv import load_dotenv

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Load database credentials
env_path = os.path.join(script_dir, 'prod.env')
load_dotenv(env_path)

# Build the full path to site_ids.csv
csv_path = os.path.join(script_dir, 'site_ids.csv')

site_ids = []
with open(csv_path, 'r') as f:
    reader = csv.reader(f)
    next(reader)  
    for row in reader:
        siteid = row[0].strip().zfill(13)
        site_ids.append(siteid)

print(f"Loaded {len(site_ids)} site IDs") 

print("\n" + "="*50)
print("SAVING OLD ADDRESS DATA...")
print("="*50)

try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    cursor = conn.cursor()
    
    # Query old data for all site IDs
    cursor.execute("""
        SELECT 
            wo."JsonData" -> 'WorkOrder'->>'WorkOrderId' as site_number,
            ST_AsText(wo."Position") as old_position_geometry,
        
            wo."JsonData" -> 'Contact' ->> 'Address' as old_address,
            WO."JsonData" -> 'ServicePoint'->>'Latitude',
            WO."JsonData" -> 'ServicePoint'->>'Longitude'
        FROM public."WorkOrder" wo
        WHERE wo."JsonData" -> 'WorkOrder'->> 'WorkOrderId' = ANY(%s)
    """, (site_ids,))
    
    old_data = cursor.fetchall()
    
    # Save to old_address.csv
    old_csv_path = os.path.join(script_dir, 'old_address.csv')
    with open(old_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Site Number', 'Old Position Geometry', 'Old Address', 'Old Latitude', 'Old Longitude'])
        writer.writerows(old_data)
    
    print(f" Saved {len(old_data)} old records to {old_csv_path}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f" Error saving old data: {e}")
    exit(1)