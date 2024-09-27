from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle
from kivy.core.window import Window
import kivy.graphics.instructions
from kivy.core.audio import SoundLoader
from kivy.uix.label import CoreLabel
from kivy.clock import Clock
import librosa
import random
import csv
import os
import time
import threading
from time import perf_counter 
#Make your window non-resizable
from kivy.config import Config
from numpy import genfromtxt
import sys
import ntpath
import sklearn.utils._cython_blas
import sklearn.neighbors.typedefs
import sklearn.neighbors.quad_tree
import sklearn.tree
import sklearn.tree._utils

Window.size = (1280,720)
Window.fullscreen = True
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

y, sr = [0,0]
tempo, beats = [0,0]
beats = 0
first_onset = True
timer = beats
timer_firstTap = 1 #1 second
x1=223+15
x2=328+67
x3=437+105
x4=542+159
x5=649+195
x6=755+228
lanes = 2
consequentHits = 0
musicStartThread = 0
noteGenerationThread = 0
game = 0
hittableCircles = set()
genre = 'others'
#0 = initialization, 1 = home, 2 = song list, 3 = game, 4 highscore 
gameState = 0
class Song():
    def __init__(self,filename):
        global genre
        self.name = filename
        self.genre = genre
    def genre_detect(self):
        pass
def initializeEverything():
    print("initializeEverything")
    global y, sr
    global tempo, beats
    global beats
    global timer
    global lanes
    global consequentHits
    global musicStartThread 
    global noteGenerationThread 
    global songSelected
    songpath = songFolder+songSelected
    y, sr = librosa.load(songpath,sr = 44100)
    librosa.output.write_wav('./songs/song.wav', y, sr)
    with open('highscores.csv', mode='r') as infile:
        reader = csv.reader(infile)
        scores = {rows[0]:rows[1] for rows in reader}
    
    if songSelected in scores:
        print("int(scores[songName]) "+str(int(scores[songSelected])))
        intt = int(scores[songSelected])
        game._highscore_label.text = str(intt)
        game._highscore_label.refresh()
        print("intt > game.score")
    else:
        game._highscore_label.text = str(0)
        game._highscore_label.refresh()
    y, sr = librosa.load(str(songFolder) + str(songSelected),sr = 44100)
    tempo, beats = librosa.beat.beat_track(y, sr=sr, units='time')
    librosa.output.times_csv(('./songs/beat_times.csv'), beats)
    
    from numpy import genfromtxt
    beats = genfromtxt(('./songs/beat_times.csv'), delimiter='')
    timer = beats[0]
    lanes = 2
    consequentHits = 0
    musicStartThread = MusicStarterThread(threadID=2,name = "Music Starter",counter=2)
    noteGenerationThread = NoteGeneratorThread(threadID = 1,name = "Note Generator",counter=1)  # ...Instantiate a thread and pass a unique ID to it
    
class GameWidget(Widget):
    onset_ctr = 0
    global app
    global game
    
    def generate_note(self):
        global gameState
        global done
        global timer
        global lanes
        lane = random.randrange(1, lanes+1)
        if lane is 1:
            game.add_entity(HitCircle((x3, Window.height - 50)))
        if lane is 2:
            game.add_entity(HitCircle((x4, Window.height - 50)))
        if lane is 3:
            game.add_entity(HitCircle((x2, Window.height - 50)))
        if lane is 4:
            game.add_entity(HitCircle((x5, Window.height - 50)))
        if lane is 5:
            game.add_entity(HitCircle((x1, Window.height - 50)))
        if lane is 6: 
            game.add_entity(HitCircle((x6, Window.height -50)))
            
        if self.onset_ctr+1 > beats.size-1:
            songScore = str(ntpath.basename(songSelected))
            # sys.exit()
            writeToCSV(songScore)
            print("onset ctr exceeded beats.size")
            # done = True
            # # main.MyMainApp.run()
            # # exit()
            # app.on_stop()
            # exit()
            done = True
            # gameState = 4
            # changeState()
            
        else:    
            print("Beats: ",self.onset_ctr,"/",beats.size-1)
            if self.onset_ctr is 0:
                timer = beats[self.onset_ctr]
            else:
                timer = beats[self.onset_ctr]-beats[self.onset_ctr-1]
    def on_touch_down(self, touch):
        global done
        global consequentHits
        global hittableCircles
        global noteGenerationThread
        global musicStartThread
        global gameState
        global previousState
        
        print("Mouse Down", touch)
        # print(touch.pos[0])
        # print(touch.pos[1])
        #exit button
        
        if gameState is 0:
            if touch.pos[0]>508.0 and touch.pos[0]<752 and touch.pos[1]>91 and touch.pos[1]<171:
                previousState = gameState
                gameState = 2
                changeState()
                # showSongList()
        if gameState is 2:
            global songSelected
            if touch.pos[0]>820.0 and touch.pos[0]<1122 and touch.pos[1]>118 and touch.pos[1]<217:
                songScore = str(ntpath.basename(songSelected))
                writeToCSV(songScore)   
                previousState = gameState
                gameState = 3
                game.score = 0
                changeState()
                # startGameState3()
                game.sound = SoundLoader.load(
                "./songs/song.wav")
                noteGenerationThread.start()
                musicStartThread.start()
            if touch.pos[0]>656.0 and touch.pos[0]<715 and touch.pos[1]>432 and touch.pos[1]<491:
                print("Change Song Right")
                print("gameState:"+str(gameState))
                changeSong(True)
            if touch.pos[0]>120.0 and touch.pos[0]<188 and touch.pos[1]>432 and touch.pos[1]<491:
                print("Change Song False")
                changeSong(False)
        if gameState is 3:
            
            if touch.pos[0]>32.0 and touch.pos[0]<106 and touch.pos[1]>631 and touch.pos[1]<704:
                # main.MyMaingameState3.run()
                songScore = str(ntpath.basename(songSelected))
                writeToCSV(songScore)
                previousState = gameState
                gameState = 4
                changeState()
                # gameState3.on_stop()
                game.sound.stop()
                done = True
                writeToCSV(songScore)
                
            #TapButton1    
            if touch.pos[0]>263.0 and touch.pos[0]<355 and touch.pos[1]>51 and touch.pos[1]<170:
                # print("Lane 1 Condition: ",game.check_all_circles(lane = 1))
                for e in hittableCircles:
                    if e.pos[1]<170 and e.pos[0] is x1:
                        # print("e:",e)
                        e.stop_callbacks()
                        game.remove_entity(e)
                        game.add_entity(Explosion(e.pos,True))
                        game.score += 1
                        consequentHits +=1
                        hittableCircles.remove(e)
                        return 
                
            #TapButton2
            if touch.pos[0]>396.0 and touch.pos[0]<486 and touch.pos[1]>51  and touch.pos[1]<170:
                # print("Lane 2 Condition: ",game.check_all_circles(lane = 2))
                for e in hittableCircles:
                    # print("e:",e )

                    if e.pos[1]<170 and e.pos[0] is x2:
                        e.stop_callbacks()
                        game.remove_entity(e)
                        game.add_entity(Explosion(e.pos,True))
                        game.score += 1
                        consequentHits +=1
                        hittableCircles.remove(e)
                        return 
            #TapButton3
            if touch.pos[0]>526.0 and touch.pos[0]<623 and touch.pos[1]>51 and touch.pos[1]<170:
                # print("Lane 3 Condition: ",game.check_all_circles(lane = 3))
                for e in hittableCircles:
                    # print("e:",e)
                    if e.pos[1]<170 and e.pos[0] is x3:
                        e.stop_callbacks()
                        game.remove_entity(e)
                        game.add_entity(Explosion(e.pos,True))
                        game.score += 1
                        consequentHits +=1
                        hittableCircles.remove(e)
                        return 
            #TapButton4
            if touch.pos[0]>661.0 and touch.pos[0]<756 and touch.pos[1]>51 and touch.pos[1]<170:
                # print("Lane 4: ",game.check_all_circles(lane = 4))
                for e in hittableCircles:
                    # print("e:",e)
                    if e.pos[1]<170 and e.pos[0] is x4:
                        e.stop_callbacks()
                        game.remove_entity(e)
                        game.add_entity(Explosion(e.pos,True))
                        game.score += 1
                        consequentHits +=1
                        hittableCircles.remove(e)
                        return 
            #TapButton5
            if touch.pos[0]>794.0 and touch.pos[0]<887 and touch.pos[1]>51 and touch.pos[1]<170:
                # print("Lane 5: ",game.check_all_circles(lane = 5))
                for e in hittableCircles:
                    if e.pos[1]<170 and e.pos[0] is x5:
                        e.stop_callbacks()
                        game.remove_entity(e)
                        game.add_entity(Explosion(e.pos,True))
                        game.score += 1
                        consequentHits +=1
                        hittableCircles.remove(e)
                        return 
            #TapButton6
            if touch.pos[0]>929.0 and touch.pos[0]<1024 and touch.pos[1]>51 and touch.pos[1]<170:
                # print("Lane 5: ",game.check_all_circles(lane = 6))
                for e in hittableCircles:
                    if e.pos[1]<170 and e.pos[0] is x6:
                        e.stop_callbacks()
                        game.remove_entity(e)
                        game.score += 1
                        game.add_entity(Explosion(e.pos,True))
                        consequentHits +=1
                        hittableCircles.remove(e)
                        return 
            else:
                consequentHits = 0
        if gameState is 4:
            #Play again
            if touch.pos[0]>814.0 and touch.pos[0]<1114 and touch.pos[1]>451 and touch.pos[1]<541:
                previousState = gameState
                gameState = 3
                changeState()
                game.score = 0
                # startGameState3()
                reinitialize_threads()
                game.sound = SoundLoader.load(
                "./songs/song.wav")
                noteGenerationThread.start()
                musicStartThread.start()                
                
                # A = self._entities
                # for e in A:
                #     self.remove_entity(A)

                
            #To Songs
            if touch.pos[0]>814.0 and touch.pos[0]<1114 and touch.pos[1]>210 and touch.pos[1]<307:
                previousState = gameState
                gameState = 2
                game._highscore_label.text = songSelected
                game._highscore_label.font = 15
                game._highscore_label.refresh()
                changeState()
                reinitialize_threads()
                # showSongList()
    def on_touch_move(self, touch):
        # print("Mouse Move", touch)
        pass
    def on_touch_up(self, touch):
        # print("Mouse Up------------", touch)
        pass
    def __init__(self, **kwargs):
        global timer
        super().__init__(**kwargs)

        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        self._keyboard.bind(on_key_up=self._on_key_up)

        self._score_label = CoreLabel(text="Score: 0",font_size=40)
        self._score_label.refresh()
        self._score = 0
        self._highscore_label = CoreLabel(text=str(songSelected),font_size=15)
        self._highscore_label.refresh()
        self._highscore = 0
            
        self.register_event_type("on_frame")

        with self.canvas:
            self._background_instruction = Rectangle(source="./assets/START.png", pos=(0, 0),
                      size=(Window.width, Window.height))
            self._score_instruction =     Rectangle(texture=self._score_label.texture, pos=(
                2000, 2000), size=self._score_label.texture.size)
            self._highscore_instruction = Rectangle(texture=self._highscore_label.texture, pos=(
                2000, 2000), size=self._highscore_label.texture.size)
                
        self.keysPressed = set()
        self._entities = set()
        Clock.schedule_interval(self._on_frame, 0)
        # Clock.schedule_interval(self.spawn_enemies, 2)
    def spawn_enemies(self):
            print("spawn_enemies")
        # for i in range(5):  
         #   random_speed = random.randint(100, 300)
        
            self.add_entity(TapButton((x1, 50)))
            self.add_entity(TapButton((x2, 50)))
            self.add_entity(TapButton((x3, 50)))
            self.add_entity(TapButton((x4, 50)))
            self.add_entity(TapButton((x5, 50)))
            self.add_entity(TapButton((x6, 50)))
        # pass
    def _on_frame(self, dt):
        self.dispatch("on_frame", dt)

    def on_frame(self, dt):
        global consequentHits
        global hittableCircles
            # shoot
        if "d" in game.keysPressed: 
            # game.add_entity(HitCircle((186, Window.height - 50)))
            for e in hittableCircles:
                if e.pos[1]<170 and e.pos[0] is x1:
                    # print("e:",e)
                    e.stop_callbacks()
                    game.remove_entity(e)
                    game.add_entity(Explosion(e.pos,True))
                    game.score += 1
                    consequentHits +=1
                    hittableCircles.remove(e)
                    return 
        if "f" in game.keysPressed: 
            # print("Lane 2 Condition: ",game.check_all_circles(lane = 2))
            for e in hittableCircles:
                # print("e:",e )

                if e.pos[1]<170 and e.pos[0] is x2:
                    e.stop_callbacks()
                    game.remove_entity(e)
                    game.add_entity(Explosion(e.pos,True))
                    game.score += 1
                    consequentHits +=1
                    hittableCircles.remove(e)
                    return 
        if "g" in game.keysPressed: 
            for e in hittableCircles:
                # print("e:",e)
                if e.pos[1]<170 and e.pos[0] is x3:
                    e.stop_callbacks()
                    game.remove_entity(e)
                    game.add_entity(Explosion(e.pos,True))
                    game.score += 1
                    consequentHits +=1
                    hittableCircles.remove(e)
                    return 
        if "h" in game.keysPressed: 
            for e in hittableCircles:
                # print("e:",e)
                if e.pos[1]<170 and e.pos[0] is x4:
                    e.stop_callbacks()
                    game.remove_entity(e)
                    game.add_entity(Explosion(e.pos,True))
                    game.score += 1
                    consequentHits +=1
                    hittableCircles.remove(e)
                    return 
        if "j" in game.keysPressed: 
            # print("Lane 5: ",game.check_all_circles(lane = 5))
            for e in hittableCircles:
                if e.pos[1]<170 and e.pos[0] is x5:
                    e.stop_callbacks()
                    game.remove_entity(e)
                    game.add_entity(Explosion(e.pos,True))
                    game.score += 1
                    consequentHits +=1
                    hittableCircles.remove(e)
                    return 
        if "k" in game.keysPressed: 
                # print("Lane 5: ",game.check_all_circles(lane = 6))
            for e in hittableCircles:
                if e.pos[1]<170 and e.pos[0] is x6:
                    e.stop_callbacks()
                    game.remove_entity(e)
                    game.score += 1
                    game.add_entity(Explosion(e.pos,True))
                    consequentHits +=1
                    hittableCircles.remove(e)
                    return 

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        self._score = value
        self._score_label.text = "Score: " + str(value)
        self._score_label.refresh()
        self._score_instruction.texture = self._score_label.texture
        self._score_instruction.size = self._score_label.texture.size

    def add_entity(self, entity):
        self._entities.add(entity)
        self.canvas.add(entity._instruction)

    def remove_entity(self, entity):
        if entity in self._entities:
            self._entities.remove(entity)
            self.canvas.remove(entity._instruction)

    def circle_is_hittable(self, e1, e2):
        global lanes
        r1x = e1.pos[0]
        r1y = e1.pos[1]
        r2x = e2.pos[0]
        r2y = e2.pos[1]
        r1w = e1.size[0]
        r1h = e1.size[1]
        r2w = e2.size[0]
        r2h = e2.size[1]

        if (r1x < r2x + r2w and r1x + r1w > r2x and r1y < r2y + r2h and r1y + r1h > r2y):
            self.difficultyChange()
            
            return True
        else:
            self.difficultyChange()
            return False
    def difficultyChange(self):
        global lanes
        global consequentHits
        if consequentHits is 10 and lanes is not 6:
            lanes +=2
            consequentHits = 0
        if consequentHits is -3 and lanes is not 2:
            lanes -=2
            consequentHits = 0
    def check_all_circles(self, entity):
        result = set()
        eSet = self._entities
        for e in eSet:
            if self.circle_is_hittable(e, entity) and e == entity:
                result.add(e)
        return result
        

    def _on_keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard.unbind(on_key_up=self._on_key_up)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        self.keysPressed.add(keycode[1])

    def _on_key_up(self, keyboard, keycode):
        text = keycode[1]
        if text in self.keysPressed:
            self.keysPressed.remove(text)
class Entity(object):
    def __init__(self):
        self._pos = (0, 0)
        self._size = (50, 50)
        self._source = "assets/TapButton.png"
        self._instruction = Rectangle(
            pos=self._pos, size=self._size, source=self._source)

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        self._pos = value
        self._instruction.pos = self._pos

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value
        self._instruction.size = self._size

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, value):
        self._source = value
        self._instruction.source = self._source
class HitCircle(Entity):
    def __init__(self, pos, speed=300):
        super().__init__()
        # sound = SoundLoader.load("assets/bullet.wav")
        # sound.play()
        self._speed = speed
        self.pos = pos
        self.source = "./assets/hitcircle.png"
        game.bind(on_frame=self.move_step)

    def stop_callbacks(self):
        game.unbind(on_frame=self.move_step)

    def move_step(self, sender, dt):
        # t1_start = perf_counter()  
        global consequentHits
        global hittableCircles
        # check for collision/out of bounds
        if self.pos[1] < 55:
            # print("Circle < 50")
            # print("Source:",self.source)
            self.stop_callbacks()
            game.remove_entity(self)
            game.add_entity(Explosion(self.pos,False))
            hittableCircles.remove(self)
            consequentHits-=1
            return
        for e in game.check_all_circles(self):
            if isinstance(e, HitCircle):
                hittableCircles.add(self)
                # self.stop_callbacks()
                # game.remove_entity(self)
                # # e.stop_callbacks()
                # # game.remove_entity(e)
                # game.score += 1
                # consequentHits +=1
       
        # move
        self._speed = 500
        step_size = self._speed * dt
        new_x = self.pos[0]
        new_y = self.pos[1] - step_size
        
        self.pos = (new_x, new_y)
class TapButton(Entity):
    def __init__(self, pos):
        super().__init__()
        self.pos = pos
        self.source = "assets/TapButton.png"
    def stop_callbacks(self):
        game.unbind(on_frame=self.move_step)
previousState = 0
def changeState():
    print("changeBG")
    global gameState
    
    with game.canvas:
        if gameState is 99:
            game.canvas.remove(game._background_instruction)
            game._background_instruction = Rectangle(source="assets/loadingscreen6.png", pos=(0, 0),
                      size=(Window.width, Window.height))
        if gameState is 1:
            source = "assets/START.png"
            game.canvas.remove(game._background_instruction)
            game.canvas.remove(game._score_instruction)
            game._background_instruction = Rectangle(source=source, pos=(0, 0),
                      size=(Window.width, Window.height))
            game._score_instruction = Rectangle(texture=game._score_label.texture, pos=(
                2000, 2000), size=game._score_label.texture.size)                
        if gameState is 2:
            source = "assets/SONGLIST.png"
            game.canvas.remove(game._background_instruction)
            game.canvas.remove(game._score_instruction)
            game.canvas.remove(game._highscore_instruction)
            game._background_instruction = Rectangle(source=source, pos=(0, 0),
                      size=(Window.width, Window.height))
            game._score_instruction = Rectangle(texture=game._score_label.texture, pos=(
                2000, 2000), size=game._score_label.texture.size) 
            game._highscore_instruction = Rectangle(text = str(songSelected),texture=game._highscore_label.texture, pos=(
                232 , 456), size=game._highscore_label.texture.size)
        if gameState is 3:
            if(previousState is not 4):
                initializeEverything()
            game.spawn_enemies()
            source = "assets/BEATMAP.png"
            game.canvas.remove(game._background_instruction)
            game.canvas.remove(game._score_instruction)
            
            # game._highscore_instruction = Rectangle(text = "Controls from Left to Right: D, F, G, H, J, K",texture=game._highscore_label.texture, pos=(
            #     230 , 30), size=game._highscore_label.texture.size)
            game._background_instruction = Rectangle(source=source, pos=(0, 0),
                      size=(Window.width, Window.height))
            game._score_instruction = Rectangle(texture=game._score_label.texture, pos=(
                593.0, 673.0), size=game._score_label.texture.size) 
        if gameState is 4:

            source = "assets/HIGHSCORE.png"
            game.canvas.remove(game._background_instruction)
            game.canvas.remove(game._highscore_instruction)
            game._background_instruction = Rectangle(source=source, pos=(0, 0),
                      size=(Window.width, Window.height))
            
            game._highscore_instruction = Rectangle(texture=game._highscore_label.texture, pos=(
                370 , 510), size=game._highscore_label.texture.size)
            game._score_instruction = Rectangle(text = str(game.score),texture=game._score_label.texture, pos=(
                310, 315), size=game._score_label.texture.size)   
class Explosion(Entity):
    def __init__(self, pos, hit):
        super().__init__()
        self.pos = pos
        # sound = SoundLoader.load("assets/explosion.wav")
        if hit is True:
            self.source = "assets/hit.png"
        else:
            self.source = "assets/miss.png"
        # sound.play()
        Clock.schedule_once(self._remove_me, 0.089)

    def _remove_me(self, dt):
        game.remove_entity(self)
done = False
last_lane = 1
class NoteGeneratorThread(threading.Thread):
    def __init__(self, threadID, name, counter):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.counter = counter
    def run(self):
        print("NoteGeneratorThread Called")
    # "Thread-x finished!"
        global lanes
        while(done is not True):
            second = random.randrange(1, 1000)
            game.generate_note()
            game.onset_ctr+=1
            if second>500:
                game.generate_note()
            if second>500 and 700>second and lanes > 2:
                game.generate_note()
            print("timer: "+str(timer))
            time.sleep(timer)
class MusicStarterThread(threading.Thread):
    def __init__(self, threadID, name, counter):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.counter = counter
    def run(self):
        print("MusicStarterThread")
    # "Thread-x finished!"
        time.sleep(.96)
        game.sound.play()

def reinitialize_threads():
    print("reinitialize_threads")
    
    global noteGenerationThread
    global musicStartThread
    global timer
    global beats
    global lanes
    global done
    done = False
    global consequentHits
    game.onset_ctr = 0
    timer = beats[0]
    lanes = 2
    consequentHits = 0
    noteGenerationThread = NoteGeneratorThread(threadID = 1,name = "Note Generator",counter=1)
    musicStartThread = MusicStarterThread(threadID=2,name = "Music Starter",counter=2)  
def writeToCSV(songName):
    scores = {None:None}
    print("write to csv: "+str(songName))
    with open('highscores.csv', mode='r') as infile:
        reader = csv.reader(infile)
        scores = {rows[0]:rows[1] for rows in reader}
    
    if songName in scores:
        print("int(scores[songName]) "+str(int(scores[songName])))
        intt = int(scores[songName])
        if intt > game.score:
            game._highscore_label = CoreLabel(text=str(intt),font_size=40)
            game._highscore_label.text = str(intt)
            game._highscore_label.refresh()
            print("intt > game.score")
        else:
            scores[songName] = game.score
            print("Else scores[songName] = game.score: "+str(game.score))
    else:
        scores[songName] = game.score
        print("Else scores[songName] = game.score: "+str(game.score))
    with open('highscores.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        for e in scores:
            writer.writerow([e, scores.get(e)])  
def getAllSongs():
    global songFolder
    global songs
    global songSelected
    path = librosa.util.find_files(songFolder)
    songs = [] #change into a dictionary
    for p in path:
        songName = str(ntpath.basename(p))
        songs.append(songName)
        print("Song: "+str(songName))
    songSelected = str(songs[0])
    print("songSelected:"+songSelected)
def changeSong(goingRight):
    global songs
    global songSelected
    i = songs.index(songSelected)
    print(songSelected)
    if goingRight is True:
        if i+1 > len(songs)-1:
            i = 0
            songSelected = songs[i]
        else:
            songSelected = songs[i+1]
            
    else:
        if i-1 < 0:
            i = len(songs)-1
            songSelected = songs[i]
        else:
            songSelected = songs[i-1]
    with game.canvas:
        game.canvas.remove(game._highscore_instruction)
        game._highscore_label = CoreLabel(text=str(songSelected[0:56]),font_size=15)
        game._highscore_label.refresh()
        game._highscore_instruction = Rectangle(text = str(songSelected[0:56]),texture=game._highscore_label.texture, pos=(
                232 , 456), size=game._highscore_label.texture.size)
        game._highscore_label.refresh()
    print("i read the code here") 
class MyApp(App):

    def build(self):
        print("App.run()")
        noteGenerationThread = NoteGeneratorThread(threadID = 1,name = "Thread-Test",counter=1)
        return game
    def on_stop(self):
        print("on_stop")
        global done
        done = True
        exit()
        return super().on_stop()
songs = [] #change into a dictionary
songFolder = "./songs/"
songSelected = f"DEAF KEV - Invincible [NCS Release].mp3"
if __name__ == "__main__":
    print("__main__")
    getAllSongs()
    game = GameWidget()
    app = MyApp()
    app.run()
