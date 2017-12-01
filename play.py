#!/usr/bin/python
# coding=utf8

# 1 - Import library
import cStringIO
import pygame
import random
import math
from pygame.locals import *
from MyLibrary import *
from os import remove

# 2 - Initialize the game
pygame.init()
pygame.display.set_caption('捍卫荣誉')
width, height = 640, 480
screen = pygame.display.set_mode((width, height))
keys = [False, False, False, False]
playerpos = [130, 240]
acc = [0, 0]  # [0]是击中数，[1]是发射数
arrows = []  # 发射箭头列表，点击鼠标时向其中填充bullet列表
badtimer = 100
badtimer1 = 0
badguys = [[640, random.randint(40, 400)]]
healthvalue = 194  # 总血量
pygame.mixer.init()
# 创建精灵组
flame_group = pygame.sprite.Group()
# 初始化火焰精灵组
flame = MySprite()
flame.load("resources/images/flame.png", 64, 64, 4)
flame.position = 80, 80
flame_group.add(flame)
timer = pygame.time.Clock()

# 3 - Load images
start = pygame.image.load("resources/images/start.png")
grass = pygame.image.load("resources/images/bg2.png")
castle = pygame.image.load("resources/images/hq1.png")
player = pygame.image.load("resources/images/p1.1.png")
player1 = pygame.image.load("resources/images/p1.1.png")
player2 = pygame.image.load("resources/images/p1.2.png")
arrow = pygame.image.load("resources/images/bullet6.png")
badguyimg1 = pygame.image.load("resources/images/badguy1.1.png")
badguyimg2 = pygame.image.load("resources/images/badguy1.2.png")
badguyimg3 = pygame.image.load("resources/images/badguy1.3.png")
badguyimg4 = pygame.image.load("resources/images/badguy1.4.png")
badguyimgs = [badguyimg1, badguyimg2, badguyimg3, badguyimg4]
# badguyimg = badguyimg1
healthbar = pygame.image.load("resources/images/healthbar.png")
health = pygame.image.load("resources/images/health.png")
gameover = pygame.image.load("resources/images/gameover2.png")
youwin = pygame.image.load("resources/images/youwin.png")
# 3.1 - Load audio
begin = pygame.mixer.Sound("resources/audio/start.wav")
hit = pygame.mixer.Sound("resources/audio/explode.wav")
enemy = pygame.mixer.Sound("resources/audio/enemy.wav")
shoot = pygame.mixer.Sound("resources/audio/shoot.wav")
win = pygame.mixer.Sound("resources/audio/win.wav")
lost = pygame.mixer.Sound("resources/audio/lost.wav")
bgm = 'resources/audio/cowBGM.wav'
hit_castle = pygame.mixer.Sound("resources/audio/explode2.wav")
begin.set_volume(0.50)
hit.set_volume(0.07)
enemy.set_volume(0.20)
shoot.set_volume(0.07)
win.set_volume(0.25)
hit_castle.set_volume(0.18)
pygame.mixer.music.load(bgm)
pygame.mixer.music.play(-1, 0.0)
pygame.mixer.music.set_volume(0.25)

# 开局画面
running = 1
while running:
    screen.fill(0)
    screen.blit(start, (0, 0))
    # 提示按键开始
    font = pygame.font.Font(None, 30)
    text1 = font.render("Press [SPACE] to start", True, (255, 0, 0))
    screen.blit(text1, (230, 450))  # 调整显示文字位置
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == K_SPACE:
                begin.play()
                running = 0
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)
    pygame.display.flip()

# 按下确定键后的透明渐变效果
from PIL import Image


def addTransparency(img, factor):
    img = img.convert('RGBA')
    img_blender = Image.new('RGBA', img.size, (0, 0, 0, 0))
    img = Image.blend(img_blender, img, factor)
    return img


img = Image.open("resources/images/start.png")
tran = 1
while tran > 0.8:
    img = addTransparency(img, factor=tran)
    imgBuf = cStringIO.StringIO(img.tobytes())
    imgx = pygame.image.frombuffer(imgBuf.getvalue(), (640, 480), "RGBA")
    screen.blit(imgx, (0, 0))
    tran -= 0.001
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)
    pygame.display.flip()

# 4 - keep looping through
running = 1
exitcode = 0
n = 0
ticksnow = pygame.time.get_ticks()
gametime = ticksnow + 90000
spacetime = []
boompos = []
while running:
    timer.tick(60)
    ticks = pygame.time.get_ticks()
    badtimer -= 1
    # 5 - clear the screen before drawing it again
    screen.fill(0)
    # 6 - draw the screen elements
    for x in range(width / grass.get_width() + 1):
        for y in range(height / grass.get_height() + 1):
            screen.blit(grass, (x * 100, y * 100))
    # screen.blit(grass, (0,0))
    screen.blit(castle, (0, 30))
    screen.blit(castle, (0, 135))
    screen.blit(castle, (0, 240))
    screen.blit(castle, (0, 345))
    # 6.1 - Set player position and rotation
    position = pygame.mouse.get_pos()
    angle = math.atan2(position[1] - (playerpos[1] + player.get_height() / 2),
                       position[0] - (playerpos[0] + player.get_width() / 2))
    # print angle
    # playerrot = pygame.transform.rotate(player, 360-angle*57.29)
    playerrot = pygame.transform.rotate(
        player, 360 - 180 * angle / math.pi)  # 180*angle/math.pi为偏转角度
    playerpos1 = (playerpos[0] - playerrot.get_rect().width / 2,
                  playerpos[1] - playerrot.get_rect().height / 2)
    screen.blit(playerrot, playerpos1)
    # 6.2 - Draw arrows
    for bullet in arrows:  # arrow中的bullet列表是在按鼠标发射时追加的，bullet[0]是atan(y,x)
        # print bullet
        index = 0
        velx = math.cos(bullet[0]) * 10  # 乘数调整子弹横向速度
        # print math.cos(bullet[0])
        vely = math.sin(bullet[0]) * 10  # 乘数调整子弹竖向速度
        # print math.sin(bullet[0])
        bullet[1] += velx
        bullet[2] += vely
        if bullet[1] < -64 or bullet[1] > 640 or bullet[2] < -64 or bullet[2] > 480:
            arrows.pop(index)
        index += 1
        for projectile in arrows:
            arrow1 = pygame.transform.rotate(
                arrow, 360 - projectile[0] * 57.29)
            screen.blit(arrow1, (projectile[1], projectile[2]))
    # 6.3 - Draw badgers
    if badtimer == 0:
        badguys.append([640, random.randint(50, 430)])
        badtimer = 100 - (badtimer1 * 2)
        if badtimer1 >= 35:
            badtimer1 = 35
        else:
            badtimer1 += 5
    index = 0
    for badguy in badguys:
        # 獾奔跑动画
        n = n + 1
        if n > (len(badguyimgs)) * 10 - 1:
            n = 0
        screen.blit(badguyimgs[int(n / 10)], badguy)
        if badguy[0] < -64:
            badguys.pop(index)
        badguy[0] -= 1  # 调整獾的移动速度
        # 6.3.1 - Attack castle
        badrect = pygame.Rect(badguyimg1.get_rect())
        badrect.top = badguy[1]
        badrect.left = badguy[0]
        if badrect.left < 64:
            # hit.play()
            hit_castle.play()
            healthvalue -= random.randint(5, 20)  # 敌人碰撞城堡掉血
            badguys.pop(index)
            spacetime = [badguy[0], badguy[1], ticks]
            boompos.append(spacetime)
        # hit player
        playerrect = pygame.Rect(player.get_rect())
        playerrect.left = playerpos[0] - 32  # 增减一些值使触碰画面看上去更贴合
        playerrect.top = playerpos[1] - 10  # 增减一些值使触碰画面看上去更贴合
        # print playerrect
        if badrect.colliderect(playerrect):
            hit.play()
            healthvalue -= random.randint(3, 12)  # 玩家碰撞敌人掉血
            badguys.pop(index)
            spacetime = [badguy[0], badguy[1], ticks]
            boompos.append(spacetime)
        # 6.3.2 - Check for collisions
        index1 = 0
        for bullet in arrows:
            bullrect = pygame.Rect(arrow.get_rect())
            bullrect.left = bullet[1]
            bullrect.top = bullet[2]
            if badrect.colliderect(bullrect):
                enemy.play()
                acc[0] += 1
                badguys.pop(index)
                arrows.pop(index1)
                spacetime = [badguy[0], badguy[1], ticks]
                boompos.append(spacetime)
            index1 += 1
        # 6.3.3 - Next bad guy
        index += 1
        #flame
        bindex = 0
        for boom in boompos:
            flame.position = (boom[0], boom[1] - 20)
            flame_group.update(ticks)
            flame_group.draw(screen)
            if (ticks - boom[2]) > 1000:
                boompos.pop(bindex)
            bindex += 1
    # 6.4 - Draw clock
    font = pygame.font.Font(None, 24)
    # 此处为漏洞，当点击窗口标题时，时间依然在流逝，但是游戏却暂停了，导致点击标题即可获胜
    survivedtext = font.render(str((gametime - pygame.time.get_ticks()) / 60000) + ":" + str(
        (gametime - pygame.time.get_ticks()) / 1000 % 60).zfill(2), True, (0, 0, 0))
    textRect = survivedtext.get_rect()
    textRect.topright = [635, 5]
    screen.blit(survivedtext, textRect)
    # 6.5 - Draw health bar
    screen.blit(healthbar, (5, 5))
    for health1 in range(healthvalue):
        screen.blit(health, (health1 + 8, 8))
    # 在健康值上方显示文字
    hfont = pygame.font.Font(None, 20)
    htext = hfont.render("Health", True, (255, 0, 0))
    screen.blit(htext, (50, 8))  # 调整显示文字位置，覆盖在健康值上方
    # 7 - update the screen
    pygame.display.flip()
    # 8 - loop through the events
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == K_w:
                keys[0] = True
            elif event.key == K_a:
                keys[1] = True
            elif event.key == K_s:
                keys[2] = True
            elif event.key == K_d:
                keys[3] = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                keys[0] = False
            elif event.key == pygame.K_a:
                keys[1] = False
            elif event.key == pygame.K_s:
                keys[2] = False
            elif event.key == pygame.K_d:
                keys[3] = False

        # check if the event is the X button
        if event.type == pygame.QUIT:
            # if it is quit the game
            pygame.quit()
            exit(0)
        # 检测是否是鼠标左键发射
        if event.type == pygame.MOUSEBUTTONDOWN:
            pressed_array = pygame.mouse.get_pressed()
            for index in range(len(pressed_array)):
                if pressed_array[index]:
                    if index == 0:
                        shoot.play()
                        player = player2
                        position = pygame.mouse.get_pos()
                        acc[1] += 1
                        arrows.append([math.atan2(position[1] - (playerpos1[1] + 32), position[0] - (
                            playerpos1[0] + 26)), playerpos1[0] + 32, playerpos1[1] + 32])
                    #     print('Pressed LEFT Button!')
                    # elif index == 1:
                    #     print('The mouse wheel Pressed!')
                    # elif index == 2:
                    #     print('Pressed RIGHT Button!')
        if event.type == pygame.MOUSEBUTTONUP:
            player = player1
    # 9 - Move player
    if keys[0]:
        if not playerpos[1] < 0:
            playerpos[1] -= 3
    elif keys[2]:
        if not playerpos[1] > height:
            playerpos[1] += 3
    if keys[1]:
        if not playerpos[0] < 100:
            playerpos[0] -= 3
    elif keys[3]:
        if not playerpos[0] > width:
            playerpos[0] += 3

    # 10 - Win/Lose check
    if pygame.time.get_ticks() >= gametime:
        running = 0
        exitcode = 1
    if healthvalue <= 0:
        running = 0
        exitcode = 0
    if acc[1] != 0:
        accuracy = acc[0] * 1.0 / acc[1] * 100
    else:
        accuracy = 0
# 11 - Win/lose display
if exitcode == 0:
    pygame.font.init()
    font = pygame.font.Font(None, 24)
    text = font.render("Accuracy: " + str(accuracy) + "%", True, (255, 0, 0))
    textRect = text.get_rect()
    textRect.centerx = screen.get_rect().centerx
    textRect.centery = screen.get_rect().centery + 24
    pygame.mixer.music.set_volume(0)
    lost.play()
    screen.blit(gameover, (0, 0))
    screen.blit(text, textRect)
else:
    pygame.font.init()
    font = pygame.font.Font(None, 24)
    text = font.render("Accuracy: " + str(accuracy) + "%", True, (0, 255, 0))
    textRect = text.get_rect()
    textRect.centerx = screen.get_rect().centerx
    textRect.centery = screen.get_rect().centery + 24
    screen.blit(youwin, (0, 0))
    pygame.mixer.music.set_volume(0)
    win.play()
    screen.blit(text, textRect)
ticksstart = pygame.time.get_ticks()  # 作为延时开启背景音乐
while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)
    ticksend = pygame.time.get_ticks()
    ticksdiff = ticksend - ticksstart  # 计算延时
    if ticksdiff == 3500:  # 开启背景音乐
        pygame.mixer.music.set_volume(0.25)
    pygame.display.flip()
