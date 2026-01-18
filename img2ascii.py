# pyenv activate asciiart
import sys
import numpy as np
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
from PIL import ImageEnhance

# Character density calculation
def char_density(ch):
    img = Image.new('RGB', (16, 24), color=(255,255,255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("Courier New.ttf", 20)
    draw.text((0, 0),ch,(0,0,0),font=font)
    img = img.convert('L').convert('1')
    # img.save('sample-out.png') save only for debugging
    nblack=0
    for px in list(img.getdata()):
        if px < 0.01:
            nblack = nblack+1
    return nblack

# Contrast adjustment (not used now)
contrast  = 1.5   # 1 is neutral, more is higher contrast, less is lower
sharpness = 1.2   # 2 is neutral, more is sharper, less is blurrier
brightness = 1.5   # 2 is neutral, more is sharper, less is blurrier
overprint = True  # Generates lines two times for high constrast overprinting
invert    = True

# German diablo typewheel charset
charset  = ('!"$%&\'()*+,-./0123456789:;<=>?ßABCDEFGHIJKLMNOPQRSTUVWXYZ^_`abcdefghijklmnopqrstuvwxyz~ ')

# array with most dense to least dense chars from charset
density = ('')

ddict = dict()
for c in charset:
    d = char_density(c)
    ddict[d] = c

l = sorted(ddict.keys(), reverse=invert)
for k in l: 
    density = density + ddict[k]

# print(density)
n = len(density)

img_name = sys.argv[1]
try:
    width = int(sys.argv[2])
except IndexError:
    # Default ASCII image width.
    width = 132

# Read in the image, convert to greyscale.
img = Image.open(img_name)

# Apply image enhancements
enhancer = ImageEnhance.Contrast(img)
img = enhancer.enhance(contrast)

enhancer = ImageEnhance.Sharpness(img)
img = enhancer.enhance(sharpness)

enhancer = ImageEnhance.Brightness(img)
img = enhancer.enhance(brightness)

img = img.convert('L') # to Grayscale
# Resize the image as given by width => will be the number of characters wide
orig_width, orig_height = img.size
r = orig_height / orig_width

# The ASCII character glyphs are taller than they are wide. Maintain the aspect
# ratio by reducing the image height.
height = int(width * r * 0.5)
img = img.resize((width, height), Image.LANCZOS)

# Normalize the image so that we have graylevels from 0 .. 255
arr = np.array(img)
arr = arr.astype('float')
minval = arr.min()
maxval = arr.max()
if minval != maxval:
    arr[...] -= minval
    arr[...] *= (255.0/(maxval-minval))

# Now map the pixel brightness to the charset by density.
# arr = np.array(img)
for i in range(height):
    for j in range(width):
        p = arr[i,j]
        p = p / 255.0             # Map to 0..1
        k = int(np.floor(p * n))  # Map to charset
        k = max(k, 0)             # Clamp to charset range
        k = min(k, n-1)           # Clamp to charset range
        print(density[k], end='')

    # Optional overprint with high density chars to improve contrast
    if overprint:
        # First round of overprint with half of the characterset
        print("\x0D", end='')                 # Send carriage return w/o linefeed
        lowclamp = int(n*0.5)-1
        for j in range(width):
            p = arr[i,j]
            p = p / 255.0             # Map to 0..1
            k = int(np.floor(p * n))  # Map to charset
            k = max(k, 0)             # Clamp to charset range
            k = min(k, lowclamp)      # Clamp to charset range
            
            if (k!=lowclamp):
                print(density[k], end='')
            else:
                print(' ', end='')

        # Second round overprint with the upper third of the most dense chars
        # to further enhance contrast. Here, the charset also is shifted to 
        # yield more blackness.
        print("\x0D", end='')         # Send carriage return w/o linefeed
        lowclamp = int(n*0.25)-1
        for j in range(width):
            p = arr[i,j]
            p = p / 255.0             # Map to 0..1
            k = int(np.floor(p * n))  # Map to charset
            k = max(k, 0)             # Clamp to charset range
            k = min(k, lowclamp)      # Clamp to charset range
            
            if (k!=lowclamp):
                print(density[k], end='')
            else:
                print(' ', end='')

        # Third round overprint with the upper 1/8th most dense chars
        # Here, the charset also is shifted by 1 char to yield more blackness.
        print("\x0D", end='')         # Send carriage return w/o linefeed
        lowclamp = int(n*0.125)-1
        for j in range(width):
            p = arr[i,j]
            p = p / 255.0             # Map to 0..1
            k = int(np.floor(p * n))  # Map to charset
            k = max(k, 0)             # Clamp to charset range
            k = min(k, lowclamp)      # Clamp to charset range
            
            if (k!=lowclamp):
                print(density[k+1], end='')
            else:
                print(' ', end='')
    print("\x0D", end='\x0A')         # Send CR LF 
