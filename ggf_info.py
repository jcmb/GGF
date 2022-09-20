#!/usr/bin/env python3

from pprint import pprint
import sys
import logging
import argparse
from struct import *
import json



class GGF:

    GRID_HEADER_LENGTH=146


    @property
    def errorNumber(self):
         return self._errorNumber

    @property
    def errorString(self):
         return self._errorString

    @property
    def Grid(self):
         return self._grid

    @property
    def LatInterval(self):
         return self._LatInterval

    @property
    def LatGridSize(self):
         return self._LatGridSize

    @property
    def LatMin(self):
         return self._LatMin

    @property
    def LatMax(self):
         return self._LatMax

    @property
    def LongInterval(self):
         return self._LongInterval

    @property
    def LongGridSize(self):
         return self._LongGridSize

    @property
    def LongMin(self):
         return self._LongMin

    @property
    def LongMax(self):
         return self._LongMax

    @property
    def GridMissing(self):
         return self._GridMissing


    @property
    def GridNPole(self):
         return self._GridNPole

    @property
    def GridScalar(self):
         return self._GridScalar

    @property
    def GridSPole(self):
         return self._GridSPole

    @property
    def GridWindow(self):
         return self._GridWindow

    @property
    def MinValue(self):
         return self._MinValue

    @property
    def MinValueFooter(self):
         return self._MinValueFooter

    @property
    def MaxValue(self):
         return self._MaxValue

    @property
    def MaxValueFooter(self):
         return self._MaxValueFooter

    @property
    def Name(self):
         return self._Name

    @property
    def valid(self):
         return self._valid

    @property
    def version(self):
         return self._version


    def bitSet(self,b,bit):
#       Bit0=1
#       Bit7=128

        testBit=1<<bit
#        print(b)
#        print(testBit)
#        print((b & testBit) != 0)
        return ((b & testBit) != 0)

    def parseFlags(self,flags,strict):
        self._flags={}

#        pprint(flags)
        self._flags["GIF_GRID_WRAPS"]=self.bitSet(flags[0],0)
        self._flags["GIF_GRID_SCALED"]=self.bitSet(flags[0],1)
        self._flags["GIF_GRID_CHECK_MISSING"]=self.bitSet(flags[0],2)
        self._flags["GIF_GRID_NPOLE"]=self.bitSet(flags[0],3)
        self._flags["GIF_GRID_SPOLE"]=self.bitSet(flags[0],4)
        self._flags["GIF_GRID_XY"]=self.bitSet(flags[0],5)
        self._flags["GIF_REVERSE_AXES"]=self.bitSet(flags[0],6)
        self._flags["GIF_WGS84_BASED"]=self.bitSet(flags[0],7)

#       Flags 1 is documented in the standard but it is ignored in all the Trimble readers

        self._flags["GIF_UNITS_MILLIMETERS"]=self.bitSet(flags[1],0)
        self._flags["GIF_UNITS_CENTIMETERS"]=self.bitSet(flags[1],1)
        self._flags["GIF_UNITS_METERS"]=self.bitSet(flags[1],2)
        self._flags["GIF_UNITS_SURVEY_INCHES"]=self.bitSet(flags[1],3)
        self._flags["GIF_UNITS_SURVEY_FEET"]=self.bitSet(flags[1],4)
        self._flags["GIF_UNITS_INTL_INCHES"]=self.bitSet(flags[1],5)
        self._flags["GIF_UNITS_INTL_FEET"]=self.bitSet(flags[1],6)

        if flags[1]==0:
            if strict:
                return(False,101,"Units not set")
            else:
                self._flags["GIF_UNITS_METERS"]=True



        if flags[2]==0: #Really should have a striuck option
#            self._flags["GIF_INTERP_BILINEAR_DEFAULT"]=True
            return(False,102,"Interpolation not set")

        self._flags["GIF_INTERP_LINEAR"]=self.bitSet(flags[2],0)
        # Also known as NO_INTERP
        self._flags["GIF_INTERP_BILINEAR"]=self.bitSet(flags[2],1)
        self._flags["GIF_INTERP_SPLINE"]=self.bitSet(flags[2],2)
        self._flags["GIF_INTERP_BIQUADRATIC"]=self.bitSet(flags[2],3)
        self._flags["GIF_INTERP_QUADRATIC"]=self.bitSet(flags[2],4)
        self._flags["GIF_INTERP_GPS_MSL"]=self.bitSet(flags[2],5)
        #Also known as _AG_BILINEAR


        if flags[3]==0:
            return(False,103,"Data formatat not set")

        self._flags["GIF_FORMAT_BYTE"]=self.bitSet(flags[3],0)
        self._flags["GIF_FORMAT_SHORT"]=self.bitSet(flags[3],1)
        self._flags["GIF_FORMAT_LONG"]=self.bitSet(flags[3],2)
        self._flags["GIF_FORMAT_FLOAT"]=self.bitSet(flags[3],3)
        self._flags["GIF_FORMAT_DOUBLE"]=self.bitSet(flags[3],4)
        self._flags["GIF_FORMAT_LONG_DOUBLE"]=self.bitSet(flags[3],5)

        if not self._flags["GIF_FORMAT_FLOAT"]:
           return(False,202,"Only Floats are supported at this time")


        self._flags["GIF_LAT_ASCENDING"]=self.bitSet(flags[4],0)
        self._flags["GIF_LAT_DESCENDING"]=self.bitSet(flags[4],1)
        self._flags["GIF_LAT_NOT_ASCENDING"]=not self._flags["GIF_LAT_ASCENDING"]
        if flags[4]==0:
            if strict:
                return(False,104,"Lat direction not set")
            else:
                self._flags["GIF_LAT_ASCENDING"]=True

#        self._flags["GIF_LAT_NORTHINGS"]=self.bitSet(flags[4],2)
#        self._flags["GIF_LAT_SOUTHINGS"]=self.bitSet(flags[4],3)

        self._flags["GIF_LON_ASCENDING"]=self.bitSet(flags[5],0)
        self._flags["GIF_LON_DESCENDING"]=self.bitSet(flags[5],1)
        self._flags["GIF_LON_NOT_ASCENDING"]=not self._flags["GIF_LON_ASCENDING"]
        if flags[5]==0:
            if strict:
                return(False,105,"Long direction not set")
            else:
                self._flags["GIF_LON_ASCENDING"]=True
#        self._flags["GIF_LON_EASTINGS"]=self.bitSet(flags[5],2)
#        self._flags["GIF_LON_WESTINGS"]=self.bitSet(flags[5],3)

        return(True,0,"")


    def parseGrid(self, ggfFile):
        self._grid=[]
        self._MinValue=None
        self._MaxValue=None
        for lat in range(self._LatGridSize):
            start=self.GRID_HEADER_LENGTH + lat * self._LongGridSize * 4
            end=self.GRID_HEADER_LENGTH + (lat+1) * self._LongGridSize * 4
#            print(start,end,end-start)

#            print("<{}f".format(self._LongGridSize))
            longs=list(unpack("<{}f".format(self._LongGridSize),ggfFile[start: end]))
            # Has to be a list to do the assignment

            for longs_index in range(len(longs)):
                if longs[longs_index]==self._GridMissing:
                    longs[longs_index]=None
                else:
                    if self._MinValue == None or longs[longs_index] < self._MinValue:
                        self._MinValue = longs[longs_index]
                    if self._MaxValue == None or longs[longs_index] > self._MaxValue:
                        self._MaxValue = longs[longs_index]
#            pprint(longs)
            self._grid.append(longs)



    def validateAndParse(self, ggfFile,strict):
        # Validates the basic parts of GGF file.
        if len(ggfFile) < 146:
            return(False,1,"File to small to have the whole header")
#        pprint(ggfFile)
        if ggfFile[2:16] != b'TNL GRID FILE\x00':
            return(False,2,"Missing the Trimble Header")

        version=unpack("<H",ggfFile[0:2])[0]
        if version > 1 :
            return(False,3,"Version number is greater than 1")
        self._version=version

        Name=unpack("32s",ggfFile[16:48])[0]
        Name=Name.decode('ascii')
        Name=Name.rstrip("\x00")
        Name=Name.rstrip()
        self._Name=Name

        self._LatMin=unpack("<d",ggfFile[48:56])[0]
        self._LatMax=unpack("<d",ggfFile[56:64])[0]
        self._LongMin=unpack("<d",ggfFile[64:72])[0]
        self._LongMax=unpack("<d",ggfFile[72:80])[0]

        self._LatInterval=unpack("<d",ggfFile[80:88])[0]
        self._LongInterval=unpack("<d",ggfFile[88:96])[0]

        self._LatGridSize=unpack("<I",ggfFile[96:100])[0]
        self._LongGridSize=unpack("<I",ggfFile[100:104])[0]

        if abs((self._LatMin+(self._LatGridSize-1)*self._LatInterval) - self._LatMax) > 0.0001:
            return(False,4,"Lat Grid is inconsisten with Min and Step")

        if abs(self._LongMin+(self._LongGridSize-1)*self._LongInterval - self._LongMax) > 0.0001:
            return(False,5,"Long Grid is inconsisten with Min and Step")


        self._GridNPole=unpack("<d",ggfFile[104:112])[0]
        self._GridSPole=unpack("<d",ggfFile[112:120])[0]
        self._GridMissing=unpack("<d",ggfFile[120:128])[0]
        self._GridScalar=unpack("<d",ggfFile[128:136])[0]

        self._GridWindow=unpack("<H",ggfFile[136:138])[0]

        (valid, errNum, errString) = self.parseFlags(ggfFile[138:146],strict)
        if not valid:
            return (valid, errNum, errString)

        gridSize=(self._LatGridSize) * (self._LongGridSize) * 4

#        print(len(ggfFile),gridSize, gridSize+GRID_HEADER_LENGTH, gridSize+GRID_HEADER_LENGTH+16)

        if version == 0:
            if len(ggfFile) != gridSize + self.GRID_HEADER_LENGTH:
                return(False,6,"File size not consistent with the grid. V0")
            self._MinValue=None
            self._MaxValue=None

        elif version == 1:
            if len(ggfFile) != gridSize + self.GRID_HEADER_LENGTH+16:
                return(False,6,"File size not consistent with the grid. V1")
            self._MinValueFooter=unpack("<d",ggfFile[gridSize + self.GRID_HEADER_LENGTH:gridSize + self.GRID_HEADER_LENGTH+8])[0]
            self._MaxValueFooter=unpack("<d",ggfFile[gridSize + self.GRID_HEADER_LENGTH+8:gridSize + self.GRID_HEADER_LENGTH+16])[0]

        self.parseGrid(ggfFile)

        return(True,0,"")

    def __init__(self, ggfFile,strict):
        self._version=None
        (self._valid,self._errorNumber,self._errorString)=self.validateAndParse(ggfFile,strict)

    def dump(self,output):
        print(f"Version: {self.version}",file=output)
        print(f"Name: {self.Name}",file=output)
        print(f"Latitude:  Min: {self.LatMin}   Max: {self.LatMax}",file=output)
        print(f"Longitude: Min: {self.LongMin}   Max: {self.LongMax}",file=output)
        print(f"Interval: Lat: {self.LatInterval}   Max: {self.LongInterval}",file=output)
        print(f"GridSize: Lat: {self.LatGridSize}   Max: {self.LongGridSize}",file=output)
        print(f"Latitude:  Min: {self.LatMin}   Max: {self.LatMax} Max Step: {self.LatMin+(self.LatGridSize-1)*self.LatInterval}",file=output)
        print(f"Longitude: Min: {self.LongMin}   Max: {self.LongMax} Max Step: {self.LongMin+(self.LongGridSize-1)*self.LongInterval}",file=output)
        print(f"Poles:     North: {self.GridNPole}   South: {self.GridSPole}",file=output)
        print(f"Missing: {self.GridMissing}",file=output)
        print(f"Scalar:  {self.GridScalar}",file=output)
        print(f"Window:  {self.GridWindow}",file=output)
        print(f"Min Values:  {self.MinValue:.3f} from Footer {self.MinValueFooter:.3f}",file=output)
        print(f"Max Values:  {self.MaxValue:.3f} from Footer {self.MaxValueFooter:.3f}",file=output)
        pprint(self._flags,stream=output)

    def JSON(self):
        json={}
        json["column_count"]=self.LongGridSize
        if self._flags["GIF_INTERP_BIQUADRATIC"]:
            json["interpolation_method"]="bilinear"
        if self._flags["GIF_INTERP_SPLINE"]:
            json["interpolation_method"]="spline"
        json["interpolation-window"]=self.GridWindow
        json["latitude_interval"]=self.LatInterval
        json["longitude_interval"]=self.LongInterval
        json["name"]=self.Name
        json["origin_latitude"]=self.LatMin
        json["origin_longitude"]=self.LongMin
        json["row_count"]=self.LatGridSize
        json["separations"]=self._grid
        return(json)



def get_args():

    parser = argparse.ArgumentParser(fromfile_prefix_chars="@",description='Geoid File Summary.')

    parser.add_argument("GGF", type=argparse.FileType('rb'), help="GGF File to display info on",)
    parser.add_argument('--strict', action='store_true', help='Check the file for being strictly valid.\nIf not given use default values')
    parser.add_argument('--json', action='store_true', help='Output in JSON format.')
    parser.add_argument('--plot', action='store_true', help='Create a plot of the data.')
    parser.add_argument('--image', action='store_true', help='Create a image of the data.')
    parser = parser.parse_args()
    return (vars(parser))


def main():
    args=get_args()

    ggf=GGF(args["GGF"].read(),args["strict"])
    if ggf.valid:
        if args["json"]:
            json=ggf.JSON()
            print(json)
        elif args["plot"] or args["image"]:
            from matplotlib import pyplot as plt
            import numpy as np

            y = []
            for i in range (ggf.LatGridSize):
                y.append(ggf.LatMin + i*ggf.LatInterval)
#            pprint(x)
#            y = np.arange(start = ggf.LatMin,stop= ggf.LatMin+(ggf.LatGridSize)*ggf.LatInterval ,step=ggf.LatInterval)
#            x = np.arange(start = ggf.LongMin,stop= ggf.LongMin+(ggf.LongGridSize)*ggf.LongInterval ,step=ggf.LongInterval)
            x = []
            for i in range (ggf.LongGridSize):
                x.append(ggf.LongMin + i*ggf.LongInterval)


            if args["image"]:
                plt.figure(figsize=(12,9),dpi=200)
            else:
                plt.figure(figsize=(12,9))
            plt.ylabel('Latitude (Degrees)')
            plt.xlabel('Longitude (Degrees)')
            plt.title(ggf.Name)
            h = plt.contourf(x, y, ggf.Grid)
            plt.colorbar(h,label="Seperation")
            if args["image"]:
                plt.savefig(ggf.Name+".png")
            else:
                plt.show()
        else:
            ggf.dump(sys.stdout)


    else:
        print("GGF File is Invalid. Error {}. {}".format(ggf.errorNumber,ggf.errorString))
#   pprint(ggf)



if __name__ == '__main__':
    main()
