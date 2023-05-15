import sqlite3
from sqlite3 import Error
from typing import List

class Database:
    def __init__(self):
        self.conn = self.create_connection("team_management.db")
        self.create_tables()

    def update_tasks_table(self):
        # Create a new table with the correct schema
        new_tasks_table = """CREATE TABLE IF NOT EXISTS new_tasks (
                                 id integer PRIMARY KEY,
                                 user_id integer NOT NULL,
                                 title text NOT NULL,
                                 due_date text NOT NULL
                             );"""

        self.create_table(new_tasks_table)

        # Copy the data from the old table to the new one
        cur = self.conn.cursor()
        cur.execute("INSERT INTO new_tasks SELECT * FROM tasks;")
        self.conn.commit()

        # Drop the old table
        cur.execute("DROP TABLE tasks;")
        self.conn.commit()

        # Rename the new table to the original table name
        cur.execute("ALTER TABLE new_tasks RENAME TO tasks;")
        self.conn.commit()

    def create_connection(self, db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file, check_same_thread=False)
        except Error as e:
            print(e)

        return conn

    def create_table(self, create_table_sql):
        try:
            c = self.conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)

    def create_tables(self):
        tasks_table = """CREATE TABLE IF NOT EXISTS tasks (
                            id integer PRIMARY KEY,
                            user_id integer NOT NULL,
                            title text NOT NULL,
                            due_date text NOT NULL
                        );"""

        events_table = """CREATE TABLE IF NOT EXISTS events (
                                id integer PRIMARY KEY,
                                user_id integer NOT NULL,
                                name text NOT NULL,
                                date_time text NOT NULL
                            );"""

        files_table = """CREATE TABLE IF NOT EXISTS files (
                                id integer PRIMARY KEY,
                                user_id integer NOT NULL,
                                file_id text NOT NULL
                            );"""

        self.create_table(tasks_table)
        self.create_table(events_table)
        self.create_table(files_table)

    def add_task(self, user_id: int, title: str, due_date: str):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO tasks (user_id, title, due_date) VALUES (?, ?, ?)", (user_id, title, due_date))
        self.conn.commit()

    def delete_task(self, task_id: int):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()

    def add_event(self, user_id: int, name: str, date_time: str):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO events (user_id, name, date_time) VALUES (?, ?, ?)", (user_id, name, date_time))
        self.conn.commit()

    def delete_event(self, event_id: int):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM events WHERE id = ?", (event_id,))
        self.conn.commit()

    def upload_file(self, user_id: int, file_id: str, file_name: str):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO files (user_id, file_id, file_name) VALUES (?, ?, ?)", (user_id, file_id, file_name))
        self.conn.commit()

    def delete_file(self, file_id: int):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM files WHERE id = ?", (file_id,))
        self.conn.commit()

    def get_tasks_by_user_id(self, user_id: int) -> List[dict]:
        cur = self.conn.cursor()
        cur.execute("SELECT id, title, due_date FROM tasks WHERE user_id = ?", (user_id,))
        tasks = [{"id": row[0], "title": row[1], "due_date": row[2]} for row in cur.fetchall()]
        return tasks

    def get_events_by_user_id(self, user_id):
        with self.conn:
            cur = self.conn.cursor()
            cur.execute("SELECT id, name, date_time FROM events WHERE user_id = ?", (user_id,))
            events = [{'id': row[0], 'name': row[1], 'date_time': row[2]} for row in cur.fetchall()]
        return events

    def get_files_by_user_id(self, user_id: int) -> List[dict]:
        cur = self.conn.cursor()
        cur.execute("SELECT id, file_id, file_name FROM files WHERE user_id = ?", (user_id,))
        files = [{"id": row[0], "file_id": row[1], "file_name": row[2]} for row in cur.fetchall()]
        return files

if __name__ == "__main__":
    db = Database()