import csv
import psycopg2

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
    
    for row in reader:
        try:

            site_number = row['Site Number'].strip().zfill(13)

            # Update the JSON fields in the database
            cursor.execute("""
                UPDATE public."WorkOrder"
                SET "JsonData" = jsonb_set(
                    jsonb_set(
                        jsonb_set(
                            "JsonData",
                            '{ServicePoint,Latitude}',
                            %s::jsonb
                        ),
                        '{ServicePoint,Longitude}',
                        %s::jsonb
                    ),
                    '{Contact,Address}',
                    %s::jsonb
                )
                WHERE "JsonData"->'WorkOrder'->>'WorkOrderId' = %s
            """, (
                f'"{row["Latitude"]}"',
                f'"{row["Longitude"]}"',
                f'"{row["Full Address"]}"',
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
    # Commit or rollback
    response = input(f"\nUpdated {success_count} records, {error_count} errors. Commit? (yes/no): ")
    if response.lower() == 'yes':
        conn.commit()
        print("Changes committed!")
    else:
        conn.rollback()
        print("Changes rolled back!")

cursor.close()
conn.close()