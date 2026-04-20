-- ===============================
-- DATABASE
-- ===============================
CREATE DATABASE IF NOT EXISTS final_project;
USE final_project;

-- ===============================
-- USERS (AUTH)
-- ===============================
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('staff', 'donor', 'recipient') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===============================
-- HOSPITAL
-- ===============================
CREATE TABLE hospital (
    hospital_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    latitude FLOAT,
    longitude FLOAT
);

-- ===============================
-- STAFF
-- ===============================
CREATE TABLE staff (
    staff_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(100),
    specialization VARCHAR(100),
    phone VARCHAR(20),
    hospital_id INT,
    FOREIGN KEY (hospital_id) REFERENCES hospital(hospital_id)
);

-- ===============================
-- DONOR
-- ===============================
CREATE TABLE donor (
    donor_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    dob DATE,
    blood_group VARCHAR(5),
    gender VARCHAR(10),
    phone VARCHAR(20),
    address TEXT,
    latitude FLOAT,
    longitude FLOAT,
    status VARCHAR(50),
    hospital_id INT,
    FOREIGN KEY (hospital_id) REFERENCES hospital(hospital_id)
);

-- ===============================
-- ORGAN
-- ===============================
CREATE TABLE organ (
    organ_id INT AUTO_INCREMENT PRIMARY KEY,
    type VARCHAR(50),
    blood_group VARCHAR(5),
    status VARCHAR(50) DEFAULT 'Available',
    donor_id INT,
    hospital_id INT,
    FOREIGN KEY (donor_id) REFERENCES donor(donor_id),
    FOREIGN KEY (hospital_id) REFERENCES hospital(hospital_id)
);

-- ===============================
-- RECIPIENT
-- ===============================
CREATE TABLE recipient (
    recipient_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    dob DATE,
    blood_group VARCHAR(5),
    gender VARCHAR(10),
    phone VARCHAR(20),
    address TEXT,
    urgency_level VARCHAR(50),
    registered_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    hospital_id INT,
    FOREIGN KEY (hospital_id) REFERENCES hospital(hospital_id)
);

-- ===============================
-- TRANSPLANT REQUEST
-- ===============================
CREATE TABLE transplant_request (
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    organ_needed VARCHAR(50),
    urgency_level VARCHAR(50),
    requested_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'Pending',
    recipient_id INT,
    FOREIGN KEY (recipient_id) REFERENCES recipient(recipient_id)
);

-- ===============================
-- MATCHING RECORD
-- ===============================
CREATE TABLE matching_record (
    match_id INT AUTO_INCREMENT PRIMARY KEY,
    compatibility_score FLOAT,
    status VARCHAR(50) DEFAULT 'Pending',
    matched_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    request_id INT,
    organ_id INT,
    approved_by INT,
    FOREIGN KEY (request_id) REFERENCES transplant_request(request_id),
    FOREIGN KEY (organ_id) REFERENCES organ(organ_id),
    FOREIGN KEY (approved_by) REFERENCES staff(staff_id)
);

-- ===============================
-- TRANSPLANT
-- ===============================
CREATE TABLE transplant (
    transplant_id INT AUTO_INCREMENT PRIMARY KEY,
    surgery_date DATE,
    outcome VARCHAR(100),
    match_id INT,
    surgeon_id INT,
    hospital_id INT,
    FOREIGN KEY (match_id) REFERENCES matching_record(match_id),
    FOREIGN KEY (surgeon_id) REFERENCES staff(staff_id),
    FOREIGN KEY (hospital_id) REFERENCES hospital(hospital_id)
);

-- ===============================
-- NOTIFICATIONS
-- ===============================
CREATE TABLE notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    message TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);