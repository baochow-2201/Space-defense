# src/core/database.py
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "game.db")

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.create_tables()

    def create_tables(self):
        c = self.conn.cursor()
        # Bảng người chơi
        c.execute("""
            CREATE TABLE IF NOT EXISTS players(
                id INTEGER PRIMARY KEY,
                name TEXT,
                highest_level INTEGER DEFAULT 1,
                total_score INTEGER DEFAULT 0,
                current_level INTEGER DEFAULT 1
            )
        """)
        # Bảng điểm từng level
        c.execute("""
            CREATE TABLE IF NOT EXISTS scores(
                player_id INTEGER,
                level INTEGER,
                score INTEGER,
                PRIMARY KEY(player_id, level),
                FOREIGN KEY(player_id) REFERENCES players(id)
            )
        """)
        self.conn.commit()

    # Lấy dữ liệu người chơi đầu tiên
    def get_player_data(self):
        c = self.conn.cursor()
        c.execute("SELECT id, name, highest_level, total_score, current_level FROM players ORDER BY id LIMIT 1")
        row = c.fetchone()
        if not row:
            c.execute("INSERT INTO players(name) VALUES ('Player')")
            self.conn.commit()
            return {"id": 1, "name": "Player", "highest_level": 1, "total_score": 0, "level_scores": {}, "current_level": 1}
        player_id, name, hl, ts, cl = row
        # Load điểm từng level
        c.execute("SELECT level, score FROM scores WHERE player_id=?", (player_id,))
        scores = {lvl: sc for lvl, sc in c.fetchall()}
        return {"id": player_id, "name": name, "highest_level": hl, "total_score": ts, "level_scores": scores, "current_level": cl}

    # Alias get_player() để tương thích code cũ
    def get_player(self):
        return self.get_player_data()

    # Cập nhật tên người chơi
    def update_player_name(self, new_name):
        c = self.conn.cursor()
        c.execute("UPDATE players SET name=? WHERE id=(SELECT id FROM players ORDER BY id LIMIT 1)", (new_name,))
        self.conn.commit()

    # Cập nhật điểm level
    def update_level_score(self, player_id, level, score):
        c = self.conn.cursor()
        c.execute("""
            INSERT INTO scores(player_id, level, score)
            VALUES (?, ?, ?)
            ON CONFLICT(player_id, level) DO UPDATE SET score=excluded.score
        """, (player_id, level, score))
        self.conn.commit()

    # Cập nhật tổng điểm
    def update_total_score(self, player_id, total_score):
        c = self.conn.cursor()
        c.execute("UPDATE players SET total_score=? WHERE id=?", (total_score, player_id))
        self.conn.commit()

    # Cập nhật highest_level
    def update_highest_level(self, player_id, highest_level):
        c = self.conn.cursor()
        c.execute("UPDATE players SET highest_level=? WHERE id=?", (highest_level, player_id))
        self.conn.commit()

    # Lấy màn chơi hiện tại
    def get_current_level(self):
        c = self.conn.cursor()
        c.execute("SELECT current_level FROM players ORDER BY id LIMIT 1")
        row = c.fetchone()
        return row[0] if row else 1

    # Cập nhật màn chơi hiện tại
    def set_current_level(self, level):
        c = self.conn.cursor()
        c.execute("UPDATE players SET current_level=? WHERE id=(SELECT id FROM players ORDER BY id LIMIT 1)", (level,))
        self.conn.commit()

    # -----------------------------
    # RESET TẤT CẢ ĐIỂM
    # -----------------------------
    def reset_scores(self, player_id=None):
        """Reset tất cả điểm, highest_level, current_level về mặc định."""
        c = self.conn.cursor()

        # Lấy player_id nếu chưa truyền
        if player_id is None:
            c.execute("SELECT id FROM players ORDER BY id LIMIT 1")
            row = c.fetchone()
            if not row:
                return
            player_id = row[0]

        # Xóa tất cả điểm level
        c.execute("DELETE FROM scores WHERE player_id=?", (player_id,))
        # Reset tổng điểm, highest_level, current_level
        c.execute("""
            UPDATE players
            SET total_score=0,
                highest_level=1,
                current_level=1
            WHERE id=?
        """, (player_id,))
        self.conn.commit()
