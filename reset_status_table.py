import psycopg2
from database import get_db_connection

def reset_status_reports_table():
    print("กำลังล้างและสร้างตาราง status_reports ใหม่...")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. ลบตารางเดิมทิ้ง (DROP)
        print("1. ลบตาราง status_reports เดิม...")
        cursor.execute("DROP TABLE IF EXISTS status_reports")
        
        # 2. สร้างตารางใหม่ให้ถูกต้อง (CREATE)
        print("2. สร้างตารางใหม่...")
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
        
        # 3. (แถม) ตรวจสอบ persistent_statuses ด้วย
        print("3. ตรวจสอบตาราง persistent_statuses...")
        cursor.execute("CREATE TABLE IF NOT EXISTS persistent_statuses (id TEXT PRIMARY KEY)") # สร้างหลอกถ้าไม่มี
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'persistent_statuses'")
        cols = [row[0] for row in cursor.fetchall()]
        if 'department' not in cols:
            print("   -> เพิ่มคอลัมน์ department")
            cursor.execute("ALTER TABLE persistent_statuses ADD COLUMN department TEXT")
        
        conn.commit()
        print("\n✅ รีเซ็ตตารางเสร็จสมบูรณ์! พร้อมใช้งาน")
        print("หมายเหตุ: ข้อมูลการส่งยอด 'ของสัปดาห์นี้' จะถูกรีเซ็ต (ต้องส่งใหม่)")
        
    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาด: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    reset_status_reports_table()