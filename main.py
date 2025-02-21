import pygame
import random
import time
import math
import json
from moviepy import VideoFileClip, AudioFileClip

# Initialize pygame
pygame.init()
clock = pygame.time.Clock()
# Constants
WIDTH, HEIGHT = 1920 // 1.5, 1080 // 1.5
FPS = 60
TILE_SIZE = 40

BLUE = (70, 130, 180)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)
TEAL = (0, 128, 128)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)
DARK_BLUE = (0, 0, 70)

data_file = "leaderboard.json"

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ocean Cleanup")

# Load fish images with alpha channel
red_fish = pygame.image.load("redfish.png").convert_alpha()
blue_fish = pygame.image.load("bluefish.png").convert_alpha()
red_fish = pygame.transform.scale(red_fish, (TILE_SIZE + 20, TILE_SIZE + 20))
blue_fish = pygame.transform.scale(blue_fish, (TILE_SIZE + 20, TILE_SIZE + 20))

# Button and screen constants
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
BUTTON_SPACING = 20

#for pause mechanism:
PAUSE_OVERLAY_ALPHA = 10

# Load background image
background = pygame.image.load("background.png").convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Screen states
class ScreenState:
    MAIN_MENU = "main_menu"
    CONTROLS = "controls"
    SETTINGS = "settings"
    PAUSED = "paused"


current_screen = ScreenState.MAIN_MENU
music_enabled = True  # Default music setting


# Button class
class Button:
    def __init__(self, text, x, y, callback):
        self.rect = pygame.Rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.text = text
        self.callback = callback
        self.color = (70, 130, 180)
        self.hover_color = (100, 150, 200)

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        current_color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(surface, current_color, self.rect, border_radius=10)
        font = pygame.font.Font(None, 36)
        text = font.render(self.text, True, WHITE)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback()


# Screen functions
def show_controls_screen():
    global current_screen
    current_screen = ScreenState.CONTROLS


def show_settings_screen():
    global current_screen
    current_screen = ScreenState.SETTINGS


def return_to_main_menu():
    global current_screen
    current_screen = ScreenState.MAIN_MENU


def start_game():
    fade_out()
    play_intro_video("We can’t let this happen!.mp4")
    
    # Initialize game state
    global game_started, countdown_start
    game_started = False
    countdown_start = time.time()
    
    # Start the main game loop
    run_game()


def draw_main_menu():
    screen.blit(background, (0, 0))

    # Draw title
    title_font = pygame.font.Font(None, 72)
    title_text = title_font.render("Guardians of the Ocean", True, WHITE)
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    screen.blit(title_text, title_rect)

    # Calculate button positions
    start_y = HEIGHT // 3
    buttons = [
        Button("Play", WIDTH // 2 - BUTTON_WIDTH // 2, start_y, start_game),
        Button("Controls", WIDTH // 2 - BUTTON_WIDTH // 2, start_y + BUTTON_HEIGHT + BUTTON_SPACING, show_controls_screen),
        Button("Settings", WIDTH // 2 - BUTTON_WIDTH // 2, start_y + 2 * (BUTTON_HEIGHT + BUTTON_SPACING), show_settings_screen)
    ]

    for button in buttons:
        button.draw(screen)


def draw_controls_screen():
    screen.fill(WHITE)

    # Back button
    back_button = Button("Back", 20, 20, return_to_main_menu)
    back_button.draw(screen)

    # Controls text
    font = pygame.font.Font(None, 36)
    controls = [
        "Red Fish Controls:",
        "WASD to move",
        "",
        "Blue Fish Controls:",
        "Arrow keys to move",
        "",
        "Collect matching colored trash!",
        "Avoid wrong colors and obstacles!",
        "",  # Add these new lines
        "Press SPACE to pause game"
    ]

    y = 100
    for line in controls:
        text = font.render(line, True, BLACK)
        screen.blit(text, (WIDTH // 4, y))
        y += 40


def draw_settings_screen():
    global music_enabled
    screen.fill(WHITE)

    # Back button
    back_button = Button("Back", 20, 20, return_to_main_menu)
    back_button.draw(screen)

    # Settings content
    font = pygame.font.Font(None, 36)
    text = font.render("Music:", True, BLACK)
    screen.blit(text, (WIDTH // 3, HEIGHT // 3))

    # Checkbox
    checkbox_rect = pygame.Rect(WIDTH // 3 + 100, HEIGHT // 3, 30, 30)
    pygame.draw.rect(screen, BLACK, checkbox_rect, 2)
    if music_enabled:
        pygame.draw.rect(screen, GREEN, checkbox_rect.inflate(-6, -6))


def create_pause_buttons():
    return [
        Button("Resume", WIDTH//2 - BUTTON_WIDTH//2, HEIGHT//2 - 100, resume_game),
        Button("Restart Game", WIDTH//2 - BUTTON_WIDTH//2, HEIGHT//2 - 20, restart_game),
        Button("Main Menu", WIDTH//2 - BUTTON_WIDTH//2, HEIGHT//2 + 60, return_to_main_menu_from_pause)
    ]

def restart_game():
    global current_screen, game_started, countdown_start
    fade_out()
    reset_game_state()
    current_screen = ScreenState.MAIN_MENU
    start_game()  # This will trigger a new game with fade and countdown

def resume_game():
    global current_screen, game_started, countdown_start
    current_screen = ScreenState.MAIN_MENU  # Exit pause state
    game_started = False
    countdown_start = time.time()  # Restart countdown

def return_to_main_menu_from_pause():
    global current_screen, running
    current_screen = ScreenState.MAIN_MENU
    
def reset_game_state():
    global stage, level_num, level, player1, player2, rocks, algae_list, game_started
    stage = 1
    level_num = 1
    rocks = []
    algae_list = []
    player1 = Player(100, HEIGHT-100, (255,0,0), ORANGE, red_fish)
    player2 = Player(200, HEIGHT-100, (0,0,255), TEAL, blue_fish)
    level = Level(stage, level_num)
    game_started = False

# Main menu loop
def main_menu():
    global current_screen, music_enabled
    reset_game_state()
    # Create buttons outside the loop
    main_menu_buttons = [
        Button("Play", WIDTH // 2 - BUTTON_WIDTH // 2, HEIGHT // 3, start_game),
        Button("Controls", WIDTH // 2 - BUTTON_WIDTH // 2, HEIGHT // 3 + BUTTON_HEIGHT + BUTTON_SPACING, show_controls_screen),
        Button("Settings", WIDTH // 2 - BUTTON_WIDTH // 2, HEIGHT // 3 + 2 * (BUTTON_HEIGHT + BUTTON_SPACING), show_settings_screen)
    ]
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # Handle button events based on current screen
            if current_screen == ScreenState.MAIN_MENU:
                for button in main_menu_buttons:
                    button.handle_event(event)
            elif current_screen == ScreenState.CONTROLS:
                back_button = Button("Back", 20, 20, return_to_main_menu)
                back_button.handle_event(event)
            elif current_screen == ScreenState.SETTINGS:
                back_button = Button("Back", 20, 20, return_to_main_menu)
                back_button.handle_event(event)

                # Handle checkbox click
                if event.type == pygame.MOUSEBUTTONDOWN:
                    checkbox_rect = pygame.Rect(WIDTH // 3 + 100, HEIGHT // 3, 30, 30)
                    if checkbox_rect.collidepoint(event.pos):
                        music_enabled = not music_enabled

        # Draw appropriate screen
        if current_screen == ScreenState.MAIN_MENU:
            draw_main_menu()
        elif current_screen == ScreenState.CONTROLS:
            draw_controls_screen()
        elif current_screen == ScreenState.SETTINGS:
            draw_settings_screen()

        pygame.display.flip()
        clock.tick(FPS)


# Fade out function
def fade_out():
    fade = pygame.Surface((WIDTH, HEIGHT))
    fade.fill(BLACK)
    for alpha in range(0, 255, 5):
        fade.set_alpha(alpha)
        screen.blit(fade, (0, 0))
        pygame.display.update()
        pygame.time.delay(30)


# Intro video function
def play_intro_video(video_path):
    # Initialize audio first
    pygame.mixer.init()
    pygame.mixer.music.load("audio.wav")

    # Load video
    clip = VideoFileClip(video_path)
    video_fps = clip.fps
    video_duration = clip.duration

    # Start audio and video simultaneously
    pygame.mixer.music.play()
    start_time = time.time()

    clock = pygame.time.Clock()

    try:
        for frame in clip.iter_frames(fps=video_fps, dtype="uint8"):
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            # Check if we've exceeded video duration
            if time.time() - start_time > video_duration:
                break

            # Process frame
            frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
            frame_surface = pygame.transform.scale(frame_surface, (WIDTH, HEIGHT))
            screen.blit(frame_surface, (0, 0))
            pygame.display.update()

            # Maintain video timing
            clock.tick(video_fps)
    finally:
        clip.close()
        pygame.mixer.music.stop()

    fade_out()


# Player class with sprite handling
class Player:
    def __init__(self, x, y, color, trash_color, image):
        self.original_image = image
        self.image = self.original_image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.color = color
        self.trash_color = trash_color
        self.vel = 3
        self.touching_wrong_trash = False
        self.immobilized = False
        self.immobilized_start_time = 0
        self.facing_right = False
        self.last_direction = "left"
        self.mask = pygame.mask.from_surface(self.image)

    def move(self, keys, up, down, left, right):
        if self.immobilized:
            if time.time() - self.immobilized_start_time >= 3:
                self.immobilized = False
            return

        dx, dy = 0, 0
        direction_changed = False
        
        # Horizontal movement takes priority for facing direction
        if keys[left]:
            dx -= 1
            if self.last_direction != "left" or not keys[right]:
                self.facing_right = False
                direction_changed = True
        if keys[right]:
            dx += 1
            if self.last_direction != "right" or not keys[left]:
                self.facing_right = True
                direction_changed = True
        
        # Vertical movement
        if keys[up]: dy -= 1
        if keys[down]: dy += 1

        # Update image based on direction
        if direction_changed:
            self.image = pygame.transform.flip(self.original_image, self.facing_right, False)
            self.mask = pygame.mask.from_surface(self.image)
        
        # Update last direction
        if dx != 0:
            self.last_direction = "right" if dx > 0 else "left"

        if dx != 0 or dy != 0:
            length = math.hypot(dx, dy)
            dx, dy = dx/length, dy/length
            new_x = self.rect.x + dx * self.vel
            new_y = self.rect.y + dy * self.vel
            
            # Create temp rect for collision checking
            temp_rect = self.image.get_rect(topleft=(new_x, new_y))
            
            # Keep within screen bounds
            if temp_rect.left < 0: new_x = 0
            if temp_rect.right > WIDTH: new_x = WIDTH - temp_rect.width
            if temp_rect.top < 0: new_y = 0
            if temp_rect.bottom > HEIGHT: new_y = HEIGHT - temp_rect.height
            
            # Check collisions with rocks
            collision = False
            for rock in rocks:
                if temp_rect.colliderect(rock.rect):
                    collision = True
                    break
            
            if not collision:
                self.rect.topleft = (new_x, new_y)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# Trash class with mask
class Trash:
    def __init__(self, color, existing_trashes):
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, color, (0, 0, TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        
        while True:
            print()
            self.rect.topleft = (
                random.randint(0, int(WIDTH - TILE_SIZE)),
                random.randint(0, int(HEIGHT - TILE_SIZE))
            )
            collision = False
            # Check against existing trash:
            for t in existing_trashes:
                if self.rect.colliderect(t.rect):
                    collision = True
                    break
            # Check against players:
            for p in [player1, player2]:
                if self.rect.colliderect(p.rect):
                    collision = True
                    break
            # Check against rocks:
            for rock in rocks:
                if self.rect.colliderect(rock.rect):
                    collision = True
                    break
            # Check against algae:
            for algae in algae_list:
                if self.rect.colliderect(algae.rect):
                    collision = True
                    break
            if not collision:
                break
        
        self.color = color
        self.collected = False
        
    def draw(self, surface):
        if not self.collected:
            surface.blit(self.image, self.rect)


# Rock class with mask
class Rock:
    def __init__(self):
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(GRAY)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        
        while True:
            self.rect.topleft = (
                random.randint(0, int(WIDTH - TILE_SIZE)),
                random.randint(0, int(HEIGHT - TILE_SIZE))
            )
            collision = False
            # Check against existing rocks:
            for rock in rocks:
                if self.rect.colliderect(rock.rect):
                    collision = True
                    break
            # Check against players:
            for p in [player1, player2]:
                if self.rect.colliderect(p.rect):
                    collision = True
                    break
            # Check against trash:
            for trash in level.trashes:
                if self.rect.colliderect(trash.rect):
                    collision = True
                    break
            # Check against algae:
            for algae in algae_list:
                if self.rect.colliderect(algae.rect):
                    collision = True
                    break
            if not collision:
                break

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# Algae class with mask
class Algae:
    def __init__(self):
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        
        while True:
            self.rect.topleft = (
                random.randint(0, int(WIDTH - TILE_SIZE)),
                random.randint(0, int(HEIGHT - TILE_SIZE))
            )
            collision = False
            # Check against existing algae:
            for algae in algae_list:
                if self.rect.colliderect(algae.rect):
                    collision = True
                    break
            # Check against players:
            for p in [player1, player2]:
                if self.rect.colliderect(p.rect):
                    collision = True
                    break
            # Check against rocks:
            for rock in rocks:
                if self.rect.colliderect(rock.rect):
                    collision = True
                    break
            # Check against trash:
            for trash in level.trashes:
                if self.rect.colliderect(trash.rect):
                    collision = True
                    break
            if not collision:
                break

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# Level class with 3 levels per stage
class Level:
    def __init__(self, stage, level_num):
        self.stage = stage
        self.level_num = level_num
        self.trashes = []
        self.required_orange = 5
        self.required_teal = 5
        
        # Create non-overlapping trash
        for _ in range(5):
            self.trashes.append(Trash(ORANGE, self.trashes))
        for _ in range(5):
            self.trashes.append(Trash(TEAL, self.trashes))

    def add_trash(self, color):
        new_trash = Trash(color, self.trashes)
        self.trashes.append(new_trash)
        if color == ORANGE:
            self.required_orange += 1
        else:
            self.required_teal += 1

    def draw(self):
        for trash in self.trashes:
            trash.draw(screen)

# Collision detection functions
def check_mask_collision(sprite1, sprite2):
    offset_x = sprite2.rect.x - sprite1.rect.x
    offset_y = sprite2.rect.y - sprite1.rect.y
    return sprite1.mask.overlap(sprite2.mask, (offset_x, offset_y)) is not None


def check_wrong_trash_collisions():
    for player in [player1, player2]:
        current_touching = False
        for trash in level.trashes:
            if not trash.collected and check_mask_collision(player, trash):
                if trash.color != player.trash_color:
                    current_touching = True
                    if not player.touching_wrong_trash:
                        # Add 2 new pieces of the player's trash
                        for _ in range(2):
                            level.add_trash(player.trash_color)
                        player.touching_wrong_trash = True
        if not current_touching:
            player.touching_wrong_trash = False

def check_algae_collisions():
    for player in [player1, player2]:
        for algae in algae_list[:]:  # Iterate over a copy of the list
            if check_mask_collision(player, algae):
                player.immobilized = True
                player.immobilized_start_time = time.time()
                player.color = BLACK  # Turn player black
                algae_list.remove(algae)  # Remove algae from the screen

def check_collections():
    all_collected = True
    for trash in level.trashes:
        if not trash.collected:
            all_collected = False
            for player in [player1, player2]:
                if check_mask_collision(player, trash):
                    if trash.color == player.trash_color:
                        trash.collected = True
    
    if all_collected:
        next_level()

def next_level():
    global level, level_num, stage
    level_num += 1
    if level_num <= 3:  # 3 levels per stage
        level = Level(stage, level_num)
    else:
        next_stage()

def next_stage():
    global stage, level_num, rocks, algae_list
    stage += 1
    level_num = 1
    if stage == 2:
        display_stage_complete("Stage 1 Complete. Onto Stage 2...")
        rocks = [Rock() for _ in range(10)]  # Add rocks for Stage 2
    elif stage == 3:
        display_stage_complete("Stage 2 Complete. Onto Stage 3...")
        algae_list = [Algae() for _ in range(5)]  # Add algae for Stage 3
    elif stage > 3:
        end_game()
    level = Level(stage, level_num)

def display_stage_complete(message):
    screen.fill(WHITE)
    font = pygame.font.Font(None, 48)
    text = font.render(message, True, BLACK)
    screen.blit(text, (WIDTH//2 - 200, HEIGHT//2))
    pygame.display.flip()
    pygame.time.delay(3000)

def run_game():
    global current_screen, game_started, start_time, countdown_start
    running = True
    pause_buttons = create_pause_buttons()
    
    while running:
        clock.tick(FPS)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_started:
                    current_screen = ScreenState.PAUSED
                    
            if current_screen == ScreenState.PAUSED:
                for button in pause_buttons:
                    button.handle_event(event)
            
            if current_screen == ScreenState.MAIN_MENU:
                break

        

        # Handle countdown logic
        if not game_started:
            screen.fill(BLUE)  # Clear screen for countdown
            elapsed = time.time() - countdown_start
            remaining = countdown_seconds - int(elapsed)
            
            if remaining > 0:
                # Draw countdown
                text = countdown_font.render(str(remaining), True, WHITE)
                text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
                screen.blit(text, text_rect)
                
                # Draw game elements (static during countdown)
                level.draw()
                for rock in rocks:
                    rock.draw(screen)
                for algae in algae_list:
                    algae.draw(screen)
                player1.draw(screen)
                player2.draw(screen)
                
                pygame.display.flip()
                continue  # Skip the rest of the loop during countdown
            else:
                game_started = True
                start_time = time.time()
        
        # Main game rendering (only if game is started and not paused)
        if current_screen != ScreenState.PAUSED:
            screen.fill(BLUE)
            
            # Draw game elements
            level.draw()
            for rock in rocks:
                rock.draw(screen)
            for algae in algae_list:
                algae.draw(screen)
            player1.draw(screen)
            player2.draw(screen)
            
            # Handle player movement
            keys = pygame.key.get_pressed()
            player1.move(keys, pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d)
            player2.move(keys, pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT)
            
            # Check collisions and collections
            check_wrong_trash_collisions()
            if stage == 3:
                check_algae_collisions()
            check_collections()
            
            # Draw UI elements
            timer_text = pygame.font.Font(None, 36).render(
                f"Time: {round(time.time()-start_time, 1)}s", True, WHITE)
            screen.blit(timer_text, (WIDTH-200, 20))
            
            # Calculate remaining trash
            orange_collected = sum(1 for t in level.trashes if t.color == ORANGE and t.collected)
            teal_collected = sum(1 for t in level.trashes if t.color == TEAL and t.collected)
            
            level_text = pygame.font.Font(None, 36).render(
                f"Stage: {stage}  Level: {level_num}  Orange: {orange_collected}/{level.required_orange}  Teal: {teal_collected}/{level.required_teal}", True, WHITE)
            screen.blit(level_text, (20, 20))
            
        # Pause menu rendering
        if current_screen == ScreenState.PAUSED:
            # Create a semi-transparent dark blue overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)  # Use SRCALPHA for transparency
            overlay.fill((*DARK_BLUE, PAUSE_OVERLAY_ALPHA))  # Use RGBA format for the fill color
            screen.blit(overlay, (0, 0))
            
            # Draw pause menu text and buttons
            pause_font = pygame.font.Font(None, 72)
            pause_text = pause_font.render("PAUSED", True, WHITE)
            screen.blit(pause_text, (WIDTH//2 - 100, HEIGHT//4))
            
            for button in pause_buttons:
                button.draw(screen)
                
        pygame.display.flip()


def end_game():
    total_time = round(time.time() - start_time, 2)
    screen.fill(WHITE)
    font = pygame.font.Font(None, 48)
    text = font.render(f"Game Over! Time: {total_time}s", True, BLACK)
    screen.blit(text, (WIDTH//2 - 200, HEIGHT//4))
    
    # Leaderboard handling
    team_name = ""
    input_active = True
    while input_active:
        screen.fill(WHITE)
        screen.blit(text, (WIDTH//2 - 200, HEIGHT//4))
        prompt = font.render("Enter team name: " + team_name, True, BLACK)
        screen.blit(prompt, (WIDTH//4, HEIGHT//2))
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    team_name = team_name[:-1]
                else:
                    team_name += event.unicode

    # Save to leaderboard
    try:
        with open(data_file, "r") as f:
            leaderboard = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        leaderboard = []
    
    leaderboard.append({"team": team_name, "score": total_time})
    leaderboard.sort(key=lambda x: x["score"])
    
    with open(data_file, "w") as f:
        json.dump(leaderboard, f, indent=4)
    
    # Display leaderboard
    screen.fill(WHITE)
    title = font.render("Leaderboard:", True, BLACK)
    screen.blit(title, (WIDTH//3, HEIGHT//4))
    y = HEIGHT//3
    for entry in leaderboard[:5]:
        entry_text = font.render(f"{entry['team']}: {entry['score']}s", True, BLACK)
        screen.blit(entry_text, (WIDTH//3, y))
        y += 40
    
    pygame.display.flip()
    pygame.time.delay(5000)
    pygame.quit()
    exit()

# Game initialization
player1 = Player(100, HEIGHT-100, (255,0,0), ORANGE, red_fish)
player2 = Player(200, HEIGHT-100, (0,0,255), TEAL, blue_fish)
stage = 1
level_num = 1
rocks = []
algae_list = []
level = Level(stage, level_num)

# Countdown setup
countdown_font = pygame.font.Font(None, 120)
countdown_seconds = 3
game_started = False

# Start with main menu
main_menu()

pygame.quit()
