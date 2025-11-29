import psycopg2
from datetime import date, timedelta
from database import get_db_connection

def rewind_one_week():
    print("⏳ กำลังย้อนเวลาระบบกลับไป 1 สัปดาห์...")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. ดึงค่าปัจจุบัน
        cursor.execute("SELECT value FROM system_settings WHERE key = 'current_week_start_date'")
        row = cursor.fetchone()
        
        if row:
            current_start_date = date.fromisoformat(row[0])
            # 2. ถอยหลัง 7 วัน
            new_start_date = current_start_date - timedelta(days=7)
            
            # 3. อัปเดตค่าใหม่
            cursor.execute("UPDATE system_settings SET value = %s WHERE key = 'current_week_start_date'", 
                           (new_start_date.isoformat(),))
            conn.commit()
            
            print(f"✅ สำเร็จ! รอบสัปดาห์ถูกเปลี่ยนจาก {current_start_date} เป็น {new_start_date}")
            print("   (ตอนนี้ระบบจะคิดว่าอยู่ในสัปดาห์ที่แล้ว)")
        else:
            print("❌ ไม่พบการตั้งค่า 'current_week_start_date' ในระบบ")
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    rewind_one_week()