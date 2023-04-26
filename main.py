import sys
sys.path.append('../')
from Common.project_library import *

# Modify the information below according to you setup and uncomment the entire section

# 1. Interface Configuration
project_identifier = 'P3B' # enter a string corresponding to P0, P2A, P2A, P3A, or P3B
ip_address = '' # enter your computer's IP address
hardware = False # True when working with hardware. False when working in the simulation

# 2. Servo Table configuration
short_tower_angle = 315 # enter the value in degrees for the identification tower 
tall_tower_angle = 90 # enter the value in degrees for the classification tower
drop_tube_angle = 180#270# enter the value in degrees for the drop tube. clockwise rotation from zero degrees

# 3. Qbot Configuration
bot_camera_angle = 0 # angle in degrees between -21.5 and 0

# 4. Bin Configuration
# Configuration for the colors for the bins and the lines leading to those bins.
# Note: The line leading up to the bin will be the same color as the bin

bin1_offset = 0.60 # offset in meters
bin1_color = [1,0,0] # e.g. [1,0,0] for red
bin2_offset = 0.45
bin2_color = [0,0,1]
bin3_offset = 0.30
bin3_color = [1,1,1]
bin4_offset = 0.20
bin4_color = [0,0,0]

#--------------- DO NOT modify the information below -----------------------------

if project_identifier == 'P0':
    QLabs = configure_environment(project_identifier, ip_address, hardware).QLabs
    bot = qbot(0.1,ip_address,QLabs,None,hardware)
    
elif project_identifier in ["P2A","P2B"]:
    QLabs = configure_environment(project_identifier, ip_address, hardware).QLabs
    arm = qarm(project_identifier,ip_address,QLabs,hardware)

elif project_identifier == 'P3A':
    table_configuration = [short_tower_angle,tall_tower_angle,drop_tube_angle]
    configuration_information = [table_configuration,None, None] # Configuring just the table
    QLabs = configure_environment(project_identifier, ip_address, hardware,configuration_information).QLabs
    table = servo_table(ip_address,QLabs,table_configuration,hardware)
    arm = qarm(project_identifier,ip_address,QLabs,hardware)
    
elif project_identifier == 'P3B':
    table_configuration = [short_tower_angle,tall_tower_angle,drop_tube_angle]
    qbot_configuration = [bot_camera_angle]
    bin_configuration = [[bin1_offset,bin2_offset,bin3_offset,bin4_offset],[bin1_color,bin2_color,bin3_color,bin4_color]]
    configuration_information = [table_configuration,qbot_configuration, bin_configuration]
    QLabs = configure_environment(project_identifier, ip_address, hardware,configuration_information).QLabs
    table = servo_table(ip_address,QLabs,table_configuration,hardware)
    arm = qarm(project_identifier,ip_address,QLabs,hardware)
    bins = bins(bin_configuration)
    bot = qbot(0.1,ip_address,QLabs,bins,hardware)
    

#---------------------------------------------------------------------------------
# STUDENT CODE BEGINS
#---------------------------------------------------------------------------------

#CYCLE ATTRIBUTES
mass_on_qbot = 0
current_binID = None
containers_on_bot = 0
container_on_table = False

#QBOT POSITIONS
bin01_position = [1.027132272720337, 1.1968436241149902, 0.0007716274121776223]
bin02_position = [-0.0034288715105503798, 1.0386208295822144, 0.0007558059296570718]
bin03_position = [0.02494536153972149, -0.8869115114212036, 0.0007570171146653593]
bin04_position = [1.0486294031143188, -0.7918563485145569, 0.0007568645523861051]
qbot_home_position = [1.5, 0, 0]

#QARM POSITIONS
arm_pickup_position = [0.644, 0, 0.2733]
arm_home_position = [0.4065, 0, 0.4826]
arm_pre_load_position = [0.026, -0.0, 0.787]
arm_load_position1 = [0.0, -0.406, 0.483]
arm_load_position2 = [0.018, -0.515, 0.487]
arm_load_position3 = [0.018,-0.523, 0.518]
arm_post_load_position = [0.006, -0.184, 0.826]

def dispense_container(containerID):
    global container_on_table
    container_on_table = True #Set to true when container is dispensed
    material, mass, binID = table.dispense_container(containerID, True) #dispense container and save attributes
    print('Container with ID', containerID, 'dispensed.') #print attributes
    print('Material:', material)
    print('Mass:', mass, 'g')
    print('Destination:', binID)
    print()
    return material, mass, binID #return attributes

def load_container(container_info):
    material, mass, binID = container_info #extract container attributes
    global current_binID, mass_on_qbot, containers_on_bot #get global variables

    if current_binID == None: #Check if no containers loaded
        current_binID = binID #Set current binID to container's bin ID if no containers loaded
    
    if mass_on_qbot + mass > 90:  
        print('Weight exceeded by', mass_on_qbot + mass - 90, 'grams. Container will not be loaded.\n')#print if mass exceeds 90g
        return False #return false if container not loaded
    elif current_binID != binID:
        print('Container destination does not match qbot destination. Container will not be loaded.\n')
        return False #return false if container not loaded
    elif containers_on_bot >= 3:
        print('Qbot capacity reached. Container will not be loaded.\n')
        return False #return false if container not loaded
    print('Loading container...')
    mass_on_qbot += mass 
    containers_on_bot += 1
    #update information of containers
    arm.move_arm(*arm_pickup_position) #move arm to pickup
    time.sleep(1) 
    arm.control_gripper(45) #grab container
    time.sleep(1)
    arm.move_arm(*arm_home_position)#move arm to home
    time.sleep(1)
    arm.move_arm(*arm_pre_load_position) #move arm up to avoid knocking over other containers
    time.sleep(1)
    arm.rotate_base(-90) #rotate arm towards qbot
    time.sleep(1)
    arm.move_arm(*arm_load_position1) #move arm to loading position
    time.sleep(1)
    if containers_on_bot == 1:
       arm.move_arm(*arm_load_position2) #move arm forward a lot
    if containers_on_bot == 2:
       arm.move_arm(*arm_load_position3) #move arm forward a little
    time.sleep(1)
    arm.control_gripper(-45) #release container
    time.sleep(1)
    print('Current weight =', mass_on_qbot) #print total weight on the qbot
    arm.move_arm(*arm_post_load_position) #move arm back up to avoid knocking containers
    time.sleep(1)
    arm.home() #move arm back home
    global container_on_table #update container_on_table to be false once container is picked up
    container_on_table = False
    print("Done!")
    print()
    return True #return true if container loaded

def transfer_container(binID):
    bot.activate_ultrasonic_sensor() #activate sensor
    threshold = get_bin_distance(binID) #get maximum distance from qbot to correct bin
    ultrasonic_reading = bot.read_ultrasonic_sensor() 
    print('Transfering container...')
    while ultrasonic_reading > threshold: #follow yellow line until bin is found
        follow_line()
        ultrasonic_reading = bot.read_ultrasonic_sensor() #update readings
        print("Ultrasonic Distance: ", ultrasonic_reading) #print reading
        time.sleep(0.1)
    print("Bin found!") #print when bin is found by ultrasonic
    if binID == 'Bin01': #get specific position of bin1
        bin_position = bin01_position
    elif binID == 'Bin02': #get specific position of bin2
        bin_position = bin02_position
    elif binID == 'Bin03': #get specific position of bin3
        bin_position = bin03_position   
    elif binID == 'Bin04':#get specific position of bin4
        bin_position = bin04_position
    current_position = bot.position() #get position of qbot
    print("Positioning bot...")
    while abs(bin_position[0] - current_position[0]) > 0.01: #keep following line until bot is positioned well with bin
        follow_line()
        current_position = bot.position() #update bot position
    print("Done!")
    print()
    bot.stop() #stop bot and deactivate sensors
    bot.deactivate_ultrasonic_sensor()

def deposit_container(binID):
    threshold = get_bin_distance(binID) #get maximum distance from qbot to correct bin
    bot.activate_linear_actuator() #activate actuators and sensors
    bot.activate_ultrasonic_sensor()
    print('Depositing container...')
    if binID != 'Bin04': #dont move closer to bin if bin ID is Bin04 (bot is already close enough)
        align_bot() #align bot with yellow line before continuing for improved accurracy
        bot.rotate(-98) #rotate towards bin
        time.sleep(0.1)
    if binID == 'Bin01': #get specific position of bin1
        bin_position = bin01_position
    elif binID == 'Bin02': #get specific position of bin2
        bin_position = bin02_position
    elif binID == 'Bin03': #get specific position of bin3
        bin_position = bin03_position   
    elif binID == 'Bin04':#get specific position of bin4
        bin_position = bin04_position
    current_position = bot.position() #get position of qbot
    while abs(bin_position[1] - current_position[1]) > 0.03 and binID != 'Bin04': #loop until bin is close
        bot.set_wheel_speed([0.05, 0.05]) #move forward
        current_position = bot.position() #get bot position
    bot.stop() #stop once in position
    if binID != 'Bin04': #dont move closer to bin if bin ID is Bin04 (bot is already close enough)
        bot.rotate(95) #rotate hopper to face bin
        bot.dump() #dump containers
        bot.rotate(-95) #rotate back to face bin'
        bot.set_wheel_speed([-0.07, -0.07]) #move back
        ultrasonic_reading = bot.read_ultrasonic_sensor() #get ultrasonic readings
        print("Backing away from bin...")
        while ultrasonic_reading < threshold:#move back until bin is out of range
            ultrasonic_reading = bot.read_ultrasonic_sensor() #update ultrasonic readings
            print("Ultrasonic reading:", ultrasonic_reading)
        bot.stop()
        bot.rotate(98) #rotate to face forward on line
    else:
        bot.dump() #just dump container if BinID equals Bin04
    global current_binID, containers_on_bot, mass_on_qbot #reset container attributes
    containers_on_bot = 0 #reset container count  
    mass_on_qbot = 0 #reset total mass
    current_binID = None #reset qbot destination
    print("Done!")
    print()

def return_home():
    global qbot_home_position #coordinates of home position
    position = bot.position() #get current position of bot
    print('Returning to home position...')
    while abs(position[0] - qbot_home_position[0]) > 0.05 or abs(position[1] - qbot_home_position[1]) > 0.01:
        #follow yellow line until home position is in range
        follow_line()
        position = bot.position()
    align_bot() #align bot with yellow line and stop
    bot.stop()
    print("Done!")
    print()

def follow_line():
    left_IR, right_IR = bot.line_following_sensors() #get line following sensor data
    if left_IR == 0 and right_IR == 1: #if bot veers to the right of line, move left
        bot.set_wheel_speed([0.055,0.035])
    elif left_IR == 1 and right_IR == 0:#if bot veers to the left of line, move right
        bot.set_wheel_speed([0.035, 0.055])
    elif left_IR == 1 and right_IR == 1: #if bot is on line, move forward
        bot.set_wheel_speed([0.05, 0.05])
    else:
        bot.set_wheel_speed([-0.05, -0.05]) #if bot is off line, move back until line is found

def get_bin_distance(container_ID): #outputs maximum distance between qbot and desired bin.
    if container_ID == 'Bin01': 
        threshold = 0.5 #maximum distance from qbot to bin1
    elif container_ID == 'Bin02':
        threshold = 0.33 #maximum distance from qbot to bin2
    elif container_ID == 'Bin03':
        threshold = 0.2 #maximum distance from qbot to bin3
    elif container_ID == 'Bin04':
        threshold = 0.09 #maximum distance from qbot to bin4
    return threshold

def align_bot(): #aligns bot with yellow line for more accurate movements
    left_IR, right_IR = bot.line_following_sensors() #get line following sensor data
    while left_IR == 0 and right_IR == 1: #if bot is to the left of line, rotate right until on line
        left_IR, right_IR = bot.line_following_sensors()
        bot.set_wheel_speed([0.02,-0.02])
    while left_IR == 1 and right_IR == 0: #if bot is to the right of line, rotate left until on line
        left_IR, right_IR = bot.line_following_sensors()
        bot.set_wheel_speed([-0.02, 0.02])

def set_qbot_load_position(load_position): #moves qbot closer to qarm when loading and back onto line when transfering
    if load_position: 
        direction = 1
    else: #reverse direction of rotation if transfering
        direction = -1
    print("Preparing qbot for loading..." if load_position else "Preparing qbot for transfering...")
    bot.rotate(-95 * direction) #turn towards qarm if loading, otherwise turn away
    time.sleep(1)
    bot.forward_distance(0.07) #move closer to qarm if loading, otherwise move back onto yellow line
    time.sleep(1)
    bot.rotate(95 * direction) #turn to align with yellow line
    print()
 
def main():
    arm.home() #reset arm position
    global container_on_table
    while True:
        set_qbot_load_position(True) #move qbot closer to qarm for loading
        load_more = True #true if qarm should load more containers
        while load_more: #keep loading if load_more is true
            if not container_on_table: #dispense a random container if there is no container already dispensed
               info = dispense_container(random.randint(1,6)) 
            load_more = load_container(info) #update load_more based on container attributes
        set_qbot_load_position(False) #move qbot back onto line
        align_bot() #align qbot with line to ensure it is straight
        transfer_container(current_binID) #transfer container to correct bin
        deposit_container(current_binID) #deposit containers
        return_home() #follow yellow line back home
        align_bot() #align bot before starting a new cycle

main() #run main code

#---------------------------------------------------------------------------------
# STUDENT CODE ENDS
#---------------------------------------------------------------------------------
