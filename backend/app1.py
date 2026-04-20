from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from db import get_db_connection
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ---------------- MATCHING HELPERS ----------------

def is_blood_compatible(donor_bg, recipient_bg):
    compatibility = {
        "O+": ["O+"],
        "A+": ["A+", "O+"],
        "B+": ["B+", "O+"],
        "AB+": ["A+", "B+", "AB+", "O+"]
    }
    return recipient_bg in compatibility.get(donor_bg, [])

def calculate_score(organ, request):
    score = 0

    if organ['blood_group'] == request['blood_group']:
        score += 50
    elif is_blood_compatible(organ['blood_group'], request['blood_group']):
        score += 30
    else:
        return 0

    urgency_map = {"High": 30, "Medium": 20, "Low": 10}
    score += urgency_map.get(request['urgency_level'], 0)

    if organ['hospital_id'] == request.get('hospital_id'):
        score += 10

    if organ['status'] == "Available":
        score += 10

    return score


def find_best_match(cursor, organ):
    cursor.execute("""
        SELECT r.*, rec.blood_group
        FROM transplant_request r
        JOIN recipient rec ON r.recipient_id = rec.recipient_id
        WHERE r.organ_needed = %s AND r.status = 'Pending'
    """, (organ["organ_type"],))

    requests = cursor.fetchall()

    best = None
    best_score = -1

    for r in requests:
        score = calculate_score(
            organ,
            {
                "blood_group": r["blood_group"],
                "urgency_level": r["urgency_level"],
                "hospital_id": r.get("hospital_id")
            }
        )

        if score == 0:
            continue

        # SAFE datetime handling
        days = 0
        if r.get("requested_on"):
            try:
                if isinstance(r["requested_on"], str):
                    dt = datetime.strptime(r["requested_on"], "%Y-%m-%d %H:%M:%S")
                else:
                    dt = r["requested_on"]
                days = (datetime.now() - dt).days
            except:
                days = 0

        score += days * 2

        if score > best_score:
            best_score = score
            best = r

    return best, best_score


# ---------------- BASIC ----------------
@app.route('/')
def home():
    return jsonify({"message": "API is running"}), 200


@app.route('/db-test', methods=['GET'])
def db_test():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        return jsonify({"message": "Database connection successful"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()


# ---------------- AUTH ----------------
@app.route('/register', methods=['POST'])
def register_user():
    conn = get_db_connection()
    cursor = conn.cursor()

    data = request.get_json()

    cursor.execute("""
        INSERT INTO users (username, password, role)
        VALUES (%s, %s, %s)
    """, (data['username'], data['password'], data['role']))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "User registered"})


@app.route('/login', methods=['POST'])
def login_user():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    data = request.get_json()

    cursor.execute("""
        SELECT user_id, username, role
        FROM users
        WHERE username=%s AND password=%s
    """, (data['username'], data['password']))

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user:
        return jsonify({"user": user})
    return jsonify({"error": "Invalid credentials"}), 401


# ---------------- MATCHING ROUTE ----------------
@app.route("/match/<int:organ_id>", methods=["POST"])
def auto_match(organ_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT * FROM organ 
            WHERE organ_id = %s AND status = 'Available'
        """, (organ_id,))
        organ = cursor.fetchone()

        if not organ:
            return jsonify({"error": "Organ not available"}), 400

        best, score = find_best_match(cursor, organ)

        if not best:
            return jsonify({"error": "No match found"}), 404

        return jsonify({
            "request_id": best["request_id"],
            "recipient_id": best["recipient_id"],
            "score": score
        })

    finally:
        cursor.close()
        conn.close()


# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)