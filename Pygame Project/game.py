# This game was made possible using a platforming tutorial
# to help organize the game and its mechanics.

# Quite a few suppression statements were used for the
# game to be able to run.

# Import pygame elements.
import pygame
from pygame import mixer
import pickle
from os import path


def main():

    pygame.mixer.pre_init(44100, -16, 2, 512)
    mixer.init()
    pygame.init()

    # Establish the frames per second.
    clock = pygame.time.Clock()
    fps = 60

    # Establish the dimensions of the screen.
    window_width = 650
    window_height = 650

    # Establish the screen itself.
    game_window = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption('Eternal Woods')

    # Declare the font.
    font = pygame.font.SysFont('Bauhaus 93', 70)
    font_score = pygame.font.SysFont('Bauhaus 93', 30)

    # Create game variables.
    tile_size = 33
    game_over = 0
    main_menu = True
    level = 1
    max_levels = 8
    score = 0

    # Declare colors
    white = (255, 255, 255)
    blue = (0, 0, 255)

    # Store images in variables.
    sun_image = pygame.image.load('Platformer-master/img/sun.png')
    background_image = pygame.image.load('Platformer-master/img/sky.png')
    restart_image = pygame.image.load('Platformer-master/img/restart_btn.png')
    start_image = pygame.image.load('Platformer-master/img/start_btn.png')
    exit_image = pygame.image.load('Platformer-master/img/exit_btn.png')

    # Add in sounds and music.
    pygame.mixer.music.load('Platformer-master/img/music.wav')
    pygame.mixer.music.play(-1, 0.0, 5000)
    coin_fx = pygame.mixer.Sound('Platformer-master/img/coin.wav')
    coin_fx.set_volume(0.5)
    jump_fx = pygame.mixer.Sound('Platformer-master/img/jump.wav')
    jump_fx.set_volume(0.5)
    game_over_fx = pygame.mixer.Sound('Platformer-master/img/game_over.wav')
    game_over_fx.set_volume(0.5)

    # Function draw text on the screen.
    def draw_text(text, fonts, text_col, x, y):
        image = fonts.render(text, True, text_col)
        game_window.blit(image, (x, y))

    # Function declared to reset level.
    def reset_level(lvl):
        player.reset(65, window_height - 85)
        blob_group.empty()
        platform_group.empty()
        coin_group.empty()
        lava_group.empty()
        exit_group.empty()

        # Load level data and create the game world.
        if path.exists(f'level{lvl}_data'):
            pickle_in = open(f'level{lvl}_data', 'rb')
            # noinspection PyUnusedLocal
            wrld_data = pickle.load(pickle_in)

        # Create variable for storing level data and game world.
        # noinspection PyUnboundLocalVariable
        wrld = World(wrld_data)

        # Return the wrld (world) variable.
        return wrld

    # Class made for establishing button clicks.
    class Button:
        def __init__(self, x, y, image):
            self.image = image
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.clicked = False

        def draw(self):
            click = False

            # Find the mouse's location.
            position = pygame.mouse.get_pos()

            # Check mouse and clicked conditions.
            if self.rect.collidepoint(position):
                # noinspection PyArgumentList
                if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                    click = True
                    self.clicked = True

            # noinspection PyArgumentList
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            # Draw the button.
            game_window.blit(self.image, self.rect)

            # Return value of the click variable.
            return click

    # Class created for player movement.
    class Player:
        def __init__(self, x, y):
            self.reset(x, y)

        # Function for updating the player's status.
        # noinspection PyAttributeOutsideInit
        def update(self, game_ovr):
            dx = 0
            dy = 0
            walk_cooldown = 5
            col_thresh = 20

            if game_ovr == 0:
                # Get key inputs.
                key = pygame.key.get_pressed()
                if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                    jump_fx.play()
                    self.vel_y = -15
                    self.jumped = True
                if not key[pygame.K_SPACE]:
                    self.jumped = False
                if key[pygame.K_LEFT]:
                    dx -= 5
                    self.counter += 1
                    self.direction = -1
                if key[pygame.K_RIGHT]:
                    dx += 5
                    self.counter += 1
                    self.direction = 1
                if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                    self.counter = 0
                    self.index = 0
                    if self.direction == 1:
                        self.image = self.images_right[self.index]
                    if self.direction == -1:
                        self.image = self.images_left[self.index]

                # Deals with animation
                if self.counter > walk_cooldown:
                    self.counter = 0
                    self.index += 1
                    if self.index >= len(self.images_right):
                        self.index = 0
                    if self.direction == 1:
                        self.image = self.images_right[self.index]
                    if self.direction == -1:
                        self.image = self.images_left[self.index]

                # Gravity added to player for jumps.
                self.vel_y += 1
                if self.vel_y > 10:
                    self.vel_y = 10
                dy += self.vel_y

                # Checking for collision.
                self.in_air = True
                for tile in world.tile_list:
                    # Checking collision in x direction.
                    if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                        dx = 0
                    # Checking for collision in y direction.
                    if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                        # Check for jumping.
                        if self.vel_y < 0:
                            dy = tile[1].bottom - self.rect.top
                            self.vel_y = 0
                        # Check for falling.
                        elif self.vel_y >= 0:
                            dy = tile[1].top - self.rect.bottom
                            self.vel_y = 0
                            self.in_air = False

                # Check for collision with bloops.
                # noinspection PyTypeChecker
                if pygame.sprite.spritecollide(self, blob_group, False):
                    game_ovr = -1
                    game_over_fx.play()

                # Check for collision with lava.
                # noinspection PyTypeChecker
                if pygame.sprite.spritecollide(self, lava_group, False):
                    game_ovr = -1
                    game_over_fx.play()

                # Check for collision with an exit.
                # noinspection PyTypeChecker
                if pygame.sprite.spritecollide(self, exit_group, False):
                    game_ovr = 1

                # Check for collision with platforms.
                for platform in platform_group:
                    # Checking for collision in the x direction.
                    if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                        dx = 0
                    # Checking for collision in the y direction.
                    if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                        # Checking if character is below platform.
                        if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                            self.vel_y = 0
                            dy = platform.rect.bottom - self.rect.top
                        # # Checking if character is above platform.
                        elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                            self.rect.bottom = platform.rect.top - 1
                            self.in_air = False
                            dy = 0
                        # Move player sideways with platform.
                        # noinspection PyUnresolvedReferences
                        if platform.move_x != 0:
                            # noinspection PyUnresolvedReferences
                            self.rect.x += platform.move_direction

                # Update the player's location.
                self.rect.x += dx
                self.rect.y += dy

            elif game_ovr == -1:
                self.image = self.dead_image
                draw_text('GAME OVER!', font, blue, (window_width // 2) - 200, window_height // 2)
                if self.rect.y > 200:
                    self.rect.y -= 5

            # Draw the player into the game.
            game_window.blit(self.image, self.rect)

            # Return the game_ovr (game_over) variable.
            return game_ovr

        # Function for resetting the player image
        # after a game over.
        # noinspection PyAttributeOutsideInit
        def reset(self, x, y):
            self.images_right = []
            self.images_left = []
            self.index = 0
            self.counter = 0
            for num in range(1, 5):
                img_right = pygame.image.load(f'Platformer-master/img/guy{num}.png')
                img_right = pygame.transform.scale(img_right, (26, 52))
                img_left = pygame.transform.flip(img_right, True, False)
                self.images_right.append(img_right)
                self.images_left.append(img_left)
            self.dead_image = pygame.image.load('Platformer-master/img/ghost.png')
            self.image = self.images_right[self.index]
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.width = self.image.get_width()
            self.height = self.image.get_height()
            self.vel_y = 0
            self.jumped = False
            self.direction = 0
            self.in_air = True

    # Class used to get all the aspects of the game world.
    class World:
        def __init__(self, data):
            self.tile_list = []

            # Get the basic world images.
            dirt_img = pygame.image.load('Platformer-master/img/dirt.png')
            grass_img = pygame.image.load('Platformer-master/img/grass.png')

            # Places all the game world elements where they
            # should be.
            row_count = 0
            for row in data:
                col_count = 0
                for tile in row:
                    if tile == 1:
                        img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                        img_rect = img.get_rect()
                        img_rect.x = col_count * tile_size
                        img_rect.y = row_count * tile_size
                        tile = (img, img_rect)
                        self.tile_list.append(tile)
                    if tile == 2:
                        img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                        img_rect = img.get_rect()
                        img_rect.x = col_count * tile_size
                        img_rect.y = row_count * tile_size
                        tile = (img, img_rect)
                        self.tile_list.append(tile)
                    if tile == 3:
                        blob = Enemy(col_count * tile_size, row_count * tile_size + 15)
                        blob_group.add(blob)
                    if tile == 4:
                        platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
                        platform_group.add(platform)
                    if tile == 5:
                        platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
                        platform_group.add(platform)
                    if tile == 6:
                        lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                        lava_group.add(lava)
                    if tile == 7:
                        coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
                        coin_group.add(coin)
                    if tile == 8:
                        ext = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                        exit_group.add(ext)
                    col_count += 1
                row_count += 1

        # Draw the game world onto the screen.
        def draw(self):
            for tile in self.tile_list:
                game_window.blit(tile[0], tile[1])

    # Class for creating the Bloop enemy and its movement.
    class Enemy(pygame.sprite.Sprite):
        def __init__(self, x, y):
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.image.load('Platformer-master/img/blob.png')
            self.image = pygame.transform.scale(self.image, (33, 33))
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.move_direction = 1
            self.move_counter = 0

        # Function adds movement to the Bloop.
        def update(self):
            self.rect.x += self.move_direction
            self.move_counter += 1
            if abs(self.move_counter) > 50:
                self.move_direction *= -1
                self.move_counter *= -1

    # Class for creating the moving platforms.
    class Platform(pygame.sprite.Sprite):
        def __init__(self, x, y, move_x, move_y):
            pygame.sprite.Sprite.__init__(self)
            img = pygame.image.load('Platformer-master/img/platform.png')
            self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.move_counter = 0
            self.move_direction = 1
            self.move_x = move_x
            self.move_y = move_y

        # Function adds movement in both directions to the platforms.
        def update(self):
            self.rect.x += self.move_direction * self.move_x
            self.rect.y += self.move_direction * self.move_y
            self.move_counter += 1
            if abs(self.move_counter) > 50:
                self.move_direction *= -1
                self.move_counter *= -1

    # Class for creating the lava.
    class Lava(pygame.sprite.Sprite):
        def __init__(self, x, y):
            pygame.sprite.Sprite.__init__(self)
            img = pygame.image.load('Platformer-master/img/lava.png')
            self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y

    # Class for creating the collectible coin.
    class Coin(pygame.sprite.Sprite):
        def __init__(self, x, y):
            pygame.sprite.Sprite.__init__(self)
            img = pygame.image.load('Platformer-master/img/coin.png')
            self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
            self.rect = self.image.get_rect()
            self.rect.center = (x, y)

    # Class for creating the escape gate.
    class Exit(pygame.sprite.Sprite):
        def __init__(self, x, y):
            pygame.sprite.Sprite.__init__(self)
            img = pygame.image.load('Platformer-master/img/exit.png')
            self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y

    # Layout or shape of the game world.
    world_data = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 1],
        [1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 2, 2, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 7, 0, 5, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 1],
        [1, 7, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 7, 0, 0, 0, 0, 1],
        [1, 0, 2, 0, 0, 7, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 2, 0, 0, 4, 0, 0, 0, 0, 3, 0, 0, 3, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 7, 0, 0, 0, 0, 2, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 2, 2, 2, 2, 2, 1],
        [1, 0, 0, 0, 0, 0, 2, 2, 2, 6, 6, 6, 6, 6, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]

    # Variable for setting player location.
    player = Player(65, window_height - 85)

    # Group variables for each enemies, platforms, etc.
    blob_group = pygame.sprite.Group()
    platform_group = pygame.sprite.Group()
    lava_group = pygame.sprite.Group()
    coin_group = pygame.sprite.Group()
    exit_group = pygame.sprite.Group()

    # Create pseudo coin for showing score.
    score_coin = Coin(tile_size // 2, tile_size // 2)
    coin_group.add(score_coin)

    # Load level data and create world.
    if path.exists(f'level{level}_data'):
        pckle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pckle_in)
    world = World(world_data)

    # Create buttons the player will use click in the game.
    restart_button = Button(window_width // 2 - 50, window_height // 2 + 100, restart_image)
    start_button = Button(window_width // 2 - 228, window_height // 2, start_image)
    exit_button = Button(window_width // 2 + 98, window_height // 2, exit_image)
    exit_button2 = Button(window_width // 2 - 50, window_height // 2 + 150, exit_image)

    # Actions are preformed while the game runs.
    run = True
    while run:

        clock.tick(fps)

        # Background images put on screen.
        game_window.blit(background_image, (0, 0))
        game_window.blit(sun_image, (100, 100))

        # Start at the main menu.
        if main_menu:
            draw_text('Eternal Woods', font, blue, (window_width // 2) - 150, window_height // 2 - 200)
            # Stop running the game if exit button clicked.
            if exit_button.draw():
                run = False
            # Main menu to game if start button clicked.
            if start_button.draw():
                main_menu = False
        else:
            world.draw()

            if game_over == 0:
                blob_group.update()
                platform_group.update()
                # Update the player's score.
                # Check if a coin has been collected
                # noinspection PyTypeChecker
                if pygame.sprite.spritecollide(player, coin_group, True):
                    score += 1
                    coin_fx.play()
                draw_text('X ' + str(score), font_score, white, tile_size - 10, 10)

            blob_group.draw(game_window)
            platform_group.draw(game_window)
            lava_group.draw(game_window)
            coin_group.draw(game_window)
            exit_group.draw(game_window)

            game_over = player.update(game_over)

            # Once the player gets a game over
            # and selects restart, the level, player's
            # position, and score is reset.
            # If they press the second exit button th game ends.
            if game_over == -1:
                if exit_button2.draw():
                    run = False
                if restart_button.draw():
                    world = reset_level(level)
                    game_over = 0
                    score = 0

            # Once the player has completed a level.
            if game_over == 1:
                # Go to the next level.
                level += 1
                if level <= max_levels:
                    world = reset_level(level)
                    game_over = 0
                else:
                    # Victory screen displayed after all levels
                    # are beaten.
                    draw_text('YOU WIN!', font, blue, (window_width // 2) - 140, window_height // 2)
                    # Exit the game if done playing.
                    if exit_button2.draw():
                        run = False
                    # Restart and play the whole game again.
                    if restart_button.draw():
                        level = 1
                        world = reset_level(level)
                        game_over = 0
                        score = 0

        # Ends the game.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        pygame.display.update()

    pygame.quit()


main()
