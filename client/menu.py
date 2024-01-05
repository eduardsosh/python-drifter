# menu.py
import pygame
import sys
from main import Game  # Import the Game class

def show_menu():
    pygame.init()

    # Initialize Pygame window
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Game Menu")

    # Colors
    white = (255, 255, 255)
    black = (0, 0, 0)

    # Fonts
    font = pygame.font.Font(None, 36)

    # Buttons
    start_button = pygame.Rect(300, 200, 200, 50)
    leaderboard_button = pygame.Rect(300, 300, 200, 50)
    quit_button = pygame.Rect(300, 400, 200, 50)

    while True:
        screen.fill(white)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    # Start button clicked
                    pygame.quit()  # Exit the menu loop
                    game = Game()  # Create an instance of the Game class
                    game.run()     # Run the game loop

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

        screen.blit(start_text, (start_button.x + 50, start_button.y + 15))
        screen.blit(leaderboard_text, (leaderboard_button.x + 20, leaderboard_button.y + 15))
        screen.blit(quit_text, (quit_button.x + 60, quit_button.y + 15))

        pygame.display.flip()

if __name__ == "__main__":
    show_menu()
