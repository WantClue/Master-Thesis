from influxdb_client import InfluxDBClient
import pandas as pd

# Define your InfluxDB connection details
url = "test"  # Update with your InfluxDB URL
token = "test"  # Replace with your actual API token
org = "test"  # Replace with your organization
bucket = "test"  # Replace with your bucket name

# Connect to the InfluxDB client
client = InfluxDBClient(url=url, token=token, org=org)

# Define the measurements to query
fields = ['hashRate', 'power', 'asicVoltage', 'Freq', 'temp']

for field in fields:
    query = f'''
    from(bucket: "{bucket}")
      |> range(start: -30d)
      |> filter(fn: (r) => r._field == "{field}")
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''
    result = client.query_api().query_data_frame(query, org=org)
    
    # Export to CSV
    result.to_csv(f'{field}.csv', index=False)

print("Data exported successfully.")
