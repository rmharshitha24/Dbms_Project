from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from db import get_db_connection

app = Flask(__name__)
CORS(app)


def is_blood_compatible(donor_bg, recipient_bg):
    compatibility = {
        "O+": ["O+"],
        "A+": ["A+", "O+"],
        "B+": ["B+", "O+"],
        "AB+": ["A+", "B+", "AB+", "O+"]
    }
    return donor_bg in compatibility.get(recipient_bg, [])


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

    if organ['hospital_id'] == request['hospital_id']:
        score += 10

    if organ['status'] == "Available":
        score += 10

    return score

def is_blood_compatible(donor_bg, recipient_bg):
    compatibility = {
        "O+": ["O+"],
        "A+": ["A+", "O+"],
        "B+": ["B+", "O+"],
        "AB+": ["A+", "B+", "AB+", "O+"]
    }
    return donor_bg in compatibility.get(recipient_bg, [])


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

    if organ['hospital_id'] == request['hospital_id']:
        score += 10

    if organ['status'] == "Available":
        score += 10

    return score
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
        result = cursor.fetchone()
        return jsonify({
            "message": "Database connection successful",
            "result": result
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


# ---------------- AUTH ----------------
@app.route('/register', methods=['POST'])
def register_user():
    conn = None
    cursor = None
    try:
        data = request.get_json()

        if not data.get('username') or not data.get('password') or not data.get('role'):
            return jsonify({"error": "username, password and role are required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO users (username, password, role)
            VALUES (%s, %s, %s)
        """, (data['username'], data['password'], data['role']))

        conn.commit()
        return jsonify({"message": "User registered"}), 201

    except mysql.connector.IntegrityError:
        return jsonify({"error": "Username exists"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


@app.route('/login', methods=['POST'])
def login_user():
    conn = None
    cursor = None
    try:
        data = request.get_json()

        if not data.get('username') or not data.get('password'):
            return jsonify({"error": "username and password are required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT user_id, username, role
            FROM users
            WHERE username=%s AND password=%s
        """, (data['username'], data['password']))

        user = cursor.fetchone()

        if user:
            return jsonify({"message": "Login successful", "user": user}), 200
        return jsonify({"error": "Invalid credentials"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


# ---------------- HOSPITAL ----------------
@app.route('/hospital', methods=['POST'])
def add_hospital():
    conn = None
    cursor = None
    try:
        data = request.get_json()

        if not data.get('name') or not data.get('address'):
            return jsonify({"error": "name and address are required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO hospital (name, address) VALUES (%s, %s)",
            (data['name'], data['address'])
        )

        conn.commit()
        return jsonify({"message": "Hospital added"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


@app.route('/hospital', methods=['GET'])
def get_hospitals():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM hospital")
        result = cursor.fetchall()

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


# ---------------- STAFF ----------------
@app.route('/staff', methods=['POST'])
def add_staff():
    conn = None
    cursor = None
    check_cursor = None
    try:
        data = request.get_json()

        required_fields = ['name', 'role', 'specialization', 'hospital_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Missing field: {field}"}), 400

        conn = get_db_connection()
        check_cursor = conn.cursor(dictionary=True)

        check_cursor.execute("""
            SELECT staff_id
            FROM staff
            WHERE hospital_id = %s AND role = %s AND specialization = %s
        """, (
            data['hospital_id'],
            data['role'],
            data['specialization']
        ))

        existing = check_cursor.fetchone()
        if existing:
            return jsonify({"error": "This hospital already has that role + specialization combination"}), 400

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO staff (name, role, specialization, phone, hospital_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            data['name'],
            data['role'],
            data['specialization'],
            data.get('phone'),
            data['hospital_id']
        ))

        conn.commit()
        return jsonify({"message": "Staff added successfully"}), 201

    except mysql.connector.IntegrityError:
        return jsonify({"error": "This hospital already has that role + specialization combination"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if check_cursor:
            check_cursor.close()
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


@app.route('/staff', methods=['GET'])
def get_staff():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM staff")
        result = cursor.fetchall()

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


# ---------------- RECIPIENT BASIC ----------------
@app.route('/recipients', methods=['POST'])
def add_recipient():
    conn = None
    cursor = None
    try:
        data = request.get_json()

        if not data.get('name') or not data.get('dob') or not data.get('blood_group') or not data.get('hospital_id'):
            return jsonify({"error": "name, dob, blood_group and hospital_id are required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO recipient
            (name, dob, blood_group, gender, phone, address, urgency_level, hospital_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['name'],
            data['dob'],
            data['blood_group'],
            data.get('gender'),
            data.get('phone'),
            data.get('address'),
            data.get('urgency_level'),
            data['hospital_id']
        ))

        conn.commit()
        return jsonify({"message": "Recipient added"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


@app.route('/recipients', methods=['GET'])
def get_recipients():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM recipient")
        result = cursor.fetchall()

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


@app.route('/recipients/<int:recipient_id>', methods=['GET'])
def get_recipient_by_id(recipient_id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM recipient WHERE recipient_id = %s"
        cursor.execute(query, (recipient_id,))
        data = cursor.fetchone()

        if data:
            return jsonify(data), 200
        return jsonify({"error": "Recipient not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


# ---------------- DONOR BASIC ----------------
@app.route('/donors', methods=['POST'])
def add_donor():
    conn = None
    cursor = None
    try:
        data = request.get_json()

        cursor = None
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO donor
            (name, dob, blood_group, gender, phone, address, latitude, longitude, status, hospital_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['name'],
            data['dob'],
            data['blood_group'],
            data.get('gender'),
            data.get('phone'),
            data.get('address'),
            data.get('latitude'),
            data.get('longitude'),
            data['status'],
            data['hospital_id']
        ))

        conn.commit()
        donor_id = cursor.lastrowid

        return jsonify({
            "message": "Donor added successfully",
            "donor_id": donor_id
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


# ---------------- RECIPIENT PROFILE ----------------
@app.route('/recipients/profile', methods=['POST'])
def create_recipient_profile():
    conn = None
    cursor = None
    insert_cursor = None
    try:
        data = request.get_json()

        required_fields = ['user_id', 'name', 'dob', 'blood_group', 'hospital_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Missing field: {field}"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT recipient_id FROM recipient WHERE user_id = %s", (data['user_id'],))
        existing = cursor.fetchone()
        if existing:
            return jsonify({"error": "Recipient profile already exists"}), 400

        insert_cursor = conn.cursor()
        insert_cursor.execute("""
            INSERT INTO recipient
            (user_id, name, dob, blood_group, gender, phone, address, hospital_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['user_id'],
            data['name'],
            data['dob'],
            data['blood_group'],
            data.get('gender'),
            data.get('phone'),
            data.get('address'),
            data['hospital_id']
        ))

        conn.commit()
        recipient_id = insert_cursor.lastrowid

        return jsonify({
            "message": "Recipient profile created successfully",
            "recipient_id": recipient_id
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if insert_cursor:
            insert_cursor.close()
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


@app.route('/recipients/profile/<int:user_id>', methods=['GET'])
def get_recipient_profile_by_user(user_id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM recipient WHERE user_id = %s", (user_id,))
        data = cursor.fetchone()

        if not data:
            return jsonify({"error": "Recipient profile not found"}), 404

        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


# ---------------- DONOR PROFILE ----------------
@app.route('/donors/profile', methods=['POST'])
def create_donor_profile():
    conn = None
    cursor = None
    insert_cursor = None
    try:
        data = request.get_json()

        required_fields = ['user_id', 'name', 'dob', 'blood_group', 'hospital_id', 'condition']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Missing field: {field}"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT donor_id FROM donor WHERE user_id = %s", (data['user_id'],))
        existing = cursor.fetchone()
        if existing:
            return jsonify({"error": "Donor profile already exists"}), 400

        insert_cursor = conn.cursor()
        insert_cursor.execute("""
            INSERT INTO donor
            (user_id, name, dob, blood_group, gender, phone, address, status, donor_condition, hospital_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'Active', %s, %s)
        """, (
            data['user_id'],
            data['name'],
            data['dob'],
            data['blood_group'],
            data.get('gender'),
            data.get('phone'),
            data.get('address'),
            data['condition'],
            data['hospital_id']
        ))

        conn.commit()
        donor_id = insert_cursor.lastrowid

        return jsonify({
            "message": "Donor profile created successfully",
            "donor_id": donor_id
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if insert_cursor:
            insert_cursor.close()
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


@app.route('/donors/profile/<int:user_id>', methods=['GET'])
def get_donor_profile(user_id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM donor WHERE user_id = %s", (user_id,))
        data = cursor.fetchone()

        if not data:
            return jsonify({"error": "Donor profile not found"}), 404

        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


# ---------------- REQUESTS ----------------
@app.route('/requests', methods=['POST'])
def add_request():
    conn = None
    cursor = None
    try:
        data = request.get_json()

        if not data.get('organ_needed') or not data.get('urgency_level') or not data.get('recipient_id'):
            return jsonify({"error": "organ_needed, urgency_level and recipient_id are required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO transplant_request
            (organ_needed, urgency_level, status, recipient_id)
            VALUES (%s, %s, %s, %s)
        """, (
            data['organ_needed'],
            data['urgency_level'],
            data.get('status', 'Pending'),
            data['recipient_id']
        ))

        conn.commit()

        return jsonify({
            "message": "Request created",
            "request_id": cursor.lastrowid
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


@app.route('/requests', methods=['GET'])
def get_requests():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT tr.*, r.name AS recipient_name
            FROM transplant_request tr
            JOIN recipient r ON tr.recipient_id = r.recipient_id
        """)

        result = cursor.fetchall()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


@app.route('/requests/recipient/<int:recipient_id>', methods=['GET'])
def get_requests_by_recipient(recipient_id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT request_id, organ_needed, urgency_level, status, requested_on
            FROM transplant_request
            WHERE recipient_id = %s
            ORDER BY requested_on DESC
        """, (recipient_id,))

        data = cursor.fetchall()
        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


@app.route('/requests/<int:request_id>/status', methods=['PUT'])
def update_request_status(request_id):
    conn = None
    cursor = None
    try:
        data = request.get_json()

        if not data.get('status'):
            return jsonify({"error": "status is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE transplant_request
            SET status = %s, notes = %s
            WHERE request_id = %s
        """, (
            data['status'],
            data.get('notes'),
            request_id
        ))

        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Request not found"}), 404

        return jsonify({"message": "Request status and notes updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


@app.route('/requests/<int:request_id>/urgency', methods=['PUT'])
def update_request_urgency(request_id):
    conn = None
    cursor = None
    try:
        data = request.get_json()
        if not data or not data.get('urgency_level'):
            return jsonify({"error": "urgency_level is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE transplant_request
            SET urgency_level = %s
            WHERE request_id = %s
        """, (data['urgency_level'], request_id))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Request not found"}), 404

        return jsonify({"message": "Urgency level updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


@app.route('/requests/<int:request_id>', methods=['DELETE'])
def delete_request(request_id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM transplant_request WHERE request_id = %s", (request_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Request not found"}), 404

        return jsonify({"message": "Request deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


# ---------------- NOTIFICATIONS ----------------
@app.route('/notifications/<int:user_id>', methods=['GET'])
def get_notifications(user_id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT notification_id, message, is_read, created_at
            FROM notifications
            WHERE user_id = %s
              AND created_at >= NOW() - INTERVAL 1 DAY
            ORDER BY created_at DESC
        """, (user_id,))

        notifications = cursor.fetchall()
        return jsonify(notifications), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


# ---------------- ORGANS ----------------
@app.route('/organs', methods=['POST'])
def add_organ():
    conn = None
    cursor = None
    notify_cursor = None
    try:
        data = request.get_json()

        required_fields = ['type', 'blood_group', 'donor_id', 'hospital_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Missing field: {field}"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO organ (organ_type, blood_group, status, donor_id, hospital_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            data['type'],
            data['blood_group'],
            data.get('status', 'Available'),
            data['donor_id'],
            data['hospital_id']
        ))
        organ_id = cursor.lastrowid

        notify_cursor = conn.cursor()
        notify_cursor.execute("SELECT user_id FROM recipient WHERE user_id IS NOT NULL")
        recipient_users = notify_cursor.fetchall()

        for row in recipient_users:
            notify_cursor.execute("""
                INSERT INTO notifications (user_id, message, is_read)
                VALUES (%s, %s, FALSE)
            """, (
                row[0],
                f"New organ available: {data['type']}. Please check if it matches your requirement."
            ))

        conn.commit()

        return jsonify({
            "message": "Organ added successfully",
            "organ_id": organ_id
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if notify_cursor:
            notify_cursor.close()
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


# ---------------- MATCHING ----------------
@app.route('/matches/approve', methods=['POST'])
def approve_match():
    conn = None
    cursor = None
    notify_cursor = None

    try:
        data = request.get_json()

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert match
        cursor.execute("""
            INSERT INTO matching_record
            (compatibility_score, status, request_id, organ_id, approved_by)
            VALUES (%s, 'Approved', %s, %s, %s)
        """, (
            data['score'],
            data['request_id'],
            data['organ_id'],
            data['approved_by']
        ))

        # Update request + organ
        cursor.execute("""
            UPDATE transplant_request SET status='Approved'
            WHERE request_id=%s
        """, (data['request_id'],))

        cursor.execute("""
            UPDATE organ SET status='Reserved'
            WHERE organ_id=%s
        """, (data['organ_id'],))

        # Notifications
        notify_cursor = conn.cursor(dictionary=True)

        notify_cursor.execute("""
            SELECT r.user_id AS recipient_user_id,
                   d.user_id AS donor_user_id,
                   o.organ_type
            FROM transplant_request tr
            JOIN recipient r ON tr.recipient_id = r.recipient_id
            JOIN organ o ON o.organ_id = %s
            JOIN donor d ON o.donor_id = d.donor_id
            WHERE tr.request_id = %s
        """, (data['organ_id'], data['request_id']))

        row = notify_cursor.fetchone()

        if row:
            if row['recipient_user_id']:
                notify_cursor.execute("""
                    INSERT INTO notifications (user_id, message)
                    VALUES (%s, %s)
                """, (
                    row['recipient_user_id'],
                    f"Your request has been approved for {row['organ_type']}"
                ))

            if row['donor_user_id']:
                notify_cursor.execute("""
                    INSERT INTO notifications (user_id, message)
                    VALUES (%s, %s)
                """, (
                    row['donor_user_id'],
                    f"Your organ {row['organ_type']} has been matched"
                ))

        conn.commit()

        return jsonify({"message": "Match approved"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if notify_cursor:
            notify_cursor.close()
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

@app.route('/hospital/profile', methods=['POST'])
def create_hospital_profile():
    conn = None
    cursor = None
    insert_cursor = None
    try:
        data = request.get_json()

        required_fields = ['user_id', 'name', 'address']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Missing field: {field}"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT hospital_id FROM hospital WHERE user_id = %s", (data['user_id'],))
        existing = cursor.fetchone()
        if existing:
            return jsonify({"error": "Hospital already registered for this user"}), 400

        insert_cursor = conn.cursor()
        insert_cursor.execute("""
            INSERT INTO hospital (user_id, name, address)
            VALUES (%s, %s, %s)
        """, (
            data['user_id'],
            data['name'],
            data['address']
        ))

        conn.commit()

        return jsonify({
            "message": "Hospital created successfully",
            "hospital_id": insert_cursor.lastrowid
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if insert_cursor:
            insert_cursor.close()
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

@app.route('/hospital/profile/<int:user_id>', methods=['GET'])
def get_hospital_profile_by_user(user_id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM hospital WHERE user_id = %s", (user_id,))
        data = cursor.fetchone()

        if not data:
            return jsonify({"error": "Hospital profile not found"}), 404

        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

@app.route('/requests/details', methods=['GET'])
def get_request_details():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                tr.request_id,
                tr.organ_needed,
                tr.urgency_level,
                tr.status,
                tr.notes,
                tr.requested_on,
                r.name AS recipient_name,
                d.name AS donor_name,
                o.organ_type AS matched_organ_type,
                mr.match_id
            FROM transplant_request tr
            JOIN recipient r ON tr.recipient_id = r.recipient_id
            LEFT JOIN matching_record mr ON tr.request_id = mr.request_id
            LEFT JOIN organ o ON mr.organ_id = o.organ_id
            LEFT JOIN donor d ON o.donor_id = d.donor_id
            ORDER BY tr.request_id DESC
        """)

        return jsonify(cursor.fetchall()), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

@app.route('/transplants', methods=['POST'])
def create_transplant():
    conn = None
    cursor = None
    try:
        data = request.get_json()

        required_fields = ['match_id', 'surgery_date', 'outcome', 'surgeon_id', 'hospital_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Missing field: {field}"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO transplant (surgery_date, outcome, match_id, surgeon_id, hospital_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            data['surgery_date'],
            data['outcome'],
            data['match_id'],
            data['surgeon_id'],
            data['hospital_id']
        ))

        conn.commit()

        return jsonify({
            "message": "Transplant recorded successfully",
            "transplant_id": cursor.lastrowid
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)