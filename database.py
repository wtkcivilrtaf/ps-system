# -*- coding: utf-8 -*-
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime, date, timedelta
import os
import hashlib
import hmac

# --- START: NEW POSTGRESQL CONFIG ---
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "ps_system_db"
DB_USER = "ps_admin"
DB_PASS = "Sup3rS@f3P@ssw0rd!" # ต้องตรงกับ docker-compose.yml
# --- END: NEW POSTGRESQL CONFIG ---

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    return conn

def hash_password(password, salt=None):
    if salt is None: salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt, key

# --- ฟังก์ชันที่ตกหล่นคราวที่แล้ว ---
def verify_password(salt, key, password_to_check):
    return hmac.compare_digest(key, hash_password(password_to_check, salt)[1])

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=DictCursor)

    cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, salt BYTEA NOT NULL, key BYTEA NOT NULL, rank TEXT, first_name TEXT, last_name TEXT, position TEXT, department TEXT, role TEXT NOT NULL)')
    cursor.execute('CREATE TABLE IF NOT EXISTS personnel (id TEXT PRIMARY KEY, rank TEXT, first_name TEXT, last_name TEXT, position TEXT, specialty TEXT, department TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS status_reports (id TEXT PRIMARY KEY, date TEXT NOT NULL, submitted_by TEXT, department TEXT, timestamp TIMESTAMPTZ, report_data JSONB)')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS archived_reports (
            id TEXT PRIMARY KEY,
            week_range TEXT,
            report_data JSONB,
            archived_by TEXT,
            timestamp TIMESTAMPTZ
        )
    ''')
    cursor.execute('CREATE TABLE IF NOT EXISTS sessions (token TEXT PRIMARY KEY, username TEXT NOT NULL, created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (username) REFERENCES users (username) ON DELETE CASCADE)')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS persistent_statuses (
            id TEXT PRIMARY KEY,
            personnel_id TEXT NOT NULL,
            department TEXT NOT NULL,
            status TEXT,
            details TEXT,
            start_date DATE,
            end_date DATE,
            FOREIGN KEY (personnel_id) REFERENCES personnel (id) ON DELETE CASCADE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_reports (
            id TEXT PRIMARY KEY,
            report_date DATE NOT NULL,
            department TEXT NOT NULL,
            submitted_by TEXT NOT NULL,
            timestamp TIMESTAMPTZ,
            summary_data JSONB,
            report_data JSONB
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS archived_daily_reports (
            id TEXT PRIMARY KEY,
            year INTEGER NOT NULL,
            month INTEGER NOT NULL,
            report_date DATE NOT NULL,
            department TEXT NOT NULL,
            submitted_by TEXT NOT NULL,
            timestamp TIMESTAMPTZ,
            summary_data JSONB,
            report_data JSONB
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS holidays (
            date DATE PRIMARY KEY,
            description TEXT NOT NULL
        )
    ''')
    cursor.execute('CREATE TABLE IF NOT EXISTS system_settings (key TEXT PRIMARY KEY, value TEXT)')

    cursor.execute("SELECT value FROM system_settings WHERE key = 'current_week_start_date'")
    if not cursor.fetchone():
        today = date.today()
        start_of_current_week = today - timedelta(days=today.weekday())
        cursor.execute("INSERT INTO system_settings (key, value) VALUES (%s, %s)", 
                       ('current_week_start_date', start_of_current_week.isoformat()))

    cursor.execute("SELECT * FROM users WHERE username = %s", ('jeerawut',))
    if not cursor.fetchone():
        print("กำลังสร้างผู้ดูแลระบบ 'jeerawut'...")
        salt, key = hash_password("Jee@wut2534")
        cursor.execute("INSERT INTO users (username, salt, key, rank, first_name, last_name, position, department, role) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                       ('jeerawut', salt, key, 'น.อ.', 'จีราวุฒิ', 'ผู้ดูแลระบบ', 'ผู้ดูแลระบบ', 'ส่วนกลาง', 'admin'))

    conn.commit()
    cursor.close()
    conn.close()
    print("ฐานข้อมูล PostgreSQL พร้อมใช้งาน")