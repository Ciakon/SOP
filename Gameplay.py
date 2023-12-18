from wall_crasher_v1 import Wall_crasher
import pygame
import keyboard

env = Wall_crasher(True, 60)
env.reset()

running = True

turnRight = True
framecount = 0

while running:
    framecount += 1
    
    
    if keyboard.is_pressed("a") or keyboard.is_pressed("left arrow"):
        state = env.step(0)

    elif keyboard.is_pressed("d") or keyboard.is_pressed("right arrow"):
        state = env.step(1)

    else:
        if turnRight:
            state = env.step(1)
            turnRight = False
        else:
            state = env.step(0)
            turnRight = True

    crash, timeout = state[2], state[3]

    if framecount % 30 == 1:
        print(state)

    if (crash or timeout):
        env.reset()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
