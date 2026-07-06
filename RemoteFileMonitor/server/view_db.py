import sqlite3
from config import DB_PATH

def main():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("\n" + "=" * 60)
        print("=== BẢNG TRẠNG THÁI CLIENTS (clients) ===")
        print("=" * 60)
        cursor.execute("SELECT * FROM clients")
        rows = cursor.fetchall()
        if not rows:
            print("(Không có dữ liệu client nào)")
        for row in rows:
            print(f"Client ID: {row[0]:<12} | Status: {row[1]:<8} | Last Heartbeat: {row[2]} | IP: {row[3]}:{row[4]}")
            
        print("\n" + "=" * 60)
        print("=== LỊCH SỬ SỰ KIỆN FILE (20 dòng mới nhất) ===")
        print("=" * 60)
        cursor.execute("SELECT * FROM events ORDER BY id DESC LIMIT 20")
        rows = cursor.fetchall()
        if not rows:
            print("(Không có sự kiện file nào được ghi nhận)")
        for row in rows:
            print(f"[{row[6]}] Client: {row[1]:<12} | Event: {row[2]:<8} | File: {row[3]:<15} | Path: {row[4]}")
        print("=" * 60 + "\n")
        
        conn.close()
    except Exception as e:
        print(f"Lỗi khi đọc Cơ sở dữ liệu: {e}")

if __name__ == "__main__":
    main()
