import pygame
import sys
import glob
from game import Game  # Import the Game class
import re


def validate_username(username):
    if len(username) < 3:
        return False
    if re.match(r'^(?!^(PRN|AUX|CLOCK\$|NUL|CON|COM\d|LPT\d|\..*|.*\.$|.*\s$|.*\.$)(\..+)?$)[^<>:"/\\|?*\.\s]+$', username):
        return True
    else:
        return False

def convert_ticks_to_time(ticks):
    # There are 45 ticks in a second, so we calculate the total seconds first
    total_seconds = ticks / 45

    # Extract minutes from the total seconds
    minutes = int(total_seconds // 60)

    # Remainder seconds after extracting minutes
    seconds = int(total_seconds % 60)

    # Calculate milliseconds
    # First, find the fractional part of the total seconds, then convert it to milliseconds
    milliseconds = int((total_seconds - int(total_seconds)) * 1000)

    return f"{minutes}:{seconds:02}:{milliseconds:03}"


def leaderboard_list():
    files = glob.glob("recordings/*")
    entries = []
    for filename in files:
        entry=filename
        entry=entry[11:]
        entry=entry[:-4]
        index = entry.rfind('_')
        name = entry[:index]
        time = entry[index + 1:]
        entries.append({'username' : name, 'time' : convert_ticks_to_time(int(time)), 'filename' : filename[11:]})

    #print(entries)
    entries.sort(key=lambda x: x['time'])
    return entries


def show_leaderboard(screen, screen_width, set_username):
    # Sample leaderboard data (replace with your actual data)
    leaderboard_data = leaderboard_list()

    # Colors
    white = (255, 255, 255)
    black = (0, 0, 0)

    # Fonts
    font = pygame.font.Font(None, 36)

    # Calculate button positions
    back_button = pygame.Rect(20, 20, 100, 50)

    while True:
        screen.fill(white)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    return  # Return to the main menu if back button is clicked

                # Check for clicks on leaderboard entries
                for entry in leaderboard_data:
                    entry_rect = entry["rect"]
                    if entry_rect.collidepoint(event.pos):
                        print(f"Clicked on entry: {entry['username']} - Time: {entry['time']}")
                        print(f"Filename: {entry['filename']}")
                        print(f"Username: {set_username}")
                        if validate_username(set_username):
                            game = Game(entry['filename'], set_username)
                            game.run()
                            return

        # Draw back button
        pygame.draw.rect(screen, black, back_button)
        back_text = font.render("Back", True, white)
        screen.blit(back_text, (back_button.x + (back_button.width - back_text.get_width()) // 2, back_button.y + (back_button.height - back_text.get_height()) // 2))

        # Draw leaderboard entries
        entry_height = 50
        entry_margin = 10
        y_position = 100

        for entry in leaderboard_data:
            username = entry["username"]
            time = entry["time"]
            entry_rect = pygame.Rect((screen_width - 300) // 2, y_position, 300, entry_height)

            entry["rect"] = entry_rect  # Store the rect in the entry dict
            pygame.draw.rect(screen, black, entry_rect)
            entry_text = font.render(f"{username} - {time}", True, white)

            screen.blit(entry_text, (entry_rect.x + 10, entry_rect.y + (entry_rect.height - entry_text.get_height()) // 2))

            y_position += entry_height + entry_margin


        pygame.display.flip()


def show_menu():
    pygame.init()

    screen_sizes = pygame.display.get_desktop_sizes()
    screen_width = screen_sizes[0][0] - 100
    screen_height = screen_sizes[0][1] - 100
    show_warning = False

    while True:
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Game Menu")

        # Colors
        white = (255, 255, 255)
        black = (0, 0, 0)

        # Fonts
        font = pygame.font.Font(None, 36)

        # Calculate button and input field positions
        button_width, button_height = 200, 50
        button_margin = 20
        button_y_start = (screen_height - (4 * button_height + 3 * button_margin)) // 2

        start_button = pygame.Rect((screen_width - button_width) // 2, button_y_start, button_width, button_height)
        leaderboard_button = pygame.Rect((screen_width - button_width) // 2, button_y_start + button_height + button_margin, button_width, button_height)
        quit_button = pygame.Rect((screen_width - button_width) // 2, button_y_start + 2 * (button_height + button_margin), button_width, button_height)

        # Input field for username
        username_rect = pygame.Rect((screen_width - button_width) // 2, button_y_start + 3 * (button_height + button_margin), button_width, button_height)
        username = ''
        active = False

        while True:
            screen.fill(white)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if start_button.collidepoint(event.pos) and username:  # Only start if the username is entered
                        game = Game(None, username)
                        game.run()
                        break

                    elif leaderboard_button.collidepoint(event.pos):
                        show_leaderboard(screen, screen_width, username)  # Call the function to display the leaderboard

                    elif quit_button.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()

                if event.type == pygame.KEYDOWN:
                    if active:
                        if event.key == pygame.K_RETURN:
                            active = False
                        elif event.key == pygame.K_BACKSPACE:
                            username = username[:-1]
                        else:
                            username += event.unicode

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if username_rect.collidepoint(event.pos):
                        active = not active
                    else:
                        active = False

            # Draw buttons
            pygame.draw.rect(screen, black, start_button)
            pygame.draw.rect(screen, black, leaderboard_button)
            pygame.draw.rect(screen, black, quit_button)

            # Draw input field with gray color
            pygame.draw.rect(screen, (200, 200, 200), username_rect, 2)  # Gray border
            pygame.draw.rect(screen, (220, 220, 220), username_rect)  # Gray background
            txt_surface = font.render(username, True, black)
            width = max(200, txt_surface.get_width()+10)
            username_rect.w = width
            screen.blit(txt_surface, (username_rect.x+5, username_rect.y+5))

            # Draw label for the username input field
            username_label = font.render("Username:", True, black)
            screen.blit(username_label, (username_rect.x - username_label.get_width() - 10, username_rect.y + (button_height - username_label.get_height()) // 2))

            # Draw warning message if the username is not entered
            if not username or not validate_username(username):
                show_warning = True  # Set the flag to show the warning
            else:
                show_warning = False  # Reset the flag when the username is entered

            # Draw button text
            start_text = font.render("Start", True, white)
            leaderboard_text = font.render("Leaderboard", True, white)
            quit_text = font.render("Quit", True, white)

            screen.blit(start_text, (start_button.x + (button_width - start_text.get_width()) // 2, start_button.y + (button_height - start_text.get_height()) // 2))
            screen.blit(leaderboard_text, (leaderboard_button.x + (button_width - leaderboard_text.get_width()) // 2, leaderboard_button.y + (button_height - leaderboard_text.get_height()) // 2))
            screen.blit(quit_text, (quit_button.x + (button_width - quit_text.get_width()) // 2, quit_button.y + (button_height - quit_text.get_height()) // 2))

            # Draw the warning message if the flag is set
            if show_warning:
                warning_text = font.render("Lai spēlētu ievadiet lietotājvārdu (virs 3 simboli)", True, (255, 0, 0))
                warning_rect = warning_text.get_rect(center=(screen_width // 2, username_rect.bottom + 20))
                pygame.draw.rect(screen, white, warning_rect)
                screen.blit(warning_text, warning_rect.topleft)

            pygame.display.flip()


if __name__ == "__main__":
    show_menu()
