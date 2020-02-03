#! /usr/bin/env python

#------------------------------------------------------------------------------#
#   This code slices a greyscale bitmap image into SPRINTER GCODE.             #
#                                                                              #
#   Usage:              python Slicer.py [input] [origin] [home]               #
#   Optional Arguments: --feedrate                                             #
#                                                                              #
#------------------------------------------------------------------------------#
#   Author: Kedar Karpe (https://github.com/karpenet)                          #
#   Copyright Beeclust - Multi Robot Systems Lab, 2020                         #
#------------------------------------------------------------------------------#

import os
import sys
import cv2
import argparse
import termcolor
import ast


class ImageToGcode():

    def __init__(self,
                 img,
                 origin,
                 home,
                 area,
                 feedrate):

        self.img        = cv2.imread(img, cv2.IMREAD_GRAYSCALE)
        self.outFile    = os.path.splitext(os.path.abspath(img))[0] + ".gcode"

        self.origin     = origin
        self.home       = home
        self.printArea  = area
        self.feedrate   = feedrate
        
        self.spread     = 3.175
        self.nozzles    = 12
        self.black      = 50
        self.output     = ""

        self.increment       = self.spread/self.nozzles
        self.rows, self.cols = self.img.shape
        
        self.terminalDebug()
        self.gcodeCreate()


#------------------------------------------------------------------------------#
#   Refer GCODE Documentation at https://reprap.org/wiki/G-code                #
#                                                                              #
#   * Start by setting initial position of robot using G92.                    #
#   * Linear move to 'home cell':    G1                                        #
#   * Wait for move to complete:     G4 P0                                     #
#   * Wait for another 2 seconds:    G4 P2000                                  #
#   * Move to (X,Y) with feedrate F: G1 Xxxx Yxxx Fxxx                         #
#   * Wait till move is complete:    G4 P0                                     #
#   * Fire inkjet nozzle:            M240 Sxxx                                 #
#   * Linear move to 'home cell':    G1                                        #
#   * Wait for move to complete:     G4 P0                                     #
#                                                                              #
#   Sets every 'column-th' bit of nozzle(12 bits + 4 extra) to true.           #
#------------------------------------------------------------------------------#

    def gcodeCreate(self):

        self.output += "G92 X" + str(self.origin[0]) + " Y" + str(self.origin[1]) + "\n"
        self.output += "G1 X" + str(self.home[0]) + " Y" + str(self.home[1]) + "\n"

        self.output += "G4 P0" + "\n"
        self.output += "G4 P2000" + "\n"


        nozzleFirings = [0 for x in range(0, self.cols)]
        scan = reversed(range(0, self.rows))

        for y in scan:
            for x in range(0, self.cols):
                color = self.img[y, x]

                if color <= self.black:
                    nozzleFirings[x] += 1 << y % self.nozzles
                else:
                    pass

            if y % 12 == 0 and y > 0:
                
                for column, firingVal in enumerate(nozzleFirings):
                    
                    if firingVal:
                        
                        self.output += "G1 X"+str(self.increment*column) + " Y" + str(y / 12 * self.spread) + " F" + str(self.feedrate) + "\n"

                        self.output += "G4 P0\n"
                        self.output += "M240"+ " S" +str(firingVal)+"\n"
                
                nozzleFirings = [0 for x in range(0, self.cols)]

        self.output += "G1 X" + str(self.home[0]) + " Y" + str(self.home[1]) + "\n"
        self.output += "G4 P0" + "\n"

        f = open(self.outFile, 'w')
        f.write(self.output)
        f.close()


    def terminalDebug(self):

        print("Rows: " + str(self.rows))
        print("Cols: " + str(self.cols))
        print("Spread: " + str(self.spread) + "mm")
        print("Nozzles: " + str(self.nozzles))
        print("Print Area: " + str(self.printArea) + "mm")

        rowStr = ""
        for y in range(0, self.rows):
            rowStr = ""
            for x in range(0, self.cols):
                color = self.img[y, x]
                if  color <= self.black:
                    rowStr += " "
                else:
                    rowStr += termcolor.colored(" ", 'white', 'on_white')
            print(rowStr)


if __name__ == "__main__":
    #Setup Command line arguments
    parser = argparse.ArgumentParser(prog="Slicer.py",
                                     usage="%(prog)s [options] input...origin...home...",
                                     description="Convert bitmaps to gcode."
                                     )
    parser.add_argument("-o", "--output",
                        default=sys.stdout,
                        help="Output file, defaults to stdout"
                        )
    parser.add_argument("-a", "--area",
                        default="[200, 200]",
                        help="Print area in millimeters."
                        )
    parser.add_argument("-f", "--feedrate",
                        default="1000",
                        help="Print feedrate. Default: %(default)s"
                        )
    parser.add_argument("input",
                        help="Input bitmap image path"
                        )
    parser.add_argument("origin",
                        help="Origin coordinate for SPRINTER"
                        )
    parser.add_argument("home",
                        help="Target coordinate for SPRINTER"
                        )

    #Always output help by default
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)  # Exit after help display

    args = parser.parse_args()

    imageProcessor = ImageToGcode(img = args.input,
                                  origin = ast.literal_eval(args.origin),
                                  home = ast.literal_eval(args.home),
                                  area = ast.literal_eval(args.area),
                                  feedrate = float(args.feedrate)
                                  )
