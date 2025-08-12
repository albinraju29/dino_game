import pygame
import random
import sys
import os

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Colorful Dino Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (83, 83, 83)
DINO_COLOR = (60, 60, 60)
CACTUS_COLOR = (80, 180, 80)
BIRD_COLOR = (200, 100, 100)
GROUND_COLOR = (240, 240, 240)
SKY_COLOR = (235, 245, 255)
CLOUD_COLOR = (245, 245, 245)

# Game variables
clock = pygame.time.Clock()
FPS = 60
game_speed = 8
score = 0
high_score = 0
font = pygame.font.SysFont('Arial', 20)
game_active = False
game_started = False

# Load high score
try:
    with open("highscore.txt", "r") as f:
        high_score = int(f.read())
except:
    high_score = 0

class Dino:
    def __init__(self):
        self.x = 50
        self.y = 225
        self.jump_vel = 0
        self.is_jumping = False
        self.width = 44
        self.height = 47
        self.ducking = False
        self.run_frame = 0
        self.run_animation_count = 0
        self.color = DINO_COLOR
        
    def jump(self):
        if not self.is_jumping and not self.ducking:
            self.jump_vel = -12
            self.is_jumping = True
    
    def duck(self):
        if not self.is_jumping:
            self.ducking = True
            self.height = 24
            self.y = 248
    
    def stand(self):
        self.ducking = False
        self.height = 47
        self.y = 225
    
    def update(self):
        # Gravity
        self.y += self.jump_vel
        self.jump_vel += 0.6
        
        # Ground collision
        if self.y >= 225:
            self.y = 225
            self.is_jumping = False
        
        # Animation
        if not self.ducking:
            self.run_animation_count += 0.1
            if self.run_animation_count >= 2:
                self.run_animation_count = 0
            self.run_frame = int(self.run_animation_count)
    
    def draw(self):
        # Draw dino body
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
        # Draw legs (animation)
        if not self.ducking:
            if self.run_frame == 0:
                pygame.draw.rect(screen, self.color, (self.x - 10, self.y + 35, 10, 15))
                pygame.draw.rect(screen, self.color, (self.x + 10, self.y + 40, 10, 10))
            else:
                pygame.draw.rect(screen, self.color, (self.x - 10, self.y + 40, 10, 10))
                pygame.draw.rect(screen, self.color, (self.x + 10, self.y + 35, 10, 15))
        else:
            # Ducking position
            pygame.draw.rect(screen, self.color, (self.x, self.y + 10, 59, self.height))
        
        # Draw eye
        eye_y = self.y + 10 if not self.ducking else self.y + 5
        pygame.draw.rect(screen, BLACK, (self.x + 30, eye_y, 8, 8))
    
    def get_rect(self):
        if self.ducking:
            return pygame.Rect(self.x, self.y, 59, self.height)
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Cactus:
    def __init__(self):
        self.type = random.choice(["small", "small", "small", "large", "multiple"])
        if self.type == "small":
            self.width = 17
            self.height = 35
            self.y = 235
        elif self.type == "large":
            self.width = 25
            self.height = 50
            self.y = 220
        else:  # multiple
            self.width = 50
            self.height = 35
            self.y = 235
        
        self.x = WIDTH
        self.color = CACTUS_COLOR
    
    def update(self):
        self.x -= game_speed
    
    def draw(self):
        if self.type == "small":
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        elif self.type == "large":
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        else:  # multiple
            pygame.draw.rect(screen, self.color, (self.x, self.y, 17, 35))
            pygame.draw.rect(screen, self.color, (self.x + 20, self.y, 17, 35))
            pygame.draw.rect(screen, self.color, (self.x + 33, self.y, 17, 35))
    
    def collide(self, dino):
        dino_rect = dino.get_rect()
        if self.type == "multiple":
            # Check collision with each part of multiple cactus
            part1 = pygame.Rect(self.x, self.y, 17, 35)
            part2 = pygame.Rect(self.x + 20, self.y, 17, 35)
            part3 = pygame.Rect(self.x + 33, self.y, 17, 35)
            return (dino_rect.colliderect(part1) or 
                    dino_rect.colliderect(part2) or 
                    dino_rect.colliderect(part3))
        else:
            obstacle_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            return dino_rect.colliderect(obstacle_rect)

class Bird:
    def __init__(self):
        self.x = WIDTH
        self.y = random.choice([220, 240, 210])
        self.width = 46
        self.height = 30
        self.animation_count = 0
        self.wing_position = 0  # 0 = up, 1 = down
        self.color = BIRD_COLOR
    
    def update(self):
        self.x -= game_speed * 1.2  # Birds are faster
        self.animation_count += 0.1
        if self.animation_count >= 1:
            self.animation_count = 0
            self.wing_position = 1 if self.wing_position == 0 else 0
    
    def draw(self):
        # Body
        pygame.draw.ellipse(screen, self.color, (self.x, self.y, self.width, self.height))
        # Head
        pygame.draw.circle(screen, self.color, (self.x + 40, self.y + 10), 10)
        # Eye
        pygame.draw.circle(screen, BLACK, (self.x + 45, self.y + 8), 2)
        # Beak
        pygame.draw.polygon(screen, (240, 200, 0), [
            (self.x + 50, self.y + 10),
            (self.x + 60, self.y + 10),
            (self.x + 50, self.y + 15)
        ])
        
        # Wings
        if self.wing_position == 0:
            pygame.draw.ellipse(screen, self.color, (self.x + 10, self.y - 10, 30, 15))
        else:
            pygame.draw.ellipse(screen, self.color, (self.x + 10, self.y + self.height - 5, 30, 15))
    
    def collide(self, dino):
        dino_rect = dino.get_rect()
        bird_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return dino_rect.colliderect(bird_rect)

class Cloud:
    def __init__(self):
        self.x = WIDTH
        self.y = random.randint(50, 100)
        self.width = random.randint(40, 70)
        self.height = random.randint(15, 25)
        self.speed = random.randint(1, 3)
    
    def update(self):
        self.x -= self.speed
    
    def draw(self):
        pygame.draw.ellipse(screen, CLOUD_COLOR, (self.x, self.y, self.width, self.height))

def draw_ground():
    pygame.draw.rect(screen, GROUND_COLOR, (0, 270, WIDTH, 30))
    # Draw ground lines
    line_x = 0
    while line_x < WIDTH:
        pygame.draw.line(screen, GRAY, (line_x, 280), (line_x + 20, 280), 2)
        line_x += 30

def draw_score():
    score_text = font.render(f"HI {high_score:05d} {score:05d}", True, GRAY)
    screen.blit(score_text, (WIDTH - 180, 20))

def draw_game_over():
    game_over_text = font.render("GAME OVER", True, GRAY)
    screen.blit(game_over_text, (WIDTH//2 - 50, HEIGHT//2 - 50))
    
    restart_text = font.render("PRESS R TO RESTART", True, GRAY)
    screen.blit(restart_text, (WIDTH//2 - 80, HEIGHT//2 + 20))

def draw_start_screen():
    title_text = font.render("PRESS SPACE TO START", True, GRAY)
    screen.blit(title_text, (WIDTH//2 - 100, HEIGHT//2))
    
    controls_text = font.render("SPACE: JUMP | DOWN: DUCK | Q: QUIT", True, GRAY)
    screen.blit(controls_text, (WIDTH//2 - 150, HEIGHT//2 + 40))

def reset_game():
    global game_speed, score, game_active
    game_speed = 8
    score = 0
    game_active = True
    return Dino(), [], [], 0

def main():
    global game_speed, score, high_score, game_active, game_started
    
    dino = Dino()
    obstacles = []
    clouds = []
    obstacle_timer = 0
    
    # Main game loop
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_active:
                        dino.jump()
                    elif game_started:
                        # Restart game
                        dino, obstacles, clouds, obstacle_timer = reset_game()
                    else:
                        game_started = True
                        game_active = True
                if event.key == pygame.K_DOWN:
                    if game_active and not dino.is_jumping:
                        dino.duck()
                if event.key == pygame.K_r and not game_active and game_started:
                    dino, obstacles, clouds, obstacle_timer = reset_game()
                if event.key == pygame.K_q:
                    running = False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN and dino.ducking:
                    dino.stand()
        
        # Background
        screen.fill(SKY_COLOR)
        
        # Draw ground
        draw_ground()
        
        # Generate clouds
        if random.random() < 0.01 and len(clouds) < 3:
            clouds.append(Cloud())
        
        # Update and draw clouds
        for cloud in clouds[:]:
            cloud.update()
            cloud.draw()
            if cloud.x + cloud.width < 0:
                clouds.remove(cloud)
        
        if game_active:
            # Generate obstacles
            obstacle_timer += 1
            if obstacle_timer > random.randint(40, 100):
                if score > 100 and random.random() < 0.3:  # 30% chance for bird after score 100
                    obstacles.append(Bird())
                else:
                    obstacles.append(Cactus())
                obstacle_timer = 0
            
            # Update dino
            dino.update()
            
            # Update obstacles
            for obstacle in obstacles[:]:
                obstacle.update()
                if obstacle.x + obstacle.width < 0:
                    obstacles.remove(obstacle)
                    score += 1
                if obstacle.collide(dino):
                    game_active = False
                    if score > high_score:
                        high_score = score
                        with open("highscore.txt", "w") as f:
                            f.write(str(high_score))
            
            # Increase game speed over time
            if score % 100 == 0 and score > 0:
                game_speed += 0.25
        
        # Draw everything
        for cloud in clouds:
            cloud.draw()
        
        dino.draw()
        
        for obstacle in obstacles:
            obstacle.draw()
        
        draw_score()
        
        if not game_started:
            draw_start_screen()
        elif not game_active:
            draw_game_over()
        
        pygame.display.update()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()