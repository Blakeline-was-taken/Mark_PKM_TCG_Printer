Hi ! 

This is a card printer for a custom Pokémon TCG project lead by a friend of mine called Mark.
He made most of the art, with very few exceptions, all credit goes to him for making the art.
Pokémon is obviously owned by Nintendo and have full control over the franchise. If for some reason we are asked to take this down, we will.

---

# How to launch ?

### **1. Install Python.**
Yeah, you're gonna find it pretty hard to launch python files without installing Python first. To install python, simply go to this page : https://www.python.org/downloads/ and you can download the latest version.

### **2. Installing dependencies**
This printer uses a couple of librairies not native to Python. To install them, please do the following :
1. Open Python using the Start Menu. Just start typing "Python" in the search bar and you should see it. If you see a terminal open, you're doing great !
2. In the console, use the following commands: `pip install toml`, `pip install pillow`. (note : that last one is extremely important, the project CANNOT work without it.)
3. If you see no errors pop up, you should be able to launch the python files now ! :D

### **3. Making card data**
To add new cards to print, simply run the `add_card.py` file. This will open a graphical interface that should hopefully be self-explanatory. No more hand-writing hard-coded data !

### **4. Simply printing cards**
To print existing cards, simply run the `print.py` file. Hopefully the instructions there are self-explanatory.

---

# Okay no but really, how do I use this ?

## **I. How does one make a new Pokémon card ?**

The task may seem daunting at first, but it's actually surprisingly simple.

#### 1. Art

Obviously you can't have a card without a portrait. Portraits are stored in the `assets/card_art/` folder. Simply make a beautiful piece of art, only take the part of it that goes in the frame, and export it in there. You don't even have to scale it up, the programm will do that for you !

#### 2. Use the `add_card.py` file to create the card.

I wish I was joking but it's literally as simple as that. Just go through the process of adding every bit of information you could want about your card in the graphical interface, and the rest will work itself out !

## **II. Okay but how do I color text, and use icons, and all this fancy stuff ?**

Good question! I provided examples in the existing `data/cards.csv` file (this is where your cards are hard-coded btw !) but here's the gist of it :

#### 1. Colors

To color text, simply place one of these corresponding flags to apply your desired color (don't blame me if it looks off tho) :
- `/r` : Red
- `/g` : Green
- `/b` : Blue
- `/y` : Yellow
- `/p` : Purple
- `/o` : Orange
- `/w` : White
- `/s` : Silver? Steel?
- `/n` : Normal (use this when you want to write with no color again)

You can place these flags pretty much anywhere in any text, and it will color the thing ! Pretty cool, right ?

#### 2. Icons

Okay you're not gonna believe this but it's even simpler than colors. Simply place a set of brackets anywhere in your text, and the name of the icon you want to use inside.

So for example : "If you have [1] [Fire], this move will [burning] the target."
- "[1]" will be replaced by a big "1" icon
- "[Fire]" will be replaced by the Fire type icon
- "[burning]" will be replaced by a custom burning icon in the `assets/icons/` folder.

It really is that simple. And of course if you want to add more icons, just place more in the icons folder and type their name !

## **III. MMMkay but like how do I make a new type ?**

Okay this is a bit more complicated because you would have to dive into the `assets/cardbase/` folder and change some things, but it is doable.

I won't explain it here though because quite frankly this is still kinda messy code-wise, there's some constants that should definitely be in the config file instead so while I haven't fixed that it's gonna be kinda hard making a new type. Sorry :(

---

# Final words

Thank you very much for reading all this, and I would also like to thank my good friend Mark for allowing me to make this generator for him (and for me, I am planning on helping him with this project). I hope this will be useful somehow, and that I will get to fix lots and lots of unforeseen issues ! :,D

---

Turkey sandwich
