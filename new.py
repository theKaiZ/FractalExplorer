from myGUI.GUI import myGUI
from myGUI.Rect import ScrollTextfeld



class GUI(myGUI):
    iterations =0
    it_grow = 0
    steps = 1
    zoom = 1.0
    def __init__(self):
        super().__init__()

    def setup_buttons(self):
        ScrollTextfeld(self, (0,0),(50,50),"iterations", change_value=1, limits=[0,10])


if __name__ == "__main__":
    GUI().run()