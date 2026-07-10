import pygame

from asteroid import Asteroid
from asteroidfield import AsteroidField
from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from logger import log_event, log_state
from player import Player
from shot import Shot


def initialize_game():
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()

    Player.containers = (updatable, drawable)
    AsteroidField.containers = updatable
    Asteroid.containers = (asteroids, updatable, drawable)
    Shot.containers = (shots, drawable, updatable)

    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    asteroid_field = AsteroidField()

    return updatable, drawable, asteroids, shots, player, asteroid_field


def main():
    pygame.init()
    clock = pygame.time.Clock()
    dt = 0.0  # Δ
    game_over = False
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    game_over_font = pygame.font.SysFont(None, 72)
    restart_font = pygame.font.SysFont(None, 36)
    updatable, drawable, asteroids, shots, player, asteroid_field = initialize_game()
    while True:
        log_state()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_over = False
                dt = 0.0
                updatable, drawable, asteroids, shots, player, asteroid_field = initialize_game()

        if not game_over:
            updatable.update(dt)
            for asteroid in asteroids:
                for shot in shots:
                    if asteroid.collides_with(shot):
                        log_event("asteroid_shot")
                        asteroid.split()
                        shot.kill()
                if player.collides_with(asteroid):
                    log_event("player_hit")
                    game_over = True
        screen.fill("black")

        for sprite in drawable:
            sprite.draw(screen)

        if game_over:
            game_over_surface = game_over_font.render("Game Over", True, "white")
            restart_surface = restart_font.render("click SPACE to restart", True, "white")
            game_over_rect = game_over_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 20))
            restart_rect = restart_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 30))
            screen.blit(game_over_surface, game_over_rect)
            screen.blit(restart_surface, restart_rect)

        pygame.display.flip()
        dt = clock.tick(60) / 1000
    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")


if __name__ == "__main__":
    main()
