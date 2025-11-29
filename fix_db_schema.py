import psycopg2
from database import get_db_connection

def fix_schema():
    print("กำลังตรวจสอบและซ่อมแซมโครงสร้างฐานข้อมูล...")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. ตรวจสอบตาราง status_reports
        print("- ตรวจสอบตาราง status_reports...")
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'status_reports'")
        columns = [row[0] for row in cursor.fetchall()]
        
        if 'department' not in columns:
            print("  -> ไม่พบคอลัมน์ 'department' กำลังเพิ่ม...")
            cursor.execute("ALTER TABLE status_reports ADD COLUMN department TEXT")
        
        if 'report_data' not in columns:
            print("  -> ไม่พบคอลัมน์ 'report_data' กำลังเพิ่ม...")
            cursor.execute("ALTER TABLE status_reports ADD COLUMN report_data JSONB")

        # 2. ตรวจสอบตาราง persistent_statuses
        print("- ตรวจสอบตาราง persistent_statuses...")
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'persistent_statuses'")
        ps_columns = [row[0] for row in cursor.fetchall()]
        
        if 'department' not in ps_columns:
            print("  -> ไม่พบคอลัมน์ 'department' กำลังเพิ่ม...")
            cursor.execute("ALTER TABLE persistent_statuses ADD COLUMN department TEXT")

        conn.commit()
        print("\n✅ ซ่อมแซมฐานข้อมูลเสร็จสมบูรณ์!")
        
    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาด: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    fix_schema()