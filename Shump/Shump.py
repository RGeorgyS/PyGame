import pygame
import random
import os
from os import  path

img_dir = path.join(path.dirname(__file__), 'images')

snd_dir = path.join(path.dirname(__file__), 'sound_effects')

sc_width = 480
sc_height = 600
fps = 60

white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

power_time_const = 5000

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((sc_width, sc_height))
pygame.display.set_caption("Shump")
clock = pygame.time.Clock()

bg = pygame.image.load(path.join(img_dir, 'starfield.png')).convert()
bg_rect = bg.get_rect()
player_img = pygame.image.load(path.join(img_dir, "playerShip1_orange2.png")).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(black)
bullet_img = pygame.image.load(path.join(img_dir, "laserRed162.png")).convert()
explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(black)
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)
    filename = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename))
    img.set_colorkey(black)
    explosion_anim['player'].append(img)
powerup_images = {}
powerup_images['shield'] = pygame.image.load(path.join(img_dir, 'shield_gold.png')).convert()
powerup_images['gun'] = pygame.image.load(path.join(img_dir, 'bolt_gold.png')).convert()

shoot_sound = pygame.mixer.Sound(path.join(snd_dir, 'pew.wav'))
powerup_shield_sound = pygame.mixer.Sound(path.join(snd_dir, 'SFX_Powerup_01.wav'))
powerup_gun_sound = pygame.mixer.Sound(path.join(snd_dir, 'SFX_Powerup_03.wav'))
expl_sounds = []
for snd in ['expl3.wav', 'expl6.wav']:
    expl_sounds.append(pygame.mixer.Sound(path.join(snd_dir, snd)))
pygame.mixer.music.load(path.join(snd_dir, 'spaceship.wav'))
pygame.mixer.music.set_volume(0.4)


meteor_list = ['Вирус.png', 'meteorBrown_med12.png']
meteor_img = [pygame.image.load(path.join(img_dir, img)).convert() for img in meteor_list]

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

class NPC(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((30, 40))
        self.image_orig = random.choice(meteor_img)
        self.image_orig.set_colorkey(black)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.85 / 2)
        #pygame.draw.circle(self.image, red, self.rect.center, self.radius)
        self.rect.x = random.randrange(-self.rect.width * 2, -self.rect.width)
        self.rect.y = random.randrange((sc_height // 2) - self.rect.height)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > sc_height + 10 or self.rect.left < -25 or self.rect.right > sc_width + 20:
            self.rect.x = random.randrange(sc_width - self.rect.width)
            self.rect.y = random.randrange (-100, -40)
            self.speedy = random.randrange(1,8)
            self.speedx = random.randrange(-3, 3)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((50, 40))
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.radius = 20
        #pygame.draw.circle(self.image, red, self.rect.center, self.radius)
        self.rect.centerx = sc_width / 2
        self.rect.bottom = sc_height - 10
        self.shoot_delay = 150
        self.last_update = pygame.time.get_ticks()
        self.speedx = 0
        self.hp = 100
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_time = pygame.time.get_ticks()

    def update(self):
        self.speedx = 0
        now = pygame.time.get_ticks()

        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx += -8
        if keystate[pygame.K_RIGHT]:
            self.speedx += 8
        if keystate[pygame.K_SPACE]:
            self.shoot()
        if self.rect.right > sc_width:
            self.rect.right = sc_width
        if self.rect.left < 0:
            self.rect.left = 0

        self.rect.x += self.speedx

        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = sc_width / 2
            self.rect.bottom = sc_height - 10

        if self.power >= 2 and pygame.time.get_ticks() - self.power_time > power_time_const:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()


    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.shoot_delay:
            self.last_update = now
            if self.power == 1:
                shoot_sound.play()
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)

            if self.power >= 2:
                 bullet1 = Bullet(self.rect.left, self.rect.centery)
                 bullet2 = Bullet(self.rect.right, self.rect.centery)
                 all_sprites.add(bullet1)
                 all_sprites.add(bullet2)
                 bullets.add(bullet1)
                 bullets.add(bullet2)
                 shoot_sound.play()

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (sc_width / 2, sc_height + 200 )

    def powerup(self):
        self.power +=1
        self.power_time = pygame.time.get_ticks()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y) :
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((10, 20))
        self.image = bullet_img
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 2

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > sc_height:
            self.kill()

font_name = pygame.font.match_font('arial')

def draw_text(surf, text, size, x, y, colour):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, colour)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

bar_lenght = 100
bar_height = 20

def draw_hp_bar(surf, x, y, hp):
    if hp < 0:
        hp = 0
    '''bar_lenght = 100
    bar_height = 20'''
    fill = (hp / 100) * bar_lenght
    outline_rect = pygame.Rect(x, y, bar_lenght, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    pygame.draw.rect(surf, red, fill_rect)
    pygame.draw.rect(surf, white, outline_rect, 2)

def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)

def new_npc():
    npc = NPC()
    all_sprites.add(npc)
    npcs.add(npc)

def show_go_screen():
    screen.blit(bg, bg_rect)
    draw_text(screen, "SHUMP", 64, sc_width / 2, sc_height / 4, white)
    draw_text(screen, "Arrow keys move, Space to fire", 22, sc_width / 2, sc_height / 2, white)
    draw_text(screen, "Press a key to begin", 18, sc_width / 2, sc_height * 3 / 4, white)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False

powerups = pygame.sprite.Group()

all_sprites = pygame.sprite.Group()
npcs = pygame.sprite.Group()
player = Player()
bullets = pygame.sprite.Group()
all_sprites.add(player)
for i in range(8):
    new_npc()
score = 0

pygame.mixer.music.play(loops=-1)

run = True
game_over = True
while run:
    if game_over:
        show_go_screen()
        game_over = False
        all_sprites = pygame.sprite.Group()
        nps = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        for i in range(8):
            new_npc()
        score = 0
    clock.tick(fps)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    all_sprites.update()

    hits = pygame.sprite.groupcollide(npcs, bullets, True, True)
    for hit in hits:
        score += int(10 - ((hit.radius * 2 / 0.85) // 40))
        random.choice(expl_sounds).play()
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        if random.random() > 0.9:
            pow = Pow(hit.rect.center)
            all_sprites.add(pow)
            powerups.add(pow)
        new_npc()

    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        if hit.type == 'shield':
            powerup_shield_sound.play()
            player.hp += random.randrange(10, 30)
            if player.hp >= 100:
                player.hp = 100
        if hit.type == 'gun':
            powerup_gun_sound.play()
            player.powerup()


    hits = pygame.sprite.spritecollide(player, npcs, True, pygame.sprite.collide_circle)
    for hit in hits:
        player.hp -= hit.radius // 2
        if player.hp < 0:
            player.hp = 0
        random.choice(expl_sounds).play()
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        new_npc()
        if player.hp == 0:
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            player.hp = 100

    if player.lives == 0 and not death_explosion.alive():
        game_over = True


    screen.fill(black)
    screen.blit(bg, bg_rect)
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, sc_width / 2, 10, white)
    draw_hp_bar(screen, 5, 5, player.hp)
    draw_lives(screen, sc_width - 100, 5, player.lives, player_mini_img)
    draw_text(screen, str(player.hp), 10, 5 + bar_lenght / 2,bar_height / 2, white)

    pygame.display.update()
