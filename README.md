# LLMQueryBot

## Overview

**LLMQueryBot** is a Streamlit-based web application that enables users to query a student database using natural language. It leverages Google Gemini (Generative AI) to convert user questions into SQL queries, allowing for intuitive and flexible data exploration. The app supports fuzzy keyword matching, so users do not need to type exact city or branch names, and it features a Retrieval-Augmented Generation (RAG) system to improve query accuracy over time.

---

## Architecture

![Architecture](architecture/architecture.png)


## Features

- **Natural Language to SQL**: Ask questions in plain English; the app translates them into SQL queries.
- **Fuzzy Matching**: Handles incomplete or misspelled city/branch names using fuzzy logic.
- **RAG (Retrieval-Augmented Generation)**: Learns from good examples to improve future query generation.
- **Admin Controls**: Write operations (insert, update, delete) require admin authentication.
- **Excel Upload**: Easily populate or refresh the student database by uploading an Excel file.
- **Pagination**: View large query results in a paginated table.
- **Example Saving**: Save successful queries as examples to enhance the RAG system.

---

## Project Structure

```
.
├── Home_Page.py                # Streamlit page for uploading Excel files to the database
├── pages/
│   └── 2_Query_Database.py     # Main query interface (natural language to SQL)
├── scripts/
│   ├── create_examples_db.py   # Script to create the examples database for RAG
│   └── query.py                # Script to inspect the database contents
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (API keys, admin password)
├── students.db                 # Main SQLite database (auto-generated)
├── data/
│   └── examples.db             # Example queries for RAG (auto-generated)
└── README.md                   # Project documentation
```

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd LLMQueryBot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the root directory with the following content:

```
GOOGLE_API_KEY=your_google_gemini_api_key
ADMIN_PASSWORD=your_admin_password
```

### 4. Run the Application

```bash
streamlit run Home_Page.py
```

- Start by uploading an Excel file with student data.
- After a successful upload, proceed to the query page.

---

## Usage Guide

### 1. Upload Student Data

- Go to the home page.
- Upload an Excel file with columns: `Name`, `CGPA`, `Location`, `Email`, `Phone Number`, `Preferred Work Location`, `Specialization in Degree`.
- The app will create or refresh the `students.db` database.

### 2. Query the Database

- On the query page, type your question in natural language (e.g., "Show all students from bangalor in computer").
- The app will:
  - Fuzzily match incomplete city/branch names (e.g., "bangalor" → "Bangalore", "computer" → "Computer Science").
  - Generate and display the corresponding SQL query.
  - Show the results in a paginated table.

### 3. Save Good Examples

- If a query returns the desired result, click "Save this as a good example for future (RAG)" to help the system learn.

### 4. Admin Operations

- If a query attempts to modify the database (insert, update, delete), you will be prompted for the admin password.

---

## RAG (Retrieval-Augmented Generation)

- The app stores good question-query pairs in `data/examples.db`.
- When a new question is asked, it retrieves similar past examples to guide the LLM, improving SQL generation accuracy over time.

---

## Security

- All write operations require admin authentication.
- API keys and passwords are stored in the `.env` file (never commit this file to version control).

---

## Dependencies

- `streamlit`
- `pandas`
- `openpyxl`
- `sqlite3`
- `google-generativeai`
- `python-dotenv`
- `rapidfuzz`
- `sentence-transformers` (for advanced RAG, if needed)

---

## Example Excel Format

| Name      | CGPA | Location   | Email           | Phone Number | Preferred Work Location | Specialization in Degree   |
|-----------|------|------------|-----------------|--------------|------------------------|----------------------------|
| John Doe  | 8.5  | Bangalore  | john@abc.com    | 1234567890   | Hyderabad              | Computer Science           |
| ...       | ...  | ...        | ...             | ...          | ...                    | ...                        |

---

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## License

[MIT License](LICENSE)

---

## Acknowledgements

- Google Gemini for LLM-powered SQL generation
- Streamlit for rapid web app development
- RapidFuzz for fuzzy string matching 