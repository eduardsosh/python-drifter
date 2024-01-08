# menu.py
import pygame
import sys
from game import Game  # Import the Game class

def show_menu():
    pygame.init()

    screen_width, screen_height = 1600, 600

    while True:
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Game Menu")

        # Colors
        white = (255, 255, 255)
        black = (0, 0, 0)

        # Fonts
        font = pygame.font.Font(None, 36)

        # Calculate button positions
        button_width, button_height = 200, 50
        button_margin = 20
        button_y_start = (screen_height - (3 * button_height + 2 * button_margin)) // 2

        start_button = pygame.Rect((screen_width - button_width) // 2, button_y_start, button_width, button_height)
        leaderboard_button = pygame.Rect((screen_width - button_width) // 2, button_y_start + button_height + button_margin, button_width, button_height)
        quit_button = pygame.Rect((screen_width - button_width) // 2, button_y_start + 2 * (button_height + button_margin), button_width, button_height)

        while True:
            screen.fill(white)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if start_button.collidepoint(event.pos):
                        game = Game('recording20240107-195930.pkl')
                        game.run()
                        break

                    elif leaderboard_button.collidepoint(event.pos):
                        print("Leaderboard button clicked")
                        # Add code to show leaderboard here

                    elif quit_button.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()

            # Draw buttons
            pygame.draw.rect(screen, black, start_button)
            pygame.draw.rect(screen, black, leaderboard_button)
            pygame.draw.rect(screen, black, quit_button)

            # Draw button text
            start_text = font.render("Start", True, white)
            leaderboard_text = font.render("Leaderboard", True, white)
            quit_text = font.render("Quit", True, white)

            screen.blit(start_text, (start_button.x + (button_width - start_text.get_width()) // 2, start_button.y + (button_height - start_text.get_height()) // 2))
            screen.blit(leaderboard_text, (leaderboard_button.x + (button_width - leaderboard_text.get_width()) // 2, leaderboard_button.y + (button_height - leaderboard_text.get_height()) // 2))
            screen.blit(quit_text, (quit_button.x + (button_width - quit_text.get_width()) // 2, quit_button.y + (button_height - quit_text.get_height()) // 2))

            pygame.display.flip()

if __name__ == "__main__":
    show_menu()
