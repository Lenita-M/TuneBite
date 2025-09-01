# import libraries #

import pygame
import sys 
import random
from pygame.math import Vector2

pygame.init()

# background music tracks
background_tracks = [
    'Sounds/bg1.mp3',
    'Sounds/bg2.mp3',
    'Sounds/bg3.mp3'
]

#Title and score fonts

title_font = pygame.font.Font(None, 60)
score_font = pygame.font.Font(None, 40)

#Colors
GREEN = (173, 205, 96)
DARK_GREEN = (43, 51, 24)

#Grid setup
cell_size = 25
number_of_cells = 20

# Margin around the grid
OFFSET = 75

# Food class #

class Food:
    def __init__(self, snake_body): #food should spawn in a free cell
        self.position = self.generate_random_pos(snake_body)

    def draw(self): #draw food on the screen
        food_rect = pygame.Rect(OFFSET + self.position.x * cell_size, OFFSET + self.position.y * cell_size, cell_size, cell_size)
        screen.blit(food_surface, food_rect)

    def generate_random_cell(self): #generate random position for food
        x = random.randint(0, number_of_cells - 1)
        y = random.randint(0, number_of_cells - 1)
        return Vector2(x, y)
    
    def generate_random_pos(self, snake_body): #ensure food does not spawn on the snake body
        position = self.generate_random_cell()
        while position in snake_body:
            position = self.generate_random_cell()
        return position

#Special food class #

class SpecialFood(Food):
    def __init__(self, snake_body):
        super().__init__(snake_body)
        self.timer = 100  # Special food lasts for 100 frames

    def update(self): #
        self.timer -= 1
        return self.timer <= 0  # Return True if timer runs out

    def draw(self):
        special_food_rect = pygame.Rect(OFFSET + self.position.x * cell_size, OFFSET + self.position.y * cell_size, cell_size, cell_size)
        screen.blit(special_food_surface, special_food_rect)


# Snake class #

class Snake: 
    def __init__(self): #snake starts with 3 segments
        self.body = [Vector2(6, 9), Vector2(5, 9), Vector2(4, 9)]
        self.direction = Vector2(1, 0)
        self.add_segment = False
        self.eat_sound = pygame.mixer.Sound('Sounds/eat.mp3')
        self.wall_hit = pygame.mixer.Sound('Sounds/wall.mp3')

        
    def draw(self): #Draw each segment of the snake
        for segment in self.body:
            segment_rect = pygame.Rect(OFFSET + segment.x * cell_size, OFFSET + segment.y * cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, DARK_GREEN, segment_rect, border_radius=10)

    def update(self): #Insert new segment at the beginning of the snake
        self.body.insert(0, self.body[0] + self.direction)
        if self.add_segment == True: #if snake eats, do not remove the last segment
            self.add_segment = False
        else: # 
            self.body = self.body[:-1] #otherwise, remove the last segment to simulate movement

    def reset(self): #reset snake to initial position and direction
        self.body = [Vector2(6, 9), Vector2(5, 9), Vector2(4, 9)]
        self.direction = Vector2(1, 0)

# Game class #

class Game:
    def __init__(self): #initialize game with snake, food and score
        self.snake = Snake()
        self.food = Food(self.snake.body)
        self.special_food = None
        self.state = "RUNNING"
        self.score = 0
        self.current_track = None
        self.play_music(random.choice(background_tracks))

    def play_music(self, track): #play background music
        if self.current_track != track:
            pygame.mixer.music.load(track)
            pygame.mixer.music.play(-1)
            self.current_track = track

    def draw (self): #draw snake and food
        self.snake.draw()
        self.food.draw()

        if self.special_food:
            self.special_food.draw()

    def update(self): #update game state
        if self.state == "RUNNING":
            self.snake.update()
            self.check_collision_food()
            self.check_collision_special_food()
            self.check_collision_walls()
            self.check_collision_body()

            # Spawn special food randomly
            if not self.special_food and random.randint(1, 200) == 1:  # ~0.5% chance per frame
                self.special_food = SpecialFood(self.snake.body)
            
            # Update special food timer
            if self.special_food:
                if self.special_food.update():
                    self.special_food = None

    def check_collision_food(self): #check if snake head collides with food
        if self.snake.body[0] == self.food.position: #Respawn normal food, grow snake, add score, play sound
            self.food.position = self.food.generate_random_pos(self.snake.body)
            self.snake.add_segment = True
            self.score += 1
            self.snake.eat_sound.play()

            # 20% chance to spawn special food
            if self.special_food is None and random.random() < 0.2:
                self.special_food = SpecialFood(self.snake.body)

    def check_collision_special_food(self): #check if snake head collides with special food
        if self.special_food and self.snake.body[0] == self.special_food.position:
            self.snake.add_segment = True
            self.score += 5  # Special food gives more points
            self.special_food = None  # Remove special food after eating

            # Change background music
            new_track = random.choice(background_tracks)
            self.play_music(new_track)


    def check_collision_walls(self): #check if snake head collides with walls
        if self.snake.body[0].x == number_of_cells or self.snake.body[0].x == -1:
            self.game_over()
        if self.snake.body[0].y == number_of_cells or self.snake.body[0].y == -1:
            self.game_over()
    
    def game_over(self): # Reset snake & food, reset score, stop game
       self.snake.reset()
       self.food.position = self.food.generate_random_pos(self.snake.body)
       self.state = "STOPPED"
       self.score = 0
       self.snake.wall_hit.play()

    def check_collision_body(self): #check if snake head collides with its body
        headless_body = self.snake.body[1:]
        if self.snake.body[0] in headless_body:
            self.game_over()
    
# Game setup #

#Create screen with border offset

screen = pygame.display.set_mode((2*OFFSET + cell_size*number_of_cells, 2*OFFSET + cell_size*number_of_cells))

pygame.display.set_caption("TuneBite")

clock = pygame.time.Clock()

game=Game()
food_surface = pygame.image.load('Graphics/food.png')
special_food_surface = pygame.image.load('Graphics/special_food.png')   

#Event for updating the snake position

SNAKE_UPDATE = pygame.USEREVENT
pygame.time.set_timer(SNAKE_UPDATE, 200)

# Main loop #

while True: #handle events
    for event in pygame.event.get():
        if event.type == SNAKE_UPDATE:
            game.update()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN: #Restart game on any key press
            if game.state == "STOPPED": 
                game.state = "RUNNING" 
            # Change snake direction based on arrow key pressed
            if event.key == pygame.K_UP and game.snake.direction.y != Vector2(0, 1).y:
                game.snake.direction = Vector2(0, -1)
            if event.key == pygame.K_DOWN and game.snake.direction.y != Vector2(0, -1).y:
                game.snake.direction = Vector2(0, 1)
            if event.key == pygame.K_LEFT and game.snake.direction.x != Vector2(1, 0).x:
                game.snake.direction = Vector2(-1, 0)
            if event.key == pygame.K_RIGHT and game.snake.direction.x != Vector2(-1, 0).x:
                game.snake.direction = Vector2(1, 0)
   

    # Drawing #

    screen.fill(GREEN)

    # Draw game border

    pygame.draw.rect(screen,DARK_GREEN, 
                     (OFFSET-5, OFFSET-5, cell_size*number_of_cells+10, cell_size*number_of_cells+10), 5)
    
    #Draw snake and food
    game.draw() 

    # Draw title and score
    title_surface = title_font.render("TuneBite", True, DARK_GREEN)
    score_surface = score_font.render(str(game.score), True, DARK_GREEN)
    screen.blit(title_surface, (OFFSET-5, 20))
    screen.blit(score_surface, (OFFSET-5 + cell_size*number_of_cells+10, 20))

    # Refresh screen
    pygame.display.update()
    clock.tick(60)




