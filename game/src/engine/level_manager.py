# src/engine/level_manager.py

import random

WIDTH = 1280
PLAYER_DEFAULT = {"speed": 5, "hp": 100, "images": ["mbayf1.png", "mbayf2.png"]}

ENEMY_TYPES = {
    "bat": {"hp": 10, "images": ["doif1.png", "doif4.png"], "score": 10},
    "head": {"hp": 15, "images": ["dauf1.png", "dauf2.png"], "score": 15},
    "ghost": {"hp": 20, "images": ["ma1.png", "ma2.png"], "score": 20},
    "trees": {"hp": 25, "images": ["poke1.png", "poke2.png"], "score": 25},
    "boss": {"hp": 1000, "images": ["poke12.png", "poke13.png"], "score": 500},
}

LEVEL_BLUEPRINTS = {
    1: [{"type": "bat", "count": 6, "pattern": "zigzag"}],
    2: [{"type": "bat", "count": 8, "pattern": "wave"}],
    3: [{"type": "head", "count": 5, "pattern": "spiral"}, {"type": "bat", "count": 4, "pattern": "zigzag"}],
    4: [{"type": "ghost", "count": 6, "pattern": "wave"}, {"type": "head", "count": 3, "pattern": "zigzag"}],
    5: [{"type": "bat", "count": 6, "pattern": "random"}, {"type": "ghost", "count": 4, "pattern": "chase"}],
    6: [{"type": "trees", "count": 5, "pattern": "zigzag"}, {"type": "bat", "count": 6, "pattern": "wave"}],
    7: [{"type": "ghost", "count": 8, "pattern": "spiral"}, {"type": "head", "count": 4, "pattern": "zigzag"}],
    8: [{"type": "bat", "count": 10, "pattern": "random"}, {"type": "ghost", "count": 6, "pattern": "chase"}],
    9: [{"type": "head", "count": 8, "pattern": "spiral"}, {"type": "ghost", "count": 4, "pattern": "wave"}],
    10: [{"type": "boss", "count": 1, "pattern": "drop_then_stationary"}, {"type": "trees", "count": 8, "pattern": "wave"}]
}

class LevelManager:
    @staticmethod
    def get_level_config(level):
        blueprint = LEVEL_BLUEPRINTS.get(level, LEVEL_BLUEPRINTS[1])
        enemies = []

        for group in blueprint:
            etype = group.get("type", "bat")
            count = group.get("count", 5)
            pattern = group.get("pattern")
            base = ENEMY_TYPES.get(etype, ENEMY_TYPES["bat"]).copy()

            for _ in range(count):
                x = random.randint(50, WIDTH - 50)
                y = random.randint(-300, -50)

                if etype == "boss":
                    width, height = 350, 300
                    pattern = "drop_then_stationary"
                    x = WIDTH // 2
                    y = -100
                else:
                    width, height = 135, 75
                    pattern = pattern if pattern else random.choice(["straight", "zigzag", "wave", "spiral", "chase"])

                cfg = {
                    "type": etype,
                    "hp": base.get("hp", 10) + level * 2,
                    "images": base.get("images", []),
                    "pattern": pattern,
                    "speed": base.get("speed", 2) + level * 0.2,
                    "rows": 1,
                    "cols": 1,
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height,
                    "score_value": base.get("score", 10)
                }
                enemies.append(cfg)

        player_cfg = PLAYER_DEFAULT.copy()
        player_cfg["hp"] = PLAYER_DEFAULT["hp"] + level * 10
        player_cfg["speed"] = PLAYER_DEFAULT["speed"] + level * 0.2

        return {"player": player_cfg, "enemies": enemies}
 # ============================
    # Thêm hàm này ↓↓↓↓↓
    # ============================
    @staticmethod
    def get_max_level():
        return max(LEVEL_BLUEPRINTS.keys())