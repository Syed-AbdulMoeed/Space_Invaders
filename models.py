# This file stores the model
from abc import ABC, abstractmethod
import time
import random

#parent class for defenders and invaders
class Spaceship(ABC):
    def __init__(self, x, y , speed, width, height):
        self.x = x
        self.y = y
        self.speed = speed
        self.width = width
        self.height = height
        self.bullets = []  #list to store currently active bullets

    @abstractmethod
    def move(self):
        pass

    @abstractmethod
    def shoot(self):
        pass

    def update_bullets(self):
        self.bullets = [b for b in self.bullets if b.active == True] # filter out the unactive bullets (those which go out of bounds)

#class for defender
class Defender(Spaceship):
    def __init__(self, x, y,  speed, width, height, color='red', cooldown=0.5):
        super().__init__(x, y, speed, width, height)
        
        self.can_shoot = True

        self.color = color
        self.lvl = 1
        self.time1 = -10 # for cool down (this lets u fire the gun immediately when game starts without waiting for cd)
        self.time_lvl_2 = 0

        self.cd = cooldown
        self.can_shoot = True
        
        self.move_right = False
        self.move_left = False
        self.shoot_bullet = False

    def update(self):
        dx = 0
        bullets = []
        
        if self.move_right:
            dx = self.speed

        if self.move_left:
            dx = -self.speed

        
        if self.shoot_bullet:
            if (time.time() - self.time1) >= self.cd:
                self.time1 = time.time()
                bullets = self.shoot()
                self.bullets.extend(bullets)

        dx = self.move(dx)
        self.update_bullets()

        # level 2 5 sec cool down
        if int(time.time()) - self.time_lvl_2 >= 5:
                self.lvl = 1
                self.cd = 0.5

        return dx, bullets


    def move(self, dx):
        #if moving right dont overshoot
        if dx > 0 and (self.x + self.width) < 800: 
            self.x += dx
            return dx
        if dx < 0 and (self.x) > 0:
            self.x += dx
            return dx
        dx = 0 #returns 0 if not moving
        return dx


    def shoot(self): 
        if self.lvl == 1:
            bullet  = Defender_Bullets(self.x + (self.width // 2) - 3, self.y)
            return [bullet]
        
        elif self.lvl ==2:
            # lasts for 5 seconds

            bullet1 = Defender_Bullets(self.x + (self.width // 4)- 3, self.y)
            bullet2 = Defender_Bullets(self.x + (3 * (self.width // 4)) - 3, self.y)
            bullet3 = Defender_Bullets(self.x + (self.width // 2) - 3, self.y)
            return [bullet1, bullet2, bullet3]


class Bullets(ABC):
    def __init__(self, x, y, color, width=6, height=6, speed=20):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.active = True
        self.speed = speed
        self.color = color

    @abstractmethod
    def move(self):
        pass

 
class Defender_Bullets(Bullets):
    def __init__(self, x, y):
        super().__init__(x, y, color='yellow')
    

    # moves bullet upwards
    def move(self):
        if self.y > 0:
            self.y -= self.speed
        else:
            self.active = False #if out of bound deactivate


class Invader_Bullets(Bullets):
    def __init__(self, x, y):
        super().__init__(x, y, color='red', speed=5, height=-6)
    

    # moves bullet upwards
    def move(self):
        if self.y < 600:
            self.y += self.speed
        else:
            self.active = False #if out of bound deactivate


#th
def collision(obj1, obj2):
    x1_a, y1_a = obj1.x, obj1.y
    x2_a, y2_a = obj1.x + obj1.width, obj1.y + obj1.height

    x1_b, y1_b = obj2.x, obj2.y
    x2_b, y2_b = obj2.x + obj2.width, obj2.y + obj2.height

    return (x1_a < x2_b and
            x2_a > x1_b and
            y1_a < y2_b and
            y2_a > y1_b)


class Upgrade():
    def __init__(self):
        self.x = random.randint(0, 760)
        self.y = 0
        self.width = 20
        self.height = 20
        self.active = True
        self.speed = 10


    def move(self):
        if self.y < 600:
            self.y += 10
        else:
            self.active = False


class Invader(Spaceship):
    def __init__(self, x, y,  speed, width = 50, height = 20, color='blue'):
        super().__init__(x, y,  speed, width, height)

        self.color = color

    # flip speed to change dir
    def move(self):
        self.x += self.speed


    def move_down(self):
        self.y += 20


    # shoots based on probablity
    def attempt_fire(self, prob):
        chance = random.random()
        if chance <= prob:
            return self.shoot()
            


    def shoot(self):
        bullet = Invader_Bullets(self.x + (self.width // 2) - 3, self.y + self.height)
        return bullet


def create_grid(speed):

    # 8 in 1 row
    #width is?

    x_start = 150
    x_space = 75
    y_start = 50
    y_space = 50
    invaders = []
    for row in range(4):
        for col in range(7):
            invaders.append(Invader( (col * x_space) + x_start, y_start + (y_space * row), speed))
    
    return invaders


def create_pyramid(speed,rows = 5):
    #spawn enemies in a pyramid shape 
    x_spacing = 75
    y_space = 50
    y_start = 50

    invaders = []

    for row in range(rows):
        count = row + 1 #num enemies in this row
        total_width = count * x_spacing
        start_x = 800 // 2 -  total_width // 2

        for col in range(count):
            x = start_x + col * x_spacing
            y = y_start + row * y_space
            invader = Invader(x, y, speed)
            invaders.append(invader)

    return invaders
                            


        