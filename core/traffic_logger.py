import os
import sqlite3
import threading
from datetime import datetime, timedelta, timezone
from core.config import DB_PATH, DATA_DIR, TRAFFIC_API_URL, NETWORK_TIMEOUT


class TrafficLogger:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            """CREATE TABLE IF NOT EXISTS log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT,
                toko TEXT,
                tgl_qc TEXT,
                timestamp TEXT,
                layout TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT,
                sent_at TEXT
            )"""
        )
        conn.commit()
        conn.close()

    def log(self, user, toko, tgl_qc, layout):
        tz_jkt = timezone(timedelta(hours=7))
        ts = datetime.now(tz_jkt).strftime("%d %B %y / %H:%M")
        created = datetime.now(tz_jkt).isoformat()

        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO log (user, toko, tgl_qc, timestamp, layout, status, created_at) "
            "VALUES (?, ?, ?, ?, ?, 'pending', ?)",
            (user, toko, tgl_qc, ts, layout, created),
        )
        conn.commit()
        conn.close()

        threading.Thread(target=self._try_sync, daemon=True).start()

    def sync_on_startup(self):
        threading.Thread(target=self._try_sync, daemon=True).start()

    def _try_sync(self):
        try:
            import requests as req
            from core.connectivity import is_online

            if not is_online():
                return

            conn = sqlite3.connect(DB_PATH)
            rows = conn.execute(
                "SELECT id, user, toko, tgl_qc, timestamp, layout FROM log WHERE status='pending'"
            ).fetchall()
            conn.close()

            if not rows:
                return

            try:
                resp = req.get(TRAFFIC_API_URL, timeout=NETWORK_TIMEOUT)
                data = resp.json() if resp.status_code == 200 else []
                if not isinstance(data, list):
                    data = []
            except Exception:
                data = []

            sent_ids = []
            for row in rows:
                entry = {
                    "Nama Pengguna": row[1],
                    "Nama Toko": row[2],
                    "Tanggal QC": row[3],
                    "Timestamp": row[4],
                    "Ukuran Layout": row[5],
                }
                data.append(entry)
                sent_ids.append(row[0])

            headers = {"Content-Type": "application/json", "Accept": "application/json"}
            put = req.put(TRAFFIC_API_URL, json=data, headers=headers, timeout=NETWORK_TIMEOUT)
            if put.status_code in (200, 201):
                tz_jkt = timezone(timedelta(hours=7))
                now = datetime.now(tz_jkt).isoformat()
                conn = sqlite3.connect(DB_PATH)
                for rid in sent_ids:
                    conn.execute(
                        "UPDATE log SET status='sent', sent_at=? WHERE id=?",
                        (now, rid),
                    )
                conn.commit()
                conn.close()
        except Exception:
            pass
