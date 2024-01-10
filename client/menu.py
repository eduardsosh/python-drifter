import pygame
import sys
import glob
import re
import os
import shutil
from game import Game
from clientside import get_files_from_server

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
BUTTON_MARGIN = 20
USERNAME_RECT_WIDTH = 200

def validate_username(username):
    if len(username) < 3:
        return False
    if re.match(r'^(?!^(PRN|AUX|CLOCK\$|NUL|CON|COM\d|LPT\d|\..*|.*\.$|.*\s$|.*\.$)(\..+)?$)[^<>:"/\\|?*\.\s]+$', username):
        return True
    else:
        return False

def convert_ticks_to_time(ticks):
    total_seconds = ticks / 45
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    milliseconds = int((total_seconds - int(total_seconds)) * 1000)
    return f"{minutes}:{seconds:02}:{milliseconds:03}"

def leaderboard_list():
    files = glob.glob("recordings/*")
    entries = []
    for filename in files:
        entry = filename[11:-4]
        index = entry.rfind('_')
        name = entry[:index]
        time = entry[index + 1:]
        entries.append({'username': name, 'time': convert_ticks_to_time(int(time)), 'filename': filename[11:]})
    entries.sort(key=lambda x: x['time'])
    return entries

def draw_button(screen, rect, color, text, font, text_color):
    pygame.draw.rect(screen, color, rect)
    text_surface = font.render(text, True, text_color)
    screen.blit(text_surface, (rect.x + (rect.width - text_surface.get_width()) // 2, rect.y + (rect.height - text_surface.get_height()) // 2))

def download_rides():
    get_files_from_server()
    print("Downloading rides")

def delete_rides():
    folder = 'recordings'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def show_leaderboard(screen, screen_width, set_username):


    username = ''
    leaderboard_data = leaderboard_list()

    # Colors
    white = (255, 255, 255)
    black = (0, 0, 0)

    # Fonts
    font = pygame.font.Font(None, 36)

    # Calculate button positions
    button_width = 100
    button_height = 50
    button_margin = 20

    # Back button in the top-left corner
    back_button = pygame.Rect(10, 10, button_width, button_height)

    # Next and Prev buttons at the bottom-center
    next_button = pygame.Rect((screen_width - button_width) // 2 + button_margin, screen.get_height() - button_height - 20, button_width, button_height)
    prev_button = pygame.Rect(next_button.left - button_width - button_margin, screen.get_height() - button_height - 20, button_width, button_height)
    
    # Download and Delete buttons at the top-right
    download_button = pygame.Rect(screen_width - button_width - button_margin, 10, button_width, button_height)
    delete_button = pygame.Rect(screen_width - button_width - button_margin, 10 + button_height + 10, button_width, button_height)

    # Pagination variables
    entries_per_page = 5
    current_page = 0

    # Initialize 'rect' key for each entry
    for entry in leaderboard_data:
        entry["rect"] = None

    while True:
        screen.fill(white)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    show_menu()

                elif next_button.collidepoint(event.pos):
                    current_page += 1

                elif prev_button.collidepoint(event.pos):
                    current_page = max(0, current_page - 1)

                # Check for clicks on leaderboard entries
                for entry in leaderboard_data[current_page * entries_per_page: (current_page + 1) * entries_per_page]:
                    entry_rect = entry["rect"]
                    if entry_rect and entry_rect.collidepoint(event.pos):
                        print(f"Clicked on entry: {entry['username']} - Time: {entry['time']}")
                        print(f"Filename: {entry['filename']}")
                        print(f"Username: {set_username}")
                        if validate_username(set_username):
                            game = Game(entry['filename'], set_username)
                            game.run()
                            return

                # Check for clicks on the download and delete buttons
                if download_button.collidepoint(event.pos):
                    download_rides()  # Call the download function
                    show_leaderboard(screen, screen_width, username)

                elif delete_button.collidepoint(event.pos):
                    delete_rides()  # Call the delete function
                    show_leaderboard(screen, screen_width, username)

        # Draw back button
        pygame.draw.rect(screen, black, back_button)
        back_text = font.render("Back", True, white)
        screen.blit(back_text, (back_button.x + (back_button.width - back_text.get_width()) // 2, back_button.y + (back_button.height - back_text.get_height()) // 2))

        # Draw next button
        pygame.draw.rect(screen, black, next_button)
        next_text = font.render("Next", True, white)
        screen.blit(next_text, (next_button.x + (next_button.width - next_text.get_width()) // 2, next_button.y + (next_button.height - next_text.get_height()) // 2))

        # Draw previous button
        pygame.draw.rect(screen, black, prev_button)
        prev_text = font.render("Prev", True, white)
        screen.blit(prev_text, (prev_button.x + (prev_button.width - prev_text.get_width()) // 2, prev_button.y + (prev_button.height - prev_text.get_height()) // 2))

        # Draw download button
        pygame.draw.rect(screen, black, download_button)
        download_text = font.render("Atjaunot", True, white)
        screen.blit(download_text, (download_button.x + (download_button.width - download_text.get_width()) // 2,
                                    download_button.y + (download_button.height - download_text.get_height()) // 2))

        # Draw delete button
        pygame.draw.rect(screen, black, delete_button)
        delete_text = font.render("Dzēst", True, white)
        screen.blit(delete_text, (delete_button.x + (delete_button.width - delete_text.get_width()) // 2,
                                  delete_button.y + (delete_button.height - download_text.get_height()) // 2))

        # Draw leaderboard entries
        entry_height = 50
        entry_margin = 10
        y_position = 100

        for entry in leaderboard_data[current_page * entries_per_page: (current_page + 1) * entries_per_page]:
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

        font = pygame.font.Font(None, 36)

        button_y_start = (screen_height - (4 * BUTTON_HEIGHT + 3 * BUTTON_MARGIN)) // 2

        drifter_text = font.render("Drifter", True, (0, 0, 0))
        drifter_text_rect = drifter_text.get_rect(center=(screen_width // 2, 50))

        start_button = pygame.Rect((screen_width - BUTTON_WIDTH) // 2, button_y_start, BUTTON_WIDTH, BUTTON_HEIGHT)
        leaderboard_button = pygame.Rect((screen_width - BUTTON_WIDTH) // 2, button_y_start + BUTTON_HEIGHT + BUTTON_MARGIN, BUTTON_WIDTH, BUTTON_HEIGHT)
        quit_button = pygame.Rect((screen_width - BUTTON_WIDTH) // 2, button_y_start + 2 * (BUTTON_HEIGHT + BUTTON_MARGIN), BUTTON_WIDTH, BUTTON_HEIGHT)

        username_rect = pygame.Rect((screen_width - BUTTON_WIDTH) // 2, button_y_start + 3 * (BUTTON_HEIGHT + BUTTON_MARGIN), BUTTON_WIDTH, BUTTON_HEIGHT)
        username = ''
        active = False

        while True:
            screen.fill(WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if start_button.collidepoint(event.pos) and username:
                        game = Game(None, username)
                        game.run()
                        break

                    elif leaderboard_button.collidepoint(event.pos):
                        show_leaderboard(screen, screen_width, username)

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

            screen.blit(drifter_text, drifter_text_rect.topleft)

            draw_button(screen, start_button, BLACK, "Start", font, WHITE)
            draw_button(screen, leaderboard_button, BLACK, "Leaderboard", font, WHITE)
            draw_button(screen, quit_button, BLACK, "Quit", font, WHITE)

            pygame.draw.rect(screen, (200, 200, 200), username_rect, 2)
            pygame.draw.rect(screen, (220, 220, 220), username_rect)
            txt_surface = font.render(username, True, BLACK)
            width = max(USERNAME_RECT_WIDTH, txt_surface.get_width() + 10)
            username_rect.width = width
            screen.blit(txt_surface, (username_rect.x + 5, username_rect.y + 5))

            username_label = font.render("Username:", True, BLACK)
            screen.blit(username_label, (username_rect.x - username_label.get_width() - 10, username_rect.y + (BUTTON_HEIGHT - username_label.get_height()) // 2))

            if not username or not validate_username(username):
                show_warning = True
            else:
                show_warning = False

            if show_warning:
                warning_text = font.render("Lai spēlētu ievadiet lietotājvārdu (virs 3 simboli)", True, (255, 0, 0))
                warning_rect = warning_text.get_rect(center=(screen_width // 2, username_rect.bottom + 20))
                pygame.draw.rect(screen, WHITE, warning_rect)
                screen.blit(warning_text, warning_rect.topleft)

            pygame.display.flip()

if __name__ == "__main__":
    show_menu()