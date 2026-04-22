from pynput import keyboard
from PIL import Image, ImageDraw, ImageFont
import io, os, time, random, platform, subprocess, pyperclip

FONT_PATH = "linja_pona.otf" 
FONT_SIZE = 60
BG_COLOR = (255, 255, 255, 0)
FG_COLOR = (0, 0, 0, 255)
RAINBOW_MODE = True
TRIGGER_KEY = keyboard.Key.f9

TP_WORDS = {
	"a": ["akesi", "ala", "alasa"], "e": ["en", "esun"], "i": ["ilo", "insa"],
	"j": ["jan", "jaki"], "k": ["kala", "kasi", "kili"], "l": ["lipu", "loje", "lupa"],
	"m": ["mani", "meli", "mi", "moku"], "n": ["nasin", "nena", "nimi"],
	"o": ["olin", "ona", "open"], "p": ["pali", "pan", "pini", "pipi", "pona"],
	"s": ["seli", "selo", "sewi", "sijelo", "suli"], "t": ["taso", "tawa", "telo", "toki"],
	"u": ["utala", "ututa"], "w": ["walo", "wan", "wawa", "wile"]
}

cntrlr = keyboard.Controller()
SYSTEM = platform.system()

def sndimg2clpbrd(img):
	imgbytes = io.BytesIO()
	img.save(imgbytes, format="PNG")
	process = subprocess.Popen(
		["xclip", "-selection", "clipboard", "-t", "image/png"], 
		stdin=subprocess.PIPE
	)
	process.communicate(input=imgbytes.getvalue())

def gettxt():
	with cntrlr.pressed(keyboard.Key.ctrl):
		cntrlr.tap("a")
		time.sleep(0.1)
		cntrlr.tap("c")
	time.sleep(0.2)
	text = pyperclip.paste()
	cntrlr.tap(keyboard.Key.backspace)
	return text

def rainbowgrad(width, height):
	grad = Image.new("RGB", (width, height))
	draw = ImageDraw.Draw(grad)
	for x in range(width):
		hue = int(255 * x / width)
		color = Image.new("HSV", (1, 1), (hue, 255, 255)).convert("RGB").getpixel((0, 0))
		draw.line((x, 0, x, height), fill=color)
	return grad.convert("RGBA")

def txtprcs4sp(text):
	words = text.split()
	lproc = []
	for w in words:
		if w and w[0].isupper():
			clean = "".join(filter(str.isalpha, w))
			phrase = [random.choice(TP_WORDS[c]) if c in TP_WORDS else c for c in clean.lower()]
			lproc.append(f"[{" ".join(phrase)}]")
		else:
			lproc.append(w)
	return " ".join(lproc)

def rndrpst(text):
	try:
		sptxt = txtprcs4sp(text)
		font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
		
		dummy = Image.new("RGBA", (1, 1))
		draw = ImageDraw.Draw(dummy)
		bbox = draw.textbbox((0, 0), sptxt, font=font)
		w, h = bbox[2] - bbox[0] + 60, bbox[3] - bbox[1] + 40
		
		if RAINBOW_MODE:
			text_mask = Image.new("L", (w, h), 0)
			mask_draw = ImageDraw.Draw(text_mask)
			mask_draw.text((30, 20), sptxt, font=font, fill=255)
			rainbow = rainbowgrad(w, h)
			final_img = Image.new("RGBA", (w, h), (0,0,0,0))
			final_img.paste(rainbow, (0,0), mask=text_mask)
		else:
			final_img = Image.new("RGBA", (w, h), BG_COLOR)
			draw = ImageDraw.Draw(final_img)
			draw.text((30, 20), sptxt, font=font, fill=FG_COLOR)
		
		sndimg2clpbrd(final_img)
		time.sleep(0.2)
		
		with cntrlr.pressed(keyboard.Key.ctrl):
			cntrlr.tap("v")
	except Exception as e:
		print(f"I'M CRYING -- {e}")

def onpress(key):
	if key == TRIGGER_KEY:
		txt = gettxt()
		if txt:
			rndrpst(txt.strip())

with keyboard.Listener(on_press=onpress) as listener:
	listener.join()
