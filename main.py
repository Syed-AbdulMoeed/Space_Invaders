import tkinter as tk
from view import StartScreen, GameScreen, EndScreen
from models import Defender, collision, Upgrade, Invader, create_grid, create_pyramid
import time
import random
import pygame
import csv


#Main Game class
class Game(tk.Tk):
    def __init__(self): #self is the root
        super().__init__() 
        self.geometry('800x600')
        self.title('Space Invaders v1')
        
        self.time = time.time() # for spawning upgrade buff
        self.upgrade_spawned = False
        self.score = 0
        self.lvl2 = False # is defender in lvl2
        self.capped = False # caps the probability for an invader to shoot
        self.inv_fire = False # fires when defenders go down a level
        self.speed_counter = 8 # added to invader speed 
        self.last_speed_score = -1 # checker to make sure score doesnt break speed
        self.invaders = [] # list to store invaders
        self.invader_bullets = []
        self.game_over = False

        #flags to control movement
        self.flags = {
            "move_left": False,
            "move_right": False,
            "shoot": False
        }

        # dictionary to map bullet objects to ids to edit in view
        self.object_map = {}

        #binds which call a function to change functions
        self.bind("<KeyPress>", self.key_down)
        self.bind("<KeyRelease>", self.key_up)

    
    def get_best_player(self):
        with open('highscores.csv', 'r') as file:
            reader = csv.reader(file)
            # Find the row where the 'value' column is the highest
            # We convert the value to an integer for a proper numeric comparison
            self.best_player  = max(reader, key=lambda row: int(row[1]))
            


        
    # shows start screen
    def start(self):
        self.get_best_player()
        self.view = StartScreen(self)
        self.view.pack()
        

    # starts the game after start screen
    def start_game(self, username):

        pygame.mixer.music.load("Megalovania.mp3") # sans
        pygame.mixer.music.play(-1)   # -1 means play in an infinite loop

        self.username = username
        self.view.destroy() # delete the start screen
        self.view = GameScreen(self) # start the game screen
        self.view.pack()
        self.view.create_defender(360, 550, 80, 30, 'red')
        self.defender = Defender(360, 550, 10, 80, 30)
        
        self.score_id = self.view.create_score()

        self.update_game()

    def update_game(self):
        
        if self.game_over:
            return

        # respawn invaders if all ded
        if len(self.invaders) == 0:
            self.invaders = self.spawn_invaders()

            for invader in self.invaders:
                inv_id = self.view.create_invader(invader.x, invader.y, invader.width, invader.height, invader.color)
                self.object_map[invader] = inv_id

        self.bullet_invader_collision() # delete shot invaders
        self.move_invaders() # move invaders

        #upgrade spawning and collision check
        self.upgrade_update()
        if self.upgrade_spawned:
            self.upgrade_collision_check()

        #defender actions
        def_dx, bullets = self.defender.update()
        self.view.move_defender(def_dx)
        
        # add bullet to the mapping dict
        for bullet in bullets:
            bullet_id = self.view.create_bullet(bullet.x, bullet.y, bullet.width, bullet.height, bullet.color)
            self.object_map[bullet] = bullet_id
        
        self.move_bullets()

        self.up_speed_invader()
        if self.inv_fire:
            self.invader_fire()
            self.inv_fire = False
        self.invader_bullet_move()


        self.game_loop_id = self.after(30, self.update_game)

    # move the defender's bullets using the mapping
    def move_bullets(self):
        for b in self.defender.bullets:
            b.move()
            id = self.object_map[b]
            self.view.move_bullet_defender(id, b.speed)


    # changes defender status flags
    def key_down(self, event):
        if event.keysym == "Left":
            self.defender.move_left = True
        if event.keysym == "Right":
            self.defender.move_right = True
        if event.keysym == "space":
            self.defender.shoot_bullet = True


    # release key stops event
    def key_up(self, event):
        if event.keysym == "Left":
            self.defender.move_left = False
        if event.keysym == "Right":
            self.defender.move_right = False
        if event.keysym == "space":
            self.defender.shoot_bullet = False


    # handles upgrade movement
    def upgrade_update(self):
        if not self.upgrade_spawned: 
            #no upgrade
            if (time.time() - self.time ) >= 1: #5 seconds must pass
                self.upgrade = Upgrade()
                id = self.view.create_upgrade(self.upgrade.x, self.upgrade.width)
                self.object_map[self.upgrade] = id 
                self.upgrade_spawned = True
        # move upgrade if spawned
        elif self.upgrade.active == True:
            self.upgrade.move()
            id = self.object_map[self.upgrade]
            self.view.move_upgrade(id, self.upgrade.speed)

        # reset upgrade pointer and time
        else:
            self.upgrade_spawned = False
            self.time = time.time()
            self.view.del_obj(self.object_map[self.upgrade])


    # spawns invaders randomlys
    def spawn_invaders(self):
        spawn = random.randint(0,1)
        if spawn == 0:
            return create_grid(self.speed_counter)
        else: 
            return create_pyramid(self.speed_counter)
        
    #moves invaders left --> down --> right
    def move_invaders(self):
        for invader in self.invaders:
            if invader.y >= 550:
                self.game_kill()
                return # to stop func running after game ended
        #check if the invaders should move down first
        down = False
        for invader in self.invaders:
            if invader.x <= 0:
                down = True
                self.inv_fire = True
                break
            if invader.x + invader.width >= 800: 
                down = True
                self.inv_fire = True
        
        if down:
            for invader in self.invaders:
                invader.move_down()
                id = self.object_map[invader]
                self.view.move_invader_down(id, 20)

                invader.speed = -invader.speed # flip direction

        
        for invader in self.invaders:
            invader.move()
            id = self.object_map[invader]
            self.view.move_invader(id, invader.speed)


    # check collision of upgrade and defender
    def upgrade_collision_check(self):
        if collision(self.defender, self.upgrade):
            self.upgrade_spawned = False
            self.view.del_obj(self.object_map[self.upgrade])
            self.defender.lvl = 2
            self.defender.cd = 0.25
            self.defender.time_lvl_2 = int(time.time())
            del self.object_map[self.upgrade]
            
    
    # checks if any bullet has colidded with an invader
    def bullet_invader_collision(self):
        # for every bullet check every invader
        for bullet in self.defender.bullets:
            for invader in self.invaders:
                if collision(bullet, invader):
                    bullet.active = False # deactivate bullet
                    self.invaders.remove(invader)
                    b_id = self.object_map[bullet]
                    id = self.object_map[invader]

                    del self.object_map[invader]
                    del self.object_map[bullet]
                    self.view.del_obj(id)
                    self.view.del_obj(b_id)

                    self.score += 1
                    self.change_score()

    # fire bullets from invader whenever it collides 
    def invader_fire(self):
        if not self.capped:
            prob = self.score/100 #probability to shoot
        else:
            prob = 1
        if prob == 1:
            self.capped = True
        
        for invader in self.invaders:
            bullet = invader.attempt_fire(prob)
            if bullet:
                id = self.view.create_bullet(bullet.x, bullet.y, bullet.width, bullet.height, bullet.color)
                self.object_map[bullet] = id
                self.invader_bullets.append(bullet)
    

    #moves bullet and checks for collision
    def invader_bullet_move(self):
        for bullet in self.invader_bullets:
            
            if collision(bullet, self.defender):
                self.game_kill()
                return # to stop from func running after game ended
            id = self.object_map[bullet]
            if bullet.active:
                bullet.move()
                self.view.bullet_move_invader(id, bullet.speed)
            else:
                del self.object_map[bullet]
                self.view.del_obj(id)
                self.invader_bullets.remove(bullet)
    

    # modifies score
    def change_score(self):
        self.view.change_score(self.score_id, f'Score: {self.score}')


    # implements game over
    def game_kill(self):
        
        self.game_over = True
        if self.game_loop_id:
            self.after_cancel(self.game_loop_id)
        
        self.view.destroy()
        pygame.mixer.music.fadeout(2000)  # fade out over 2 seconds
        self.view = EndScreen(self, self.score)
        self.view.pack()

        self.save_info()


    # handles increased invader speed
    def up_speed_invader(self):
        # every +20 score speed increases
        if self.score != 0 and self.score % 20 == 0 and self.last_speed_score != self.score: 
            self.last_speed_score = self.score
            self.speed_counter += 1
            for invader in self.invaders:
                invader.speed += 1

    
    def save_info(self):
        with open('highscores.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([self.username, self.score])


        
    

pygame.mixer.init()
game = Game()
game.start()
game.mainloop()

