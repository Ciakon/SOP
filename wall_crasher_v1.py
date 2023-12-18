import pygame
import math
import json

class Light:
    def __init__(self, car_center, angle, range, center_length):
        self.angle = angle;
        self.range = range
        self.center_length = center_length # length from car center to light's start position
        self.car_center = car_center
        self.collision_point = None
        self.collision_distance = 0
        
        self.update()

    def update(self):
        x = self.car_center[0] + math.cos(self.angle) * self.center_length
        y = self.car_center[1] - math.sin(self.angle) * self.center_length
        self.point = [x, y]

        x2 = x + math.cos(self.angle) * self.range
        y2 = y - math.sin(self.angle) * self.range
        self.line = [x, y, x2, y2]

    def draw(self, canvas):
        pygame.draw.line(canvas, "yellow", self.line[:2], self.line[2:])
    

class Car:
    def __init__(self, x, y, lightrange, render = False):
        self.size = [30, 18]
        self.position = [x, y] # position is in center of the car
        self.angle = 0 # angle in radians
        self.turnSpeed = 0.1
        self.speed = 3
        self.car_image = None
        self.collision_distance = 5

        if (render):
            self.car_image = pygame.Surface(self.size)
            self.car_image.fill("blue")
            self.car_image.set_colorkey ("white")

        # create lights
        self.lights = [
            Light(
                self.position, 
                math.atan(self.size[1] / self.size[0]), 
                lightrange, 
                math.sqrt(self.size[0]**2 + self.size[1] ** 2) / 2),

            Light(
                self.position, 
                -math.atan(self.size[1] / self.size[0]), 
                lightrange, 
                math.sqrt(self.size[0]**2 + self.size[1] ** 2) / 2)        
        ]
    
    def move(self, turnspeed):
        self.angle += turnspeed
        
        x_movement = math.cos(self.angle) * self.speed
        y_movement = - math.sin(self.angle) * self.speed

        self.position[0] += x_movement
        self.position[1] += y_movement

        for light in self.lights:
            light.angle += turnspeed
            light.update()
    
    def draw(self, canvas):
        for light in self.lights:
            light.draw(canvas)
        
        degrees = self.angle * 180/math.pi
        rotated_car_image = pygame.transform.rotate(self.car_image, degrees)

        rotated_car_rect = rotated_car_image.get_rect(
            center = [self.position[0], self.position[1]]
        )
        canvas.blit(rotated_car_image, rotated_car_rect)

class Wall:
    def __init__(self, lines):
        self.lines = lines

    def draw(self, canvas):
        for line in self.lines:
            pygame.draw.line(canvas, "black", line[:2], line[2:], 3)


class Wall_crasher():
    def __init__(self, render = False, fps = 60, car_position = [50, 50], wall_filename = "walls.txt", timeout_time = 500):
        self._window_size = 500
        self._light_range = 100
        self.render = render
        self._fps = fps
        self._reward = None
        self._crashed = False
        self._timeout = False
        self._timer = None
        self._timeout_time = timeout_time
        self._car = None
        self._car_start_position = car_position
        self._wall_filename = wall_filename

        # add walls
        walls = []
        self._walls = []

        with open(self._wall_filename) as file:
            walls = json.load(file)

        for lines in walls:
            self._walls.append(Wall(lines))

        # each light can measure distance from 0 to light_range
        self.observation_space = [
            [0, 0],
            [self._light_range, self._light_range]
        ]

        self.action_space = [0, 1]

        # used when rendering
        self._window = None

    # there are 2 actions: "Left", "Right"
    def action_to_turnspeed(self, action):
        if (action == 1):
            return -self._car.turnSpeed
        elif (action == 0):
            return self._car.turnSpeed
    
    def _get_observation(self):
        return [light.collision_distance for light in self._car.lights]
    
    def reset(self):
        self._car = Car(self._car_start_position[0], self._car_start_position[1], self._light_range, self.render)
        self._crashed = False
        self._timer = self._timeout_time
        self._timeout = False

        observation = self._get_observation()
        self._reward = 0

        if self.render:
            self.render_frame()
    
        return [observation, self._reward, self._crashed, self._timeout]
    
    def step(self, action):

        if (self._crashed):
            raise Exception("car has crashed, reset environment")
        
        if (self._timeout):
            raise Exception("timeout, reset environment")
        
        turnspeed = self.action_to_turnspeed(action)
        self._car.move(turnspeed)

        self._calculate_collision()

        self._reward = 0
        observation = self._get_observation()

        self._timer -= 1

        if (self._timer <= 0):
            self._timeout = True

        if (self._crashed):
            self._reward = -1

        if self.render:
            self.render_frame()

        state = [observation, self._reward, self._crashed, self._timeout]
        return state
    
    def _calculate_collision(self):

        for light in self._car.lights:
            points_seen = []
            light.collision_point = None
            light.collision_distance = light.range # default is max

            for wall in self._walls:
                for wall_line in wall.lines:

                    collision_point = self._line_collision(light.line, wall_line)


                    if collision_point is None:
                        continue

                    if (self._point_on_line(collision_point, light.line) and self._point_on_line(collision_point, wall_line)):
                        points_seen.append(collision_point)

            if len(points_seen) == 0:
                continue

            # save closest point, if light overlaps multiple walls
            closest_point = points_seen[0]

            if len(points_seen) > 1:
                for point in points_seen:
                    if ( math.dist(point, light.point) < math.dist(closest_point, light.point) ):
                        closest_point = point

            light.collision_point = closest_point

            collision_distance = math.dist(closest_point, light.point)
            light.collision_distance = collision_distance

            if (collision_distance <= self._car.collision_distance):
                self._crashed = True
                    

    def render_frame(self):

        # Render setup
        if (self._window is None):
            pygame.init()
            pygame.display.init()
            self._window = pygame.display.set_mode((self._window_size, self._window_size))

            self._window.set_colorkey("dark gray")
        
            self.clock = pygame.time.Clock()
        

        canvas = pygame.Surface((self._window_size, self._window_size))
        canvas.fill("dark gray")        
        
        self._car.draw(canvas)

        for wall in self._walls:
            wall.draw(canvas)

        for light in self._car.lights:
            if (light.collision_point is None): 
                continue

            pygame.draw.circle(canvas, "red", light.collision_point, 2)

        self._window.blit(canvas, canvas.get_rect())
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()

        self.clock.tick(self._fps)

    def close(self):
        pygame.quit()
        self._window = None

    def _line_collision(self, line1, line2):
        x1, y1, x2, y2 = line1
        x3, y3, x4, y4 = line2

        a1 = (y1 - y2) / (x1 - x2)
        b1 = y1 - a1 * x1

        #paralel vertical lines
        if (x1 - x2) == 0 and (x3 - x4) == 0:
            return
        
        #vertical lines
        if (x1 - x2) == 0:
            a2 = (y3 - y4) / (x3 - x4)
            b2 = y3 - a2 * x3
            y = a2 * x1 + b2
            return (x1, y)

        if (x3 - x4) == 0:
            a1 = (y1 - y2) / (x1 - x2)
            b1 = y1 - a1 * x1
            y = a1 * x3 + b1
            return (x3, y)

        a1 = (y1 - y2) / (x1 - x2)
        b1 = y1 - a1 * x1

        a2 = (y3 - y4) / (x3 - x4)
        b2 = y3 - a2 * x3

        #parallel lines
        if (a2-a1) == 0:
            return

        x = (b1-b2)/(a2-a1)
        y = a1 * x + b1

        return (x, y)

    def _point_on_line(self, point, line):
        px, py = point
        x1, y1, x2, y2 = line

        if (
            (px >= x1 and px <= x2 or
            px <= x1 and px >= x2)
            and
            (py >= y1 and py <= y2 or
            py <= y1 and py >= y2)
        ):
            return True