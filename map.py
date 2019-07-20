# Self Driving Car

# Importing the libraries
import numpy as np
import matplotlib.pyplot as plt
import mss
import mss.tools

# Importing the Kivy packages
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.config import Config
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.properties import ListProperty
from kivy.core.window import Window

# Importing the Dqn object from our AI in ai.py
from ai import Dqn

# Adding this line if we don't want the right click to put a red point
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

# Introducing last_x and last_y, used to keep the last point in memory when we draw the sand on the map
last_x = 0
last_y = 0
n_points = 0
length = 0
# Getting our AI, which we call "brain", and that contains our neural network that represents our Q-function
brain = Dqn(5,3,0.9)
action2rotation = [0,20,-20]
last_reward = 0
scores = []

# Initializing the map
first_update = True
def init():
    global sand
    global goal_x
    global goal_y
    global first_update
 #   global lastx
  #  global lasty
    sand = np.zeros((longueur,largeur))
    goal_x = 35
    goal_y = largeur - 35
    first_update = False
  #  lastx = 0
   # lasty = 0

# Initializing the last distance
last_distance = 0

# Creating the car class

class Car(Widget):
    
    angle = NumericProperty(0)
    rotation = NumericProperty(0)
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    sensor1_x = NumericProperty(0)
    sensor1_y = NumericProperty(0)
    sensor1 = ReferenceListProperty(sensor1_x, sensor1_y)
    sensor2_x = NumericProperty(0)
    sensor2_y = NumericProperty(0)
    sensor2 = ReferenceListProperty(sensor2_x, sensor2_y)
    sensor3_x = NumericProperty(0)
    sensor3_y = NumericProperty(0)
    sensor3 = ReferenceListProperty(sensor3_x, sensor3_y)
    signal1 = NumericProperty(0)
    signal2 = NumericProperty(0)
    signal3 = NumericProperty(0)

    def move(self, rotation):
        
        self.pos = Vector(*self.velocity) + self.pos
        self.rotation = rotation
        self.angle = self.angle + self.rotation
        self.sensor1 = Vector(45, 0).rotate(self.angle) + self.pos
        self.sensor2 = Vector(45, 0).rotate((self.angle+30)%360) + self.pos
        self.sensor3 = Vector(45, 0).rotate((self.angle-30)%360) + self.pos
        self.signal1 = int(np.sum(sand[int(self.sensor1_x)-10:int(self.sensor1_x)+10, int(self.sensor1_y)-10:int(self.sensor1_y)+10]))/400.
        self.signal2 = int(np.sum(sand[int(self.sensor2_x)-10:int(self.sensor2_x)+10, int(self.sensor2_y)-10:int(self.sensor2_y)+10]))/400.
        self.signal3 = int(np.sum(sand[int(self.sensor3_x)-10:int(self.sensor3_x)+10, int(self.sensor3_y)-10:int(self.sensor3_y)+10]))/400.
        if self.sensor1_x>longueur-10 or self.sensor1_x<10 or self.sensor1_y>largeur-10 or self.sensor1_y<10:
            self.signal1 = 1.
        if self.sensor2_x>longueur-10 or self.sensor2_x<10 or self.sensor2_y>largeur-10 or self.sensor2_y<10:
            self.signal2 = 1.
        if self.sensor3_x>longueur-10 or self.sensor3_x<10 or self.sensor3_y>largeur-10 or self.sensor3_y<10:
            self.signal3 = 1.
      

class Ball1(Widget):
    pass
class Ball2(Widget):
    pass
class Ball3(Widget):
    pass
class Car2(Widget):
    lastx=0
    lasty=0
    velocity = ListProperty([1, 0])
class Car3(Widget):
    lastx=0
    lasty=0
    velocity = ListProperty([0, 1])
class Car4(Widget):
    lastx=0
    lasty=0
    velocity = ListProperty([0, 1])

# Creating the game class
class Game(Widget):

    car = ObjectProperty(None)
    ball1 = ObjectProperty(None)
    ball2 = ObjectProperty(None)
    ball3 = ObjectProperty(None)
    car2 = ObjectProperty(None)
    
    def serve_car(self):
       # self.car.center = self.center
        self.car.velocity = Vector(3, 0)

    def update(self, dt):

        global brain
        global last_reward
        global scores
        global last_distance
        global goal_x
        global goal_y
        global longueur
        global largeur
        
        longueur = self.width
        largeur = self.height
        if first_update:
            init()

        xx = goal_x - self.car.x
        yy = goal_y - self.car.y
        orientation = Vector(*self.car.velocity).angle((xx,yy))/180.
        last_signal = [self.car.signal1, self.car.signal2, self.car.signal3, orientation, -orientation]
        action = brain.update(last_reward, last_signal)
        scores.append(brain.score())
        rotation = action2rotation[action]
        self.car.move(rotation)
        distance = np.sqrt((self.car.x - goal_x)**2 + (self.car.y - goal_y)**2)
        self.ball1.pos = self.car.sensor1
        self.ball2.pos = self.car.sensor2
        self.ball3.pos = self.car.sensor3

        if sand[int(self.car.x),int(self.car.y)] > 0:
            self.car.velocity = Vector(1, 0).rotate(self.car.angle)
           # print("grass")
            last_reward = -1
        else: # otherwise
            self.car.velocity = Vector(3, 0).rotate(self.car.angle)
            last_reward = -0.2
            if distance < last_distance:
                last_reward = 0.1

        if self.car.x < 10:
            self.car.x = 15
            last_reward = -1
        if self.car.x > self.width - 10:
            self.car.x = self.width - 15
            last_reward = -1
        if self.car.y < 10:
            self.car.y = 15
            last_reward = -1
        if self.car.y > self.height - 10:
            self.car.y = self.height - 15
            last_reward = -1

        if distance < 100:
            goal_x = self.width-goal_x
            goal_y = self.height-goal_y
        last_distance = distance
        
        
        for i in range(self.car2.x-10,self.car2.x+40):
            for j in range(self.car2.y-10,self.car2.y+25):
                sand[i][j]=1
        if(self.car2.x-self.car2.lastx>0):
            for i in range(self.car2.lastx-10,self.car2.x-10):
                for j in range(self.car2.y-10,self.car2.y+25):
                    sand[i][j]=0
        else:
            for i in range(self.car2.x+40,self.car2.lastx+40):
                for j in range(self.car2.y-10,self.car2.y+25):
                    sand[i][j]=0
        
        if self.car2.x <= 11 or (self.car2.x + self.car2.width) >= Window.width-222:
            self.car2.velocity[0] *= -1
        if self.car2.y <= 0 or (self.car2.y + self.car2.height) >= Window.height:
            self.car2.velocity[1] *= -1
        self.car2.lastx=self.car2.x
        self.car2.lasty=self.car2.y
        self.car2.x += self.car2.velocity[0]
        self.car2.y += self.car2.velocity[1]
        
        
        for i in range(self.car3.x-10,self.car3.x+25):
            for j in range(self.car3.y-10,self.car3.y+40):
                sand[i][j]=1
        if(self.car3.y-self.car3.lasty>0):
            for i in range(self.car3.x-10,self.car3.x+25):
                for j in range(self.car3.lasty-10,self.car3.y-10):
                    sand[i][j]=0
        else:
            for i in range(self.car3.x-10,self.car3.x+25):
                for j in range(self.car3.y+40,self.car3.lasty+40):
                    sand[i][j]=0
        if self.car3.x <= 11 or (self.car3.x + self.car3.width) >= Window.width-222:
            self.car3.velocity[0] *= -1
        if self.car3.y <= 110 or (self.car3.y + self.car3.height) >= Window.height-11:
            self.car3.velocity[1] *= -1
        self.car3.lastx=self.car3.x
        self.car3.lasty=self.car3.y
        self.car3.x += self.car3.velocity[0]
        self.car3.y += self.car3.velocity[1]

        for i in range(self.car4.x-10,self.car4.x+25):
            for j in range(self.car4.y-10,self.car4.y+40):
                sand[i][j]=1
        if(self.car4.y-self.car4.lasty>0):
            for i in range(self.car4.x-10,self.car4.x+25):
                for j in range(self.car4.lasty-10,self.car4.y-10):
                    sand[i][j]=0
        else:
            for i in range(self.car4.x-10,self.car4.x+25):
                for j in range(self.car4.y+40,self.car4.lasty+40):
                    sand[i][j]=0
        
        if self.car4.x <= 11 or (self.car4.x + self.car4.width) >= Window.width-222:
            self.car4.velocity[0] *= -1
        if self.car4.y <= 110 or (self.car4.y + self.car4.height) >= Window.height-11:
            self.car4.velocity[1] *= -1
        #print(self.car4.x,self.car4.y)
        self.car4.lastx=self.car4.x
        self.car4.lasty=self.car4.y
        self.car4.x += self.car4.velocity[0]
        self.car4.y += self.car4.velocity[1]

        
    def __init__(self, **kwargs):
        super(Game, self).__init__(**kwargs)    
        with self.canvas.before:
            Color(0.14,0.92,0.22,1)
            Rectangle(pos=(0,0),size=(210,160))#breadth,height
            Rectangle(pos=(295,0),size=(210,160))
            Rectangle(pos=(595,95),size=(210,285))
            Rectangle(pos=(0,245),size=(210,135))
            Rectangle(pos=(295,245),size=(210,135))
            Rectangle(pos=(95,470),size=(115,135))
            Rectangle(pos=(295,470),size=(210,135))
            Rectangle(pos=(590,470),size=(210,135))
            # White Boundary
            Color(1,1,1,1)
            Rectangle(pos=(0,160),size=(215,5))
            Rectangle(pos=(210,0),size=(5,165))
            Rectangle(pos=(290,0),size=(5,165))
            Rectangle(pos=(505,0),size=(5,165))
            Rectangle(pos=(295,160),size=(210,5))
            Rectangle(pos=(590,90),size=(215,5))
            Rectangle(pos=(590,380),size=(215,5))
            Rectangle(pos=(590,95),size=(5,285))
            Rectangle(pos=(0,240),size=(215,5))
            Rectangle(pos=(0,380),size=(215,5))
            Rectangle(pos=(210,245),size=(5,135))
            Rectangle(pos=(290,240),size=(220,5))
            Rectangle(pos=(290,380),size=(220,5))
            Rectangle(pos=(290,245),size=(5,135))
            Rectangle(pos=(505,245),size=(5,135))
            Rectangle(pos=(90,465),size=(120,5))
            Rectangle(pos=(210,465),size=(5,135))
            Rectangle(pos=(90,470),size=(5,135))
            Rectangle(pos=(290,470),size=(5,135))
            Rectangle(pos=(290,465),size=(215,5))
            Rectangle(pos=(505,465),size=(5,135))
            Rectangle(pos=(590,470),size=(5,135))
            Rectangle(pos=(590,465),size=(215,5))
            # Constructing Trees
            Color(0.8,0.51,0,1)
            Rectangle(pos=(163,0),size=(6,20))
            Rectangle(pos=(163,250),size=(6,20))
            Rectangle(pos=(123,250),size=(6,20))
            Rectangle(pos=(24,100),size=(6,20))
            Rectangle(pos=(24,280),size=(6,20))
            Rectangle(pos=(325,80),size=(6,30))
            Rectangle(pos=(739,95),size=(6,20))
            Rectangle(pos=(781,300),size=(8,30))
            Rectangle(pos=(641,250),size=(10,25))
            Rectangle(pos=(26,330),size=(8,20))
            Rectangle(pos=(123,280),size=(6,20))
            Rectangle(pos=(325,310),size=(8,30))
            Rectangle(pos=(375,260),size=(8,30))
            Rectangle(pos=(325,500),size=(8,22))
            Rectangle(pos=(467,520),size=(8,30))
            Rectangle(pos=(607,490),size=(8,30))
            Rectangle(pos=(781,530),size=(8,30))
            Rectangle(pos=(601,230),size=(8,30))
            Rectangle(pos=(601,130),size=(8,30))
            Rectangle(pos=(739,500),size=(6,20))
            Rectangle(pos=(325,700),size=(8,22))
            Rectangle(pos=(163,490),size=(6,20))
            Rectangle(pos=(641,300),size=(10,25))
            Color(5/256,183/256,55/256) 
            Ellipse(pos=(155,18),size=(22,27))
            Ellipse(pos=(155,268),size=(22,27))
            Ellipse(pos=(115,268),size=(22,27))
            Ellipse(pos=(16,118),size=(22,27))
            Ellipse(pos=(16,298),size=(22,27))
            Ellipse(pos=(317,98),size=(22,27))
            Ellipse(pos=(731,108),size=(25,32))
            Ellipse(pos=(771,318),size=(27,27))
            Ellipse(pos=(631,268),size=(30,30))
            Ellipse(pos=(16,348),size=(30,30))
            Ellipse(pos=(115,298),size=(22,27))
            Ellipse(pos=(315,328),size=(27,27))
            Ellipse(pos=(367,278),size=(27,27))
            Ellipse(pos=(315,522),size=(27,27))
            Ellipse(pos=(457,542),size=(27,27))
            Ellipse(pos=(597,512),size=(27,27))
            Ellipse(pos=(771,548),size=(27,27))
            Ellipse(pos=(591,257),size=(27,27))
            Ellipse(pos=(591,157),size=(27,27))
            Ellipse(pos=(731,518),size=(25,32))
            Ellipse(pos=(155,499),size=(22,27))
            Ellipse(pos=(631,318),size=(30,30))
            '''
            # Constructing Zebra
            
            Color(1,1,1,1)
            Rectangle(pos=(165,170),size=(25,8))
            Rectangle(pos=(165,189),size=(25,8))
            Rectangle(pos=(165,208),size=(25,8))
            Rectangle(pos=(165,227),size=(25,8))
            Rectangle(pos=(311,170),size=(25,8))
            Rectangle(pos=(311,189),size=(25,8))
            Rectangle(pos=(311,208),size=(25,8))
            Rectangle(pos=(311,227),size=(25,8))
            Rectangle(pos=(220,260),size=(8,25))
            Rectangle(pos=(239,260),size=(8,25))
            Rectangle(pos=(258,260),size=(8,25))
            Rectangle(pos=(277,260),size=(8,25))
            Rectangle(pos=(220,108),size=(8,25))
            Rectangle(pos=(239,108),size=(8,25))
            Rectangle(pos=(258,108),size=(8,25))
            Rectangle(pos=(277,108),size=(8,25))
            Rectangle(pos=(165,390),size=(25,8))
            Rectangle(pos=(165,409),size=(25,8))
            Rectangle(pos=(165,428),size=(25,8))
            Rectangle(pos=(165,447),size=(25,8))
            Rectangle(pos=(311,390),size=(25,8))
            Rectangle(pos=(311,409),size=(25,8))
            Rectangle(pos=(311,428),size=(25,8))
            Rectangle(pos=(311,447),size=(25,8))
            Rectangle(pos=(220,340),size=(8,25))
            Rectangle(pos=(239,340),size=(8,25))
            Rectangle(pos=(258,340),size=(8,25))
            Rectangle(pos=(277,340),size=(8,25))
            Rectangle(pos=(466,170),size=(25,8))
            Rectangle(pos=(466,189),size=(25,8))
            Rectangle(pos=(466,208),size=(25,8))
            Rectangle(pos=(466,227),size=(25,8))
            Rectangle(pos=(466,390),size=(25,8))
            Rectangle(pos=(466,409),size=(25,8))
            Rectangle(pos=(466,428),size=(25,8))
            Rectangle(pos=(466,447),size=(25,8))
            Rectangle(pos=(612,390),size=(25,8))
            Rectangle(pos=(612,409),size=(25,8))
            Rectangle(pos=(612,428),size=(25,8))
            Rectangle(pos=(612,447),size=(25,8))
            Rectangle(pos=(515,108),size=(10,25))
            Rectangle(pos=(536,108),size=(10,25))
            Rectangle(pos=(555,108),size=(10,25))
            Rectangle(pos=(574,108),size=(10,25))
            Rectangle(pos=(515,260),size=(10,25))
            Rectangle(pos=(536,260),size=(10,25))
            Rectangle(pos=(555,260),size=(10,25))
            Rectangle(pos=(574,260),size=(10,25))
            Rectangle(pos=(515,340),size=(10,25))
            Rectangle(pos=(536,340),size=(10,25))
            Rectangle(pos=(574,340),size=(10,25))
            Rectangle(pos=(365,485),size=(10,25))
            Rectangle(pos=(384,485),size=(10,25))
            Rectangle(pos=(403,485),size=(10,25))
            Rectangle(pos=(422,485),size=(10,25)) 
            '''
      
# Adding the painting tools

class MyPaintWidget(Widget):

    def on_touch_down(self, touch):
        global length, n_points, last_x, last_y
        with self.canvas:
            Color(0.8,0.7,0)
            touch.ud['line'] = Line(points = (touch.x, touch.y), width = 10)
            last_x = int(touch.x)
            last_y = int(touch.y)
            n_points = 0
            length = 0
            sand[int(touch.x),int(touch.y)] = 1

    def on_touch_move(self, touch):
        global length, n_points, last_x, last_y
        if touch.button == 'left':
            touch.ud['line'].points += [touch.x, touch.y]
            x = int(touch.x)
            y = int(touch.y)
            length += np.sqrt(max((x - last_x)**2 + (y - last_y)**2, 2))
            n_points += 1.
            density = n_points/(length)
            touch.ud['line'].width = int(20 * density + 1)
            sand[int(touch.x) - 10 : int(touch.x) + 10, int(touch.y) - 10 : int(touch.y) + 10] = 1
            last_x = x
            last_y = y

# Adding the API Buttons (clear, save and load)
class ClockRect(Widget):
    
    velocity = ListProperty([3, 0])
    global sand
    lastx=0
    lasty=0
    sand = np.zeros((800,600))
    def __init__(self, **kwargs):
        super(ClockRect, self).__init__(**kwargs)
        Clock.schedule_interval(self.update, 1/30.)

    def update(self, *args):
        for i in range(self.x-10,self.x+40):
            for j in range(self.y-10,self.y+25):
                sand[i][j]=1
        if(self.x-self.lastx>0):
            for i in range(self.lastx-10,self.x-10):
                for j in range(self.y-10,self.y+25):
                    sand[i][j]=0
        else:
            for i in range(self.x+40,self.lastx+40):
                for j in range(self.y-10,self.y+25):
                    sand[i][j]=0
        
        if self.x <= 11 or (self.x + self.width) >= Window.width-12:
            self.velocity[0] *= -1
        if self.y <= 0 or (self.y + self.height) >= Window.height:
            self.velocity[1] *= -1
        self.lastx=self.x
        self.lasty=self.y
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        
       
        
class CarApp(App):

    def build(self):
        parent = Game()
        parent.serve_car()
        Clock.schedule_interval(parent.update, 1.0/60)
        self.painter = MyPaintWidget()
        clearbtn = Button(text = 'clear')
        savebtn = Button(text = 'save', pos = (parent.width, 0))
        loadbtn = Button(text = 'load', pos = (2 * parent.width, 0))
        learnbtn=Button(text='learn',pos=(3*parent.width,0))
        clearbtn.bind(on_release = self.clear_canvas)
        savebtn.bind(on_release = self.save)
        loadbtn.bind(on_release = self.load)
        learnbtn.bind(on_release= self.learn)
        parent.add_widget(self.painter)
        parent.add_widget(clearbtn)
        parent.add_widget(savebtn)
        parent.add_widget(loadbtn)
        parent.add_widget(learnbtn)
        return parent

    def clear_canvas(self, obj):
        global sand
        self.painter.canvas.clear()
        sand = np.zeros((longueur,largeur))

    def save(self, obj):
        print("saving brain...")
        brain.save()
        plt.plot(scores)
        plt.show()

    def load(self, obj):
        print("loading last saved brain...")
        brain.load()
        
    def learn(self, obj):
        global sand                                                   
        with mss.mss() as sct:
            monitor = {"top": 84, "left":283 , "width": 800, "height": 600}
            im = sct.grab(monitor)
        for i in range(0,799):
            for j in range(0,599):
                sand[i,j]= 0 if im.pixel(i,599-j)==(0,0,0) else 1
       
# Running the whole thing
if __name__ == '__main__':
    CarApp().run()
