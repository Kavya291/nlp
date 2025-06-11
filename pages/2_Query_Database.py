from dotenv import load_dotenv
import streamlit as st
import os
import sqlite3
import google.generativeai as genai
import pandas as pd

# ---------------- Streamlit Setup ----------------
st.set_page_config(page_title="Query Database")
st.markdown("<style>[data-testid='stSidebar'] { display: none; }</style>", unsafe_allow_html=True)

# ---------------- Load Environment Variables ----------------
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# ---------------- Prompt Base ----------------
base_prompt = """
You are an expert SQL assistant. Given a natural language request, convert it into a valid SQLite SQL query that works with the following table:

Table Name: students  
Columns (use these exact column names in your query):  
- name (TEXT)  
- cgpa (REAL)  
- location (TEXT)  
- email (TEXT)  
- phone_number (TEXT)  
- preferred_work_location (TEXT)  
- specialization (TEXT)  

When mapping user input about "specialization," restrict it strictly to one or multiple of these 10 allowed specializations (case-insensitive match):  
1. Computer Science  
2. Electronics and Communication  
3. Mechanical Engineering  
4. Civil Engineering  
5. Electrical Engineering  
6. Information Technology  
7. Chemical Engineering  
8. Aerospace Engineering  
9. Biotechnology  
10. Environmental Engineering  

If multiple specializations are mentioned, generate SQL using `IN` clause or appropriate `OR` conditions to match any of them.

Only return the SQL query, nothing else. Make string comparisons case-insensitive by using LOWER(column_name) and LOWER('value') where applicable. 
"""

# ---------------- Gemini Model Call ----------------
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content([prompt, question])
    sql_query = response.text.strip()
    
    if sql_query.startswith(""):
        sql_query = sql_query.replace("sqlite", "").replace("`", "").strip()
    
    sql_query = sql_query.replace('\n', ' ').strip()

    # Auto-insert DISTINCT if missing
    if sql_query.lower().startswith("select") and "distinct" not in sql_query.lower():
        sql_query = sql_query.replace("SELECT", "SELECT DISTINCT", 1)

    return sql_query

# ---------------- Detect if query is write operation ----------------
def is_write_query(sql):
    write_commands = ['insert', 'update', 'delete', 'drop', 'alter', 'create', 'replace', 'truncate']
    sql_start = sql.strip().split()[0].lower()
    return sql_start in write_commands

# ---------------- Execute SQL Query ----------------
def read_sql_query(sql, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    try:
        cur.execute(sql)
        rows = cur.fetchall()
        column_names = [desc[0] for desc in cur.description] if cur.description else []
    except sqlite3.Error as e:
        rows = [(f"SQL Error: {str(e)}",)]
        column_names = ["Error"]
    finally:
        conn.commit()
        conn.close()
    return rows, column_names

# ---------------- Validate SQL ----------------
def validate_sql_query(sql, db_path="students.db"):
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(f"EXPLAIN QUERY PLAN {sql}")
        conn.close()
        return True, ""
    except sqlite3.Error as e:
        return False, str(e)

# ---------------- RAG: Get Similar Examples ----------------
def get_similar_examples(question):
    conn = sqlite3.connect("data/examples.db")
    cur = conn.cursor()
    cur.execute("SELECT question, query FROM examples")
    rows = cur.fetchall()
    conn.close()

    question_words = set(question.lower().split())
    similar = []
    for q, query in rows:
        overlap = len(set(q.lower().split()) & question_words)
        if overlap > 0:
            formatted = f"-- {q}\n{query}"
            similar.append((overlap, formatted, q, query))

    similar.sort(reverse=True)
    return similar[:3]

# ---------------- UI ----------------
st.header("💡 Natural Language SQL Query")
question = st.text_input("Ask a question about the student database:", key="input")
submit = st.button("Submit")

# ---------------- Submit Handler ----------------
if submit and question.strip():
    similar_examples = get_similar_examples(question)
    examples_prompt = "\n\n".join([ex[1] for ex in similar_examples])
    full_prompt = base_prompt + "\n\nHere are some examples:\n" + examples_prompt if examples_prompt else base_prompt

    if similar_examples:
        st.subheader("📚 Similar Examples Used (RAG):")
        for _, _, q_text, sql_text in similar_examples:
            st.markdown(f"**Q:** {q_text}")
            st.code(sql_text, language="sql")

    sql_query = get_gemini_response(question, full_prompt)

    st.session_state["last_question"] = question
    st.session_state["last_sql_query"] = sql_query
    st.session_state["password_verified"] = False  # reset on new query

    st.subheader("🛠️ Generated SQL Query:")
    st.code(sql_query, language="sql")

    if is_write_query(sql_query):
        st.warning("⚠️ The generated query is a write operation and requires admin authentication.")
        st.session_state["awaiting_password"] = True
    else:
        # Read-only, validate then execute
        is_valid, error_msg = validate_sql_query(sql_query, "students.db")
        if is_valid:
            result, column_names = read_sql_query(sql_query, "students.db")
            st.session_state["last_result"] = result.copy()
            st.session_state["last_columns"] = column_names
            st.session_state["current_page"] = 1
            st.session_state["awaiting_password"] = False
        else:
            st.error(f"❌ SQL validation failed: {error_msg}")

# ---------------- Admin Password Handling ----------------
if st.session_state.get("awaiting_password", False) and not st.session_state.get("password_verified", False):
    admin_pass_input = st.text_input("Enter admin password to proceed:", type="password", key="admin_pass")

    if admin_pass_input:
        if admin_pass_input == ADMIN_PASSWORD:
            st.success("Admin authentication successful. Query executed.")
            sql_query = st.session_state["last_sql_query"]

            is_valid, error_msg = validate_sql_query(sql_query)
            if is_valid:
                result, column_names = read_sql_query(sql_query, "students.db")
                st.session_state["last_result"] = result.copy()
                st.session_state["last_columns"] = column_names
                st.session_state["current_page"] = 1
                st.session_state["password_verified"] = True
                st.session_state["awaiting_password"] = False
            else:
                st.error(f"❌ SQL validation failed: {error_msg}")
        else:
            st.error("❌ Incorrect admin password. Query execution blocked.")

# ---------------- Pagination & Table ----------------
if "last_result" in st.session_state:
    result = st.session_state["last_result"]
    columns = st.session_state.get("last_columns", [])
    st.subheader("📋 Query Results:")

    results_per_page = 10
    total_results = len(result)
    total_pages = (total_results + results_per_page - 1) // results_per_page

    if "current_page" not in st.session_state:
        st.session_state["current_page"] = 1

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.session_state["current_page"] > 1:
            if st.button("⬅️ Previous"):
                st.session_state["current_page"] -= 1
    with col3:
        if st.session_state["current_page"] < total_pages:
            if st.button("Next ➡️"):
                st.session_state["current_page"] += 1

    start = (st.session_state["current_page"] - 1) * results_per_page
    end = start + results_per_page
    page_data = result[start:end]

    if page_data:
        df = pd.DataFrame(page_data, columns=columns)
        st.dataframe(df, use_container_width=True)
    else:
        st.write("No results to show.")

    st.caption(f"Page {st.session_state['current_page']} of {total_pages}")

# ---------------- Save Button ----------------
if "last_result" in st.session_state and st.session_state["last_result"]:
    if st.button("✅ Save this as a good example for future (RAG)"):
        conn = sqlite3.connect("data/examples.db")
        cur = conn.cursor()
        question = st.session_state["last_question"]
        sql_query = st.session_state["last_sql_query"]

        cur.execute("SELECT * FROM examples WHERE question = ? AND query = ?", (question, sql_query))
        exists = cur.fetchone()

        if not exists:
            cur.execute("INSERT INTO examples (question, query) VALUES (?, ?)", (question, sql_query))
            conn.commit()
            st.success("Example saved successfully! 🎉")
        else:
            st.info("This example already exists in the database.")

        conn.close()