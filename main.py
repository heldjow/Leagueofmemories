import kivy
kivy.require('1.0.9')
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.scatter import Scatter
from kivy.uix.togglebutton import ToggleButton
from kivy.core.audio import SoundLoader
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.animation import Animation
from kivy.properties import StringProperty, ObjectProperty,NumericProperty
from kivy.uix.progressbar import ProgressBar
from random import choice,shuffle
from glob import glob
from os.path import dirname, join, basename,sep, splitext
import json
from kivy.core.window import Window

DEFAULT_SHOWTIME = 10
DEFAULT_NBITEMS = 12
MAX_NBITEMS = None


def bestRatio(nb,width,height):
    row=1
    correctRatio=1.
    minErr=None
    nbparrow = nb/row
    if nb%row !=0:
        nbparrow+=1
    x = float(width)/nbparrow
    y = float(height)/row
    ratio=x/y
    minErr=abs(ratio-correctRatio)
    while ratio<correctRatio:
        row+=1
        nbparrow = nb/row
        if nb%row !=0:
            nbparrow+=1
        x = float(width)/nbparrow
        y = float(height)/row
        ratio=x/y
        if abs(ratio-correctRatio)>minErr:
            row-=1
        minErr = abs(ratio-correctRatio)
    return row

class MemoryButton(Button):
    done=False
    playsound=True
    filenameSound = StringProperty(None)
    filenameIcon = StringProperty(None)
    sound = ObjectProperty(None)
    background = ObjectProperty(None)
    background_hide = ObjectProperty(None)
    #background_down = ObjectProperty(None)
    background_normal = ObjectProperty(None)

    def on_filenameSound(self, instance, value):
        # the first time that the filename is set, we are loading the sample
        if self.sound is None:
            self.sound = SoundLoader.load(value)
    
    def on_filenameIcon(self, instance, value):
        # the first time that the filename is set, we are loading the sample
        if self.background_normal is None:
            self.background_normal=value
            self.background = value
            self.background_down = "carta.jpg"
            self.background_hide = self.background_down
            
    @classmethod
    def toggleSound(cls,instance):
        instance.text = ["Som Ligado" if instance.state == 'normal' else "Som desligado"][0]
        cls.playsound = instance.state == 'normal'

    def on_press(self):
        if self.parent.state=='OK' and not self.done: 
            if self.parent.first is None:
                self.parent.first = self
                self.background_down,self.background_normal = self.background_normal,self.background_down
            else:
                if self is self.parent.first:
                    self.parent.first==None
                elif self.parent.first.filenameIcon == self.filenameIcon:
                    print("youhou!!")
                    self.parent.left+=1
                    if self.playsound:
                        if self.sound.state != 'stop':
                            self.sound.stop()
                        self.sound.play()
                   
                    self.background_down,self.background_normal = self.background,self.background
                    self.parent.first.background_down,self.parent.first.background_normal = self.parent.first.background,self.parent.first.background
                    self.done=True
                    self.parent.first.done=True
                    self.parent.first = None
                    #check termination
                    if self.parent.left == self.parent.items:
                        self.parent.gameOver()
                        Clock.unschedule(self.parent.elapsedTime)

                else:
                    self.parent.missed += 1
                    self.parent.first.background_down,self.parent.first.background_normal = self.parent.first.background_normal,self.parent.first.background_down
                    self.parent.first =None
                    if self.parent.missed >= 20:  # Verifica se atingiu o limite de 20 erros
                        self.parent.gameOver()

class MemoryLayout(GridLayout):
    left = NumericProperty(0)   #left items to find
    items = NumericProperty(0)  #total number of items
    level = NumericProperty(0)  #seconds to count down
    countdown = NumericProperty(0)
    missed = NumericProperty(0) # number of missed items
    elapsed = NumericProperty(0)
    click_sound1 = None 
    click_sound2 = None
    click_sound3 = None


    def on_start_easy(self, *args):
        self.reset() 
        self.level = 5
        self.items = 6
        self.click_sound1.play()
        Clock.schedule_interval(self.initialCountdown, 10)

    def on_start_medium(self, *args):
        self.reset()
        self.level = 5
        self.items = 14
        self.click_sound2.play()
        Clock.schedule_interval(self.initialCountdown, 10)

    def on_start_hard(self, *args):
        self.reset()
        self.level = 10
        self.items = 24
        self.click_sound3.play()
        Clock.schedule_interval(self.initialCountdown, 20)
         

    def __init__(self, **kwargs):
        super(MemoryLayout, self).__init__(**kwargs)
        self.state = ""
        self.first=None
        self.level=kwargs["level"]
        self.items=kwargs["items"]
        self.countdown= self.level
        self.click_sound1 = SoundLoader.load('sounds/bvs.mp3')
        self.click_sound2 = SoundLoader.load('sounds/preparar.mp3')
        self.click_sound3 = SoundLoader.load('sounds/10sec.mp3')

    def toggleButtons(self,state):
        for i in self.children:
            i.background_down,i.background_normal = i.background_normal,i.background_down
        self.state=state 

    def hideButtons(self):
        for i in self.children:
            i.done=False
            i.background_down,i.background_normal = i.background_hide,i.background_hide
            
    def showButtons(self):
        for i in self.children:
            i.background_normal = i.background
            
    def elapsedTime(self,dt):
        self.elapsed += dt

    def startGame(self,dt):
        self.reset()
        Clock.schedule_interval(self.initialCountdown,1)
        
    def initialCountdown(self,dt):
        if self.countdown == -1:
            Clock.unschedule(self.initialCountdown)
            self.toggleButtons("OK")
            Clock.schedule_interval(self.elapsedTime,0.1)
        else:
            if not hasattr(self.parent.parent,'countdown'):
                self.parent.parent.countdown=Label(text="")
                self.parent.parent.add_widget(self.parent.parent.countdown)
            popup=self.parent.parent.countdown
            popup.text=''
            popup.font_size=12
            popup.color=(0,0,0,1)
            popup.text=str(self.countdown)
            Animation(color=(1,1,1,0),font_size=100).start(popup)
            self.countdown -= 1

    def resetTime(self,instance,newLevel):
        self.level=int(newLevel)

    def resetNbItem(self,instance,newNb):
        self.items = int(newNb)

    def reset(self):
        self.countdown = self.level
        self.first = None
        self.left = 0
        self.elapsed = 0
        self.missed = 0
        self.hideButtons()
        self.state = ''
        self.updateNbItems()
 
    def restartGame(self,inst):
        self.reset()
        self.showButtons()
        Clock.schedule_interval(self.initialCountdown,1)

    def updateNbItems(self):
        if self.items != len(self.children):
            #update self.rows to keep acceptable ratio
            newRow = bestRatio(self.items*2,self.width,self.height)
            self.clear_widgets()
            self.rows=newRow
            shuffle(icons)
            iicons=icons[:self.items]
            iicons=iicons+iicons
            shuffle(iicons)

            for i in iicons:
                s = i.split(".png")[0].split(sep)[-1]
                if s in sounds:
                    aSound = choice(sounds[s])
                else:
                    aSound = "random1.wav"

                # Impressões para depuração
                print("i:", i)
                print("aSound:", aSound)
                print("\n")
                print(s)

                btn = MemoryButton(
                    text="",
                    filenameIcon=i,
                    filenameSound=aSound,
                )  
                self.add_widget(btn)
        else:
            shuffle(self.children)

            
    def gameOver(self):
        
        content2 = BoxLayout(orientation='vertical',spacing=10)
        #content.add_widget(Label(text='score: %d'%int(score)))
        content = BoxLayout(orientation='vertical',size_hint_y=.7)
        #change show time
        labelSlider = LabelTimeSlider(text='Contagem para memorização: %s s'%self.level)
        content.add_widget(labelSlider)
        newLevel = Slider(min=1, max=30, value=self.level)
        content.add_widget(newLevel)
        newLevel.bind(value = labelSlider.update)
        newLevel.bind(value = self.resetTime) 


        #change number of items
        labelNb = LabelNb(text='Número de cartas: %s'%self.items)
        content.add_widget(labelNb)
        nb_items = Slider(min=5, max = MAX_NBITEMS, value = self.items )
        content.add_widget(nb_items)
        nb_items.bind(value = labelNb.update)
        nb_items.bind(value = self.resetNbItem)
       
        content2.add_widget(content)

        replay = Button(text='Jogar!', background_color=(0.5, 0.5, 1, 1))
        info = Button(text='Informações', background_color=(0.5, 0.5, 1, 1))
        action = BoxLayout(orientation='horizontal',size_hint_y=.2)
        action.add_widget(replay)
        action.add_widget(info)
        content2.add_widget(action)


        popup = PopupGameOver(title='Fim de jogo! Faça sua partida personalizada:',
                              content=content2,
                              size_hint=(0.5, 0.5),pos_hint={'x':0.25, 'y':0.25},
                              auto_dismiss=False)
        replay.bind(on_press=popup.replay)
        replay.bind(on_press=self.restartGame)
        info.bind(on_press=popup.info)
        popup.open()

class ScrollableLabel(ScrollView):
   
    '''
   use it thisly -> scrollablelabel = ScrollableLabel().build("put your big bunch of text right here")
       or
   ScrollableLabel().build() <- thusly with no argument to just get a very big bunch of text as a demo
   
   scrolls x and y default
   '''
 
    def build(self,textinput,size):
        self.summary_label = Label(text="",text_size=(size,None),
                              size_hint_y=None,size_hint_x=None)
       
        self.summary_label.bind(texture_size=self._set_summary_height)
        # remove the above bind
        self.summary_label.text = str(textinput)
       
        #and try setting height in the following line
        self.sv = ScrollView(do_scroll_x=False)
        # it does not scroll the scroll view.
       
        self.sv.add_widget(self.summary_label)
       
        return self.sv
   
    def _set_summary_height(self, instance, size):
        instance.height = size[1]
        instance.width = size[0]
       
class PopupGameOver(Popup):
    def replay(self,inst):
        self.dismiss()
     
    def info(self,inst):
        with open(join(dirname(__file__),'info'),'r') as f:
            ti=f.read()
        content = BoxLayout(orientation='vertical')
        close = Button(text='Fechar',size_hint=(1,.1))
        sv = ScrollableLabel().build(ti,Window.width-20)
        content.add_widget(sv)
        content.add_widget(close)
        popup = Popup(title='2VA PISI 1',
                        content=content, auto_dismiss=False
                    ) 
        close.bind(on_press=popup.dismiss)
        popup.open()

class LabelTimeSlider(Label):
    def update(self,instance,value):
        self.text="Contagem para memorização: %d s"%int(value)

class LabelNb(Label):
    def update(self,instance,value):
        self.text="Número de cartas: %d"%int(value)

class MyPb(ProgressBar):
    def foundAnItem(self,instance,value):
        self.value = value

    def newNbItems(self,instance,value):
        self.value = value
        self.max = value
    

class LabelMissed(Label):
    def update(self,instance,value):
        self.text="Erros: %d"%value

def loadData():
    sounds={}
    icons=[]
    for s in glob(join(dirname(__file__),"sounds", '*.mp3')):
        name=basename(s[:-4]).split("_")[0]
        if name in sounds:
            sounds[name].append(s)
        else:
            sounds[name]=[s]
    for i in glob(join(dirname(__file__),"icons", '*.png')):
        icons.append(i)
    return sounds,icons
 

class MyLolApp(App):
    
    def loadLevel(self):
        fileName =  join(App.get_running_app().user_data_dir,'level.dat')
        try:
            with open(fileName) as fd:
                userData={}
                userData = json.load(fd)
                return userData["items"],userData["level"]
        except:
            return DEFAULT_NBITEMS , DEFAULT_SHOWTIME
        
    def build(self):
        self.icon = 'league_bw.png'
        self.title = 'League of Memories'
        global sounds,icons
        sounds,icons=loadData()
        #showmissingSounds()

        global MAX_NBITEMS
        MAX_NBITEMS = 64
        items,level = self.loadLevel()
        g = MemoryLayout(rows=4,items =items, level=level,size_hint=(1,.9))
        
        config = BoxLayout(orientation='horizontal',spacing=10, size_hint=(.4,.11), pos_hint={'right': 1})
        
        sound = ToggleButton(text='Som Ligado', size_hint=(0.15,1), background_color=(0.5, 0, 0.5, 1), bold=True)
        sound.bind(on_press=MemoryButton.toggleSound)

        barra = BoxLayout(orientation='horizontal',spacing=10, size_hint=(1,.05))
        pb = MyPb(max=items, size_hint=(1,1))
        
        missed =  LabelMissed(text="Erros:  0",size_hint=(0.15,1), color=(1, 0, 0, 1), bold=True, font_size=24, italic=True)
        
        barra.add_widget(pb)
        config.add_widget(missed)
        config.add_widget(sound)
        
        g.bind(missed=missed.update)             
        g.bind(left=pb.foundAnItem)
        g.bind(items=pb.newNbItems)

        playZone = BoxLayout(orientation='vertical')
        playZone.add_widget(g)
        playZone.add_widget(barra)
        playZone.add_widget(config)
        

        difficulty_buttons = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, size_hint_x=0.6, height=60)
        easy_button = Button(text='Bronze',  font_size=20, color=(1, 1, 1, 1), background_color=(0.8039, 0.4980, 0.1961, 1.0))
        medium_button = Button(text='Prata', font_size=20, color=(1, 1, 1, 1), background_color=(0.75, 0.75, 0.75, 1))
        hard_button = Button(text='Ouro', font_size=20, color=(1, 1, 1, 1), background_color=(1.0, 0.8431, 0.0, 1.0))

        difficulty_buttons.add_widget(easy_button)
        difficulty_buttons.add_widget(medium_button)
        difficulty_buttons.add_widget(hard_button)  
        
        root=FloatLayout()
        root.add_widget(Image(source='goat5.jpg',allow_stretch=True,keep_ratio=False))
        root.add_widget(playZone)
        root.add_widget(difficulty_buttons)
        #Adicionei restartGame pq estava bugando anteriormente, precisava clicar 2x no notão para funcionar
        easy_button.bind(on_press=g.restartGame)
        easy_button.bind(on_press=g.on_start_easy)
        medium_button.bind(on_press=g.restartGame)
        medium_button.bind(on_press=g.on_start_medium)
        hard_button.bind(on_press=g.restartGame)
        hard_button.bind(on_press=g.on_start_hard)


        return root

if __name__ in ('__main__', '__android__'):
    MyLolApp().run()