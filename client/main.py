import pygame
import sys
def background(color, image, position):
    canvas.fill(color)
    canvas.blit(image, dest = position)
def move(image, position, x ,y):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_s]:
        y -= 5
    if keys[pygame.K_w]:
        y += 5
    if keys[pygame.K_a]:
        x += 5
    if keys[pygame.K_d]:
        x -= 5
    return x, y


pygame.init()
color = (255, 255, 255)
x = 0
y = 0
position = (x, y)
canvas = pygame.display.set_mode((500, 500))

pygame.display.set_caption("My Board") 
image = pygame.image.load("..\\assets\\track.png")

exit = False
  
while not exit:
    background(color, image, position)
    x, y = move(image, position, x, y)
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT: 
            exit = True
    position = (x, y)
    pygame.display.update()
    pygame.time.Clock().tick(60)