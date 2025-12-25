from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import sqlite3
from datetime import datetime

conn, cursor, gauth, drive = None,None,None,None

def init():
    global conn, cursor
    conn = sqlite3.connect("tracks.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

def authenticate():
    global gauth, drive
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

def scan():
    if not drive:
        authenticate()
    cursor.execute("SELECT * FROM data")
    metadata = {row[0]:row[1] for row in cursor.fetchall()}
    root_folder = metadata['root_folder']
    last_scan = metadata['last_scan']
    folders = [root_folder]
    while folders:
        folder = folders.pop(0)
        subfolders = drive.ListFile({
        'q': f"'{folder}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        }).GetList()
        for sf in subfolders:
            folders.append(sf['id'])
        new_files = drive.ListFile({
        'q': f"'{folder}' in parents and mimeType!='application/vnd.google-apps.folder' and trashed=false and modifiedDate > '{last_scan}'"
        }).GetList()
        for file in new_files:
            cursor.execute("""
                INSERT OR IGNORE INTO tracks (id, name, score, last_played, play_count)
                VALUES (?, ?, ?, ?, ?)
                """, (file['id'], file['title'], 0, datetime.now().isoformat(), 0))
        conn.commit()
    cursor.execute(f"UPDATE data SET value='{datetime.now().isoformat()}' WHERE key='last_scan'")
    conn.commit()

def get_track(trackid):
    cursor.execute(f"SELECT * FROM TRACKS WHERE id='{trackid}'")
    return cursor.fetchone()

def get_all_tracks():
    cursor.execute("SELECT * FROM TRACKS")
    return cursor.fetchall()

def track_played(track):
    cursor.execute("UPDATE tracks SET last_played=?,play_count=play_count+1 WHERE id=?",(datetime.now().isoformat(),track))
    conn.commit()

def vote_track(track, score):
    cursor.execute("UPDATE tracks SET score=? WHERE id=?",(score, track))
    conn.commit()

def close():
    conn.close()
