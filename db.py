# 리팩토링된 db.py (중복 제거, 연결 함수 활용, 함수 정리)
import sqlite3
from datetime import datetime

DB_NAME = 'tossify.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    init_stats_table()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_case TEXT,
            description TEXT,
            status TEXT,
            output TEXT,
            error TEXT,
            traceback TEXT,
            log TEXT,
            timestamp DATETIME,
            duration REAL
        )
    ''')
    conn.commit()
    conn.close()

def insert_report(report):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO reports 
        (test_case, description, status, output, error, traceback, log, timestamp, duration)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        report['test_case'],
        report['description'],
        report['status'],
        str(report.get('output')),
        report.get('error'),
        report.get('traceback'),
        report.get('log'),
        report['timestamp'],
        report.get('duration')
    ))
    conn.commit()
    conn.close()

def get_all_reports():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM reports ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_report_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT status, COUNT(*) FROM reports GROUP BY status')
    result = dict(cursor.fetchall())
    conn.close()
    return result

def get_average_duration():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT AVG(duration) FROM reports WHERE duration IS NOT NULL')
    avg = cursor.fetchone()[0]
    conn.close()
    return round(avg, 3) if avg else 0.0

def get_report_by_id(report_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM reports WHERE id = ?', (report_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def delete_report_by_id(report_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM reports WHERE id = ?', (report_id,))
    conn.commit()
    conn.close()

def init_stats_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_case_stats (
            test_case TEXT PRIMARY KEY,
            run_count INTEGER DEFAULT 0,
            pass_count INTEGER DEFAULT 0,
            fail_count INTEGER DEFAULT 0,
            last_run TEXT,
            success_rate REAL
        )
    ''')
    conn.commit()
    conn.close()

def update_test_case_stats(test_case_name, status, timestamp):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT run_count, pass_count, fail_count FROM test_case_stats WHERE test_case = ?', (test_case_name,))
    row = cursor.fetchone()

    if row:
        run_count, pass_count, fail_count = row
    else:
        run_count = pass_count = fail_count = 0

    run_count += 1
    if status == 'PASS':
        pass_count += 1
    else:
        fail_count += 1

    success_rate = round((pass_count / run_count) * 100, 2)

    cursor.execute('''
        INSERT INTO test_case_stats (test_case, run_count, pass_count, fail_count, last_run, success_rate)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(test_case) DO UPDATE SET
            run_count = excluded.run_count,
            pass_count = excluded.pass_count,
            fail_count = excluded.fail_count,
            last_run = excluded.last_run,
            success_rate = excluded.success_rate
    ''', (test_case_name, run_count, pass_count, fail_count, timestamp, success_rate))

    conn.commit()
    conn.close()

def get_all_test_case_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM test_case_stats ORDER BY success_rate DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows
