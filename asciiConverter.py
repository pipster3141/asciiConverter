"""
Image Converter class that takes an image in RGB/CMYK
and returns a similar image made of only ASCII chars.
alternatively one can opt to only pixelate the image.
Created by Trevor Dalton on 8/28/19
"""

from PIL import Image, ImageDraw, ImageFont
from concurrent.futures import ProcessPoolExecutor
import functools
import multiprocessing
import time

# The following 2 functions are taken from https://www.codementor.io

# Open an Image
def open_image(path):
  newImage = Image.open(path)
  return newImage

class AsciiConverter:

  def __init__(self, image, blockSize):
    self.image = image
    self.oldWidth, self.oldHeight = image.size
    self.width = self.oldWidth - (self.oldWidth % blockSize)
    self.height = self.oldHeight - (self.oldHeight % blockSize)
    self.blockSize = blockSize
    self.blocks = self.getImageColor()
    self.newImage = None


  # Takes the list of blocks and
  # turns them into a pixelated image
  def pixelate(self):
    image = Image.new("RGB", (self.width, self.height), "white")
    pen = ImageDraw.Draw(image)
    for i in range(self.height//self.blockSize):
      for j in range(self.width//self.blockSize):
        pen.rectangle([(j*self.blockSize, i*self.blockSize), (j*self.blockSize+self.blockSize, i*self.blockSize+self.blockSize)], self.blocks[j+(i*self.width//self.blockSize)], self.blocks[j+(i*self.width//self.blockSize)], 0)
    self.newImage = image

  # Helper method that turns an RGB tuple to a Greyscale value.
  def RGBtoGreyscale(self, color):
    val = color[0] + color[1] + color[2]
    return val // 3

  # Helper method to turn a greyscale value to a particular letter.
  def determineLetter(self, darkness):
    char = ""
    if darkness < 30:
      char = "W"
    elif darkness < 60:
      char = "X"
    elif darkness < 90:
      char = "A"
    elif darkness < 120:
      char = "S"
    elif darkness < 150:
      char = "C"
    elif darkness < 180:
      char = "T"
    elif darkness < 200:
      char = ")"
    elif darkness < 215:
      char = "!"
    elif darkness < 230:
      char = "^"
    else:
      char = "."
    return char
  
  # Takes the blocks and converts them to
  # ASCII characters.
  def asciiConvert(self):
    image = Image.new("RGB", (self.width, self.height), "white")
    pen = ImageDraw.Draw(image)
    font = ImageFont.truetype("joystix_monospace.ttf", self.blockSize)
    for i in range(self.height//self.blockSize):
      for j in range(self.width//self.blockSize):
        color = self.blocks[j+(i*self.width//self.blockSize)]
        darkness = self.RGBtoGreyscale(color)
        char = self.determineLetter(darkness)
        pen.text((j*self.blockSize, i*self.blockSize), char, "black", font)
    self.newImage = image

  # For a size x size group of pixels
  # get the average (r,g,b) between
  # (start.x,start.y) and (start.x+size,start.y+size)
  # Returns a tuple (r,g,b)
  def getBlockColor(self, start):
    totalRGB = [0,0,0]

    # Loops over every pixel and adds its RGB value to the list
    for i in range(self.blockSize):
      for j in range(self.blockSize):
        pixel = self.image.getpixel((start[0]+j, start[1]+i))
        totalRGB[0] += pixel[0]
        totalRGB[1] += pixel[1]
        totalRGB[2] += pixel[2]
        
    # Integer divides the total amount of RGB by self.blockSize**2 and puts it in a tuple 
    averageRGB = ( totalRGB[0] // self.blockSize**2, totalRGB[1] // self.blockSize**2, totalRGB[2] // self.blockSize**2 )
    return averageRGB

  # Helper method so the program can assign
  # larger tasks to each thread
  def getRowColor(self, start):
    rowColors = []
    for j in range(self.width//self.blockSize):
      block = self.getBlockColor((j*self.blockSize, start))
      rowColors.append(block)
    return rowColors
    
  # Helper method to get a list
  # of the average RGB values.
  # Goes by width and then by height.
  def getImageColor(self):
    # Now threads are used to gather image data
    # about the average RGB of each blockSizexblockSize block.
    averageColors = []
    coords = []
    with ProcessPoolExecutor(multiprocessing.cpu_count()) as executor:
      for i in range(self.height//self.blockSize):
        coords.append(i*self.blockSize)
      for result in executor.map(self.getRowColor, coords):
        for block in result:
          averageColors.append(block)
    return averageColors


  # Takes a list of average RGB values of an image
  # and returns an image of those shades.
  def display(self):
    if self.newImage == None:
      self.image.show()
    else:
      self.newImage.show()

  # Save the file to the name decided by user input
  def save(self, name):
    self.newImage.save(name)
    
def main():
  imageName = input("What is the name of the image you'd like converted? ex: egg.jpg\n")
  image = Image.open(imageName)
  image.convert('RGB')
  blockSize = 0
  blockSize = int(input("What size would you like the blocks?"))
  newImage = AsciiConverter(image, blockSize)
  newImage.asciiConvert()
  newImage.display()
  newImage.save("test.jpg")

  

if __name__ == "__main__":
  main()
