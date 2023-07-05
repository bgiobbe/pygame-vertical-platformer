import pygame, sys, time
from pygame.locals import QUIT, KEYDOWN, KEYUP, K_LEFT, K_RIGHT, K_SPACE, K_d
from random import randint

 
pygame.init()
Vec = pygame.Vector2  # 2 for two dimensional
ScoreFont = pygame.font.SysFont('Verdana', 20)
BigFont = pygame.font.SysFont('Georgia', 60)
MediumFont = pygame.font.SysFont('Georgia', 36)

FPS = 60
HEIGHT = 450
WIDTH = 400

ACC = 0.5        # x
FRIC = -0.12     # x
GRAV = 0.5       # y
BIG_JUMP = -15   # y
SMALL_JUMP = -3  # y
# By experiment, these values yield a maximum jump width and height of just over 200.

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
BG = (0, 0, 64)
SCORE_COLOR = (123,255,0)

FramesPerSec = pygame.time.Clock()
 
displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vertical Platformer")

all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
coins = pygame.sprite.Group()



class Player(pygame.sprite.Sprite):
    size = (30, 30)
    color = (255, 255, 0)
    starting_pos = (10, 360)
    
    def __init__(self):
        super().__init__() 
        self.surf = pygame.Surface(Player.size)
        self.surf.fill(Player.color)
        self.rect = self.surf.get_rect()
        
        self.pos = Vec(Player.starting_pos) # position
        self.vel = Vec(0, 0)                # velocity
        self.acc = Vec(0, 0)                # acceleration
        self.jumping = False
        self.score = 0
    
    def move(self):
        self.acc = Vec(0, GRAV)
        
        # right- and left- arrow control
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_LEFT]:
            self.acc.x -= ACC
        if pressed_keys[K_RIGHT]:
            self.acc.x += ACC
        
        # laws of motion
        self.acc.x += self.vel.x * FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        
        # screen wrapping
        if self.pos.x > WIDTH: self.pos.x = 0
        if self.pos.x < 0:     self.pos.x = WIDTH
        
        # move to new position
        self.rect.midbottom = self.pos

    def jump(self):
        if not self.jumping:
            hits = pygame.sprite.spritecollide(self, platforms, False)
            if hits:  # touching a platform
                self.jumping = True
                self.vel.y = BIG_JUMP
                self.rect.bottom = hits[0].rect.top - 2
    
    def cancel_jump(self):
        if self.jumping and self.vel.y < SMALL_JUMP:
            self.vel.y = SMALL_JUMP
            
    def handle_collisions(self):
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits:         # touching a platform
            if self.vel.y > 0:   # falling     
                if self.pos.y < hits[0].rect.bottom:  # above platform
                    # score
                    if hits[0].point:
                        hits[0].point = False
                        self.score += 1
                    # land on platform
                    self.rect.bottom = hits[0].rect.top + 1
                    self.pos = Vec(self.rect.midbottom)
                    self.vel.y = 0
                    self.jumping = False
            ''' # too hard with moving platforms
            else:
                #print('DEBUG Hit something going up')
                self.vel.y = 0
                self.rect.top = hits[0].rect.bottom + 1
                self.pos = Vec(self.rect.midbottom)
            '''

    def scroll(self, delta):
        self.pos.y += delta
        
    def move_with_platform(self, speed):
        self.pos.x += speed
        self.rect.midbottom = self.pos


        
class Platform(pygame.sprite.Sprite):
    def __init__(self, floor=False, initial=False):
        super().__init__()
        if floor:
            self.surf = pygame.Surface((WIDTH, 20))
            self.surf.fill(RED)
            self.rect = self.surf.get_rect(midleft=(0, HEIGHT - 10))
            self.speed = 0
            self.moving = False
            self.point = False
        else:
            width = randint(50, 100)
            self.surf = pygame.Surface((width, 20))
            self.surf.fill(GREEN)
            x = randint(0, WIDTH-width)
            if initial:
                y = randint(0, HEIGHT-50)
            else:
                y = randint(-50, 0) 
            self.rect = self.surf.get_rect(midleft = (x, y))
            self.speed = randint(-1, 1)
            self.moving = True
            self.point = True

    def scroll(self, delta):
        self.rect.y += delta
        if self.rect.top >= HEIGHT:
            self.kill()
            
    # Move self at speed; if touching player, move player too
    def move(self):
        if self.moving and self.speed != 0:
            self.rect.move_ip(self.speed, 0)
            if self.rect.colliderect(player.rect):
                player.move_with_platform(self.speed)
            # screen wrapping
            if self.rect.left > WIDTH: self.rect.right = 0
            if self.rect.right < 0: self.rect.left = WIDTH
            


class Coin(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(self)
        self.image = pygame.image.load('Coin.png')
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        
    def update(self):
        if self.rect.colliderect(player.rect):
            player.score += 5
            self.kill()


# ----- Functions -----

def start_game():
    global player, all_sprites, platforms, score
    player = Player()
    all_sprites.add(player)
    floor = Platform(floor=True)  # first platform
    platforms.add(floor)
    all_sprites.add(floor)
    make_initial_platforms()

def make_initial_platforms():
    global platforms, all_sprites
    left_to_make = randint(5, 6)
    print(f'DEBUG making {left_to_make} initial platforms...')
    debug_count = 0
    while left_to_make > 0:
        p = Platform(initial=True)
        debug_count += 1
        if platform_is_ok(p, initial=True):
            platforms.add(p)
            all_sprites.add(p)
            left_to_make -= 1
    print(f'DEBUG ...finished making initial platforms; count={debug_count}')

# Move all sprites down
def scroll_down():
    delta = abs(player.vel.y)
    player.scroll(delta)
    for p in platforms:
        p.scroll(delta)        

# Random platform generation
def generate_platforms():
    tries = 0
    # if it takes more than 3 tries, give up to prevent infinite loop
    while len(platforms) < 7 and tries < 3:
        p = Platform()
        tries += 1
        if platform_is_ok(p):
            platforms.add(p)
            all_sprites.add(p)
            tries = 0

# Returns True if platform passes validation against group
def platform_is_ok(platform, initial=False):
    global platforms
    rect = platform.rect.inflate(0, 80)  # leave room for player on platform
    index = rect.collidelist([p.rect for p in platforms])
    if index != -1:
        return False
    
    if not initial:
        for entity in platforms:
            if (abs(platform.rect.top - entity.rect.bottom) < 50 and
                abs(platform.rect.bottom - entity.rect.top) < 50):
                return False
    return True

def game_over():
    global player
    for entity in all_sprites:
        entity.kill()
    time.sleep(1)
    displaysurface.fill(RED)
    msg = BigFont.render('Game Over', True, BLACK)
    displaysurface.blit(msg, (msg.get_rect(center=(WIDTH/2, HEIGHT*0.3))))
    score = MediumFont.render(f'Score {player.score}', True, BLACK)
    displaysurface.blit(score, (score.get_rect(center=(WIDTH/2, HEIGHT*0.5))))
    player = None
    pygame.display.update()
    time.sleep(2)
    start_game()
    


# --- Main code -------------------

start_game()

# Game loop               
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                player.jump()
        if event.type == KEYUP:
            if event.key == K_SPACE:
                player.cancel_jump()
            elif event.key == K_d: # d for debug
                print(f'Player acc {player.acc} vel {player.vel} pos {player.pos}')

    player.handle_collisions()

    if player.rect.top > HEIGHT:
        game_over()

    if player.rect.top <= HEIGHT / 3:
        scroll_down()
        generate_platforms()

    displaysurface.fill(BG)

    scoreboard = ScoreFont.render(str(player.score), True, SCORE_COLOR)
    displaysurface.blit(scoreboard, (WIDTH/2, 10))

    for entity in all_sprites:
        displaysurface.blit(entity.surf, entity.rect)
        entity.move()
 
    pygame.display.update()
    FramesPerSec.tick(FPS)
    
    