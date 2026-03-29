import tkinter as tk
from abc import abstractmethod, ABC

#parent class for invaders and defender
class spaceship(ABC):
    def __init__(self, canvas, x, y, fill, width, height=30, speed=20, health = 1):
        self.canvas = canvas
        self.health = health
        self.speed = speed
        self.width = width
        self.height = height

        self.id = canvas.create_rectangle(x, y, x+width, y+height, fill=fill) #instance of the object to refrence in the canvas
        self.bullets = [] #list for keeping track of bullets


    #moving left by speed if not going off screen
    def move_left(self):
        if self.canvas.coords(self.id)[0] > 0:
            self.canvas.move(self.id, -self.speed, 0)


    #moving right by speed if not going off screen
    def move_right(self):
        if self.canvas.coords(self.id)[2] < 800:
            self.canvas.move(self.id, self.speed, 0)

    @abstractmethod
    def shoot(self):
        pass


    #updating the position of every bullet
    def update_bullets(self):
        for b in self.bullets:
            b.move()
        self.bullets = [b for b in self.bullets if b.active == True] #updating list bullets out of bounds or consumed will be consumed
        


class Defender(spaceship):
    def __init__(self, canvas, game ,x=350, y=500, fill='red', width=100):
        super().__init__(canvas, x, y, fill, width)
        self.game = game

    #create an instance of a bullet
    def shoot(self):
        self.bullets.append(Bullet(self.canvas, self, self.game))
        
        
        
        

class Invader(spaceship):
    def __init__(self, canvas, x, y, fill='blue', width=70, ):
        super().__init__(canvas, x, y, fill, width, speed=10)

    def shoot(self):
        pass


class Bullet:
    def __init__(self, canvas, spaceship, game,speed=20, dmg=1, fill='yellow'):
        self.canvas = canvas
        self.speed = speed
        self.dmg = dmg
        self.active = True
        self.game = game


        #get cords of space ship
        x1, y1, x2, y2 = self.canvas.coords(spaceship.id)
        #setting the bullet to be 4px wide from the centre and 10px long
        self.id = self.canvas.create_rectangle(
            (x1 + spaceship.width / 2) -2,
            y1-10,
            (x1 + spaceship.width / 2) +2,
            y1, fill=fill
        )

    #move and check for collision
    def move(self):

        x1_a, y1_a, x2_a, y2_a = self.canvas.bbox(self.id)
        for i,inv in enumerate(self.game.invaders):
            
            x1_b, y1_b, x2_b, y2_b = self.canvas.bbox(inv.id)
            #check colision
            if (x1_a < x2_b and x2_a > x1_b) and ( y1_a < y2_b and y2_a > y1_b):
                del self.game.invaders[i]
                self.active = False #with active the defender will remove from the list when updating
                self.canvas.delete(self.id)
                self.canvas.delete(inv.id)
                self.game.scored = True
                self.game.score += 1
                return
        #bullet goes out of bounds 
        if y1_a <= 0:
            self.active = False #with active the defender will remove from the list when updating
            self.canvas.delete(self.id)
        else:
            self.canvas.move(self.id, 0 , -self.speed)
            






        

#main game class
class Game():
    def __init__(self):
        global scored, score

        self.root = tk.Tk()
        self.root.title('Space Invaders')
        self.root.geometry('800x600')

        self.canvas = tk.Canvas(self.root, width=800, height=600, bg='black')
        self.canvas.pack()

        self.id = []
        self.score = 0
        
        self.id.append(self.canvas.create_text(30, 50, text=f'Score: {self.score}', font=("Arial", 10), fill="blue"))
        self.invaders = []

        self.spawn_pyramid_inv()
        self.defender = Defender(self.canvas, self)
        right = False

        self.root.bind('<space>', lambda x:self.defender.shoot())
        self.root.bind('<Left>', lambda x:self.defender.move_left())
        self.root.bind('<Right>', lambda x:self.defender.move_right())
        
        self.game_over = False
        self.scored = False
        self.right = False

        self.update_game()
        
        

    def spawn_pyramid_inv(self,  rows=5):
        #spawn enemies in a pyramid shape 
        x_spacing = 80
        y_space = 50
        y_start = 50

        for row in range(rows):
            count = row + 1 #num enemies in this row
            total_width = count * x_spacing
            start_x = 800 // 2 -  total_width // 2

            for col in range(count):
                x = start_x + col * x_spacing
                y = y_start + row * y_space
                invader = Invader(self.canvas, x, y)
                self.invaders.append(invader)


    def show_game_over(self):
        
        # Darken screen
        self.canvas.create_rectangle(0, 0, 800, 600, fill="black")
        
        # Game over text
        self.canvas.create_text(
            400, 250,
            text="GAME OVER",
            fill="red",
            font=("Arial", 40, "bold")
        )
        
        self.canvas.create_text(
            400, 320,
            text=f"Final Score: {self.score}",
            fill="white",
            font=("Arial", 20)
        )

        self.root.after(10000, self.root.destroy)
    

    #move grid to left or right
    def move_enemies(self):
        #check the right most and left most to decide direction
        x1, y1, x2, y2 = self.canvas.bbox(*[i.id for i in self.invaders])
        down = False
        if x1 <= 0:
            self.right = True
            down = True
        if x2 >= 800:
            self.right = False
            down = True
        if down:
            for i in self.invaders:
                self.canvas.move(i.id, 0, 50) #move 50px down
                
        '''for inv in self.invaders:
            x1, y1, x2, y2 = self.canvas.coords(inv.id)
            if y2 >= 500:
                self.game_over = True
                break
            if x1 <= 0:
                self.right = True
                for  i in self.invaders:
                    self.canvas.move(i.id, 0, 50) #move 50px down 
                break
            if x2 >= 800:
                self.right = False
                for i in self.invaders:
                    self.canvas.move(i.id, 0, 50) #move 50px down
                break'''
        #move every space based on direction
        if self.right:
            for inv in self.invaders:
                inv.move_right()
        else:
            for inv in self.invaders:
                inv.move_left()


    def start(self):
        self.root.mainloop()

    def update_game(self):
        if self.game_over:
            self.show_game_over()
        if len(self.invaders) != 0: 
            self.move_enemies()
            pass
        else:
            self.spawn_pyramid_inv()

        self.defender.update_bullets()
        if self.scored:
            self.canvas.itemconfig(self.id[0], text=f'Score: {self.score}')
            self.scored = False
        self.root.after(50, lambda :self.update_game())



game = Game()
game.start()