import pygame
import keyboard
import json

from wall_crasher_v1 import Wall_crasher

env = Wall_crasher()
env.reset()

pygame.init()
screen = pygame.display.set_mode((env._window_size, env._window_size))

running = True

lines = []
points = []
walls = []
mouse_pressed = False

x = env._car.position[0]
y = env._car.position[1]
w = env._car.size[0]
h = env._car.size[1]

while running:
    mouse_pressed = pygame.mouse.get_pressed()[0]

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if mouse_pressed:
        continue

    screen.fill("dark grey")

    # draw car
    pygame.draw.rect(screen, "blue", (x, y, w, h))

    pygame.draw.circle(screen, "red", pygame.mouse.get_pos(), 5)
    pygame.mouse.set_visible(0)

    if pygame.mouse.get_pressed()[0]:
        points.append(pygame.mouse.get_pos())

        if len(points) > 1:
            lines.append([points[-2][0], points[-2][1], points[-1][0], points[-1][1]])
    

    # draw all lines
    for line in lines:
        pygame.draw.line(screen, "black", line[:2], line[2:], 5)

    for wall in walls:
        for line in wall:
            pygame.draw.line(screen, "black", line[:2], line[2:], 5)

    # draw line from last point to mouse
    if len(points) > 0:
        pygame.draw.line(screen, "black", points[-1], pygame.mouse.get_pos(), 5)

    if keyboard.is_pressed("enter") or keyboard.is_pressed("space"):
        if len(lines) > 0:
            walls.append(lines)

        lines = []
        points = []

    if keyboard.is_pressed("backspace"):
        lines = []
        points = []

    pygame.display.flip()

pygame.quit()

print("Save? (y/n)")
save = input()
if save == "y" or save == "yes":
    with open('walls.txt', 'w') as file:
        json.dump(walls, file)