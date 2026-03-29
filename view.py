# this file contains the 2 viewing screens in
import tkinter as tk
import random

class StartScreen(tk.Frame):
    #enter name and start
    def __init__(self, root, star_num=16, star_size=8):
        super().__init__(root) #link the frame to the root
        
        self.root = root
        self.canvas = tk.Canvas(self, bg='black', height=600, width=800)
        self.canvas.pack()

        #generate stars randomly
        for _ in range(star_num):
            x_offset = random.randint(1, 99)
            y_offset = random.randint(1, 74)
            self.canvas.create_rectangle(x_offset*star_size, y_offset*star_size,
                                          x_offset*star_size + star_size ,y_offset* star_size + star_size, fill='white')
        
        #button and entry feild for username
        button = tk.Button(self, text='Start Game!', fg='red', bg='black', command=self.start)
        self.entry = tk.Entry(self, fg='blue', bg='black')
        label = tk.Label(self, text='SPACE INVADERS', font=('Ariel', 40, 'bold'), fg='red', bg='black')
        label_goat = tk.Label(self, text=f"GOAT", font=('Ariel', 20), fg='yellow', bg='black')
        label_best = tk.Label(self, text=f"{self.root.best_player[0]} | {self.root.best_player[1]}", 
                              font=('Ariel', 20), fg='yellow', bg='black')
        self.entry.insert(0, 'Enter Username')

        
        self.canvas.create_window(400, 500, window=button)
        self.canvas.create_window(400, 400, window=self.entry)
        self.canvas.create_window(400, 300, window=label)
        self.canvas.create_window(400, 200, window=label_best)
        self.canvas.create_window(400, 170, window=label_goat)
    
    def start(self):
        username = self.entry.get()

        

        self.root.start_game(username)
        # start the game


class GameScreen(tk.Frame):
    def __init__(self, root):
        super().__init__(root)

        self.canvas = tk.Canvas(self, bg='black', width=800, height=600)
        self.canvas.pack()
        

    def create_score(self):
        return self.canvas.create_text(50, 50, text=f'Score: 0', font=("Arial", 15), fill="blue")
    

    def change_score(self, id, text):
        self.canvas.itemconfig(id, text=text)


    def create_defender(self, x, y, width, height, color):
        self.defender = self.canvas.create_rectangle(x, y, x+width, y+height, fill=color)


    def move_defender(self, dx):
        self.canvas.move(self.defender, dx ,0 )

    # create a bullet and return its id
    def create_bullet(self, x, y, width, height, color):
        bullet_id = self.canvas.create_rectangle(x, y, width+x, height+y, fill=color)
        return bullet_id

    # move bullets upwards
    def move_bullet_defender(self, bullet_id, speed):
        self.canvas.move(bullet_id, 0, -speed)


    def create_upgrade(self, x, width):
        upgrade_id = self.canvas.create_rectangle(x, 0, x+width, width, fill='green')
        return upgrade_id
    
    def move_upgrade(self,id, speed):
        self.canvas.move(id, 0, speed)


    # delete item in canvas
    def del_obj(self, id):
        self.canvas.delete(id)


    def create_invader(self, x, y, width, height, color):
        invader_id = self.canvas.create_rectangle(x, y, x + width, y + height, fill=color)
        return invader_id
    

    def move_invader(self, id, speed):
        self.canvas.move(id, speed, 0)

    def move_invader_down(self, id, speed):
        self.canvas.move(id, 0, speed)


    def bullet_move_invader(self, id, speed):
        self.canvas.move(id, 0,speed)



class EndScreen(tk.Frame):
    def __init__(self, root, score):
        super().__init__(root)
        self.canvas = tk.Canvas(self, bg='black', width=800, height=600)
        # Darken screen
        self.canvas.pack()
        # Game over text
        self.canvas.create_text(
            400, 250,
            text="GAME OVER",
            fill="red",
            font=("Arial", 40, "bold")
        )
        
        self.canvas.create_text(
            400, 320,
            text=f"Final Score: {score}",
            fill="white",
            font=("Arial", 20)
        )

        root.after(10000, root.destroy)




        
