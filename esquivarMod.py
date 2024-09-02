import pygame
import sys
import random
import pickle
import os


pygame.init()

width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Esquiva a todos los orcos!!!')

background_image = pygame.image.load('forest/PNG/game_background_1/game_background_1_mod.png').convert()

white = (255, 255, 255)
black = (0, 0, 0)

font = pygame.font.Font(None, 36)

player_x, player_y = width // 2, height - 100
player_speed = 5

player_sprite_sheet = pygame.image.load('player/PNG/Unarmed_Run/Unarmed_Run_full.png').convert_alpha()

num_columns = 8
num_rows = 4
player_sprite_width = player_sprite_sheet.get_width() // num_columns
player_sprite_height = player_sprite_sheet.get_height() // num_rows

scale_factor = 2
player_sprite_width_scaled = player_sprite_width * scale_factor
player_sprite_height_scaled = player_sprite_height * scale_factor
scaled_player_sprites = []
player_masks = []

for col in range(num_columns):
    x = col * player_sprite_width
    y = 3 * player_sprite_height 
    sprite = player_sprite_sheet.subsurface(pygame.Rect(x, y, player_sprite_width, player_sprite_height))
    scaled_sprite = pygame.transform.scale(sprite, (player_sprite_width_scaled, player_sprite_height_scaled))
    scaled_player_sprites.append(scaled_sprite)
    player_masks.append(pygame.mask.from_surface(scaled_sprite))

current_player_sprite = 0
player_sprite_animation_speed = 0.1  
player_sprite_timer = 0

enemy_sprite_sheet = pygame.image.load('orco/PNG/Orc2/Orc2_run/orc2_run_full.png').convert_alpha()

enemy_sprite_width = enemy_sprite_sheet.get_width() // num_columns
enemy_sprite_height = enemy_sprite_sheet.get_height() // num_rows

scaled_enemy_sprite_width = enemy_sprite_width * scale_factor
scaled_enemy_sprite_height = enemy_sprite_height * scale_factor
scaled_enemy_sprites = []
enemy_masks = []

for col in range(num_columns):
    x = col * enemy_sprite_width
    y = 0  # Cuarta fila
    sprite = enemy_sprite_sheet.subsurface(pygame.Rect(x, y, enemy_sprite_width, enemy_sprite_height))
    scaled_sprite = pygame.transform.scale(sprite, (scaled_enemy_sprite_width, scaled_enemy_sprite_height))
    scaled_enemy_sprites.append(scaled_sprite)
    enemy_masks.append(pygame.mask.from_surface(scaled_sprite))

base_enemy_speed = 5 
speed_increase_interval = 20
increase_amount = 2
enemies = []

score = 0
score_increment = 1 

checkpoint_file = 'checkpoint.pkl'


def load_checkpoint():
    global player_x, player_y, score, enemies, start_time
    if os.path.exists(checkpoint_file):
        try:
            with open(checkpoint_file, 'rb') as file:
                data = pickle.load(file)
                player_x = data.get('player_x', width // 2)
                player_y = data.get('player_y', height - 100)
                score = data.get('score', 0)
                enemies = data.get('enemies', [])
                start_time = pygame.time.get_ticks() - data.get('elapsed_time', 0)
        except (pickle.UnpicklingError, EOFError):
            start_time = pygame.time.get_ticks()
    else:
        start_time = pygame.time.get_ticks()


def save_checkpoint():
    global start_time
    data = {
        'player_x': player_x,
        'player_y': player_y,
        'score': score,
        'enemies': enemies,
        'elapsed_time': pygame.time.get_ticks() - start_time
    }
    with open(checkpoint_file, 'wb') as file:
        pickle.dump(data, file)


def delete_checkpoint():
    if os.path.exists(checkpoint_file):
        os.remove(checkpoint_file)


def create_enemy():
    x_pos = random.randint(0, width - scaled_enemy_sprite_width)
    y_pos = 0 - scaled_enemy_sprite_height
    enemy_sprite_index = random.randint(0, len(scaled_enemy_sprites) - 1)
    enemies.append([x_pos, y_pos, enemy_sprite_index])


def check_collision(player_pos, enemy_pos, player_mask, enemy_mask):
    offset = (enemy_pos[0] - player_pos[0], enemy_pos[1] - player_pos[1])
    return player_mask.overlap(enemy_mask, offset) is not None


def get_enemy_speed(score):
    return base_enemy_speed + (score // speed_increase_interval) * increase_amount


load_checkpoint()

running = True
while running:
    screen.blit(background_image, (0, 0))  

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_checkpoint()  
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_x += player_speed
    if keys[pygame.K_UP]:
        player_y -= player_speed
    if keys[pygame.K_DOWN]:
        player_y += player_speed

    player_x = max(0, min(player_x, width - player_sprite_width_scaled))
    player_y = max(0, min(player_y, height - player_sprite_height_scaled))

    player_sprite_timer += player_sprite_animation_speed
    if player_sprite_timer >= 1:
        player_sprite_timer = 0
        current_player_sprite = (current_player_sprite + 1) % len(scaled_player_sprites)

    screen.blit(scaled_player_sprites[current_player_sprite], (player_x, player_y))

    if random.randint(1, 20) == 1:
        create_enemy()

    enemy_speed = get_enemy_speed(score)

    for enemy in enemies:
        e_x, e_y, sprite_index = enemy
        e_y += enemy_speed
        enemy[1] = e_y 

        screen.blit(scaled_enemy_sprites[sprite_index], (e_x, e_y))

        if check_collision((player_x, player_y), (e_x, e_y), player_masks[current_player_sprite],
                           enemy_masks[sprite_index]):
            print("¡Colisión detectada! Juego terminado.")
            delete_checkpoint() 
            running = False
            break

    enemies = [enemy for enemy in enemies if enemy[1] < height]

    current_time = pygame.time.get_ticks()  
    elapsed_time = (current_time - start_time) / 1000 
    score = int(elapsed_time * score_increment)

    score_text = font.render(f"Puntuación: {score}", True, black)
    screen.blit(score_text, (10, 10))

    pygame.display.flip()

    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()
