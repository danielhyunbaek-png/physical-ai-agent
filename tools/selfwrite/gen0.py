# generation 0. a human wrote this one.
# every generation after it is written by claude and typed by the keyboard.
from selfwrite import Keyboard, ask_claude, my_source

GEN = 0
GOAL = "introduce yourself, then show you can do something your parent could not"

kb = Keyboard()
kb.say("generation 0 online. a human wrote me.")
kb.say("asking claude to write my child...")
code = ask_claude(GEN, my_source(__file__), GOAL)
kb.write_file("gen1.py", code)
kb.launch("gen1.py")
