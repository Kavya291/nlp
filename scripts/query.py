import sqlite3

# Connect to the database
conn = sqlite3.connect("students.db")
cur = conn.cursor()

# Check if the table exists
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='examples'")
if cur.fetchone():
    # Fetch and print all rows from the examples table
    cur.execute("SELECT * FROM examples")
    rows = cur.fetchall()

    print("Contents of examples.db:")
    for row in rows:
        print(row)
else:
    print("Table 'examples' does not exist in examples.db.")

conn.close()