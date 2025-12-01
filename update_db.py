import csv
import psycopg2
import time

# Connect to your DB
conn = psycopg2.connect(
    host="postgres-preprod.cuqksc7ydqcp.ca-central-1.rds.amazonaws.com",
    database="wfms_workorderexecution",
    user="admin_user",
    password="bK9FHzzciVgYin4Lg2NG"
)

cursor = conn.cursor()

# Read CSV
with open('updated_collection.csv', 'r') as f:
    reader = csv.DictReader(f)
    
    
    success_count = 0
    error_count = 0
    total_rows = 0
    start_time = time.time()
    
    for row in reader:
        try:

            site_number = row['Site Number'].strip().zfill(13)

            # Update the JSON fields in the database
            cursor.execute("""
                UPDATE public."WorkOrder"
                SET "JsonData" = jsonb_set(
                    "JsonData",
                    '{Contact,Address}',
                    %s::jsonb
                ),
                  "Position" = ST_SetSRID(ST_MakePoint(%s, %s), 4326)         
                WHERE "JsonData"->'WorkOrder'->>'WorkOrderId' = %s
            """, (
                f'"{row["Full Address"]}"',
                float(row["Longitude"]),
                float(row["Latitude"]),
                site_number
            ))
            
            if cursor.rowcount > 0:
                success_count += 1
                print(f"Updated {site_number}")
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