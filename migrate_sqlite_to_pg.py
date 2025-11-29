import sqlite3
import psycopg2
from database import get_db_connection

def migrate_data():
    print("🚀 เครื่องมือย้ายข้อมูล SQLite -> PostgreSQL")
    print("-------------------------------------------")
    print("กรุณาเลือกโหมดการทำงาน:")
    print("1. [แนะนำ] ล้างข้อมูลในระบบใหม่ทิ้งทั้งหมด แล้วนำเข้าจากไฟล์เก่า (Clean Import)")
    print("   * เหมาะสำหรับต้องการให้ข้อมูลเหมือนไฟล์เก่า 100%")
    print("2. อัปเดตทับข้อมูลเดิม (Update Overwrite)")
    print("   * ข้อมูลที่มีอยู่แล้วจะถูกทับด้วยข้อมูลจากไฟล์เก่า ข้อมูลใหม่ที่ไม่ซ้ำจะยังอยู่")
    
    choice = input("เลือก (1/2): ").strip()
    
    # 1. เชื่อมต่อฐานข้อมูล
    try:
        sqlite_conn = sqlite3.connect('database.db')
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()
        
        pg_conn = get_db_connection()
        pg_cursor = pg_conn.cursor()
    except Exception as e:
        print(f"❌ เชื่อมต่อฐานข้อมูลไม่สำเร็จ: {e}")
        return

    try:
        # --- โหมด 1: ล้างข้อมูลเก่าก่อน ---
        if choice == '1':
            print("\n🧹 กำลังล้างข้อมูลใน PostgreSQL...")
            # เรียงลำดับการลบเพื่อป้องกัน Foreign Key Error
            pg_cursor.execute("DELETE FROM status_reports")
            pg_cursor.execute("DELETE FROM daily_reports")
            pg_cursor.execute("DELETE FROM persistent_statuses")
            pg_cursor.execute("DELETE FROM holidays")
            pg_cursor.execute("DELETE FROM personnel") # ลบกำลังพล
            pg_cursor.execute("DELETE FROM sessions")
            pg_cursor.execute("DELETE FROM users")     # ลบผู้ใช้
            pg_conn.commit()
            print("✅ ล้างข้อมูลเรียบร้อย")

        # --- ย้ายข้อมูล Users ---
        print("\n👤 กำลังย้ายข้อมูลผู้ใช้งาน (Users)...")
        sqlite_cursor.execute("SELECT * FROM users")
        users = sqlite_cursor.fetchall()
        for user in users:
            try:
                role = user['role'] if 'role' in user.keys() else 'user'
                
                query = """
                    INSERT INTO users (username, salt, key, rank, first_name, last_name, position, department, role)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                if choice == '2': # ถ้าเลือก Update
                    query += """
                        ON CONFLICT (username) DO UPDATE SET
                        salt = EXCLUDED.salt, key = EXCLUDED.key, rank = EXCLUDED.rank,
                        first_name = EXCLUDED.first_name, last_name = EXCLUDED.last_name,
                        position = EXCLUDED.position, department = EXCLUDED.department, role = EXCLUDED.role
                    """
                else:
                    query += " ON CONFLICT (username) DO NOTHING"

                pg_cursor.execute(query, (
                    user['username'], user['salt'], user['key'], user['rank'],
                    user['first_name'], user['last_name'], user['position'],
                    user['department'], role
                ))
            except Exception as e:
                print(f"  - Error user {user['username']}: {e}")

        # --- ย้ายข้อมูล Personnel ---
        print("\n👥 กำลังย้ายข้อมูลกำลังพล (Personnel)...")
        # เช็คคอลัมน์ใน SQLite
        sqlite_cursor.execute("PRAGMA table_info(personnel)")
        cols = [row[1] for row in sqlite_cursor.fetchall()]
        
        sqlite_cursor.execute("SELECT * FROM personnel")
        personnel_list = sqlite_cursor.fetchall()
        for p in personnel_list:
            try:
                specialty = p['specialty'] if 'specialty' in cols else ''
                
                query = """
                    INSERT INTO personnel (id, rank, first_name, last_name, position, specialty, department)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                if choice == '2':
                    query += """
                        ON CONFLICT (id) DO UPDATE SET
                        rank = EXCLUDED.rank, first_name = EXCLUDED.first_name,
                        last_name = EXCLUDED.last_name, position = EXCLUDED.position,
                        specialty = EXCLUDED.specialty, department = EXCLUDED.department
                    """
                else:
                    query += " ON CONFLICT (id) DO NOTHING"

                pg_cursor.execute(query, (
                    p['id'], p['rank'], p['first_name'], p['last_name'],
                    p['position'], specialty, p['department']
                ))
            except Exception as e:
                print(f"  - Error personnel {p['first_name']}: {e}")

        # --- ย้ายข้อมูล Holidays ---
        print("\n📅 กำลังย้ายข้อมูลวันหยุด (Holidays)...")
        sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='holidays'")
        if sqlite_cursor.fetchone():
            sqlite_cursor.execute("SELECT * FROM holidays")
            for h in sqlite_cursor.fetchall():
                query = "INSERT INTO holidays (date, description) VALUES (%s, %s)"
                if choice == '2':
                    query += " ON CONFLICT (date) DO UPDATE SET description = EXCLUDED.description"
                else:
                    query += " ON CONFLICT (date) DO NOTHING"
                
                pg_cursor.execute(query, (h['date'], h['description']))

        pg_conn.commit()
        print("\n✅✅✅ นำเข้าข้อมูลเสร็จสมบูรณ์! ✅✅✅")

    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาดร้ายแรง: {e}")
        pg_conn.rollback()
    finally:
        if 'sqlite_conn' in locals(): sqlite_conn.close()
        if 'pg_conn' in locals(): pg_conn.close()

if __name__ == "__main__":
    migrate_data()