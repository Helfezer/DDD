#!/usr/bin/env python


"""
3D3 - ESME Sudria
2017/02/13

Little python script to copy the data file from a test from the
SDCard to the PC, you can precise the source and destination for
the copy.
This script also execute a first formatting of the data, splitting
the file into multiple (a file for each line) placed in a directory
create in the user directory (created if not existing).
"""

"""
####### IMPORTS ########
"""
import datetime as dt
import subprocess as sb
import os
import sys

"""
####### DEFINES ########
"""
SRC_PATH = "/media/seb/5A26-C954" 
DEST_PATH = os.environ["HOME"]+"/esme/PROJET/tests"
FILE_NAME = "MMS.TXT"
TEST_NAME = "test_"
CP_SRC = SRC_PATH + "/" + FILE_NAME

"""
###### MAIN SCRIPT ######
"""

args = sys.argv[1:]     # Read the arguments passed to the script

if (len(args) == 1):    # First argument is source path
    SRC_PATH = args[0]
elif (len(args) == 2):  # Second argument is destination path
    CP_SRC = args[0] + "/" + FILE_NAME
    DEST_PATH = args[1]   
elif (len(args) > 2):
    print ("ERROR: Too much arguments passed (max 2)\nUSAGE: python copy_file.py source_path destination_path")
    sys.exit(1)

ct = dt.datetime.now()      # get current date and time
date = str(ct.year) + "_" + str(ct.month) + "_" + str(ct.day) + "_" + str(ct.hour) + "_" + str(ct.minute) + "_" + str(ct.second)    # formating date
DEST_PATH = DEST_PATH + "/" + date  # update destination path name
if not(os.path.isdir(DEST_PATH)):   # check if directory exist, if not let's create it
    sb.call(["mkdir", "-p", DEST_PATH])
    
sb.call(["cp","-r", CP_SRC, DEST_PATH + "/" + FILE_NAME])   # copy file from sdcard to archive directory

my_file = open(DEST_PATH + "/" + FILE_NAME, "r")            # Opening file just copied (reading mode)
content = my_file.read()                                    # put file content into variable
my_file.close()                                             # closing file


list_test = content.rsplit("\n")         # split the raw data into multiple single test (list)
list_test.pop(-1)                        # deleting the last empty list
for i in range(len(list_test)):          # creating a file for each test
    temp_name = TEST_NAME + str(i)
    sb.call(["touch", DEST_PATH + "/" + temp_name])
    temp_file = open(DEST_PATH + "/" + temp_name, "w")
    temp_file.write(list_test[i])
    temp_file.close()
