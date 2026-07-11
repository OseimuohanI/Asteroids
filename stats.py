import json
from datetime import datetime

from constants import (
    ASTEROID_MIN_RADIUS,
    LEVEL_UP_SECONDS,
    RECORDS_FILE,
    SCORE_PER_KIND,
)
from logger import log_event


def _default_records() -> dict[str, float]:
    return {
        "best_score": 0,
        "longest_time": 0.0,
        "most_destroyed": 0,
        "best_accuracy": 0.0,
    }


def load_records() -> dict[str, float]:
    """Read persistent best-run records from disk, tolerating a missing/corrupt file."""
    records = _default_records()
    try:
        with open(RECORDS_FILE) as f:
            saved = json.load(f)
        if isinstance(saved, dict):
            for key in records:
                if isinstance(saved.get(key), (int, float)):
                    records[key] = saved[key]
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return records


class GameStats:
    """Tracks a single run and reconciles it against the persistent records."""

    def __init__(self) -> None:
        self.records = load_records()
        self.reset()

    def reset(self) -> None:
        self.score = 0
        self.elapsed = 0.0
        self.asteroids_destroyed = 0
        self.shots_fired = 0
        self.level = 1
        self.beaten: set[str] = set()  # record keys beaten this run

    @property
    def accuracy(self) -> float:
        if self.shots_fired == 0:
            return 0.0
        return 100.0 * self.asteroids_destroyed / self.shots_fired

    def register_shot(self) -> None:
        self.shots_fired += 1

    def register_hit(self, radius: float) -> None:
        kind = max(1, round(radius / ASTEROID_MIN_RADIUS))
        self.score += SCORE_PER_KIND.get(kind, 20)
        self.asteroids_destroyed += 1

    def update(self, dt: float) -> None:
        self.elapsed += dt
        self.level = 1 + int(self.elapsed // LEVEL_UP_SECONDS)

    def time_str(self) -> str:
        minutes, seconds = divmod(int(self.elapsed), 60)
        return f"{minutes:02d}:{seconds:02d}"

    def _run_values(self) -> dict[str, float]:
        return {
            "best_score": self.score,
            "longest_time": self.elapsed,
            "most_destroyed": self.asteroids_destroyed,
            "best_accuracy": self.accuracy,
        }

    def commit_records(self) -> set[str]:
        """Persist any records this run beat and return which keys were beaten."""
        beaten: set[str] = set()
        for key, value in self._run_values().items():
            if value > self.records[key]:
                self.records[key] = value
                beaten.add(key)
        self.beaten = beaten
        if beaten:
            try:
                with open(RECORDS_FILE, "w") as f:
                    json.dump(self.records, f, indent=2)
            except OSError:
                pass
            log_event(
                "records_updated",
                beaten=sorted(beaten),
                timestamp=datetime.now().isoformat(timespec="seconds"),
            )
        return beaten
