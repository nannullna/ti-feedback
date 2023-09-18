import sqlite3
import os
import json
from dataclasses import dataclass
from copy import deepcopy


DB_FILE = "data/db.db"
RESOURCE_DIR = "./"


db = sqlite3.connect(DB_FILE)

try:
    db.execute("SELECT * FROM users").fetchall()
    db.close()

except sqlite3.OperationalError:
    db.execute(
        '''
        CREATE TABLE IF NOT EXISTS questions (
            id TEXT PRIMARY KEY NOT NULL,
            file TEXT NOT NULL,
            uid TEXT,
            assigned_at DATETIME,
            FOREIGN KEY (uid) REFERENCES users (id)
        )
        '''
    )
    db.execute(
        '''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            datetime DATETIME DEFAULT CURRENT_TIMESTAMP,
            uid TEXT NOT NULL,
            qid TEXT NOT NULL,
            qno INTEGER NOT NULL,
            binary_response TEXT,
            rank_response TEXT, 
            FOREIGN KEY (qid) REFERENCES questions (id),
            FOREIGN KEY (uid) REFERENCES users (id)
        )
        '''
    )
    db.execute(
        '''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY NOT NULL,
            email TEXT NOT NULL,
            age TEXT NOT NULL,
            sex TEXT NOT NULL,
            phone TEXT,
            agreed BOOLEAN NOT NULL,
            datetime TEXT NOT NULL,
            qid TEXT NOT NULL,
            FOREIGN KEY (qid) REFERENCES questions (id)
        )
        '''
    )
    db.commit()

    # TODO: add questions
    db.execute("INSERT INTO questions (id, file) VALUES (?, ?)", ("000001", "questions/000001.json"))
    db.execute("INSERT INTO questions (id, file) VALUES (?, ?)", ("000002", "questions/000001.json"))
    db.execute("INSERT INTO questions (id, file) VALUES (?, ?)", ("000003", "questions/000001.json"))
    db.execute("INSERT INTO questions (id, file) VALUES (?, ?)", ("000004", "questions/000001.json"))
    db.execute("INSERT INTO questions (id, file) VALUES (?, ?)", ("000005", "questions/000001.json"))
    db.execute("INSERT INTO questions (id, file) VALUES (?, ?)", ("000006", "questions/000001.json"))
    db.execute("INSERT INTO questions (id, file) VALUES (?, ?)", ("000007", "questions/000001.json"))
    db.commit()
    
    db.close()


def check_email_exists(email) -> bool:
    db = sqlite3.connect(DB_FILE)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    result = cursor.fetchone()
    db.close()
    print(result)
    return result is not None


def add_user(uuid, email, age, sex, phone, agreed, datetime, question_id):
    db = sqlite3.connect(DB_FILE)
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (uuid, email, age, sex, phone, agreed, datetime, question_id)
    )
    db.commit()
    db.close()


def get_user_info(email) -> dict:
    """Returns a user dict from the database, given an email address."""
    db = sqlite3.connect(DB_FILE)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    result = cursor.fetchone()
    db.close()
    return result


# TODO: question logic
def get_questions(question_id):
    db = sqlite3.connect(DB_FILE)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM questions WHERE id=?", (question_id,))
    result = cursor.fetchone()
    db.close()

    with open(os.path.join(RESOURCE_DIR, result[1]), "r") as f:
        questions = json.load(f)
    return questions


def get_new_question_id(uuid_: str):
    db = sqlite3.connect(DB_FILE)
    cursor = db.cursor()
    # TODO: get the next question id whose uid is null
    question_id = None
    cursor.execute("SELECT * FROM questions WHERE uid IS NULL")
    result = cursor.fetchone()
    if result is not None:
        question_id = result[0]
        cursor.execute("UPDATE questions SET uid=?, assigned_at=CURRENT_TIMESTAMP WHERE id=?", (uuid_, question_id))
        db.commit()
    db.close()
    return question_id


def submit_response(uuid, question_id, progress, binary_responses, *rank_responses):
    print(uuid, question_id, progress, binary_responses)
    print(rank_responses)
    db = sqlite3.connect(DB_FILE)
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO responses (uid, qid, qno, binary_response, rank_response) VALUES (?, ?, ?, ?, ?)",
        (uuid, question_id, progress, str(binary_responses), str(rank_responses))
    )
    db.commit()

    # Print the number of responses
    cursor.execute("SELECT * FROM responses")
    print(cursor.fetchall())

    db.close()
