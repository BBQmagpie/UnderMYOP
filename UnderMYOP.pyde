#***User name can currently only be changed in save.txt file externally***# 
#***Continue mode not yet implemented***# 

import os
import random
import math
import copy
add_library("minim")
add_library("sound")

PATH=os.getcwd()
ACTION=[[191,1128],[606,1128],[1003,1128],[1385,1128]] #the coordinates of the heart during battle break are fixed sets
ITEMCHOOSE=[[218,604],[218,677],[218,748],[218,822],[218,894]]
BATTLEPOS=[687,1112,543,968] #minx, maxx, miny, maxy of the heart during battle
CD=420 #frames for one round of battle

fontPapyrus=loadFont(PATH+"/data/Papyrus-Regular-48.vlw")


#the player controls Frisk in map mode but the heart in fight mode, all follow the player class
class Player:
    def __init__(self,x,y,r,w,h,F,img,n):
        self.x=x #x coordinate
        self.y=y #y coordinate
        self.r=r #radius
        self.vx=0 #x speed
        self.vy=0 #y speed
        self.w=w #frame width
        self.h=h #frame height
        self.F=F #total frame number
        self.f=0 #current frame
        self.dir=2 #up/down/left/right->1,2,3,4
        self.img=loadImage(PATH+"/images/{0}.png".format(img))
        self.n=n #player's name
        self.keyHandler={LEFT:False,RIGHT:False,UP:False,DOWN:False,ENTER:False}
        self.hide=False #in case the character needs to be hidden for text display

    def update(self):
        if self.keyHandler[LEFT]:
            self.vx=-5
            self.dir=3
        if self.keyHandler[RIGHT]:
            self.vx=5
            self.dir=4
        if self.keyHandler[UP]:
            self.vy=-5
            self.dir=1
        if self.keyHandler[DOWN]:
            self.vy=5
            self.dir=2

        self.x+=self.vx
        self.y+=self.vy
        
    def display(self):
        if not self.hide:
            self.update()
            if self.vx!=0 or self.vy!=0:
                self.f=(self.f+0.2)%self.F
            else:
                self.f=0
            image(self.img,self.x-self.r,self.y-self.r,self.w,self.h,int(self.f)*self.w,0,(int(self.f)+1)*self.w,self.h)
        #stroke(255)
        #strokeWeight(1)
        #noFill()
        #circle(self.x,self.y,self.r*2)
        
#for map mode, not implemented
class Frisk(Player):
    def __init__(self,x,y,r,w,h,F,img,n):
        Player.__init__(self,x,y,r,w,h,F,img,n)

#for battle mode
class Heart(Player):
    def __init__(self,x,y,r,w,h,F,img,n,g,m,action):
        Player.__init__(self,x,y,r,w,h,F,img,n)
        self.g=g
        self.m=m #mode:"red"(free move)/"blue"(gravity applied)
        self.action=action #during fight break the player can choose from fight/act/item/mercy, before choosing one the player is on "choose" action
        self.actionIndex=0 #record which action is the heart on
        self.cold=0 #change of action must be spaced by 6 frames, cold records the frame count
        self.hp=20
        self.noHurtTime=0 #when hurt, cannot be hurt again within this number of frames
    
    #only under blue heart mode will gravity be applied
    def gravity(self):
        if self.y+self.r<self.g:
            self.vy+=0.3
            if self.y+self.r+self.vy>self.g:
                self.vy=self.g-self.y-self.r
        else:
            self.vy=0
        for p in game.platforms:
            if self.y+self.r<=p.y and self.x+self.r>p.x and self.x-self.r<p.x+p.w:
                self.g=p.y
                return
        self.g=game.g
        
    def update(self):
        if self.noHurtTime!=0:
            self.noHurtTime-=1
        #during battle the heart is free to move within the box
        #if hp<=0: lose
        if game.m=="bo":
            #look for collisions
            for a in game.attacks:
                if((self.x-a.x)**2+(self.y-a.y)**2)**0.5 <=self.r+a.r: #collision condition
                    if self.noHurtTime==0:
                        self.hp-=2
                        self.noHurtTime=20
            if self.hp<=0:
                game.m="lose"
                self.hide=True
                game.battlebgm.close()
                game.losebgm.play()
                return
            #determine if using blue mode movement (with gravity) or red mode movement (direct move)
            if self.m=="blue":
                self.gravity()
                if BATTLEPOS[0]<=self.x-self.r and self.x+self.r<=BATTLEPOS[1] and BATTLEPOS[2]<=self.y-self.r and self.y+self.r<=game.g: 
                    if self.keyHandler[LEFT]:
                        self.vx=-4
                        self.dir=3
                    elif self.keyHandler[RIGHT]:
                        self.vx=4
                        self.dir=4
                    else:
                        self.vx=0
                    if self.keyHandler[UP] and self.y+self.r==self.g:
                        self.vy=-8
                    self.x+=self.vx
                    self.y+=self.vy
                else:
                    if BATTLEPOS[0]>self.x-self.r:
                        self.x=BATTLEPOS[0]+self.r
                    elif self.x+self.r>BATTLEPOS[1]:
                        self.x=BATTLEPOS[1]-self.r
                    if BATTLEPOS[2]>self.y-self.r:
                        self.y=BATTLEPOS[2]+self.r
                    elif self.y+self.r>game.g:
                        self.y=game.g-self.r
            else:
                if BATTLEPOS[0]<=self.x-self.r and self.x+self.r<=BATTLEPOS[1] and BATTLEPOS[2]<=self.y-self.r and self.y+self.r<=BATTLEPOS[3]: 
                    if self.keyHandler[LEFT]:
                        self.vx=-4
                        self.dir=3
                    elif self.keyHandler[RIGHT]:
                        self.vx=4
                        self.dir=4
                    else:
                        self.vx=0
                    if self.keyHandler[UP]:
                        self.vy=-4
                        self.dir=1
                    elif self.keyHandler[DOWN]:
                        self.vy=4
                        self.dir=2
                    else:
                        self.vy=0
                    self.x+=self.vx
                    self.y+=self.vy
                else:
                    if BATTLEPOS[0]>self.x-self.r:
                        self.x=BATTLEPOS[0]+self.r
                    elif self.x+self.r>BATTLEPOS[1]:
                        self.x=BATTLEPOS[1]-self.r
                    if BATTLEPOS[2]>self.y-self.r:
                        self.y=BATTLEPOS[2]+self.r
                    elif self.y+self.r>BATTLEPOS[3]:
                        self.y=BATTLEPOS[3]-self.r
        #during battle break the heart is allowed only for choices and the coordinates are relatively fixed
        else:
            self.cold+=1
            if self.action=="choose" and self.cold==6:
                if self.keyHandler[LEFT]:
                    if self.actionIndex!=0:
                        self.actionIndex-=1
                elif self.keyHandler[RIGHT]:
                    if self.actionIndex!=3:
                        self.actionIndex+=1
                self.x=ACTION[self.actionIndex][0]
                self.y=ACTION[self.actionIndex][1]
                if self.keyHandler[ENTER]:
                    if self.actionIndex==0:
                        self.action="fight"
                    elif self.actionIndex==1:
                        self.action="act"
                    elif self.actionIndex==2:
                        self.action="item"
                    else:
                        self.action="mercy"
                    self.actionIndex=0
                self.cold=0 #recount
            #player can only move for choices in act/item mode after choose mode
            #if there is no item left, text will be shown
            #if all actions for this level are taken, game goes to the next level
            #when player hits enter in all modes after choose, game goes into battle on mode
            if self.cold==6:
                if self.action=="act":
                    if self.keyHandler[UP]:
                        if self.actionIndex!=0:
                            self.actionIndex-=1
                    elif self.keyHandler[DOWN]:
                        if self.actionIndex!=len(game.ACTIONTEXT[game.level-1])+len(game.ACTIONCOM)-1:
                            self.actionIndex+=1
                    self.x=ITEMCHOOSE[self.actionIndex][0]
                    self.y=ITEMCHOOSE[self.actionIndex][1]
                    if self.keyHandler[ENTER]:
                        if 0<=self.actionIndex<=len(game.ACTIONTEXT[game.level-1])-1:
                            del game.ACTIONTEXT[game.level-1][self.actionIndex]
                        game.m="bo"
                        game.reactionCountDown=120 #let the game display reaction text before getting into fight
                        self.hide=True #temporarily hide the heart for text display
                elif self.action=="item":
                    if len(game.ITEM)!=0:
                        if self.keyHandler[UP]:
                            if self.actionIndex!=0:
                                self.actionIndex-=1
                        elif self.keyHandler[DOWN]:
                            if self.actionIndex!=len(game.ITEM)-1:
                                self.actionIndex+=1
                        self.x=ITEMCHOOSE[self.actionIndex][0]
                        self.y=ITEMCHOOSE[self.actionIndex][1]
                        if self.keyHandler[ENTER]:
                            del game.ITEM[self.actionIndex]
                            if self.hp<18:
                                self.hp+=2
                            else:
                                self.hp=20
                            game.m="bo"
                            game.reactionCountDown=120
                            self.hide=True
                    else:
                        if self.keyHandler[ENTER]:
                            game.m="bo"
                elif self.action=="fight":
                    if self.keyHandler[ENTER]:
                        game.m="bo"
                elif self.action=="mercy":
                    if self.keyHandler[ENTER]:
                        game.m="bo"
                self.cold=0
                
#
class AttackElement:
    def __init__(self,x,y,w,h,r,img,m,theta=0,centerX=0,centerY=0,rToCenter=0):
        self.x=x
        self.y=y
        self.w=w
        self.h=h
        self.r=r
        self.img=loadImage(PATH+"/images/{0}.png".format(img))
        self.m=m #"g":the element freefall; "r": element goes in a circle from right to left; "m": the element move horizontally from right to left; "s": stay still in the box
        #following attributes only used for "r"
        self.theta=theta
        self.centerX=centerX
        self.centerY=centerY
        self.rToCenter=rToCenter
        if m=="g":
            self.vx=random.randint(-1,1)
            self.vy=random.randint(1,3)
        elif m=="m":
            self.vx=-5
            self.vy=0
        else: #for "s" and "r"
            self.vx=0
            self.vy=0
        if m=="r":
            self.x=self.centerX+self.rToCenter*math.cos(self.theta)-self.r
            self.y=self.centerY-self.rToCenter*math.sin(self.theta)-self.r
        
    def update(self):
        if self.m=="g" and self.y+self.r<=BATTLEPOS[3]:
            self.vy+=0.05
        if self.m=="g" or self.m=="m":
            self.x+=self.vx
            self.y+=self.vy
        if self.m=="r" and BATTLEPOS[0]-self.rToCenter-50<=self.centerX and self.centerX<=BATTLEPOS[1]+self.rToCenter:
            self.centerX-=2
            self.theta+=2.0/180*math.pi
            if self.theta>=2.0*math.pi:
                self.theta-=2.0*math.pi
            self.x=self.centerX+self.rToCenter*math.cos(self.theta)-self.r
            self.y=self.centerY-self.rToCenter*math.sin(self.theta)-self.r
    
    def display(self):
        self.update()
        if BATTLEPOS[0]<=self.x-self.r+self.w and self.x-self.r<=BATTLEPOS[1] and BATTLEPOS[2]<=self.y-self.r+self.h and self.y-self.r<=BATTLEPOS[3]:
            x=self.x-self.r
            y=self.y-self.r
            w=self.w
            h=self.h
            leftX=0
            leftY=0
            rightX=self.w
            rightY=self.h
            if BATTLEPOS[0]<=self.x-self.r and self.x-self.r+self.w<=BATTLEPOS[1] and BATTLEPOS[2]<=self.y-self.r and self.y-self.r+self.h<=BATTLEPOS[3]:
                image(self.img,x,y)
            else:
                if self.x-self.r<BATTLEPOS[0]:
                    x=self.x-self.r+int(BATTLEPOS[0]-self.x+self.r)
                    w=self.w-int(BATTLEPOS[0]-self.x+self.r)
                    leftX=int(BATTLEPOS[0]-self.x+self.r)
                else:
                    w=int(BATTLEPOS[1]-self.x+self.r)
                    rightX=int(BATTLEPOS[1]-self.x+self.r)
                if self.y-self.r<BATTLEPOS[2]:
                    y=self.y-self.r+int(BATTLEPOS[2]-self.y+self.r)
                    h=self.h-int(BATTLEPOS[2]-self.y+self.r)
                    leftY=int(BATTLEPOS[2]-self.y+self.r)
                else:
                    h=int(BATTLEPOS[3]-self.y+self.r)
                    rightY=int(BATTLEPOS[3]-self.y+self.r)
                image(self.img,x,y,w,h,leftX,leftY,rightX,rightY)

class Platform:
    def __init__(self,x,y,w,h,vx,img):
        self.x=x
        self.y=y
        self.w=w
        self.h=h
        self.vx=vx
        self.img=loadImage(PATH+"/images/{0}.png".format(img))
        
    def update(self):
        self.x+=self.vx
    
    def display(self):
        self.update()
        if BATTLEPOS[0]<=self.x+self.w and self.x<=BATTLEPOS[1]:
            if BATTLEPOS[0]<=self.x and self.x+self.w<=BATTLEPOS[1]:
                image(self.img,self.x,self.y)
            else:
                if self.x<BATTLEPOS[0]:
                    image(self.img,self.x+int(BATTLEPOS[0]-self.x),self.y,self.w-int(BATTLEPOS[0]-self.x),self.h,int(BATTLEPOS[0]-self.x),0,self.w,self.h)
                else:
                    image(self.img,self.x,self.y,int(BATTLEPOS[1]-self.x),self.h,0,0,int(BATTLEPOS[1]-self.x),self.h)

def keyPressed():
    if keyCode==LEFT:
        game.player.keyHandler[LEFT]=True
    if keyCode==RIGHT:
        game.player.keyHandler[RIGHT]=True
    if keyCode==UP:
        game.player.keyHandler[UP]=True
    if keyCode==DOWN:
        game.player.keyHandler[DOWN]=True
    if keyCode==10:
        game.player.keyHandler[ENTER]=True

def keyReleased():
    if keyCode==LEFT:
        game.player.keyHandler[LEFT]=False
    if keyCode==RIGHT:
        game.player.keyHandler[RIGHT]=False
    if keyCode==UP:
        game.player.keyHandler[UP]=False
    if keyCode==DOWN:
        game.player.keyHandler[DOWN]=False
    if keyCode==10:
        game.player.keyHandler[ENTER]=False
        
def mouseClicked():
    global game
    if game.m=="lose" or game.m=="win":
        game.battlebgm.close()
        game.losebgm.close()
        game=Game(1800,1240,"menu")
    elif game.m=="menu":
        if 553<=mouseX<=1246:
            if 452<=mouseY<=572:
                game.player.hide=False
                game.m="bb"
                game.menubgm.close()
                game.battlebgm.play()
            #elif 632<=mouseY<=752:
            #    game.player.hide=False
            #    game.m="bb"
            #   game.menubgm.close()
            #   game.battlebgm.play()
            elif 812<=mouseY<=932:
                game.m="rec"
    elif game.m=="rec":
        if 770<=mouseX<=1030 and 1060<=mouseY<=1180:
            game.m="menu"

class Game:
    def __init__(self,w,h,m):
        #prewritten script for dialogues
        #battle break dialogue box text of three levels
        self.BB=[["* Papyrus is choosing the gradients for your pasta","* Papyrus is stir-frying vegetables"],
                 ["* Papyrus is waiting for your choice of sauce","* Papyrus suggests spaghetti"],
                 ["* Papyrus is too busy making the final stir","* Papyrus can't hear you right now","* Papyrus is cooking like a real chef"]]
        #battle on dialogue box text of three levels
        self.DIA=[["Nyeh heh heh!! I will be the greatest pasta chef!","I can smell the jalapeno!","What is the smallest room in the world?"],
                  ["Spaghetti is the BEST!!!","Tomatoes, tomatoes, more TOMATOES!"],
                  ["I'M GONNA BE A FIVE STAR MICHELIN!!!"]]
        #items of player
        self.ITEM=["* Rotten vegan pasta","* Fresh green peas","* Cold fast-done pasta"]
        #reaction to choice of item
        self.REITEM=["* It tastes bad","* What would you expect it to give you?","* There are better choices"]
        #choice of action and reaction
        self.ACTIONTEXT=[["* Choose sweet corns","* Choose jalapeno","* Choose mushroom"],
                         ["* Choose bolognaise","* Choose spaghetti"],
                         ["* Add salt","* Add cheese","* Add SRIRACHA"]]
        self.REACTION=[["* Papyrus agrees","* Papyrus adds it for you before you ask","* Papyrus acquiesces"],
                       ["* Papyrus approves your choice","* Papyrus adds it for you before you ask"],
                       ["* Papyrus add a full spoon of salt just for \nyou","* Papyrus adds blue cheese, cheddar cheese \nand Parmesan cheese for you",
                        "* Do you listen to StrayKids songs produced \nby 3Racha? I mean, DO YOU LISTEN TO STRAYKIDS \nSONGS PRODUCED BY 3RACHA?"]]
        #common action
        self.ACTIONCOM=["* Flirt","* Insult"]
        self.REACTIONCOM=["* You smile at Papyrus. Papyrus didn't see. \nHe is focusing on the pan.",
                          "* You say that his pasta is the worst in the \nworld. Papyrus didn't hear you clearly"]
        #music
        self.losebgm=minim.loadFile(PATH+'/sounds/determination.mp3')
        self.battlebgm=minim.loadFile(PATH+'/sounds/papyrus.mp3')
        self.menubgm=minim.loadFile(PATH+'/sounds/start_menu.mp3')
        self.menubgm.play()
        #other data
        self.w=w
        self.h=h
        self.g=960
        #read player's name from save.txt
        file=open(PATH+'/save.txt','r')
        name=file.readline().strip()
        file.close()
        self.player=Heart(191,self.g,20,40,36,1,"red_heart",name.upper(),968,"red","choose")
        self.m=m #game mode: "mm","bb","bo","win","lose","menu","rec" for map mode/battle break/battle on/player win/gameover/main menu/player records
        self.papyrusImg=loadImage(PATH+"/images/{0}.png".format("papyrus"))
        self.dialogueImg=loadImage(PATH+"/images/{0}.png".format("dialogue"))
        self.level=1 #in battle mode player goes through three levels
        self.bb=self.BB[self.level-1][random.randint(0,len(self.BB[self.level-1])-1)] #randomly choose a line for initial display during the battle break
        self.battleCountDown=CD #for each round of battle it will only last a certain amount of frames
        self.reactionCountDown=-1 #some player choice will have reaction text played for 2 sec
        self.attacks=[] #records all attack elements that will be shown during the current battle round
        self.platforms=[] #records platforms that will be shown during the current battle round
        
    
    def attackLevel1(self,num):
        #num will be a random integer telling the function which kind of attack to run in this round
        if num==1:
            for i in range(5):
                self.attacks.append(AttackElement(random.randint(BATTLEPOS[0]+25,BATTLEPOS[1]-25),BATTLEPOS[2]+25,
                                                  50,50,25,"jalapeno","g"))
                self.attacks.append(AttackElement(random.randint(BATTLEPOS[0]+25,BATTLEPOS[1]-25),BATTLEPOS[2]-500,
                                                  50,50,25,"jalapeno","g"))
                self.attacks.append(AttackElement(random.randint(BATTLEPOS[0]+25,BATTLEPOS[1]-25),BATTLEPOS[2]-1100,
                                                  50,50,25,"jalapeno","g"))
        elif num==2:
            for i in range(5):
                self.attacks.append(AttackElement(0,0,40,35,18,"mushroom","r",50.0/180*math.pi*(i+4),BATTLEPOS[1],(BATTLEPOS[2]+BATTLEPOS[3])/2,150))
    
    def attackLevel2(self,num):
        if num==1:
            self.player.m="blue"
            self.player.img=loadImage(PATH+"/images/blue_heart.png")
            self.platforms.append(Platform(733,787,120,24,0.5,"pan"))
            self.platforms.append(Platform(922,888,120,24,-0.5,"pan"))
            for i in range(10):
                attack=AttackElement(random.randint(BATTLEPOS[0]+25,BATTLEPOS[1]-25),BATTLEPOS[2]-500,
                                                  16,51,8,"fusilli","g")
                attack.vx=0
                attack.vy-=3
                self.attacks.append(attack)
        
    def attackLevel3(self,num):
        if num==1:
            self.player.m="blue"
            self.player.img=loadImage(PATH+"/images/blue_heart.png")
            self.platforms.append(Platform(922,661,120,24,-1,"pan"))
            self.platforms.append(Platform(733,756,120,24,1,"pan"))
            self.platforms.append(Platform(922,850,120,24,-1,"pan"))
            y=[611,706,793,888]
            for i in range(8):
                self.attacks.append(AttackElement(1130+100*i,y[random.randint(0,3)],50,50,25,"tomato","m"))
        elif num==2:
            self.player.m="red"
            self.player.img=loadImage(PATH+"/images/red_heart.png")
            y=[611,706,793,888]
            for i in range(14):
                self.attacks.append(AttackElement(1130+100*i,y[random.randint(0,3)],50,50,25,"tomato","m"))
                
    def saveData(self):
        #called when the player win
        #read file
        file=open(PATH+"/rec.txt",'r')
        rec=[]
        for next in file:
            next=next.strip().split(',')
            rec.append(next)
        file.close()
        #see if the player wins with the top 5 highest hp
        for i in range(len(rec)):
            if self.player.hp>=int(rec[i][1]):
                holderChar=''
                if self.player.hp<10:
                    holderChar='0'
                rec.insert(i,[self.player.n,holderChar+str(self.player.hp)])
                rec.pop()
                break
        #re-write the file
        file=open(PATH+"/rec.txt",'w')
        for next in rec:
            file.write(','.join(next)+'\n')
        file.close()
    
    def bgBattleCommon(self):
        background(0,0,0)
        #action boxes
        stroke(234,153,32)
        fill(234,153,32)
        strokeWeight(8)
        noFill()
        textSize(62)
        rect(150,1069,300,120)
        text("FIGHT",234,1153)
        rect(550,1069,300,120)
        text("ACT",652,1153)
        rect(950,1069,300,120)
        text("ITEM",1046,1153)
        rect(1338,1069,300,120)
        text("MERCY",1419,1153)
        #name
        fill(255,255,255)
        textSize(42)
        text(self.player.n,150,1032)
        #blood
        text("HP",557,1032)
        text(str(self.player.hp)+"/20",821,1032)
        stroke(253,42,42)
        fill(253,42,42)
        rect(643,995,150,47)
        stroke(255,245,15)
        fill(255,245,15)
        rect(643,995,float(self.player.hp)/20*150,47)
        #papyrus
        image(self.papyrusImg,758,123)
        #image(self.dialogueImg,1100,173)
    
    def bgBattleBreak(self):
        self.bgBattleCommon()
        #dialogue box
        stroke(255,255,255)
        strokeWeight(10)
        noFill()
        rect(150,543,1500,425)
        #context in dialogue box based on player.action
        fill(255,255,255)
        textSize(48)
        text(self.bb,206,626)
        
    def bgBattleOn(self):
        if self.reactionCountDown>0:
            if self.reactionCountDown==120:
                #set reaction text at the beginning of count down
                if self.player.action=="act":
                    tempList=self.REACTION[self.level-1]+self.REACTIONCOM
                    self.bb=tempList[self.player.actionIndex]
                    if 0<=self.player.actionIndex<=len(self.REACTION[self.level-1])-1:
                        del self.REACTION[self.level-1][self.player.actionIndex]
                else: #"item"
                    self.bb=self.REITEM[self.player.actionIndex]
                    del self.REITEM[self.player.actionIndex]
            self.reactionCountDown-=1
            self.bgBattleBreak()
        else:
            self.player.hide=False
            if self.battleCountDown==CD:
                #set the player to the center of the battle box at the beginning of each round
                self.player.x=888
                self.player.y=758
                #give elements to the attacks list by calling the corresponding attack of current level
                if self.level==1:
                    self.attackLevel1(random.randint(1,2))
                elif self.level==2:
                    self.attackLevel2(random.randint(1,1))
                elif self.level==3:
                    self.attackLevel3(random.randint(1,2))
            if self.battleCountDown==0:
                #count down finished, return to break
                #randomly assign a text to display
                #check if all required actions are taken -> level up
                if len(self.ACTIONTEXT[self.level-1])==0:
                    if self.level<3:
                        self.level+=1
                    else:
                        #player wins
                        self.saveData()
                        self.m="win"
                        self.player.hide=True
                        return
                self.bb=self.BB[self.level-1][random.randint(0,len(self.BB[self.level-1])-1)]
                self.m="bb"
                self.player.action="choose"
                self.battleCountDown=CD+1
                self.reactionCountDown=-1
                self.player.actionIndex=0
                self.attacks=[]
                self.platforms=[]
            self.bgBattleCommon()
            #battle box
            stroke(255,255,255)
            strokeWeight(10)
            noFill()
            rect(687,543,425,425)
            #attacks
            for item in self.attacks:
                item.display()
            for platform in self.platforms:
                platform.display()
            self.battleCountDown-=1
            
    def bgWin(self):
        background(0)
        fill(255,255,255)
        textSize(80)
        text("ENJOY YOUR PASTA",511,470)
        textSize(50)
        text("ITS BY THE GREATEST PAPYRUS",522,560)
        winImg=loadImage(PATH+"/images/{0}.png".format("win"))
        image(winImg,700,667)
        
    def bgLose(self):
        background(0)
        loseImg=loadImage(PATH+"/images/{0}.png".format("lose"))
        image(loseImg,300,217,1200,900)
        fill(255,255,255)
        textSize(25)
        text("(CLICK ANYWHERE TO RESTART)",707,1180)
        
    def bgMenu(self):
        background(0)
        self.player.hide=True
        strokeWeight(10)
        #continue, not implemented
        stroke(120,120,120)
        fill(120,120,120)
        text("CONTINUE",739,717)
        noFill()
        rect(553,632,693,120)
        #new game and player records
        stroke(255,255,255)
        rect(553,452,693,120)
        rect(553,812,693,120)
        fill(255,255,255)
        textSize(100)
        text("UNDERMYOP",579,268)
        textSize(62)
        text("NEW PLAYER",704,538)
        text("PLAYER RECORDS",629,897)
        
        
    def bgRec(self):
        background(0)
        stroke(255,255,255)
        textSize(100)
        text("HIGHEST SCORE BOARD",320,160)
        strokeWeight(8)
        line(300,257,1500,257)
        file=open(PATH+"/rec.txt",'r')
        textSize(62)
        i=0
        for next in file:
            next=next.strip().split(',')
            text(next[0],300,365+160*i)
            text(next[1]+'/20',1310,365+160*i)
            i+=1
        file.close()
        text("BACK",820,1145)
        noFill()
        rect(770,1060,260,120)
            
    def display(self):
        if self.m=="bb":
            if self.player.action=="fight":
                self.bb="* You would not want to fight Papyrus. \nI hope. :)"
            elif self.player.action=="act":
                tempList=self.ACTIONTEXT[self.level-1]+self.ACTIONCOM
                self.bb="\n".join(tempList)
            elif self.player.action=="item":
                if len(self.ITEM)!=0:
                    self.bb="\n".join(self.ITEM)
                else:
                    self.bb="* Nothing's left in your pocket."
            elif self.player.action=="mercy":
                self.bb="* Papyrus is waiting for your choice not \nyour mercy."
            self.bgBattleBreak()
        elif self.m=="bo":
            self.bgBattleOn()
        elif self.m=="win":
            self.bgWin()
        elif self.m=="lose":
            self.bgLose()
        elif self.m=="menu":
            self.bgMenu()
        elif self.m=="rec":
            self.bgRec()
        self.player.display()

minim=Minim(this)
game=Game(1800,1240,"menu")

def setup():
    size(game.w,game.h)

def draw():
    game.display()
