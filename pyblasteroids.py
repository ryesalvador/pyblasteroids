# Pyblasteroids - A 2D Space Shooter Game
# Copyright (C) 2023 Ryan Dela Rosa Salvador

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pygame, os, platform, random, sys
from pygame.locals import *
from math import *
from pygame import Vector2

if platform.system() == 'Windows':
    os.environ['SDL_VIDEODRIVER'] = 'windib'

# Colors: R G B values, how much red, green and blue
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
CARNATION = (255, 166, 201)

# Initialize our game
SCR_SIZE = SCR_W, SCR_H = 640, 480
SHIP_W, SHIP_H = 17, 21
ROCK_W, ROCK_H = 51, 41
NUM_OF_ROCKS = 3
NUM_OF_ROCK_SPLIT = 5
ADD_NEW_ROCK_RATE = 300
SPEED_INCREMENT = 6
SPEED_DECREMENT = 13
MAX_SPEED = 200.0

# Points that create the shape of our asteroid
ROCK_SHAPE = [(5,0), (0,15), (0,30),
              (15,40), (20,30), (30,40),
              (45,30), (45,25), (25,20),
              (45,10), (36,0), (25,5)]

def exit_game():
    pygame.quit()
    sys.exit()

def press_any_key():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit_game()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    exit_game()
                return
    
def draw_text(text, font, surface, pos, color=GREEN):
    text_surf = font.render(text, 1, color)
    surface.blit(text_surf, pos)

def get_blast():
    blast = {'speed': MAX_SPEED * 3,
             'pos': Vector2(200, 150),
             'rot': 0.0,
             'surf': pygame.Surface((3, 11))}
    pygame.draw.aaline(blast['surf'], WHITE, [1, 0], [1, 10])
    return blast

def new_rock():
    # Data structure for our asteroid
    rock = {'speed': random.randint(20, 80),
            'pos': Vector2(random.randint(0, SCR_W - ROCK_W),
                           random.randint(0, SCR_H - ROCK_H)),
            'rot': 0.0,
            'rot_speed': random.randint(90, 180) / 1.0,
            'rot_direction': random.choice([-1, 1]),
            'surf': pygame.Surface((ROCK_W, ROCK_H)),
            'rect': pygame.Rect(0, 0, ROCK_W, ROCK_H),
            'hits': 0}
    
    # Draw our asteroid using geometric primitives
    pygame.draw.polygon(rock['surf'], WHITE, ROCK_SHAPE, 1)
    return rock

def new_ship():
    # Data structure for our spaceship, Vectorize
    ship = {'speed': 0,
            'pos': Vector2(200, 150),
            'rot': 0.0,
            'rot_speed': 360.0,
            'surf': pygame.Surface((SHIP_W, SHIP_H)),
            'new': True}

    # Draws spaceship using geometric primitives
    pygame.draw.aaline(ship['surf'], GREEN, [0, 20], [8, 0])
    pygame.draw.aaline(ship['surf'], GREEN, [8, 0], [16, 20])
    pygame.draw.aaline(ship['surf'], GREEN, [2, 15], [7, 15])
    pygame.draw.aaline(ship['surf'], GREEN, [14, 15], [9, 15])
    return ship

def center_rotate(image, w, h):
    """Returns the drawing position and where it's heading"""
    heading_x = sin(image['rot'] * pi / 180.0) # Convert degrees to rads then calculate x component 
    heading_y = cos(image['rot'] * pi / 180.0) # Convert degrees to rads then calculate y component
    return Vector2(image['pos'].x - w / 2, image['pos'].y - h / 2), Vector2(heading_x, heading_y)

## Main loop. Initializes PyGame and our game ##
def main():
    pygame.init()
    screen = pygame.display.set_mode(SCR_SIZE)    
    pygame.display.set_caption("pyBlasteroids")
    
    title_font = pygame.font.Font('assets/SFPixelate.ttf', 72)
    text_font = pygame.font.Font('assets/SFPixelate.ttf', 36)
    score_font = pygame.font.Font(None, 72)

    welcome_sound = pygame.mixer.Sound('assets/sfx-01.wav')
    blaster_sound = pygame.mixer.Sound('assets/blast.wav')
    asteroid_hit_sound = pygame.mixer.Sound('assets/hit.wav')
    player_collision_sound = pygame.mixer.Sound('assets/explode.wav')

    screen_rect = screen.get_rect()
    ship = new_ship()    
    blasts = []
    score = 0
    num_of_lives = 3    
    total_time_passed_secs = 0    
    rock_add_counter = 0    
    running = True

    # Displays game title screen and waits for user
    title_rect = title_font.render('pyBlasteroids', 1, GREEN).get_rect()
    start_rect = text_font.render('Press any key to start', 1, GREEN).get_rect()
    draw_text('pyBlasteroids', title_font, screen,
              (screen_rect.centerx - title_rect.width / 2,
               screen_rect.centery - (title_rect.height + start_rect.height + 10) / 2))
    draw_text('Press any key to start', text_font, screen,
              (screen_rect.centerx - start_rect.width / 2,
               screen_rect.centery + 10))
    global top_score
    if top_score > 0:
        draw_text('Top score: %s' % str(top_score), text_font, screen, (20, 10), CARNATION)
    pygame.display.update()
    welcome_sound.play()
    press_any_key()
    clock = pygame.time.Clock()

    rocks = []
    for i in range(NUM_OF_ROCKS):
        rock = new_rock()        
        rocks.append(rock)

    ## Game loop ##
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit_game()

        pressed_keys = pygame.key.get_pressed()
        rot_direction = 0.0
        mov_direction = -1

        if pressed_keys[K_ESCAPE]:
            exit_game()
        if pressed_keys[K_LEFT]: 
            rot_direction = +1.0        
        elif pressed_keys[K_RIGHT]:
            rot_direction = -1.0        
        if pressed_keys[K_UP]:
            ship['speed'] += SPEED_INCREMENT
            if ship['speed'] > MAX_SPEED: ship['speed'] = MAX_SPEED
        elif pressed_keys[K_DOWN]:
            ship['speed'] -= SPEED_DECREMENT
            if ship['speed'] < 0: ship['speed'] = 0
        if pressed_keys[K_SPACE]:
            new_blast = get_blast()
            new_blast['pos'] = Vector2(ship['pos'].x, ship['pos'].y)
            new_blast['rot'] = ship['rot']
            blasts.append(new_blast)
            blaster_sound.play()

        screen.fill(BLACK)
        time_passed = clock.tick(30)
        time_passed_secs = time_passed / 1000.0        
        total_time_passed_secs += time_passed_secs

        rock_add_counter += 1
        if rock_add_counter == ADD_NEW_ROCK_RATE:
            rock_add_counter = 0
            rock = new_rock()
            rock['pos'] = Vector2(0 - ROCK_W, random.randint(0, SCR_H - ROCK_H))
            rocks.append(rock)

        ## Updates the blasts ##
        for blast in blasts[:]:            
            # The first time around the blast is not yet rotated
            rotated_blast_surf = pygame.transform.rotate(blast['surf'], blast['rot'])

            # The rotated surface may not return the same dimensions as the original
            bw, bh = rotated_blast_surf.get_size()

            # We adjust our x and y so that the center of the blast is in the original
            # x and y position
            blast_draw_pos, b_heading = center_rotate(blast, bw, bh)
            b_heading *= mov_direction

            # New position time based
            blast['pos'] += b_heading * time_passed_secs * blast['speed']

            # Removes blasts that has left the edges of the screen from list.
            if blast['pos'].y < 0 and blast in blasts:
                blasts.remove(blast)
            if blast['pos'].y + bh > SCR_H and blast in blasts:
                blasts.remove(blast)
            if blast['pos'].x < 0 and blast in blasts:
                blasts.remove(blast)
            if blast['pos'].x + bw > SCR_W and blast in blasts:
                blasts.remove(blast)

            # Checks if enemy was hit by blast and split it in two
            # Remove from list if it has already been hit a couple of times
            blast_rect = pygame.Rect(blast_draw_pos.x, blast_draw_pos.y, bw, bh)
            for rock in rocks[:]:
                if blast_rect.colliderect(rock['rect']) and blast in blasts:
                    
                    rotated_rock_surf = pygame.transform.rotate(rock['surf'], rock['rot'])        
                    rw, rh = rotated_rock_surf.get_size()

                    rock_half = new_rock()
                    rock_half['pos'] = Vector2(rock['pos'].x, rock['pos'].y)                    

                    rock['pos'].y -= rh + (rh / 2)
                    rock_half['pos'].y += rh + (rh / 2)                    

                    rock['surf'] = pygame.transform.scale(rotated_rock_surf, (rw - (rw / 4), rh - (rh / 4)))
                    rock_half['surf'] = rock['surf']                    

                    rock['hits'] += 1

                    if rock['hits'] >= NUM_OF_ROCK_SPLIT:
                        rocks.remove(rock)
                    else:
                        rock_half['hits'] = rock['hits']
                        rocks.append(rock_half)
                    
                    blasts.remove(blast)
                    score += 100
                    asteroid_hit_sound.play()

            screen.blit(rotated_blast_surf, blast_draw_pos)

        ## Updates the asteroids, the same thing as the blasts ##
        for rock in rocks[:]:
            rotated_rock_surf = pygame.transform.rotate(rock['surf'], rock['rot'])        
            rw, rh = rotated_rock_surf.get_size()
            rock['rot'] += rock['rot_direction'] * rock['rot_speed'] * time_passed_secs
            rock_draw_pos, r_heading = center_rotate(rock, rw, rh)        
            rock['pos'].x += 1.0 * time_passed_secs * rock['speed']        
            rock['rect'] = pygame.Rect(rock_draw_pos.x, rock_draw_pos.y, rw, rh)

            if rock['pos'].y < 0:
                rocks.remove(rock)                
            if rock['pos'].y + rh > SCR_H:
                rocks.remove(rock)
            if rock['pos'].x > SCR_W + ROCK_W:
                rock['pos'].x = -ROCK_W

            screen.blit(rotated_rock_surf, rock_draw_pos)

        ## Updates the player, the same thing as the blasts ##
        if total_time_passed_secs >= 5:
            ship['new'] = False
            total_time_passed_secs = 0            
            
        rotated_ship_surf = pygame.transform.rotate(ship['surf'], ship['rot'])        
        sw, sh = rotated_ship_surf.get_size()
        
        # This is for the spaceship's rotation--time based
        ship['rot'] += rot_direction * ship['rot_speed'] * time_passed_secs
        
        ship_draw_pos, s_heading = center_rotate(ship, sw, sh)
        s_heading *= mov_direction        
        ship['pos'] += s_heading * time_passed_secs * ship['speed']

        # Stops player from leaving the edges of the screen
        if ship['pos'].y < sh:
            ship['pos'].y = sh
        if ship['pos'].y + sh > SCR_H:
            ship['pos'].y = SCR_H - sh
        if ship['pos'].x < sw:
            ship['pos'].x = sw
        if ship['pos'].x + sw > SCR_W:
            ship['pos'].x = SCR_W - sw

        # Checks if player has collided with an enemy; it doesn't check for the first 5 seconds
        ship_rect = pygame.Rect(ship_draw_pos.x, ship_draw_pos.y, sw, sh)
        for rock in rocks[:]:
            if ship_rect.colliderect(rock['rect']) and not ship['new']:
                total_time_passed_secs = 0
                num_of_lives -= 1
                ship = new_ship()
                player_collision_sound.play()

        # Blinks player to indicate time allowance
        if ship['new']:
            if total_time_passed_secs > 0.5 and total_time_passed_secs < 1:
                rotated_ship_surf.fill(BLACK)
            if total_time_passed_secs > 1.5 and total_time_passed_secs < 2:
                rotated_ship_surf.fill(BLACK)
            if total_time_passed_secs > 2.5 and total_time_passed_secs < 3:
                rotated_ship_surf.fill(BLACK)
            if total_time_passed_secs > 3.5 and total_time_passed_secs < 4:
                rotated_ship_surf.fill(BLACK)
            if total_time_passed_secs > 4.5 and total_time_passed_secs < 5:
                rotated_ship_surf.fill(BLACK)

        screen.blit(rotated_ship_surf, ship_draw_pos)            

        ## Displays the score on the left side of the screen ##
        draw_text(str(score), score_font, screen, (20, 5), CARNATION)

        ## Displays the number of lives left ##
        x = 28
        for i in range(num_of_lives):        
            screen.blit(ship['surf'], (x, 60))
            x += SHIP_W + 10

        # Displays "Game Over!" if no more lives left
        if num_of_lives <= 0:
            running = False
            screen_copy = screen.copy()
            screen_rect = screen.get_rect()
            
            if score > top_score:
                top_score = score
                top_score_rect = text_font.render('New Top Score: %s!' % str(top_score), 1, GREEN).get_rect()
                draw_text('New Top Score: %s!' % str(top_score), text_font, screen,
                          (screen_rect.centerx - top_score_rect.width / 2, 100))                
                pygame.display.update()
                pygame.time.wait(4000)

            game_over_rect = title_font.render('Game Over!', 1, GREEN).get_rect()
            draw_text('Game Over!', title_font, screen_copy,
                      (screen_rect.centerx - game_over_rect.width / 2,
                       screen_rect.centery - game_over_rect.height / 2))
            screen.blit(screen_copy, (0, 0))
            pygame.display.update()
            pygame.time.wait(4000)
                
        pygame.display.update()
        
    main()

top_score = 0
if __name__ == '__main__':
    main()
    
