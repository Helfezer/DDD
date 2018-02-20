"""
Python script to sort data from test file then create a cvs file
presenting these data as well as ploting a graph.
Pass in argument the file you want to the data sort from.
"""

"""
##### IMPORTS ####
"""
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import csv

SAMPLE_RATE = 0.5

"""
##### FUNCTION ####
"""
def extract_bytes(n, m_list):
    """
        Extract the n first elements of the array m_list
    """
    ret = []
    for i in range(n):
        ret.append(m_list.pop(0))
    ret = ''.join(ret)
    return ret

def s16(value):
    """
        Convert the unsigned value into signed one
    """
    return -(value & 0x8000) | (value & 0x7fff)
    
"""
### CLASS DEFINITION ###
"""
class IMU:
    """
        Methods
    """
    def __init__(self):
        self.time_axis = []
        self.data = []
        self.x = []
        for i in range(11):
            self.data.append([])
            
    def plot_graph(self):
        print ("<<< Ploting Data >>>")
        # Creating legend
        axe_x = mpatches.Patch(color='cyan', label='X axis')
        axe_y = mpatches.Patch(color='red', label='Y axis')
        axe_z = mpatches.Patch(color='green', label='Z axis')
        
        plt.figure(1) # creating figure
        plt.subplot(211) # 2 lines, 1 column, 1st position
        plt.ylabel("accelerometer (m/s2)")
        plt.plot(self.x, self.data[0], "c-", self.x, self.data[1], "r-", self.x, self.data[2], "g-")
        plt.legend(handles=[axe_x, axe_y, axe_z])
        
        plt.subplot(212) # 2 lines, 1 column, 2nd position
        plt.ylabel("gyrometer (deg/sec)")
        plt.plot(self.x, self.data[3], "c-", self.x, self.data[4], "r-", self.x, self.data[5], "g-")
        # Display the plot
        plt.show()       
        
    def convert_data(self, reg_type="acc"):
        """
            Convert the raw data values format data
        """
        print ("<<< Converting Data >>>")
        reg = {"acc": [0, 2, 16384], "gyr": [3, 5, 131.072]}
        for i in range(reg[reg_type][0], reg[reg_type][1]+1): 
            for j in range(len(self.data[i])):
                self.data[i][j] = float(self.data[i][j])/float(reg[reg_type][2])
        
class test_set:
    def __init__(self, nbr_imu=1):
        self.imu = []
        self.file_name = ""
        self.path_to_file = ""
        self.rtc = ""
        for i in range(nbr_imu):
            self.imu.append(IMU())
            
    def create_sheet(self, nbr_imu=1):
        print ("<<< Creating Spreadsheet >>>")
        output = open(self.path_to_file + "/" + self.file_name+'.csv', "wb")
        writer = csv.writer(output, delimiter=",")
        writer.writerow([self.file_name + " results"])
        writer.writerow(["Date : " + self.rtc])
        for i in range(len(self.imu)):
            writer.writerow(["IMU number " + str(i)])
            to_write = ["Time", "Acceleromer", "", "",  "Gyrometer", "", "", "Magnenometer", "", "", "Temperature", "ADC Value"]
            writer.writerow(to_write)
            to_write = ["", "X axis", "Y axis", "Z axis", "X axis", "Y axis", "Z axis","X axis", "Y axis", "Z axis"]
            writer.writerow(to_write)
            for j in range(len(self.imu[i].data[0])):
                to_write = [self.imu[i].x[j]]
                for k in range(11):
                    to_write.append(self.imu[i].data[k][j])
                writer.writerow(to_write)
        output.close()

"""
#### MAIN SCRIPT ####
"""
# Read the arguments passed to the script
args = sys.argv[1:]

if (len(args) != 1):
    print("ERROR: "+ str(len(args)) + " argument passed, only 1 expected\nUSAGE: python draw_graph path/test")
    sys.exit(1)
    
# ask for the number of imu used
temp_imu = raw_input("How many IMU used during the test ?\n>> ")
# create the test instance
test_ins = test_set(int(temp_imu))    
   
# Extract file name and path to this file from the argument
test_ins.file_name = (args[0].rsplit("/").pop(-1)) # slice path with / as separator, keeping only the last part
args[0] = sys.path[0] + "/" + args[0]
args[0] = args[0].rsplit("/")
args[0].pop(-1)
test_ins.path_to_file = "/".join(args[0])

# Open the file
my_file = open(test_ins.path_to_file + "/" + test_ins.file_name, "r")
content = my_file.read()
my_file.close()

content = list(content)                          # cast to list
data = []
test_ins.rtc = "".join(content[:14])             # saving RTC data
data = content[14:len(content)]                  # saving other data

# Sort data in list
register_index = 0
imu_index = 0

print ("<<< Sorting data >>>")

for _ in range(len(data)/4):
    test_ins.imu[imu_index].data[register_index].append(s16(int((extract_bytes(4, data)), 16)))
    register_index+=1
    if(register_index == 11):
        register_index = 0
        imu_index+=1
        if (imu_index == len(test_ins.imu)):
            imu_index = 0
del register_index
del imu_index

print ("<<< Adjusting list length >>>")
# Adjust lists length for ploting
for i in range(len(test_ins.imu)): # parsing all imus
    maxi = 0            # max length
    # first loop, getting max length
    for j in range(11): # for each imu parse all data
        if (len(test_ins.imu[i].data[j]) > maxi):
            maxi = len(test_ins.imu[i].data[j])
    # second loop, append 0 to short array
    for k in range(11):
        if (len(test_ins.imu[i].data[j]) < maxi):
            for _ in range(maxi-len(test_ins.imu[i].data[j])):
                test_ins.imu[i].data[j].append(0)
del maxi

# Convert data and creating x abscisse
for i in range(len(test_ins.imu)):
    test_ins.imu[i].x = np.arange(0, (len(test_ins.imu[i].data[0])*SAMPLE_RATE), SAMPLE_RATE)
    test_ins.imu[i].convert_data("acc")
    test_ins.imu[i].convert_data("gyr")
    
print test_ins.imu[0].data[0]
test_ins.create_sheet(temp_imu)
#test_ins.imu[0].plot_graph()

print ("<<< Done : " + test_ins.file_name + " >>>")






