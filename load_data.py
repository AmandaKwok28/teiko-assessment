import sqlite3
import csv

def initialize_database(conn):
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS cell_counts")
    cursor.execute("DROP TABLE IF EXISTS samples")

    cursor.execute("""
    CREATE TABLE samples (
        sample TEXT PRIMARY KEY,
        project TEXT,
        subject TEXT,
        condition TEXT,
        age REAL,
        sex TEXT,
        treatment TEXT,
        response TEXT,
        sample_type TEXT,
        time_from_treatment_start REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE cell_counts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sample_id TEXT,
        cell_type TEXT,
        count REAL,
        FOREIGN KEY(sample_id) REFERENCES samples(sample)
    )
    """)

    cursor.execute("""
        CREATE INDEX idx_sample_id
        ON cell_counts(sample_id)
    """)

    cursor.execute("""
        CREATE INDEX idx_cell_type
        ON cell_counts(cell_type)
    """)

    conn.commit()


def load_data(conn, csv_file):
    
    cursor = conn.cursor()

    with open(csv_file, newline='', encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            # insert sample data
            cursor.execute("""
                INSERT INTO samples (
                    sample, project, subject, condition, age,
                    sex, treatment, response, sample_type,
                    time_from_treatment_start
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row["sample"],
                row["project"],
                row["subject"],
                row["condition"],
                float(row["age"]),
                row["sex"],
                row["treatment"],
                row["response"],
                row["sample_type"],
                float(row["time_from_treatment_start"])
            ))

            # Insert cell counts
            cell_types = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]

            for cell_type in cell_types:
                cursor.execute("""
                    INSERT INTO cell_counts (sample_id, cell_type, count)
                    VALUES (?, ?, ?)
                """, (
                    row["sample"],
                    cell_type,
                    float(row[cell_type])
                ))

    conn.commit()
    
    
def main():
    # paths for the database and CSV file
    db_path = 'data.db'
    csv_path = 'cell-count.csv'
    
    # create database
    conn = sqlite3.connect(db_path)
    initialize_database(conn)
    load_data(conn, csv_path)
    conn.close()
    
    print("Data loaded successfully.")
    
    
if __name__ == "__main__":
    main()
