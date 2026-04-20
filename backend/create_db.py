import pandas as pd
import sqlite3

# Load the CSV data
csv_file = 'customer_support_tickets.csv'
df = pd.read_csv(csv_file)

# Clean up column names (remove spaces, make lowercase)
df.columns = df.columns.str.replace(' ', '_').str.lower()

# Create a connection to a new SQLite database file
conn = sqlite3.connect('crm_data.db')

# Define the table name
table_name = 'support_tickets'

# Write the data from the DataFrame into the SQLite table
df.to_sql(table_name, conn, if_exists='replace', index=False)

# Close the connection
conn.close()

print(f"Successfully created database 'crm_data.db' with table '{table_name}'.")