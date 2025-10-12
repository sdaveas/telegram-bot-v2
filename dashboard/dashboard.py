from fastapi import FastAPI
import sqlite3

app = FastAPI()

DB_PATH = "database/messages.db"


def query_db(query, args=()):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(query, args)
        return [dict(row) for row in cur.fetchall()]


@app.get("/")
def home():
    available_endpoints = [
        {"path": "/messages/count", "method": "GET"},
        {"path": "/messages/recent", "method": "GET"},
        {"path": "/chats", "method": "GET"},
        {"path": "/settings/{chat_id}", "method": "GET"},
    ]
    return {"available_endpoints": available_endpoints}


@app.get("/chats")
def chats():
    return query_db("SELECT DISTINCT chat_id FROM messages")


@app.get("/messages/count")
def messages_count():
    result = query_db("SELECT chat_id, COUNT(*) as count FROM messages GROUP BY chat_id")
    return result[0]


@app.get("/messages/recent")
def recent_messages(limit: int = 10, chat_id: int = None):
    if chat_id is not None:
        return query_db(
            "SELECT * FROM messages WHERE chat_id = ? ORDER BY timestamp DESC LIMIT ?",
            (chat_id, limit),
        )
    else:
        return query_db("SELECT * FROM messages ORDER BY timestamp DESC LIMIT ?", (limit,))


@app.get("/settings/{chat_id}")
def chat_settings(chat_id: int):
    return query_db("SELECT * FROM settings WHERE chat_id = ?", (chat_id,))
