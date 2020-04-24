import pygame
import numpy as np
from PIL import Image
import os
from ctypes import *
from time import time,sleep
from sys import platform

def load_cuda():
  global mandel
  os.system("nvcc frac.cu -arch sm_61 -Xcompiler -fPIC -shared -o frac.so")
  LibName = 'frac.so'
  AbsLibPath = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + LibName
  mandel = CDLL(AbsLibPath,mode=RTLD_LOCAL)

class Button():
  active = False
  def __init__(self,parent,pos,size,text):
    self.parent = parent
    self.size = size
    self.pos = pos
    self.text = text
    self.text_surface = parent.myfont.render(text[2:],False,(0,0,0))

  def draw(self):
    pygame.draw.rect(self.parent.screen,(150,150+self.active*50,150),(self.pos[0],self.pos[1],self.size[0],self.size[1]),0)
    pygame.draw.rect(self.parent.screen,(200,200,200),(self.pos[0],self.pos[1],self.size[0],self.size[1]),1)
    self.parent.screen.blit(self.text_surface,(self.pos[0]+self.size[0]/2-len(self.text[2:])*4.5,self.pos[1]+self.size[1]/2-12))
  def click(self,pos):
    if pos[0] > self.pos[0] and pos[0] < self.pos[0]+self.size[0] and pos[1]>self.pos[1] and pos[1] < self.pos[1]+self.size[1]:
      self.action()
      return True
  def action(self):
    pass

class AdvButton(Button):
  reset = False
  jump = False
  active = False
  aa = False
  group = False
  toggle = False
  def __init__(self,parent,pos,size,text,command,**kwargs):
    self.parent = parent
    self.size = size
    self.pos = pos
    self.text = text
    self.text_surface = parent.myfont.render(text,False,(0,0,0))
    self.command = command
    for param in kwargs:
      setattr(self,param,kwargs[param])
  def action(self):
    self.command()
    if self.aa:
      if self.group:
        for button in self.parent.buttons:
          if button.group == self.group:
            button.active = False
      if self.toggle:
        self.active= not self.active
      else:
        self.active = True
    
    if self.reset:
      os.system("rm -r ./pics/*.png")
      self.parent.reset()
      self.parent.jump(0)
    if self.jump:
      self.parent.jump(0)


class Textfeld():
  def __init__(self,parent,pos,size,value):
    self.parent = parent
    self.size = size
    self.pos = pos
    self.value = value
    self.update()
  def draw(self):
    pygame.draw.rect(self.parent.screen,(150,150,150),(self.pos[0],self.pos[1],self.size[0],self.size[1]),0)
    pygame.draw.rect(self.parent.screen,(200,200,200),(self.pos[0],self.pos[1],self.size[0],self.size[1]),1)
    self.parent.screen.blit(self.text_surface,(self.pos[0]+self.size[0]/2-len(self.text)*4.5,self.pos[1]+self.size[1]/2-12))
  def update(self):
    wert = getattr(self.parent,self.value)
    if isinstance(wert,float):
      wert = "{0:.3f}".format(wert)
    self.text = str(wert)
    self.text_surface = self.parent.myfont.render(self.text,False,(0,0,0))



class Animation():
    func = "Mandel"
    loadfunc = True
    size = (480,480)
    fps = 30
    screen = False
    buttons = []
    textfelder = []
    split= False
    folder = ""
    save = False
    R_mode = 1
    G_mode = 1
    B_mode = 1
    disort = False
    julia  = False
    rotate = False
    angle = 0
    fun = None
    def __init__(self,**kwargs):
        if self.loadfunc:
          self.reset()
        for param in kwargs:
          setattr(self,param,kwargs[param])
        self.init_end()

    def init_end(self):
        if self.loadfunc:
          self.set_cuda_function(self.func)
        objlength = self.size[0]*self.size[1]*3
        self.result = (c_ubyte*objlength)()

    def set_cuda_function(self,func):
        print(func)
        self.func = func
        self.fun = getattr(mandel,func)

    def make_picture(self):
        if self.rotate:
            self.angle += 1
            mandel.rotate(self.angle)
        if self.disort:
            self.fun(c_ushort(self.size[0] + int(self.size[0] * 0.2)),
                     c_ushort(self.size[1] - int(self.size[0] * 0.2)),
                     c_longdouble(self.span),
                     c_longdouble(self.center[0]),
                     c_longdouble(self.center[1]),
                     c_ushort(self.iterations),
                     c_ushort(self.frame),
                     self.result,
                     c_ubyte(self.R_mode),
                     c_ubyte(self.G_mode),
                     c_ubyte(self.B_mode),
                     c_ubyte(self.julia))

        else:
            self.fun(c_ushort(self.size[0]),
                     c_ushort(self.size[1]),
                     c_longdouble(self.span),
                     c_longdouble(self.center[0]),
                     c_longdouble(self.center[1]),
                     c_ushort(self.iterations),
                     c_ushort(self.frame),
                     self.result,
                     c_ubyte(self.R_mode),
                     c_ubyte(self.G_mode),
                     c_ubyte(self.B_mode),
                     c_ubyte(self.julia))

    def reset(self):
        self.frame = 0
        self.span = np.float128(4)
        self.center = (np.float128(0), np.float128(0))
        self.zoom = 1
        self.iterations_start = 50
        self.iterations = self.iterations_start
        self.steps = 1
        self.start = self.span
        self.end = False
        self.iterations_end = False
        self.it_grow = 0.15
        os.system("rm log.txt")
        if self.screen:
          self.update()

    def jump(self, steps):
        if steps > 0:
           self.log()
        if steps > 0:
          self.span = np.float128(self.span * self.zoom**steps)
        if steps < 0:
          self.span = np.float128(self.span / self.zoom**abs(steps) )
        self.frame += abs(steps)
        stamp = time()
        if not self.split:
            self.background()
        else:
            self.split_screen()
        if self.save:
          self.save_pic()
        print(str("{0:.4f}".format(time() - stamp)) + " Sekunden")
        self.update()
    def run(self):
        print(self.size,self.frame,self.iterations,self.center,self.func)
        s = time()
        self.background()
        self.save_2()
        print(time()-s)
    def background(self):
        if (self.start and self.start != self.end) or (self.iterations != self.iterations_start):
            self.iterations = int(self.iterations_start + self.it_grow * self.frame)
        self.make_picture()
        if self.screen:
          self.img  = pygame.image.frombuffer(self.result,(self.size[0],self.size[1]),"RGB")
          if self.disort:
            self.img = pygame.transform.scale(self.img,(self.size[0],self.size[1]+360))
          self.screen.blit(self.img,(0,0))
    def draw_grid(self):
        pygame.draw.line(self.screen,(0,0,0),(self.size[0]/2-25,self.size[1]/2),(self.size[0]/2+25,self.size[1]/2))
        pygame.draw.line(self.screen,(0,0,0),(self.size[0]/2,self.size[1]/2-25),(self.size[0]/2,self.size[1]/2+25))
    def split_screen(self):
        if self.start and self.start != self.end:
            self.iterations = int(self.iterations_start + self.it_grow * self.frame)
        if self.start:
            self.span = self.start * self.zoom ** (self.frame)
        else:
            self.span = 3 * self.zoom ** (self.frame)
        for x in range(0, int(self.size[0] / 2) + 1):
            for y in range(0, int(self.size[1] / 2) + 1):
                try:
                    a, b, l = self.method((x, y), self.size / 2, (self.span, self.span), self.center,self.iterations, self.frame)
                    r, g, b = self.coloring(a, b, l, self.iterations, self.frame)
                    r, g, b = color.check_RGB(r, g, b)
                except:
                    r = g = b = 255
                self.draw.point((x, y), fill=(r,g,b))
                self.draw.point((self.size[0] - x, y), fill=(r,g,b))
                self.draw.point((x, self.size[1] - y), fill=(r,g,b))
                self.draw.point((self.size[0] - x, self.size[1] - y), fill=(r,g,b))

                if self.screen:
                    try:
                        self.screen.set_at((x, y), ((r,g,b)))
                        self.screen.set_at((self.size[0] - x, y), ((r,g,b)))
                        self.screen.set_at((x, self.size[1] - y), ((r,g,b)))
                        self.screen.set_at((self.size[0] - x, self.size[1] - y), ((r,g,b)))
                    except:
                        pass

    def save_pic(self, ff = '.bmp'):
        self.filename = self.folder + "pics/" + (5 - len(str(self.frame))) * "0" + str(self.frame) + ff
        im = Image.frombuffer("RGB",(self.size[0],self.size[1]),self.result,"raw","RGB",0,1)
        #im = pygame.image.frombuffer(self.result,(self.size[0],self.size[1]),"RGB")
        if self.disort: 
           print("Disortion!")
           im  =im.crop((0,0,self.size[0],self.size[1]-int(self.size[0]*0.375)))
           im  = im.resize(self.size)
        #pygame.image.save(im, self.filename)
        im.save(self.filename)
        print(self.frame)

    def save_2(self):
        Image.frombuffer("RGB",(self.size[0],self.size[1]),self.result,"raw","RGB",0,1).save(
            "pics2/" + (5 - len(str(len(os.listdir("pics/"))))) * "0" + str(len(os.listdir("pics2/"))) + ".png")

    def update(self):
        for textfeld in self.textfelder:
            textfeld.update()
        for button in self.buttons:
            button.draw()
        for textfeld in self.textfelder:
            textfeld.draw()
    def toggle(self, value):
        setattr(self, value, not getattr(self, value))

    def add_value(self, attr, value):
        setattr(self, attr, getattr(self, attr) + value)

    def mult_value(self, attr, value):
        setattr(self, attr, getattr(self, attr) * value)

    def mk_video(self,ff = '.bmp'):
        os.system("ffmpeg -f image2 -i ./pics/%05d"+ff+" -pix_fmt yuv420p -y out.mp4")

    def save_spot(self):
        with open("spot.txt","a+") as f:
          f.write("cuda;" if "cu" in self.func else "c;")
          f.write(self.func + "\n")
          f.write("frame;" + str(self.frame)+"\n")
          f.write("iterations;" + str(self.iterations)+"\n")
          f.write("center;" + str(self.center[0])+";" + str(self.center[1])+"\n")
          f.write("span;"+str(self.span)+"\n")
    def load_spot(self):
        with open("spot.txt","r") as f:
          for line in f:
            if not line.find("c;"):
              self.set_c_function(line.split(";")[1])
            elif not line.find("cuda;"):
              self.set_cuda_function(line.split(";")[1])
            elif not line.find("frame;"):
              self.frame = (int) (line.split(";")[1])
            elif not line.find("iterations;"):
              self.iterations = int (line.split(";")[1])
            elif not line.find("center;"):
              self.center = (float(line.split(";")[1]), (float(line.split(";")[2])))
            elif not line.find("span;"):
              self.span  = np.float_(line.split(";")[1])
        self.jump(0)
    def log(self):
        with open("log.txt","a") as f:
          for stat in ['frame',"iterations","center",'span',"rotate",'julia']:
             f.write(str(getattr(self,stat)) + ";")
          f.write("\n")

    def make_buttons(self):
        self.buttons = []
        y = 0

        for fun in open("rep/cuda_funcs.txt", "r"):
            if fun.find("/"):
                if '#' in fun:
                    a = fun.split('#')
                    self.buttons.append(AdvButton(self, (self.size[0], y * 20), (200, 20), a[0],
                                                  (lambda x=a[0]: self.set_cuda_function(x[:])), reset=True, aa=True,
                                                  group='funcs'))
                    y += 1

        self.buttons.append(
            AdvButton(self, (100, self.size[1]), (30, 30), "+", lambda: (self.add_value("iterations_start", 5)),
                      jump=True))
        self.buttons.append(
            AdvButton(self, (0, self.size[1]), (30, 30), "-", lambda: self.add_value("iterations_start", -5),
                      jump=True))

        self.textfelder.append(Textfeld(self, (30, self.size[1]), (70, 30), "iterations"))
        self.textfelder.append(Textfeld(self, (160, self.size[1]), (70, 30), "it_grow"))
        self.textfelder.append(Textfeld(self, (400, self.size[1]), (70, 30), "steps"))
        self.textfelder.append(Textfeld(self, (530, self.size[1]), (70, 30), "zoom"))

        self.buttons.append(
            AdvButton(self, (600, self.size[1]), (30, 30), "+.01", lambda: self.add_value("zoom", +.01), jump=True))
        self.buttons.append(
            AdvButton(self, (500, self.size[1]), (30, 30), "-.01", lambda: self.add_value("zoom", -.01), jump=True))

        self.buttons.append(AdvButton(self, (470, self.size[1]), (30, 30), "++", lambda: self.add_value("steps", +1)))
        self.buttons.append(AdvButton(self, (370, self.size[1]), (30, 30), "--", lambda: self.add_value("steps", -1)))

        self.buttons.append(
            AdvButton(self, (230, self.size[1]), (30, 30), "*1.1", lambda: self.mult_value("it_grow", 1.1), jump=True))
        self.buttons.append(
            AdvButton(self, (130, self.size[1]), (30, 30), "*0.9", lambda: self.mult_value("it_grow", 0.9), jump=True))

        self.textfelder.append(Textfeld(self, (730, self.size[1] - 30), (70, 30), "R_mode"))
        self.buttons.append(
            AdvButton(self, (800, self.size[1] - 30), (30, 30), "++", lambda: self.add_value("R_mode", +1), jump=True))
        self.buttons.append(
            AdvButton(self, (700, self.size[1] - 30), (30, 30), "--", lambda: self.add_value("R_mode", -1), jump=True))
        self.textfelder.append(Textfeld(self, (730, self.size[1]), (70, 30), "G_mode"))
        self.buttons.append(
            AdvButton(self, (800, self.size[1]), (30, 30), "++", lambda: self.add_value("G_mode", +1), jump=True))
        self.buttons.append(
            AdvButton(self, (700, self.size[1]), (30, 30), "--", lambda: self.add_value("G_mode", -1), jump=True))

        self.textfelder.append(Textfeld(self, (730, self.size[1] + 30), (70, 30), "B_mode"))
        self.buttons.append(
            AdvButton(self, (800, self.size[1] + 30), (30, 30), "++", lambda: self.add_value("B_mode", +1), jump=True))
        self.buttons.append(
            AdvButton(self, (700, self.size[1] + 30), (30, 30), "--", lambda: self.add_value("B_mode", -1), jump=True))

        # self.buttons.append(AdvButton(self, (260, self.size[1]), (100, 30), "Split-Mode", (lambda: self.toggle("split"))))
        self.buttons.append(AdvButton(self, (self.size[0], self.size[1]), (50, 30), "Video", lambda: self.mk_video()))
        self.buttons.append(
            AdvButton(self, (self.size[0], self.size[1] + 30), (50, 30), "Auto", lambda: self.toggle("autozoom"),
                      aa=True, toggle=True))
        self.textfelder.append(Textfeld(self, (0, self.size[1] + 30), (70, 30), "frame"))
        self.buttons.append(
            AdvButton(self, (70, self.size[1] + 30), (100, 30), "Julia", lambda: self.toggle("julia"), jump=True,
                      aa=True, group=False, toggle=True))
        self.buttons.append(
            AdvButton(self, (170, self.size[1] + 30), (100, 30), "Rotate", lambda: self.toggle("rotate"), jump=True,
                      aa=True, group=False, toggle=True))
        self.buttons.append(
            AdvButton(self, (270, self.size[1] + 30), (100, 30), "Disort", lambda: self.toggle("disort"), jump=True,
                      aa=True, group=False, toggle=True))

    def window(self):
        '''Initialisiere Alle Einstellungen und Buttons für Pygame'''
        running = True
        left_click = right_click = self.autozoom = False
        pygame.init()
        self.myfont = pygame.font.SysFont("Comic Sans MS", 15 if 'win' in platform else 15)
        self.screen = pygame.display.set_mode((self.size[0] + 200, self.size[1] + 60))
        self.make_buttons()
        for button in self.buttons:
            button.draw()
        for textfeld in self.textfelder:
            textfeld.draw()
        tick = 0
        self.jump(0)
        while running:
            if left_click:
              pos = pygame.mouse.get_pos()
              if pos[0] < self.size[0] and pos[1] < self.size[1]:
                self.center = (
                  self.center[0] + (pos[0] - self.size[0] / 2) / ((self.size[0]) / 2 / (self.span))/4,
                  self.center[1] + (pos[1] - self.size[1] / 2) / ((self.size[1]) / 2 / (self.span))/4   )
                self.jump(self.steps)
            elif right_click:
              pos = pygame.mouse.get_pos()
              if pos[0] < self.size[0] and pos[1] < self.size[1]:
                self.center = (
                  self.center[0] + (pos[0] - self.size[0] / 2) / ((self.size[0]) / 2 / self.span)/4,
                  self.center[1] + (pos[1] - self.size[1] / 2) / ((self.size[1]) / 2 / self.span)/4)
                self.jump(-self.steps)
            elif self.autozoom and (time()-tick>0.05):
              self.jump(self.steps)
              tick  = time()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_F2:
                        self.frame = 0
                        self.center = (0,0)
                        self.span = np.float128(4)
                        self.jump(0)
                    elif event.key == pygame.K_F3:
                        self.make_buttons()
                        self.update()
                    elif event.key == pygame.K_F5:
                        self.save_spot()
                    elif event.key == pygame.K_F9:
                        self.load_spot()
                    elif event.key == pygame.K_MINUS:
                        self.jump(-self.steps)
                        for textfeld in self.textfelder:
                            textfeld.draw()
                    elif event.key == pygame.K_PLUS:
                        self.jump(self.steps)
                        for textfeld in self.textfelder:
                            textfeld.draw()
                    elif event.key == pygame.K_s:
                        ##das kann man vlt noch Threaden!
                        A = Animation(loadfunc=False, size=(4000,4000), frame=self.frame, center=self.center, iterations=self.iterations, iterations_start = self.iterations_start, start=self.start, span=self.span,zoom = self.zoom,it_grow=self.it_grow,R_mode = self.R_mode, G_mode = self.G_mode, B_mode = self.B_mode)
                        A.fun = getattr(mandel,self.func)
                        A.run()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                  if event.button == 1:
                    left_click = True
                  if event.button==3:
                    right_click = True 
                    #self.jump(-self.steps)
                  pos = pygame.mouse.get_pos()
                  for button in self.buttons:
                            button.click(pos)
                  self.update()
                  for button in self.buttons:
                        button.draw()
                  for textfeld in self.textfelder:
                        textfeld.draw()
                elif event.type == pygame.MOUSEBUTTONUP:
                 if event.button == 1:
                   left_click = False
                 elif event.button == 3:
                   right_click = False
            self.draw_grid()
            pygame.display.flip()
        pygame.quit()

  

if __name__ == '__main__':
    load_cuda()
    Animation(size=(640,640),disort=False,save=False).window()
