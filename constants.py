SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
PLAYER_RADIUS = 20
LINE_WIDTH = 2
PLAYER_TURN_SPEED = 300
PLAYER_SPEED = 200
ASTEROID_MIN_RADIUS = 20
ASTEROID_KINDS = 3
ASTEROID_SPAWN_RATE_SECONDS = 0.8
ASTEROID_MAX_RADIUS = ASTEROID_MIN_RADIUS * ASTEROID_KINDS
SHOT_RADIUS = 5
PLAYER_SHOOT_SPEED = 500
PLAYER_SHOOT_COOLDOWN_SECONDS = 0.3

# Player lives / respawn
PLAYER_LIVES = 3
PLAYER_INVULNERABLE_SECONDS = 2.0

# Scoring: points awarded per asteroid destroyed, keyed by "kind"
# (kind = radius // ASTEROID_MIN_RADIUS; 3 = large, 2 = medium, 1 = small)
SCORE_PER_KIND = {3: 20, 2: 50, 1: 100}

# How often (seconds survived) the difficulty level ticks up
LEVEL_UP_SECONDS = 20

# File where persistent best-run records are stored
RECORDS_FILE = "records.json"
