import sqlite3

def check_db_content():
    conn = sqlite3.connect('tossify.db')
    cursor = conn.cursor()
    
    # 테이블 목록 확인
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("테이블 목록:", tables)
    
    # 각 테이블의 데이터 확인
    for table in tables:
        table_name = table[0]
        print(table_name)
        

        if table_name == 'sqlite_sequence':
            print(f"\n{table_name} 테이블 내용:")
            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()
            
            # 컬럼 이름 가져오기
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = [col[1] for col in cursor.fetchall()]
            print("컬럼:", columns)
            
            # 데이터 출력
            for row in rows:
                print(row)
    conn.close()

if __name__ == "__main__":
    check_db_content()