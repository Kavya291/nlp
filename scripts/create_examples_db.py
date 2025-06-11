import sqlite3

conn = sqlite3.connect("data/examples.db")  # Or full/relative path
cur = conn.cursor()

# Create the examples table
cur.execute("""
CREATE TABLE IF NOT EXISTS examples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    query TEXT NOT NULL
)
""")

conn.commit()
conn.close()
print("Table 'examples' created successfully.")