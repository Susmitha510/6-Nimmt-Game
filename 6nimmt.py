import pygame
import random
import os
import sys

# -------------------------
# Constants
# -------------------------
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
CARD_WIDTH = 80
CARD_HEIGHT = 120
ROWS = 4
ROW_SPACING = 100
PLAYER_Y_START = 500
SELECTION_TIME = 15
MAX_PENALTY = 64

BULL_HEADS = {55: 7, 5: 2, 10: 3, 1: 1}

def get_bull_heads(card_number):
    if card_number in BULL_HEADS:
        return BULL_HEADS[card_number]
    elif card_number % 11 == 0:
        return 5
    elif card_number % 10 == 0:
        return 3
    elif card_number % 5 == 0:
        return 2
    else:
        return 1

# -------------------------
# Card Class
# -------------------------
class Card: # Card no, bull head, hovering
    def __init__(self, number):
        self.number = number
        self.penalty = get_bull_heads(number)
        self.rect = pygame.Rect(0, 0, CARD_WIDTH, CARD_HEIGHT)

# -------------------------
# Player Class
# -------------------------
class Player: 
    def __init__(self, name, is_human=False):
        self.name = name
        self.hand = []
        self.penalty_points = 0
        self.is_human = is_human
        self.selected_card = None

    def play_card(self):
        if self.is_human:
            if self.selected_card:
                card = self.selected_card
                self.selected_card = None
                return card
            return None
        else:
            if self.hand:
                return self.hand.pop(random.randint(0, len(self.hand) - 1))
        return None

# -------------------------
# Game Class
# -------------------------
class Game: # Initialization
    def __init__(self, player_count):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("6nimmt! Game")
        self.clock = pygame.time.Clock()
        self.running = True

        bg_file = r"assets\background.png.jpg"
        bull_file = r"assets\bull.png"

        if os.path.exists(bg_file):
            self.background = pygame.image.load(bg_file)
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.background.fill((50, 150, 50))

        if os.path.exists(bull_file):
            self.bull_img = pygame.image.load(bull_file)
            self.bull_img = pygame.transform.scale(self.bull_img, (CARD_WIDTH // 4, CARD_WIDTH // 4))
        else:
            self.bull_img = None

        self.players = [Player("You", is_human=True)] + \
            [Player(f"AI{i}") for i in range(1, player_count)]
        self.deck = [Card(i) for i in range(1, 105)]
        random.shuffle(self.deck)

        for _ in range(10):
            for player in self.players:
                if self.deck:
                    player.hand.append(self.deck.pop())

        self.rows = [[self.deck.pop()] for _ in range(ROWS)]

    # -------------------------
    # Drawing Methods(visuals)
    # -------------------------
    def draw_card(self, card, x, y, clickable=False):
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, CARD_WIDTH, CARD_HEIGHT))
        pygame.draw.rect(self.screen, (0, 0, 0), (x, y, CARD_WIDTH, CARD_HEIGHT), 2)

        font = pygame.font.SysFont(None, 36)
        text = font.render(str(card.number), True, (0, 0, 0))
        text_rect = text.get_rect(center=(x + CARD_WIDTH // 2, y + CARD_HEIGHT // 2))
        self.screen.blit(text, text_rect)

        if self.bull_img:
            max_per_row = CARD_WIDTH // (self.bull_img.get_width() + 2)
            rows_needed = (card.penalty + max_per_row - 1) // max_per_row
            for r in range(rows_needed):
                bulls_in_row = min(max_per_row, card.penalty - r * max_per_row)
                for i in range(bulls_in_row):
                    bx = x + i * (self.bull_img.get_width() + 2) + 5
                    by = y + r * (self.bull_img.get_height() + 2) + 5
                    self.screen.blit(self.bull_img, (bx, by))
        card.rect.topleft = (x, y)
        if clickable:
            return card.rect

    def draw_rows(self):
        for i, row in enumerate(self.rows):
            for j, card in enumerate(row):
                x = 50 + j * (CARD_WIDTH + 10)
                y = 50 + i * ROW_SPACING
                self.draw_card(card, x, y)

    def draw_players(self):
        font = pygame.font.SysFont(None, 30)
        for i, player in enumerate(self.players):
            x = SCREEN_WIDTH - 250
            y = 50 + i * 35
            text = font.render(f"{player.name}: {player.penalty_points}", True, (0, 0, 0))
            self.screen.blit(text, (x, y))

    def draw_hand(self, player, timer=None):
        self.hand_rects = []
        x_start = 100
        y = SCREEN_HEIGHT - CARD_HEIGHT - 40
        for idx, card in enumerate(player.hand):
            rect = self.draw_card(card, x_start + idx * (CARD_WIDTH + 10), y, clickable=True)
            self.hand_rects.append((rect, card))
        if timer is not None:
            font = pygame.font.SysFont(None, 28)
            timer_text = font.render(f"Time left: {timer}", True, (0, 0, 0))
            self.screen.blit(timer_text, (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 40))

    # -------------------------
    # Game Reveal & Placement Methods
    # -------------------------
    def display_played_cards(self, plays):
        # Show all played cards in the center for 3 seconds, with rows still visible
        reveal_duration = 3000  # milliseconds (3 seconds)
        font = pygame.font.SysFont(None, 26)
        title_font = pygame.font.SysFont("comicsansms", 40, bold=True)
        spacing = CARD_WIDTH + 20
        start_x = (SCREEN_WIDTH - (len(plays) * spacing)) // 2
        y = SCREEN_HEIGHT // 2 + ROW_SPACING * 2  # below all rows
        title = title_font.render("Revealing the selected cards", True, (160, 0, 0))

        start_time = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start_time < reveal_duration:
            self.screen.blit(self.background, (0, 0))
            self.draw_rows()
            self.draw_players()
            # Draw the title above revealed cards
            self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, y - 60))
            # Draw all revealed cards
            for i, (card, player) in enumerate(plays):
                self.draw_card(card, start_x + i * spacing, y)
                name = font.render(player.name, True, (0, 0, 0))
                self.screen.blit(name, (start_x + i * spacing, y + CARD_HEIGHT + 6))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.clock.tick(30)

    def get_human_row_choice(self):
        font = pygame.font.SysFont(None, 40)
        highlight_color = (255, 100, 50, 90)
        overlay = pygame.Surface((CARD_WIDTH * 6 + 14, CARD_HEIGHT + 14), pygame.SRCALPHA)
        overlay.fill((255, 150, 0, 80))  # Transparent highlight

        while True:
            self.screen.blit(self.background, (0, 0))
            self.draw_rows()
            self.draw_players()
            prompt = font.render("Your card is lowest! Click a row to take:", True, (200, 50, 50))
            self.screen.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, SCREEN_HEIGHT - 100))
            mx, my = pygame.mouse.get_pos()
            for idx in range(ROWS):
                x = 50 - 7
                y = 50 + idx * ROW_SPACING - 7
                w = CARD_WIDTH * 6 + 14
                h = CARD_HEIGHT + 14
                self.screen.blit(overlay, (x, y))
                if x <= mx <= x + w and y <= my <= y + h:
                    pygame.draw.rect(self.screen, (255, 0, 0), (x, y, w, h), 5)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for idx in range(ROWS):
                        x = 50 - 7
                        y = 50 + idx * ROW_SPACING - 7
                        w = CARD_WIDTH * 6 + 14
                        h = CARD_HEIGHT + 14
                        if x <= mx <= x + w and y <= my <= y + h:
                            return idx
            self.clock.tick(30)

    # -------------------------
    # Game Logic
    # -------------------------
    def smart_place_card(self, player, card):
        min_diff = float("inf")
        target_row = None
        for i, row in enumerate(self.rows):
            last_card = row[-1]
            if last_card.number < card.number:
                diff = card.number - last_card.number
                if diff < min_diff:
                    min_diff = diff
                    target_row = i
        if target_row is not None:
            row = self.rows[target_row]
            if len(row) >= 5:
                total_penalty = sum(c.penalty for c in row)
                player.penalty_points += total_penalty
                self.rows[target_row] = [card]
            else:
                row.append(card)
        else:
            # Card too low for all rows
            if player.is_human:
                row_index = self.get_human_row_choice()
            else:
                # AI: select row with least penalty points
                row_index = min(range(ROWS), key=lambda i: sum(c.penalty for c in self.rows[i]))
            total_penalty = sum(c.penalty for c in self.rows[row_index])
            player.penalty_points += total_penalty
            self.rows[row_index] = [card]

    def run_round(self):
        human = self.players[0]
        if human.hand:
            # -- Human selects card
            start_ticks = pygame.time.get_ticks()
            selecting = True
            while selecting:
                elapsed = int((pygame.time.get_ticks() - start_ticks) / 1000)
                timer_left = max(SELECTION_TIME - elapsed, 0)
                self.screen.blit(self.background, (0, 0))
                self.draw_rows()
                self.draw_players()
                self.draw_hand(human, timer_left)
                pygame.display.flip()
                if timer_left <= 0:
                    human.selected_card = min(human.hand, key=lambda c: c.number)
                    human.hand.remove(human.selected_card)
                    selecting = False
                    break
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mx, my = pygame.mouse.get_pos()
                        for rect, card in self.hand_rects:
                            if rect.collidepoint(mx, my):
                                human.selected_card = card
                                human.hand.remove(card)
                                selecting = False
                                break

        # -- Let all players play
        plays = []
        for player in self.players:
            card = player.play_card()
            if card:
                plays.append((card, player))

        # -- Reveal all selections
        self.display_played_cards(plays)

        # -- Place cards in ascending order
        plays.sort(key=lambda x: x[0].number)
        for card, player in plays:
            self.smart_place_card(player, card)

    def run(self):
        while True:
            for player in self.players:
                if player.penalty_points >= MAX_PENALTY:
                    self.display_game_over()
                    return

            if any(player.hand for player in self.players):
                self.run_round()
            else:
                self.deck = [Card(i) for i in range(1, 105)]
                random.shuffle(self.deck)
                for _ in range(10):
                    for player in self.players:
                        if self.deck:
                            player.hand.append(self.deck.pop())

    # -------------------------
    # Game Over Display
    # -------------------------
    def display_game_over(self):
        font = pygame.font.SysFont(None, 50)
        game_over_font = pygame.font.SysFont("comicsansms", 90, bold=True)
        blink_timer = 0
        show_text = True

        # Play Again button config
        button_w = 320
        button_h = 68
        button_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_w//2, 550, button_w, button_h)
        button_font = pygame.font.SysFont("comicsansms", 50, bold=True)

        while True:
            self.screen.blit(self.background, (0, 0))
            if pygame.time.get_ticks() - blink_timer > 1000:
                show_text = not show_text
                blink_timer = pygame.time.get_ticks()
            if show_text:
                go_text = game_over_font.render("GAME OVER", True, (0, 0, 0))
                self.screen.blit(go_text, (SCREEN_WIDTH // 2 - go_text.get_width() // 2, 50))
            # Display results
            sorted_players = sorted(self.players, key=lambda p: p.penalty_points)
            y_pos = 200
            for player_final in sorted_players:
                text = font.render(f"{player_final.name}: {player_final.penalty_points} points", True, (0, 0, 0))
                self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_pos))
                y_pos += 60

            # Draw Play Again button
            pygame.draw.rect(self.screen, (0, 0, 0), button_rect)
            button_label = button_font.render("Play Again", True, (255, 255, 255))
            self.screen.blit(
                button_label,
                (button_rect.centerx - button_label.get_width() // 2, button_rect.centery - button_label.get_height() // 2)
            )

            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if button_rect.collidepoint(event.pos):
                        main_menu()
                        return
            self.clock.tick(10)

# -------------------------
# How to Play Screen
# -------------------------
def show_how_to_play(screen, background, clock):
    font = pygame.font.SysFont("comicsansms", 42)
    rule_font = pygame.font.SysFont("comicsansms", 34)
    back_rect = pygame.Rect(SCREEN_WIDTH - 180, SCREEN_HEIGHT - 80, 150, 50)

    rules = [
        "Each player starts with 10 cards.",
        "Four rows start on the table with one card each.",
        "Each round, all players choose one card.",
        "Cards are revealed together and placed in order.",
        "If your card can’t fit, you must take a row.",
        "You get penalty points for taking rows.",
        "Game ends when someone reaches 64 points!",
    ]

    while True:
        screen.blit(background, (0, 0))
        title = font.render("How to Play", True, (0, 0, 0))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

        y_offset = 150
        for line in rules:
            bullet_text = rule_font.render(f"• {line}", True, (0, 0, 0))
            screen.blit(bullet_text, (120, y_offset))
            y_offset += 60

        pygame.draw.rect(screen, (0, 0, 0), back_rect)
        back_text = rule_font.render("Back", True, (255, 255, 255))
        screen.blit(back_text, (back_rect.centerx - back_text.get_width() // 2, back_rect.centery - back_text.get_height() // 2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and back_rect.collidepoint(event.pos):
                return
        clock.tick(30)

# -------------------------
# Menu and Flow
# -------------------------
def main_menu():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("6nimmt! Menu")
    clock = pygame.time.Clock()

    bg_file = r"assets\background.png.jpg"
    if os.path.exists(bg_file):
        background = pygame.image.load(bg_file)
        background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    else:
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        background.fill((50, 150, 50))

    title_font = pygame.font.SysFont("comicsansms", 80, bold=True)
    instr_font = pygame.font.SysFont("comicsansms", 45)
    small_font = pygame.font.SysFont("comicsansms", 35)

    play_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50, 300, 70)
    howto_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 70, 300, 70)
    exit_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 200, 300, 70)

    while True:
        screen.blit(background, (0, 0))
        title_text = title_font.render("6nimmt!", True, (0, 0, 0))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 200))

        pygame.draw.rect(screen, (0, 0, 0), play_rect)
        play_text = instr_font.render("Play", True, (255, 255, 255))
        screen.blit(play_text, (play_rect.centerx - play_text.get_width() // 2, play_rect.centery - play_text.get_height() // 2))

        pygame.draw.rect(screen, (0, 0, 0), howto_rect)
        how_text = small_font.render("How to Play", True, (255, 255, 255))
        screen.blit(how_text, (howto_rect.centerx - how_text.get_width() // 2, howto_rect.centery - how_text.get_height() // 2))

        pygame.draw.rect(screen, (0, 0, 0), exit_rect)
        exit_text = small_font.render("Exit", True, (255, 255, 255))
        screen.blit(exit_text, (exit_rect.centerx - exit_text.get_width() // 2, exit_rect.centery - exit_text.get_height() // 2))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_rect.collidepoint(event.pos):
                    return player_selection(screen, background, clock)
                elif howto_rect.collidepoint(event.pos):
                    show_how_to_play(screen, background, clock)
                elif exit_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
        clock.tick(30)

# -------------------------
# Player Selection
# -------------------------
def player_selection(screen, background, clock):
    font = pygame.font.SysFont("comicsansms", 50)
    input_str = ""

    while True:
        screen.blit(background, (0, 0))
        text = font.render("Enter number of players (2–10):", True, (0, 0, 0))
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        input_text = font.render(input_str, True, (0, 0, 0))
        screen.blit(input_text, (SCREEN_WIDTH // 2 - input_text.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and input_str.isdigit():
                    val = int(input_str)
                    if 2 <= val <= 10:
                        return tap_to_play(val, screen, background, clock)
                elif event.key == pygame.K_BACKSPACE:
                    input_str = input_str[:-1]
                elif event.unicode.isdigit():
                    input_str += event.unicode
        clock.tick(30)

# -------------------------
# Tap to Play Screen
# -------------------------
def tap_to_play(players, screen, background, clock):
    font = pygame.font.SysFont("comicsansms", 70, bold=True)
    blink_timer = 0
    show_text = True
    while True:
        screen.blit(background, (0, 0))
        if pygame.time.get_ticks() - blink_timer > 500:
            show_text = not show_text
            blink_timer = pygame.time.get_ticks()
        if show_text:
            text = font.render("Tap to Play", True, (0, 0, 0))
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                return Game(players).run()
        clock.tick(30)

# -------------------------
# Run the Game!
# -------------------------
if __name__ == "__main__":
    main_menu()