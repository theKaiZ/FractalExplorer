import pygame
import os


class Button():
    active = False

    def __init__(self, parent, pos, size, text):
        self.parent = parent
        self.size = size
        self.pos = pos
        self.text = text
        self.text_surface = parent.myfont.render(text[2:], False, (0, 0, 0))

    def draw(self):
        pygame.draw.rect(self.parent.screen, (150, 150 + self.active * 50, 150),
                         (self.pos[0], self.pos[1], self.size[0], self.size[1]), 0)
        pygame.draw.rect(self.parent.screen, (200, 200, 200), (self.pos[0], self.pos[1], self.size[0], self.size[1]), 1)
        self.parent.screen.blit(self.text_surface, (
        self.pos[0] + self.size[0] / 2 - len(self.text[2:]) * 4.5, self.pos[1] + self.size[1] / 2 - 12))

    def click(self, pos):
        if pos[0] > self.pos[0] and pos[0] < self.pos[0] + self.size[0] and pos[1] > self.pos[1] and pos[1] < self.pos[
            1] + self.size[1]:
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

    def __init__(self, parent, pos, size, text, command, **kwargs):
        self.parent = parent
        self.size = size
        self.pos = pos
        self.text = text
        self.text_surface = parent.myfont.render(text, False, (0, 0, 0))
        self.command = command
        for param in kwargs:
            setattr(self, param, kwargs[param])

    def action(self):
        self.command()
        if self.aa:
            if self.group:
                for button in self.parent.buttons:
                    if button.group == self.group:
                        button.active = False
            if self.toggle:
                self.active = not self.active
            else:
                self.active = True

        if self.reset:
            #os.system("rm -r ./pics/*.png")
            self.parent.reset()
            self.parent.jump(0)
        if self.jump:
            self.parent.jump(0)


class Textfeld():
    def __init__(self, parent, pos, size, value):
        self.parent = parent
        self.size = size
        self.pos = pos
        self.value = value
        self.update()

    def draw(self):
        pygame.draw.rect(self.parent.screen, (150, 150, 150), (self.pos[0], self.pos[1], self.size[0], self.size[1]), 0)
        pygame.draw.rect(self.parent.screen, (200, 200, 200), (self.pos[0], self.pos[1], self.size[0], self.size[1]), 1)
        self.parent.screen.blit(self.text_surface, (
        self.pos[0] + self.size[0] / 2 - len(self.text) * 4.5, self.pos[1] + self.size[1] / 2 - 12))

    def update(self):
        wert = getattr(self.parent, self.value)
        if isinstance(wert, float):
            wert = "{0:.3f}".format(wert)
        self.text = str(wert)
        self.text_surface = self.parent.myfont.render(self.text, False, (0, 0, 0))

