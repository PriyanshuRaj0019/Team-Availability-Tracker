from flask import Flask, render_template, jsonify, request
import sqlite3
import os

app = Flask(__name__)

DATABASE = os.path.join("database", "team.db")


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs("database", exist_ok=True)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            available BOOLEAN NOT NULL DEFAULT 1
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]

    if count == 0:
        users = [
            ("John Doe", True),
            ("Alice Smith", False),
            ("Bob Johnson", True),
            ("Emma Wilson", True),
            ("David Brown", False),
            ("Sophia Davis", True)
        ]

        cursor.executemany(
            "INSERT INTO users (name, available) VALUES (?, ?)",
            users
        )

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return render_template("index.html")


# ----------------------------
# GET ALL USERS
# ----------------------------
@app.route("/users", methods=["GET"])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()

    conn.close()

    users = []

    for row in rows:
        users.append({
            "id": row["id"],
            "name": row["name"],
            "available": bool(row["available"])
        })

    return jsonify(users)


# ----------------------------
# UPDATE AVAILABILITY
# ----------------------------
@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):

    data = request.get_json()

    if not data or "available" not in data:
        return jsonify({
            "success": False,
            "message": "available field is required"
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE id=?",
        (user_id,)
    )

    user = cursor.fetchone()

    if user is None:
        conn.close()
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    try:
        cursor.execute(
            "UPDATE users SET available=? WHERE id=?",
            (data["available"], user_id)
        )

        conn.commit()

        cursor.execute(
            "SELECT * FROM users WHERE id=?",
            (user_id,)
        )

        updated = cursor.fetchone()

        conn.close()

        return jsonify({
            "success": True,
            "id": updated["id"],
            "name": updated["name"],
            "available": bool(updated["available"])
        })

    except Exception:
        conn.close()

        return jsonify({
            "success": False,
            "message": "Database update failed"
        }), 500

if __name__ == "__main__":
    init_db()
    app.run(debug=True)