import pygame

from asteroid import Asteroid
from asteroidfield import AsteroidField
from constants import PLAYER_LIVES, SCREEN_HEIGHT, SCREEN_WIDTH
from logger import log_event, log_state
from player import Player
from shot import Shot
from stats import GameStats


def initialize_game(stats: GameStats):
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()

    Player.containers = (updatable, drawable)
    AsteroidField.containers = updatable
    Asteroid.containers = (asteroids, updatable, drawable)
    Shot.containers = (shots, drawable, updatable)

    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    player.on_shoot = stats.register_shot
    asteroid_field = AsteroidField()

    stats.reset()

    return updatable, drawable, asteroids, shots, player, asteroid_field


def draw_hud(screen, font, stats: GameStats, lives: int) -> None:
    lines = [
        f"Score: {stats.score}",
        f"Time:  {stats.time_str()}",
        f"Lives: {lives}",
        f"Level: {stats.level}",
        f"Destroyed: {stats.asteroids_destroyed}",
        f"Accuracy:  {stats.accuracy:.0f}%",
    ]
    for i, line in enumerate(lines):
        surface = font.render(line, True, "white")
        screen.blit(surface, (10, 10 + i * 22))


def draw_centered(screen, font, text, color, y) -> None:
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=(SCREEN_WIDTH / 2, y))
    screen.blit(surface, rect)


def draw_game_over(screen, big_font, small_font, stats: GameStats) -> None:
    draw_centered(screen, big_font, "Game Over", "white", SCREEN_HEIGHT / 2 - 140)

    summary = [
        f"Score: {stats.score}",
        f"Survived: {stats.time_str()}",
        f"Asteroids destroyed: {stats.asteroids_destroyed}",
        f"Accuracy: {stats.accuracy:.0f}%  (level {stats.level})",
    ]
    for i, line in enumerate(summary):
        draw_centered(screen, small_font, line, "white", SCREEN_HEIGHT / 2 - 70 + i * 30)

    records = [
        ("best_score", f"Best score: {int(stats.records['best_score'])}"),
        ("longest_time", f"Longest survival: {int(stats.records['longest_time'])}s"),
        ("most_destroyed", f"Most destroyed: {int(stats.records['most_destroyed'])}"),
        ("best_accuracy", f"Best accuracy: {stats.records['best_accuracy']:.0f}%"),
    ]
    for i, (key, line) in enumerate(records):
        color = "gold" if key in stats.beaten else "gray"
        label = f"{line}   NEW RECORD!" if key in stats.beaten else line
        draw_centered(screen, small_font, label, color, SCREEN_HEIGHT / 2 + 70 + i * 26)

    draw_centered(
        screen, small_font, "press SPACE to restart", "white", SCREEN_HEIGHT / 2 + 200
    )


def main():
    pygame.init()
    clock = pygame.time.Clock()
    dt = 0.0  # Δ
    game_over = False
    paused = False
    lives = PLAYER_LIVES
    stats = GameStats()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    hud_font = pygame.font.SysFont(None, 26)
    game_over_font = pygame.font.SysFont(None, 72)
    small_font = pygame.font.SysFont(None, 36)

    updatable, drawable, asteroids, shots, player, asteroid_field = initialize_game(stats)

    while True:
        log_state()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if game_over and event.key == pygame.K_SPACE:
                    game_over = False
                    paused = False
                    dt = 0.0
                    lives = PLAYER_LIVES
                    updatable, drawable, asteroids, shots, player, asteroid_field = (
                        initialize_game(stats)
                    )
                elif not game_over and event.key == pygame.K_p:
                    paused = not paused
                    log_event("pause_toggled", paused=paused)

        if not game_over and not paused:
            updatable.update(dt)
            stats.update(dt)
            for asteroid in asteroids:
                for shot in shots:
                    if asteroid.collides_with(shot):
                        log_event("asteroid_shot")
                        stats.register_hit(asteroid.radius)
                        asteroid.split()
                        shot.kill()
                if not player.is_invulnerable and player.collides_with(asteroid):
                    lives -= 1
                    log_event("player_hit", lives_remaining=lives)
                    if lives <= 0:
                        game_over = True
                        stats.commit_records()
                    else:
                        asteroid.split()
                        player.respawn()

        screen.fill("black")

        for sprite in drawable:
            sprite.draw(screen)

        draw_hud(screen, hud_font, stats, lives)

        if paused and not game_over:
            draw_centered(screen, game_over_font, "Paused", "white", SCREEN_HEIGHT / 2)
            draw_centered(
                screen, small_font, "press P to resume", "white", SCREEN_HEIGHT / 2 + 50
            )

        if game_over:
            draw_game_over(screen, game_over_font, small_font, stats)

        pygame.display.flip()
        dt = clock.tick(60) / 1000


if __name__ == "__main__":
    main()
