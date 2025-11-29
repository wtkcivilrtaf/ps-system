import psycopg2
from database import get_db_connection

def full_reset():
    print("กำลังดำเนินการล้างและสร้างฐานข้อมูลส่วนสถานะใหม่...")
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. ลบตารางเก่าทิ้ง (เพื่อให้แน่ใจว่าไม่มีคอลัมน์ตกค้าง)
        print("- ลบตาราง status_reports...")
        cursor.execute("DROP TABLE IF EXISTS status_reports")
        print("- ลบตาราง persistent_statuses...")
        cursor.execute("DROP TABLE IF EXISTS persistent_statuses")

        # 2. สร้างตาราง status_reports ใหม่
        print("- สร้างตาราง status_reports ใหม่...")
        cursor.execute("""
            CREATE TABLE status_reports (
                id TEXT PRIMARY KEY,
                date TEXT NOT NULL,
                submitted_by TEXT,
                department TEXT,
                timestamp TIMESTAMPTZ,
                report_data JSONB
            )
        """)

        # 3. สร้างตาราง persistent_statuses ใหม่ (สำคัญมากต้องมี department)
        print("- สร้างตาราง persistent_statuses ใหม่...")
        cursor.execute("""
            CREATE TABLE persistent_statuses (
                id TEXT PRIMARY KEY,
                personnel_id TEXT NOT NULL,
                department TEXT NOT NULL,
                status TEXT,
                details TEXT,
                start_date DATE,
                end_date DATE
            )
        """)
        
        conn.commit()
        print("\n✅ ดำเนินการเสร็จสิ้น! โครงสร้างฐานข้อมูลถูกต้องแล้ว 100%")
        print("หมายเหตุ: ข้อมูลสถานะการลา/ราชการ ปัจจุบันจะถูกรีเซ็ต")
        
    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาด: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    full_reset()