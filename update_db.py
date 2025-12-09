import csv
import os
import psycopg2
import time
from dotenv import load_dotenv


# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))


csv_path = os.path.join(script_dir, 'updated_collection.csv')

old_csv_path = os.path.join(script_dir, 'old_address.csv')
# Load env file from script directory
env_path = os.path.join(script_dir, 'prod.env')

print(f"Looking for env file at: {env_path}")
load_dotenv(env_path)
old_addresses = {}
with open(old_csv_path, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        site_number = row['Site Number'].strip()
        old_addresses[site_number] = row['Old Address']

print(f"Loaded {len(old_addresses)} old addresses")


# Connect to your DB
conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)

cursor = conn.cursor()

# Read CSV
print(f"Reading from: {csv_path}")

with open(csv_path, 'r') as f:
    reader = csv.DictReader(f)
    
    
    success_count = 0
    error_count = 0
    total_rows = 0
    start_time = time.time()
    
    for row in reader:
        total_rows += 1
        try:
            old_address = old_addresses.get(site_number, '')
            new_address = row["Full Address"]
            site_number = row['Site Number'].strip().zfill(13)
            latitude = row['Latitude']
            longitude = row['Longitude']

            # Update the JSON fields in the database
            cursor.execute("""
                UPDATE public."WorkOrder"
                SET "JsonData" = jsonb_set(
                    jsonb_set(
                        jsonb_set(
                            "JsonData",
                            '{Contact,Address}',
                            %s::jsonb
                        ),
                        '{ServicePoint,Latitude}',
                        %s::jsonb
                    ),
                    '{ServicePoint,Longitude}',
                    %s::jsonb
                ),
                  "Position" = ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                   "PositionSRID" = 4326                 
                WHERE "JsonData"->'WorkOrder'->>'WorkOrderId' = %s
            """, (
                f'"{new_address}"',
                f'"{latitude}"',
                f'"{longitude}"',
                float(longitude),
                float(latitude),
                site_number
            ))
            
            if cursor.rowcount > 0:
                cursor.execute("""
                    WITH new_history AS (
                        INSERT INTO public."Histories" (
                            "WorkOrderId",
                            "TaskName",
                            "UserName",
                            "ActivityTypeId",
                            "ActivityDetailId",
                            "PostProcessingId",
                            "TimeStamp",
                            "Name"
                        )
                        SELECT
                            wo."Id" as "WorkOrderId",
                            null as "TaskName",
                            'Position_updated' as "UserName",
                            -17 as "ActivityTypeId",
                            5 as "ActivityDetailId",
                            null as "PostProcessingId",
                            NOW() as "TimeStamp",
                            'STORY_' || gen_random_uuid()::text as "Name"
                        FROM public."WorkOrder" wo
                        WHERE wo."JsonData" -> 'WorkOrder' ->> 'WorkOrderId' = %s
                        RETURNING "Id", "WorkOrderId"
                    )
                    INSERT INTO public."AuditLogs" (
                        "HistoryId",
                        "FieldName",
                        "OldValue",
                        "NewValue",
                        "TimeStamp",
                        "Name"
                    )
                    SELECT
                        nh."Id" as "HistoryId",
                        'Contact.Address' as "FieldName",
                        %s as "OldValue",
                        %s as "NewValue",
                        NOW() as "TimeStamp",
                        'AUDITLOG_' || gen_random_uuid()::text as "Name"
                    FROM new_history nh
                """, (site_number, old_address, new_address))
                
                success_count += 1
                print(f"Updated {site_number}")
                print(f"  Old: {old_address}")
                print(f"  New: {new_address}")
            else:
                error_count += 1
                print(f"No match for {site_number}")

        except Exception as e:
            error_count += 1
            print(f"Error with {site_number}: {e}")
    elapsed_time = time.time() - start_time

    # Commit or rollback

    print(f"\n{'='*50}")
    print(f"Total processed: {total_rows}")
    print(f"Successfully updated: {success_count}")
    print(f"Errors/No match: {error_count}")
    print(f"Time elapsed: {elapsed_time:.2f} seconds")
    print(f"{'='*50}")

    response = input(f"\nUpdated {success_count} records, {error_count} errors. Commit? (yes/no): ")
    if response.lower() == 'yes':
        conn.commit()
        print("Changes committed!")
    else:
        conn.rollback()
        print("Changes rolled back!")

cursor.close()
conn.close()