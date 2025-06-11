import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Upload Excel", layout="centered")
st.markdown("<style>[data-testid='stSidebar'] { display: none; }</style>", unsafe_allow_html=True)

st.title("📤 Upload Excel to Populate Student DB")

uploaded_file = st.file_uploader("Upload Excel file (.xlsx)", type="xlsx")

if "upload_success" not in st.session_state:
    st.session_state.upload_success = False

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()

        required_columns = ['Name', 'CGPA', 'Location', 'Email', 'Phone Number', 'Preferred Work Location', 'Specialization in Degree']
        missing_cols = [col for col in required_columns if col not in df.columns]

        if missing_cols:
            st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
        else:
            conn = sqlite3.connect("students.db")
            cursor = conn.cursor()

            # Create table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    cgpa REAL,
                    location TEXT,
                    email TEXT,
                    phone_number TEXT,
                    preferred_work_location TEXT,
                    specialization TEXT
                )
            ''')

            # ❗ Delete all existing records before inserting new ones
            cursor.execute('DELETE FROM students')

            inserted = 0
            for index, row in df.iterrows():
                try:
                    cursor.execute('''
                        INSERT INTO students (
                            name, cgpa, location, email, phone_number, preferred_work_location, specialization
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        row['Name'],
                        row['CGPA'],
                        row['Location'],
                        row['Email'],
                        str(row['Phone Number']),
                        row['Preferred Work Location'],
                        row['Specialization in Degree']
                    ))
                    inserted += 1
                except Exception as e:
                    st.warning(f"⚠️ Skipped row {index + 2}: {e}")

            conn.commit()
            conn.close()

            st.success(f"✅ Successfully inserted {inserted} records.")
            st.session_state.upload_success = True

    except Exception as e:
        st.error(f"❌ Failed to process the uploaded file: {e}")
else:
    st.info("⬆️ Please upload an Excel file.")

if st.session_state.upload_success:
    st.markdown("---")
    st.success("🎉 Upload complete! You can now query the data.")
    if st.button("Go to Query Page"):
        st.switch_page("pages/2_Query_Database.py")