"""
Python script to sort data from a test file then create a cvs file
presenting these data as well as ploting a graph.
Pass in argument the file you want the data to be sort from.
"""

"""
##### IMPORTS ####
"""
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import csv
import madgwick as mgk # Madfwick script for quaternions

"""
##### DEFINES #####
"""
SAMPLE_RATE = 0.5

"""
##### FUNCTIONS ####
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
        Convert the unsigned values into signed one
    """
    return -(value & 0x8000) | (value & 0x7fff)
    
"""
### CLASS DEFINITIONS ###
"""
class IMU:
    """
        Class representing one IMU, and all the data it can provide
        + few functions to work on those data
    """
    def __init__(self):
        """
            Call when a instance is created
        """
        self.time_axis = []             # X axis for ploting graph
        self.data = []                  # list all data provided by the IMU
        self.x = []                     # X axis for ploting graph
        self.quaternion = []            # list of calcuted quaternions
        for i in range(4):
            self.quaternion.append([])  # create the empty list of quaternions
        for i in range(11):
            self.data.append([])        # create the empty list of data
            
    def plot_graph(self):
        """
            Call to plot the graph using data of the IMU
        """
        print ("<<< Ploting Data >>>")
        # Creating legend
        axe_x = mpatches.Patch(color='cyan', label='X axis')
        axe_y = mpatches.Patch(color='red', label='Y axis')
        axe_z = mpatches.Patch(color='green', label='Z axis')
        
        plt.figure(1)       # creating figure
        plt.subplot(211)    # 2 lines, 1 column, 1st position
        plt.ylabel("accelerometer (m/s2)")  # text to show on Y axis
        # Plot the accelerometer values
        plt.plot(self.x, self.data[0], "c-", self.x, self.data[1], "r-", self.x, self.data[2], "g-")
        plt.legend(handles=[axe_x, axe_y, axe_z]) # display the legend on this first plot
        
        plt.subplot(212) # 2 lines, 1 column, 2nd position
        plt.ylabel("gyrometer (deg/sec)")  # text to show on Y axis
        plt.plot(self.x, self.data[3], "c-", self.x, self.data[4], "r-", self.x, self.data[5], "g-")
        plt.show() # Display the plot     
        
    def convert_data(self, reg_type="acc"):
        """
            Convert the raw data values into formated data
        """
        print ("<<< Converting Data >>>")
        reg = {"acc": [0, 2, 16384], "gyr": [3, 5, 131.072]} # dictionary listing all the formating 
        for i in range(reg[reg_type][0], reg[reg_type][1]+1): 
            for j in range(len(self.data[i])):
                self.data[i][j] = float(self.data[i][j])/float(reg[reg_type][2])
    
    def comp_quaternion(self):
        """
            Compute the quaternions for each sample value
        """
        print("<<< Computing Quaternion >>>")
        for i in range(len(self.data[0])): # Calling the madgwick script for each sample
            q0, q1, q2, q3 = mgk.MadgwickAHRSupdate(self.data[3][i], self.data[4][i], self.data[5][i], self.data[0][i], self.data[1][i], self.data[2][i], self.data[6][i], self.data[7][i], self.data[8][i])
            # Append result at each list
            self.quaternion[0].append(q0)
            self.quaternion[1].append(q1)
            self.quaternion[2].append(q2)
            self.quaternion[3].append(q3)
        
class test_set:
    """
        This class define a complete test, with several IMUs and files
    """
    def __init__(self, nbr_imu=1):
        """
            Called at the instance creation
        """
        self.imu = []           # list of IMUs
        self.file_name = ""     # the file which will be used for the data
        self.path_to_file = ""  # path to the file_name
        self.rtc = ""           # the value of the rtc
        for i in range(nbr_imu):
            self.imu.append(IMU())  # Open IMU objects to imu list
            
    def create_sheet(self, nbr_imu=1):
        """
            Function to create a CVS file presenting all the data
        """
        print ("<<< Creating Spreadsheet >>>")
        output = open(self.path_to_file + "/" + self.file_name+'.csv', "wb") # Open/create the cvs file
        writer = csv.writer(output, delimiter=",")      # To write into the file
        writer.writerow([self.file_name + " results"])  # write the first line
        writer.writerow(["Date : " + self.rtc])         # write the rtc value (date and time of the test)
        # For each line in the file, write a concatenation of the value at a given time
        for i in range(len(self.imu)):
            # Turn the vertical list into horizontal ones
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
        output.close()  # closing file

"""
#### MAIN SCRIPT ####
"""
args = sys.argv[1:] # Read the arguments passed to the script

if (len(args) != 1): # Too much argument given, print the usage of the script
    print("ERROR: "+ str(len(args)) + " argument passed, only 1 expected\nUSAGE: python draw_graph path/test")
    sys.exit(1)      # exiting returning 1
    
temp_imu = raw_input("How many IMU used during the test ?\n>> ") # asking for the number of imu used
test_ins = test_set(int(temp_imu))  # create the test instance
   
# Extract file_name and path from the argument
test_ins.file_name = (args[0].rsplit("/").pop(-1)) # slice path with / as separator, keeping only the last part
args[0] = sys.path[0] + "/" + args[0]
args[0] = args[0].rsplit("/")
args[0].pop(-1)
test_ins.path_to_file = "/".join(args[0])

my_file = open(test_ins.path_to_file + "/" + test_ins.file_name, "r") # Open the file
content = my_file.read() # put file content in a variable
my_file.close()          # close file

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
# deleting local variables
del register_index
del imu_index

# Adjust lists length for ploting
print ("<<< Adjusting list length >>>")
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
del maxi    # deleting local variable

# Convert data and creating x abscisse
for i in range(len(test_ins.imu)):
    test_ins.imu[i].x = np.arange(0, (len(test_ins.imu[i].data[0])*SAMPLE_RATE), SAMPLE_RATE)
    test_ins.imu[i].convert_data("acc")
    test_ins.imu[i].convert_data("gyr")
    test_ins.imu[i].comp_quaternion()   # computing quaternion

"""
    Debugging prints
"""
print test_ins.imu[0].quaternion[0]
test_ins.create_sheet(temp_imu)
test_ins.imu[0].plot_graph()

print ("<<< Done : " + test_ins.file_name + " >>>")

"""
##### END OF SCRIPT #####
"""
