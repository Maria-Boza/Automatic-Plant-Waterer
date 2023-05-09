# Ashley Heckman (agh93) & Maria Boza (mib57)
# Wednesday Lab, Team 6
# ECE 5725 Final Project
# water.py

import time
import pygame
import os
from pygame.locals import*
import RPi.GPIO as GPIO
from plant_monitor import PlantMonitor

#########################################################################################################
# Basic Pygame Stuff
#########################################################################################################

pygame.init()

black = 0  , 0  , 0
white = 255, 255, 255
red   = 255, 0  , 0
green = 0  , 255, 0
blue  = 0  , 0  , 255
sel   = 0  , 213, 255
nsel  = 70 , 70  , 70

size = width, height = 320, 240
body  = pygame.font.Font(None, 20)
header = pygame.font.Font(None, 25)
plant = pygame.font.Font(None, 17)

screen = pygame.display.set_mode(size)
screen.fill(black)

screen_num = 0

#########################################################################################################
# TFT/Monitor Display Stuff
#########################################################################################################

# Display on the monitor (comment to display on piTFT)
'''
os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb1')
os.putenv('SDL_MOUSEDRV', 'TSLIB')
os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')
'''

# Don't show mouse cursor if we're displaying on piTFT (comment if displaying on monitor)
# pygame.mouse.set_visible(False)

#########################################################################################################
# Water Pump Basic Control
#########################################################################################################

# Water pump power output, don't want it to pump to start with
GPIO.setmode(GPIO.BCM)
GPIO.setup(5,GPIO.OUT)
GPIO.output(5, GPIO.LOW)
GPIO.setup(6,GPIO.OUT)
GPIO.output(6, GPIO.LOW)

# PWM Instance
GPIO.setup(26, GPIO.OUT)
pwm26 = GPIO.PWM(26, 100)
pwm26.start(20)

# Keep track of if we're currently watering the plant
currently_watering = False

# Keep track of the time that we last started and stopped the water
last_water_start = time.time()
last_water_end = time.time()

# Keep track of if we've watered the plant yet
watered = False

# Start water function
def start_water():

    # Send power to the motor
    GPIO.output(5, GPIO.HIGH)

    # Update variable to reflect we're currently watering
    global currently_watering
    currently_watering = True

    # Update the last water start time
    global last_water_start
    last_water_start = time.time()

    # Update to reflect that plant has been watered at least once
    global watered
    watered = True

    # Print that we've started water along with the time
    print("Water Started: " + str(time.localtime(last_water_start)[1]) + "/" + str(time.localtime(last_water_start)[2]) + " @ " + str(time.localtime(last_water_start)[3]) + ":" + str(time.localtime(last_water_start)[4]) + ":" + str(time.localtime(last_water_start)[5]))

# Stop water function
def stop_water():

    # Send power to the motor
    GPIO.output(5, GPIO.LOW)

    # Update variable to reflect we're not currently watering
    global currently_watering
    currently_watering = False

    # Update the last water stop time
    global last_water_end
    last_water_end = time.time()

    # Print that we've stopped water along with the time
    print("Water Stopped: " + str(time.localtime(last_water_end)[1]) + "/" + str(time.localtime(last_water_end)[2]) + " @ " + str(time.localtime(last_water_end)[3]) + ":" + str(time.localtime(last_water_end)[4]) + ":" + str(time.localtime(last_water_end)[5]))

#########################################################################################################
# Quit Button
#########################################################################################################

GPIO.setup(27, GPIO.IN, pull_up_down = GPIO.PUD_UP)

code_run = True

# Quit the program and stop the water pump
def GPIO27_callback(channel):
    global code_run
    code_run = False

GPIO.add_event_detect(27, GPIO.FALLING, callback = GPIO27_callback, bouncetime = 300)

#########################################################################################################
# Watering Modes
#########################################################################################################

schedule_type = ["Manual", "Moisture Sensor", "Intervals"]
schedule_selected = 0
desired_moisture = 0

#########################################################################################################
# Setup the soil moisture/temperature/humidity sensor
#########################################################################################################
moisture = 0
temp = 0
humidity = 0

pm = PlantMonitor()
pm.led_off()

#########################################################################################################
# Setup the light sensor
#########################################################################################################
light = 0


#########################################################################################################
# GUI Homescreen
#########################################################################################################

# Home screen buttons
home_buttons = {'Start/Stop Water':(int(width/4), 220), 'Edit Schedule':(int(3*width/4), 220)}
home_buttons_rect = {}

# Display the GUI homepage (screen 0)
def display_home():
    
    # Erase everything on the screen
    screen.fill(black)

    # Display moisture level
    moisture_text = "Soil Moisture: " + str(moisture) + "%"
    moisture_text_surface = body.render(moisture_text, True, white)
    moisture_rect = moisture_text_surface.get_rect(center = (int(width/2), 15))
    screen.blit(moisture_text_surface, moisture_rect)

    # Display temperature
    temp_text = "Air Temperature: " + str(temp) + "° F"
    temp_text_surface = body.render(temp_text, True, white)
    temp_rect = temp_text_surface.get_rect(center = (int(width/2), 40))
    screen.blit(temp_text_surface, temp_rect)

    # Display humidity
    humidity_text = "Humidity: " + str(humidity) + "%"
    humidity_text_surface = body.render(humidity_text, True, white)
    humidity_rect = humidity_text_surface.get_rect(center = (int(width/2), 65))
    screen.blit(humidity_text_surface, humidity_rect)

    # Display light
    light_text = "Light: " + str(light) + " lux"
    light_text_surface = body.render(light_text, True, white)
    light_rect = light_text_surface.get_rect(center = (int(width/2), 90))
    screen.blit(light_text_surface, light_rect)

    # Display time the plant was last watered header
    water_header_text = "Last Watered"
    water_header_text_surface = header.render(water_header_text, True, white)
    water_header_rect = water_header_text_surface.get_rect(center = (int(width/2), 120))
    screen.blit(water_header_text_surface, water_header_rect)

    # If we haven't watered the plant yet, display N/A for time plant was last watered
    if not watered:
        water_text = "N/A"
        water_text_surface = body.render(water_text, True, white)
        water_rect = water_text_surface.get_rect(center = (int(width/2), 140))
        screen.blit(water_text_surface, water_rect)
    # Display time the plant was last watered
    elif not currently_watering:
        last_water_start_text = str(time.localtime(last_water_start)[1]) + "/" + str(time.localtime(last_water_start)[2]) + " " + str((time.localtime(last_water_start)[3], time.localtime(last_water_start)[3] - 12)[time.localtime(last_water_start)[3] > 12]) + (":", ":0")[time.localtime(last_water_start)[4] < 10] + str(time.localtime(last_water_start)[4]) + (".", ".0")[time.localtime(last_water_start)[5] < 10] + str(time.localtime(last_water_start)[5]) + (" am", " pm")[time.localtime(last_water_start)[3] > 11]
        last_water_end_text =   str(time.localtime(last_water_end)[1])   + "/" + str(time.localtime(last_water_end)[2])   + " " + str((time.localtime(last_water_end)[3], time.localtime(last_water_end)[3] - 12)[time.localtime(last_water_end)[3] > 12])       + (":", ":0")[time.localtime(last_water_end)[4] < 10]   + str(time.localtime(last_water_end)[4])   + (".", ":0")[time.localtime(last_water_end)[5] < 10]   + str(time.localtime(last_water_end)[5])   + (" am", " pm")[time.localtime(last_water_end)[3] > 11]
        water_text = last_water_start_text + " - " + last_water_end_text
        water_text_surface = body.render(water_text, True, white)
        water_rect = water_text_surface.get_rect(center = (int(width/2), 140))
        screen.blit(water_text_surface, water_rect)
    # If we're currently watering, it doesn't make sense to display times, so just display that we're currently watering
    else:
        water_text = "Currently Watering"
        water_text_surface = body.render(water_text, True, white)
        water_rect = water_text_surface.get_rect(center = (int(width/2), 140))
        screen.blit(water_text_surface, water_rect)

    # Display the watering schedule header
    schedule_header_text = "Current Watering Schedule"
    schedule_header_text_surface = header.render(schedule_header_text, True, white)
    schedule_header_rect = schedule_header_text_surface.get_rect(center = (int(width/2), 170))
    screen.blit(schedule_header_text_surface, schedule_header_rect)

    # Display the current watering schedule
    schedule_text = (("Water for " + str(interval_w_time) + " " + str(interval_units[interval_w_time_selected]) + " every " + str(interval_b_time) + " " + str(interval_units[interval_b_time_selected]), "Water when soil moisture < " + str(desired_moisture) + "%")[schedule_selected == 1], schedule_type[0])[schedule_selected == 0]
    schedule_text_surface = body.render(schedule_text, True, white)
    schedule_rect = schedule_text_surface.get_rect(center = (int(width/2), 190))
    screen.blit(schedule_text_surface, schedule_rect)

    # Display the buttons
    for button_text, text_pos in home_buttons.items():
      if button_text == "Start/Stop Water":
          text_surface = body.render(("Start Water", "Stop Water")[currently_watering], True, (nsel, white)[schedule_selected == 0])
      else:
          text_surface = body.render(button_text, True, white)
      rect = text_surface.get_rect(center = text_pos)
      screen.blit(text_surface, rect)
      home_buttons_rect[button_text] = rect

    # Display the new screen
    pygame.display.flip()

#########################################################################################################
# GUI Select Mode Screen
#########################################################################################################

control_buttons = {'Next':(int(width/4), 220), 'Cancel':(int(3*width/4), 220)}
control_buttons_rect = {}

sched_buttons = {'Manual':(30, 10), 'Moisture':(30, 88), 'Intervals':(30, 150)}
sched_buttons_rect = {}

manual_selected = False
moisture_selected = False
intervals_selected = False

# Display the GUI to edit schedule page (screen 1)
def display_set_schedule1():
    
    # Erase everything on the screen
    screen.fill(black)

    # Display the control buttons
    for button_text, text_pos in sched_buttons.items():
      if (button_text == "Manual" and manual_selected):
        text_surface = header.render(button_text, True, sel)
      elif (button_text == "Moisture" and moisture_selected):
          text_surface = header.render(button_text, True, sel)
      elif (button_text == "Intervals" and intervals_selected):
          text_surface = header.render(button_text, True, sel)
      else:
          text_surface = header.render(button_text, True, white)
      rect = text_surface.get_rect(topleft = text_pos)
      screen.blit(text_surface, rect)
      sched_buttons_rect[button_text] = rect

    # Display the description for each schedule type
    manual_descript1_surface = body.render("The user may manually turn on and off the ", True, white)
    manual_descript2_surface = body.render("water. The system will not automatically", True, white)
    manual_descript3_surface = body.render("water the plant in this mode.", True, white)
    screen.blit(manual_descript1_surface, manual_descript1_surface.get_rect(topleft = (30, 30)))
    screen.blit(manual_descript2_surface, manual_descript2_surface.get_rect(topleft = (30, 45)))
    screen.blit(manual_descript3_surface, manual_descript3_surface.get_rect(topleft = (30, 60)))

    moisture_descript1_surface = body.render("Automatically water the plant when the", True, white)
    moisture_descript2_surface = body.render("soil moisture dips below a set level.", True, white)
    screen.blit(moisture_descript1_surface, moisture_descript1_surface.get_rect(topleft = (30, 108)))
    screen.blit(moisture_descript2_surface, moisture_descript2_surface.get_rect(topleft = (30, 123)))
    
    interval_descript1_surface = body.render("Automatically water the plant for a", True, white)
    interval_descript2_surface = body.render("set amount of time at a set interval.", True, white)
    screen.blit(interval_descript1_surface, interval_descript1_surface.get_rect(topleft = (30, 170)))
    screen.blit(interval_descript2_surface, interval_descript2_surface.get_rect(topleft = (30, 185)))

    # Display the control buttons
    for button_text, text_pos in control_buttons.items():
      if (button_text == "Next" and not (manual_selected or moisture_selected or intervals_selected)):
          text_surface = body.render(button_text, True, nsel)
      else:
        text_surface = body.render(button_text, True, white)
      rect = text_surface.get_rect(center = text_pos)
      screen.blit(text_surface, rect)
      control_buttons_rect[button_text] = rect
    
    # Display the new screen
    pygame.display.flip()

#########################################################################################################
# GUI Set Values for Selected Mode Screen
#########################################################################################################

# Basic control buttons
control_buttons2 = {"Set":(int(width/4), 220), "Back":(int(2*width/4), 220), "Cancel":(int(3*width/4), 220)}
control_buttons2_rect = {}

moisture_buttons = {"U_hund":((138,105), (141,100), (144,105)), "U_ten":((149,105), (152,100), (155,105)), "U_one":((160,105), (163,100), (166,105)),
                    "D_hund":((138,110), (141,115), (144,110)), "D_ten":((149,110), (152,115), (155,110)), "D_one":((160,110), (163,115), (166,110))}
                 
moisture_buttons_rect = {}

interval_arrows = {"U_w_ten":((45,90), (48,85), (51,90)), "U_w_one":((56,90), (59,85), (62,90)), 
                   "U_w_unit":((95,90), (100,85), (105,90)), "U_b_ten":((185,90), (188,85), (191,90)), 
                   "U_b_one":((196,90), (199,85), (202,90)), "U_b_unit":((235,90), (240,85), (245,90)), 
                   "D_w_ten":((45,95), (48,100), (51,95)), "D_w_one":((56,95), (59,100), (62,95)), 
                   "D_w_unit":((95,95), (100,100), (105,95)), "D_b_ten":((185,95), (188,100), (191,95)), 
                   "D_b_one":((196,95), (199,100), (202,95)), "D_b_unit":((235,95), (240,100), (245,95))}
interval_arrows_rect = {}

interval_units = ("seconds", "minutes", "hours", "days")
interval_w_time_selected = 0
interval_b_time_selected = 1
interval_w_time_selected_tent = 0
interval_b_time_selected_tent = 2

moisture_thous = 0
moisture_hund = 0
moisture_ten = 0
moisture_one = 0

interval_time_b_ten = 0
interval_time_b_one = 1
interval_time_w_ten = 0
interval_time_w_one = 5
interval_b_time = 10*interval_time_b_ten + interval_time_b_one
interval_w_time = 10*interval_time_w_ten + interval_time_w_one

# The time for each watering is just the watering time that the user specifies
water_time_sec = 10*interval_time_w_ten + interval_time_w_one
if interval_w_time_selected > 0:
    water_time_sec *= 60
if interval_w_time_selected > 1:
    water_time_sec *= 60
if interval_w_time_selected > 2:
    water_time_sec *= 24

# The time between waterings is equal to the "every ___" time minus the time we want to water for
# For example, if we want to water the plant for 1 second every 5 seconds, we would
# water for 1 second, wait for 4 seconds, water for 1 second, wait for 4 seconds, etc.
between_time_sec = 10*interval_time_b_ten + interval_time_b_one
if interval_b_time_selected > 0:
    between_time_sec *= 60
if interval_b_time_selected > 1:
    between_time_sec *= 60
if interval_b_time_selected > 2:
    between_time_sec *= 24
between_time_sec -= water_time_sec

# Display the GUI to edit schedule page (screen 2)
def display_set_schedule2():
    
    # Erase everything on the screen
    screen.fill(black)

    # Display header for type of schedule user chose
    sched_header_surface = header.render((("Interval Mode","Moisture Sensing Mode")[moisture_selected],"Manual Mode")[manual_selected], True, white)
    screen.blit(sched_header_surface, sched_header_surface.get_rect(center = (int(width/2), 20)))

    # If user selected manual mode, nothing more for them to do. Give brief message
    if manual_selected:
        manual_sel1_surface = body.render("The user is in charge of watering the plant. ", True, white)
        manual_sel2_surface = body.render("The system will not automatically water the", True, white)
        manual_sel3_surface = body.render("plant in this mode.", True, white)
        manual_sel4_surface = body.render("Click set to save these changes.", True, white)
        manual_sel5_surface = body.render("Click back to select a different mode.", True, white)
        manual_sel6_surface = body.render("Click cancel to return to the homescreen", True, white)
        manual_sel7_surface = body.render("and discard all changes.", True, white)
        screen.blit(manual_sel1_surface, manual_sel1_surface.get_rect(center = (int(width/2), 50)))
        screen.blit(manual_sel2_surface, manual_sel2_surface.get_rect(center = (int(width/2), 70)))
        screen.blit(manual_sel3_surface, manual_sel3_surface.get_rect(center = (int(width/2), 90)))
        screen.blit(manual_sel4_surface, manual_sel4_surface.get_rect(center = (int(width/2), 130)))
        screen.blit(manual_sel5_surface, manual_sel5_surface.get_rect(center = (int(width/2), 150)))
        screen.blit(manual_sel6_surface, manual_sel6_surface.get_rect(center = (int(width/2), 170)))
        screen.blit(manual_sel7_surface, manual_sel7_surface.get_rect(center = (int(width/2), 185)))

    # If user selected moisture mode, prompt for desired moisture level
    elif moisture_selected:
        moisture_sel1_surface = body.render("The system will automatically water the plant", True, white)
        moisture_sel2_surface = body.render("when the soil moisture level drops below", True, white)
        moisture_sel3_surface = body.render(str(moisture_hund) + " " + str(moisture_ten) + " " + str(moisture_one) + " %", True, white)
        moisture_sel4_surface = body.render("Click set to save these changes.", True, white)
        moisture_sel5_surface = body.render("Click back to select a different mode.", True, white)
        moisture_sel6_surface = body.render("Click cancel to return to the homescreen", True, white)
        moisture_sel7_surface = body.render("and discard all changes.", True, white)
        screen.blit(moisture_sel1_surface, moisture_sel1_surface.get_rect(center = (int(width/2), 50)))
        screen.blit(moisture_sel2_surface, moisture_sel2_surface.get_rect(center = (int(width/2), 70)))
        screen.blit(moisture_sel3_surface, moisture_sel3_surface.get_rect(center = (int(width/2), 90)))
        screen.blit(moisture_sel4_surface, moisture_sel4_surface.get_rect(center = (int(width/2), 130)))
        screen.blit(moisture_sel5_surface, moisture_sel5_surface.get_rect(center = (int(width/2), 150)))
        screen.blit(moisture_sel6_surface, moisture_sel6_surface.get_rect(center = (int(width/2), 170)))
        screen.blit(moisture_sel7_surface, moisture_sel7_surface.get_rect(center = (int(width/2), 185)))

        # Diplay the number control arrows
        for label, tri_pos in moisture_buttons.items():
            if (label == "U_hund"):
                tri = pygame.draw.polygon(screen, (nsel, white)[moisture_hund < 1], tri_pos)
            elif (label == "U_ten"):
                tri = pygame.draw.polygon(screen, (nsel, white)[moisture_ten < 9 and moisture_hund < 1], tri_pos)
            elif (label == "U_one"):
                tri = pygame.draw.polygon(screen, (nsel, white)[moisture_one < 9 and moisture_hund < 1], tri_pos)
            elif (label == "D_hund"):
                tri = pygame.draw.polygon(screen, (nsel, white)[moisture_hund > 0], tri_pos)
            elif (label == "D_ten"):
                tri = pygame.draw.polygon(screen, (nsel, white)[moisture_ten > 0], tri_pos)
            elif (label == "D_one"):
                tri = pygame.draw.polygon(screen, (nsel, white)[moisture_one > 0], tri_pos)
            moisture_buttons_rect[label] = tri

    # If user selected interval mode, prompt for desired watering interval
    elif intervals_selected:
        interval_sel1_surface = body.render("The system will automatically water the plant", True, white)
        interval_sel2_surface = body.render(str(interval_time_w_ten) + " " + str(interval_time_w_one) + "                    every  " + str(interval_time_b_ten) + " " + str(interval_time_b_one) + "                  ", True, white)
        interval_sel3_surface = body.render("Click set to save these changes.", True, white)
        interval_sel4_surface = body.render("Click back to select a different mode.", True, white)
        interval_sel5_surface = body.render("Click cancel to return to the homescreen", True, white)
        interval_sel6_surface = body.render("and discard all changes.", True, white)
        screen.blit(interval_sel1_surface, interval_sel1_surface.get_rect(center = (int(width/2), 50)))
        screen.blit(interval_sel2_surface, interval_sel2_surface.get_rect(center = (int(width/2), 70)))
        screen.blit(interval_sel3_surface, interval_sel3_surface.get_rect(center = (int(width/2), 130)))
        screen.blit(interval_sel4_surface, interval_sel4_surface.get_rect(center = (int(width/2), 150)))
        screen.blit(interval_sel5_surface, interval_sel5_surface.get_rect(center = (int(width/2), 170)))
        screen.blit(interval_sel6_surface, interval_sel6_surface.get_rect(center = (int(width/2), 185)))

        interval_sel7_surface = body.render(interval_units[interval_w_time_selected_tent], True, white)
        screen.blit(interval_sel7_surface, interval_sel7_surface.get_rect(center = (100, 70)))

        interval_sel7_surface = body.render(interval_units[interval_b_time_selected_tent], True, white)
        screen.blit(interval_sel7_surface, interval_sel7_surface.get_rect(center = (240, 70)))

        # Diplay the number control arrows
        for label, tri_pos in interval_arrows.items():
            if (label == "U_w_ten"):
                tri = pygame.draw.polygon(screen, (nsel, white)[interval_time_w_ten < 5], tri_pos)
            elif (label == "U_w_one"):
                tri = pygame.draw.polygon(screen, (nsel, white)[interval_time_w_one < 9], tri_pos)
            elif (label == "U_w_unit"):
                tri = pygame.draw.polygon(screen, (nsel, white)[interval_w_time_selected_tent < 3 and ((interval_w_time_selected_tent + 1) <= interval_b_time_selected_tent)], tri_pos)
            elif (label == "U_b_ten"):
                tri = pygame.draw.polygon(screen, (nsel, white)[interval_time_b_ten < 5], tri_pos)
            elif (label == "U_b_one"):
                tri = pygame.draw.polygon(screen, (nsel, white)[interval_time_b_one < 9], tri_pos)
            elif (label == "U_b_unit"):
                tri = pygame.draw.polygon(screen, (nsel, white)[interval_b_time_selected_tent < 3], tri_pos)

            elif (label == "D_w_ten"):
                tri = pygame.draw.polygon(screen, (nsel, white)[interval_time_w_ten > 0 and (10*interval_time_w_ten + interval_time_w_one) - 10 > 0], tri_pos)
            elif (label == "D_w_one"):
                tri = pygame.draw.polygon(screen, (nsel, white)[interval_time_w_one > 0 and (10*interval_time_w_ten + interval_time_w_one) - 1 > 0], tri_pos)
            elif (label == "D_w_unit"):
                tri = pygame.draw.polygon(screen, (nsel, white)[interval_w_time_selected_tent > 0], tri_pos)
            elif (label == "D_b_ten"):
                tri = pygame.draw.polygon(screen, (nsel, white)[interval_time_b_ten > 0 and (10*interval_time_b_ten + interval_time_b_one) - 10 > 0], tri_pos)
            elif (label == "D_b_one"):
                tri = pygame.draw.polygon(screen, (nsel, white)[interval_time_b_one > 0 and (10*interval_time_b_ten + interval_time_b_one) - 1 > 0], tri_pos)
            elif (label == "D_b_unit"):
                tri = pygame.draw.polygon(screen, (nsel, white)[interval_b_time_selected_tent > 0 and (interval_w_time_selected_tent <= (interval_b_time_selected_tent - 1))], tri_pos)
            interval_arrows_rect[label] = tri
            
    # Display the control buttons
    for button_text, text_pos in control_buttons2.items():
        if (intervals_selected and interval_w_time_selected_tent == interval_b_time_selected_tent and 10*interval_time_w_ten + interval_time_w_one >= 10*interval_time_b_ten + interval_time_b_one and button_text == "Set"):
            text_surface = body.render(button_text, True, nsel)
            rect = text_surface.get_rect(center = text_pos)
            screen.blit(text_surface, rect)
            control_buttons2_rect[button_text] = rect
        else:
            text_surface = body.render(button_text, True, white)
            rect = text_surface.get_rect(center = text_pos)
            screen.blit(text_surface, rect)
            control_buttons2_rect[button_text] = rect

    # Display the new screen
    pygame.display.flip()

control_buttons_m = {"Next":(int(width/4), 220), "Back":(int(2*width/4), 220), "Cancel":(int(3*width/4), 220)}
control_buttons_m_rect = {}
plant_type_buttons = {"Flower":(int(width/4), 150), "Fruit":(int(2*width/4), 150), "Tree/Shrub":(int(3*width/4), 150), "My Own Value":(int(width/2), 180)}
plant_type_buttons_rect = {}

def display_plant_sel():

    # Erase everything on the screen
    screen.fill(black)

    # Display header for type of schedule user chose
    sched_header_surface = header.render("Moisture Sensing Mode", True, white)
    screen.blit(sched_header_surface, sched_header_surface.get_rect(center = (int(width/2), 20)))

    # Display message prompting user if they want to use reference values or set their own values
    moisture_m1_surface = body.render("If you would like to use pre-defined reference", True, white)
    moisture_m2_surface = body.render("values, select your plant type. You will be", True, white)
    moisture_m3_surface = body.render("prompted for a specific plant on the next page.", True, white)
    moisture_m4_surface = body.render("Otherwise, select 'My Own Value'.", True, white)
    screen.blit(moisture_m1_surface, moisture_m1_surface.get_rect(center = (int(width/2), 50)))
    screen.blit(moisture_m2_surface, moisture_m2_surface.get_rect(center = (int(width/2), 70)))
    screen.blit(moisture_m3_surface, moisture_m3_surface.get_rect(center = (int(width/2), 90)))
    screen.blit(moisture_m4_surface, moisture_m4_surface.get_rect(center = (int(width/2), 110)))

    # Display the plant type
    for button_text, text_pos in plant_type_buttons.items():
      if (button_text == "Flower" and flower_selected):
        text_surface = body.render(button_text, True, sel)
      elif (button_text == "Fruit" and fruit_selected):
          text_surface = body.render(button_text, True, sel)
      elif (button_text == "Tree/Shrub" and tree_selected):
          text_surface = body.render(button_text, True, sel)
      elif (button_text == "My Own Value" and own_selected):
          text_surface = body.render(button_text, True, sel)
      else:
          text_surface = body.render(button_text, True, white)
      rect = text_surface.get_rect(center = text_pos)
      screen.blit(text_surface, rect)
      plant_type_buttons_rect[button_text] = rect

    # Display the control buttons
    for button_text, text_pos in control_buttons_m.items():
        if button_text == "Next" and not (flower_selected or fruit_selected or tree_selected or own_selected):
            text_surface = body.render(button_text, True, nsel)
        else:
            text_surface = body.render(button_text, True, white)
        rect = text_surface.get_rect(center = text_pos)
        screen.blit(text_surface, rect)
        control_buttons_m_rect[button_text] = rect

    # Display the new screen
    pygame.display.flip()

#########################################################################################################
# Reference Values
#########################################################################################################

# Recommended Soil Moisture Percentages
# All data from https://www.acurite.com/blog/soil-moisture-guide-for-plants-and-vegetables.html

categories = ["Flowers", "Fruits", "Trees & Shrubs"]
moisture_levels = [(0,20), (21,40), (41,60), (61,80)]

Flowers1 = [("Agave", 0, 1), ("Aster", 1), ("Astilbe", 2), ("Big Blue Stem", 1), ("Bleeding Heart", 2),
           ("Butterfly Weed", 1), ("Cactus", 0, 1), ("Catmint", 1), ("Christmas Fern", 1), ("Coneflower", 1),
           ("Daffodil", 1, 2), ("Dalia", 1, 2), ("Daylilly", 1, 2), ("Gaillardia", 1), ("Heath/Heather", 1),
           ("Hellebores", 2), ("Hosta", 1, 2), ("Hyssop", 1), ("Iris", 1, 2), ("Ironweed", 2), ("Jack In Pulpits", 2),
           ("Joe-Pye Weed", 2), ("Lavendar", 1), ("Lemon Balm", 1)]
Flowers2 = [("Lily", 1, 2), ("Lobellia", 2, 3), ("Lupine", 2),
           ("Marigold", 1), ("Marsh Marigold", 3), ("May Apple", 2), ("Meadow Rue", 2, 3), ("Monarda", 1),
           ("Ornamental Grasses", 1), ("Peony", 1, 2), ("Petunia", 1), ("Poppy", 1),
           ("Purple Coneflower", 1), ("Queen of the Prairie", 2), ("Red Milkweed", 2), ("Sedge", 1, 2, 3),
           ("Sedum", 0, 1), ("Pansy", 1, 2), ("Tulip", 1, 2), ("Violet", 1, 2), ("Yarrow", 0, 1), ("Yucca", 0, 1),
           ("Zinnia", 1)]
flower1_rect = {}
flower2_rect = {}

Fruits = [("Apple", 1, 2), ("Grape", 1, 2), ("Fig", 1, 2), ("Peach", 1, 2), ("Pear", 1, 2),
          ("Raspberry", 1, 2), ("Strawberry", 1, 2), ("Blackberry", 1, 2), ("Blueberry", 2), ("Cranberry", 3)]
fruit_rect = {}

TreesShrubs1 = [("Alpine Current", 1), ("American Filbert", 1, 2), ("American Holly", 1), ("Amur Privet", 1),
               ("Arborvitae", 1), ("Azalea", 1, 2), ("Bald Cypress", 1, 2, 3), ("Barberry", 1), ("Birch", 2),
               ("Black Tupelo", 1), ("Chinese Juniper", 1), ("Clematis", 1, 2), ("Common Boxwood", 1),
               ("Common Elderberry", 2), ("Common Lilac", 1), ("Crab Apple", 1), ("Crape Myrtle", 1, 2),
               ("Dawn Redwood", 2, 3), ("Dogwood", 2, 3), ("Eastern Red Cedar", 1), ("Elderberry", 1, 2, 3),
               ("Elm", 1, 2), ("Frazier Fir", 1), ("Gardenia", 1)]
TreesShrubs2 = [("Ginkgo", 1), ("Hawthorn", 1), ("Holly", 1),
               ("Honey Locust", 1), ("Horse Chestnut", 1), ("Hydragea", 2), ("Juniper", 1), ("Lilac", 1), ("Maple", 1),
               ("Mockorange", 1), ("New Jersey Tea", 1), ("Oak", 1), ("Ohio Buckeye", 1), ("Potentilla", 0, 1),
               ("Red Cedar", 2), ("Red Twig Dogwood", 2), ("Rhodendron", 2), ("Rose", 1), ("Rugosa Rose", 0, 1),
               ("Saucer Magnolia", 1), ("Serviceberry", 1, 2), ("Silver Maple", 1, 2), ("Spirea", 1), ("Spruce", 1)]
TreesShrubs3 = [("Sugar Maple", 1), ("Swamp White Oak", 3), ("Sweetshrub", 1, 2), ("Tamarac/Larch", 2, 3), ("White Fir", 1),
               ("White Pine", 2), ("Willow", 2, 3)]
tree1_rect = {}
tree2_rect = {}
tree3_rect = {}

sum = 0
num = 0
for flower in Flowers1:
    sum += (moisture_levels[flower[1]][0] + moisture_levels[flower[len(flower)-1]][1])/2
    num += 1
for flower in Flowers2:
    sum += (moisture_levels[flower[1]][0] + moisture_levels[flower[len(flower)-1]][1])/2
    num += 1

generalFlower = int(round(sum / num))
print(generalFlower)

sum = 0
num = 0
for fruit in Fruits:
    sum += (moisture_levels[fruit[1]][0] + moisture_levels[fruit[len(fruit)-1]][1])/2
    num += 1

generalFruit = int(round(sum / num))
print(generalFruit)

sum = 0
num = 0
for tree in TreesShrubs1:
    sum += (moisture_levels[tree[1]][0] + moisture_levels[tree[len(tree)-1]][1])/2
    num += 1
for tree in TreesShrubs2:
    sum += (moisture_levels[tree[1]][0] + moisture_levels[tree[len(tree)-1]][1])/2
    num += 1
for tree in TreesShrubs3:
    sum += (moisture_levels[tree[1]][0] + moisture_levels[tree[len(tree)-1]][1])/2
    num += 1

generalTreeShrub = int(round(sum / num))
print(generalTreeShrub)

#########################################################################################################
# Display select flower screen
#########################################################################################################

next_screen = {'>>>':(int(width - 35), 203)}
next_screen_rect = {}
flower_selected = False
fruit_selected = False
tree_selected = False
own_selected = False
other_selected = False
flower_sel = None
fruit_sel = None
tree_sel = None

def display_flowers1():

    # Erase everything on the screen
    screen.fill(black)

    # Display header for type of schedule user chose
    sched_header_surface = header.render("Moisture Sensing Mode", True, white)
    screen.blit(sched_header_surface, sched_header_surface.get_rect(center = (int(width/2), 20)))

    # Display message prompting user if they want to use reference values or set their own values
    moisture_m1_surface = body.render("Select the flower that you want to water. If", True, white)
    moisture_m2_surface = body.render("it does not appear on this screen, select '>>>'.", True, white)
    screen.blit(moisture_m1_surface, moisture_m1_surface.get_rect(center = (int(width/2), 45)))
    screen.blit(moisture_m2_surface, moisture_m2_surface.get_rect(center = (int(width/2), 65)))

    start_center = (int(width/6), 85)
    for flower in Flowers1:
        if flower[0] == flower_sel:
            text_surface = plant.render(flower[0], True, sel)
        else:
            text_surface = plant.render(flower[0], True, white)
        rect = text_surface.get_rect(center = start_center)
        screen.blit(text_surface, rect)
        flower1_rect[flower[0]] = rect
        start_center = (start_center[0], start_center[1] + 15)
        if start_center[1] >= 205:
            start_center = (start_center[0] + int(2*width/6), 85)

    # Display the control buttons
    for button_text, text_pos in control_buttons_m.items():
        if (button_text == "Next" and flower_sel == None and other_selected == False):
            text_surface = body.render(button_text, True, nsel)
        else:
            text_surface = body.render(button_text, True, white)
        rect = text_surface.get_rect(center = text_pos)
        screen.blit(text_surface, rect)
        control_buttons_m_rect[button_text] = rect
    
    # Go to next page arrow to select plants later in alphabet
    for button_text, text_pos in next_screen.items():
        text_surface = header.render(button_text, True, white)
        rect = text_surface.get_rect(center = text_pos)
        screen.blit(text_surface, rect)
        next_screen_rect[button_text] = rect

    # Display the new screen
    pygame.display.flip()

no_ref = {'<<<':(35, 203), 'Other':(int(5*width/6), 195)}
no_ref_rect = {}

def display_flowers2():

    # Erase everything on the screen
    screen.fill(black)

    # Display header for type of schedule user chose
    sched_header_surface = header.render("Moisture Sensing Mode", True, white)
    screen.blit(sched_header_surface, sched_header_surface.get_rect(center = (int(width/2), 20)))

    # Display message prompting user if they want to use reference values or set their own values
    moisture_m1_surface = body.render("Select the flower that you want to water. If", True, white)
    moisture_m2_surface = body.render("it does not appear on this screen, select 'Other'.", True, white)
    screen.blit(moisture_m1_surface, moisture_m1_surface.get_rect(center = (int(width/2), 45)))
    screen.blit(moisture_m2_surface, moisture_m2_surface.get_rect(center = (int(width/2), 65)))

    start_center = (int(width/6), 85)
    for flower in Flowers2:
        if flower[0] == flower_sel:
            text_surface = plant.render(flower[0], True, sel)
        else:
            text_surface = plant.render(flower[0], True, white)
        rect = text_surface.get_rect(center = start_center)
        screen.blit(text_surface, rect)
        flower2_rect[flower[0]] = rect
        start_center = (start_center[0], start_center[1] + 15)
        if start_center[1] >= 205:
            start_center = (start_center[0] + int(2*width/6), 85)

    # Display the control buttons
    for button_text, text_pos in control_buttons_m.items():
        if (button_text == "Next" and flower_sel == None and other_selected == False):
            text_surface = body.render(button_text, True, nsel)
        else:
            text_surface = body.render(button_text, True, white)
        rect = text_surface.get_rect(center = text_pos)
        screen.blit(text_surface, rect)
        control_buttons_m_rect[button_text] = rect
    
    # Go to next page arrow to select plants later in alphabet
    for button_text, text_pos in no_ref.items():
        if (button_text == "Other" and other_selected):
            text_surface = header.render(button_text, True, sel)
        else:
            text_surface = header.render(button_text, True, white)
        rect = text_surface.get_rect(center = text_pos)
        screen.blit(text_surface, rect)
        no_ref_rect[button_text] = rect

    # Display the new screen
    pygame.display.flip()

#########################################################################################################
# Display select fruit screen
#########################################################################################################

fruit_buttons = {'Other':(int(3*width/6), 125)}
fruit_buttons_rect = {}

def display_fruit():

    # Erase everything on the screen
    screen.fill(black)

    # Display header for type of schedule user chose
    sched_header_surface = header.render("Moisture Sensing Mode", True, white)
    screen.blit(sched_header_surface, sched_header_surface.get_rect(center = (int(width/2), 20)))

    # Display message prompting user if they want to use reference values or set their own values
    moisture_m1_surface = body.render("Select the fruit that you want to water. If", True, white)
    moisture_m2_surface = body.render("it does not appear on this screen, select 'Other'.", True, white)
    screen.blit(moisture_m1_surface, moisture_m1_surface.get_rect(center = (int(width/2), 45)))
    screen.blit(moisture_m2_surface, moisture_m2_surface.get_rect(center = (int(width/2), 65)))

    start_center = (int(width/6), 85)
    for fruit in Fruits:
        if fruit[0] == fruit_sel:
            text_surface = plant.render(fruit[0], True, sel)
        else:
            text_surface = plant.render(fruit[0], True, white)
        rect = text_surface.get_rect(center = start_center)
        screen.blit(text_surface, rect)
        fruit_rect[fruit[0]] = rect
        start_center = (start_center[0], start_center[1] + 15)
        if start_center[1] >= 205:
            start_center = (start_center[0] + int(2*width/6), 85)

    # Display the control buttons
    for button_text, text_pos in control_buttons_m.items():
        if (button_text == "Next" and fruit_sel == None and other_selected == False):
            text_surface = body.render(button_text, True, nsel)
        else:
            text_surface = body.render(button_text, True, white)
        rect = text_surface.get_rect(center = text_pos)
        screen.blit(text_surface, rect)
        control_buttons_m_rect[button_text] = rect
    
    # Other button
    for button_text, text_pos in fruit_buttons.items():
        if (button_text == "Other" and other_selected):
            text_surface = header.render(button_text, True, sel)
        else:
            text_surface = header.render(button_text, True, white)
        rect = text_surface.get_rect(center = text_pos)
        screen.blit(text_surface, rect)
        fruit_buttons_rect[button_text] = rect

    # Display the new screen
    pygame.display.flip()

#########################################################################################################
# Display select tree screen
#########################################################################################################

tree_buttons = {">>>":(int(width - 50), 203), "<<<":(35, 203), "Other":(int(3*width/6), 140)}
tree_buttons_rect = {}

def display_tree1():

    # Erase everything on the screen
    screen.fill(black)

    # Display header for type of schedule user chose
    sched_header_surface = header.render("Moisture Sensing Mode", True, white)
    screen.blit(sched_header_surface, sched_header_surface.get_rect(center = (int(width/2), 20)))

    # Display message prompting user if they want to use reference values or set their own values
    moisture_m1_surface = body.render("Select the tree/shrub that you want to water.", True, white)
    moisture_m2_surface = body.render("If it does not appear on this screen, select '>>>'.", True, white)
    screen.blit(moisture_m1_surface, moisture_m1_surface.get_rect(center = (int(width/2), 45)))
    screen.blit(moisture_m2_surface, moisture_m2_surface.get_rect(center = (int(width/2), 65)))

    start_center = (int(width/6), 85)
    for tree in TreesShrubs1:
        if tree[0] == tree_sel:
            text_surface = plant.render(tree[0], True, sel)
        else:
            text_surface = plant.render(tree[0], True, white)
        rect = text_surface.get_rect(center = start_center)
        screen.blit(text_surface, rect)
        tree1_rect[tree[0]] = rect
        start_center = (start_center[0], start_center[1] + 15)
        if start_center[1] >= 205:
            start_center = (start_center[0] + int(2*width/6), 85)

    # Display the control buttons
    for button_text, text_pos in control_buttons_m.items():
        if (button_text == "Next" and tree_sel == None and other_selected == False):
            text_surface = body.render(button_text, True, nsel)
        else:
            text_surface = body.render(button_text, True, white)
        rect = text_surface.get_rect(center = text_pos)
        screen.blit(text_surface, rect)
        control_buttons_m_rect[button_text] = rect
    
    # Other button
    for button_text, text_pos in tree_buttons.items():
        if (button_text == "<<<" or button_text == "Other"):
            continue
        text_surface = header.render(button_text, True, white)
        rect = text_surface.get_rect(center = text_pos)
        screen.blit(text_surface, rect)
        tree_buttons_rect[button_text] = rect

    # Display the new screen
    pygame.display.flip()

def display_tree2():

    # Erase everything on the screen
    screen.fill(black)

    # Display header for type of schedule user chose
    sched_header_surface = header.render("Moisture Sensing Mode", True, white)
    screen.blit(sched_header_surface, sched_header_surface.get_rect(center = (int(width/2), 20)))

    # Display message prompting user if they want to use reference values or set their own values
    moisture_m1_surface = body.render("Select the tree/shrub that you want to water.", True, white)
    moisture_m2_surface = body.render("If it does not appear on this screen, select '>>>'.", True, white)
    screen.blit(moisture_m1_surface, moisture_m1_surface.get_rect(center = (int(width/2), 45)))
    screen.blit(moisture_m2_surface, moisture_m2_surface.get_rect(center = (int(width/2), 65)))

    start_center = (int(width/6), 85)
    for tree in TreesShrubs2:
        if tree[0] == tree_sel:
            text_surface = plant.render(tree[0], True, sel)
        else:
            text_surface = plant.render(tree[0], True, white)
        rect = text_surface.get_rect(center = start_center)
        screen.blit(text_surface, rect)
        tree2_rect[tree[0]] = rect
        start_center = (start_center[0], start_center[1] + 15)
        if start_center[1] >= 205:
            start_center = (start_center[0] + int(2*width/6), 85)

    # Display the control buttons
    for button_text, text_pos in control_buttons_m.items():
        if (button_text == "Next" and tree_sel == None and other_selected == False):
            text_surface = body.render(button_text, True, nsel)
        else:
            text_surface = body.render(button_text, True, white)
        rect = text_surface.get_rect(center = text_pos)
        screen.blit(text_surface, rect)
        control_buttons_m_rect[button_text] = rect
    
    # Other button
    for button_text, text_pos in tree_buttons.items():
        if (button_text == "Other"):
            continue
        text_surface = header.render(button_text, True, white)
        rect = text_surface.get_rect(center = text_pos)
        screen.blit(text_surface, rect)
        tree_buttons_rect[button_text] = rect

    # Display the new screen
    pygame.display.flip()

def display_tree3():

    # Erase everything on the screen
    screen.fill(black)

    # Display header for type of schedule user chose
    sched_header_surface = header.render("Moisture Sensing Mode", True, white)
    screen.blit(sched_header_surface, sched_header_surface.get_rect(center = (int(width/2), 20)))

    # Display message prompting user if they want to use reference values or set their own values
    moisture_m1_surface = body.render("Select the tree/shrub that you want to water.", True, white)
    moisture_m2_surface = body.render("If it does not appear on this screen, select 'Other'.", True, white)
    screen.blit(moisture_m1_surface, moisture_m1_surface.get_rect(center = (int(width/2), 45)))
    screen.blit(moisture_m2_surface, moisture_m2_surface.get_rect(center = (int(width/2), 65)))

    start_center = (int(width/6), 85)
    for tree in TreesShrubs3:
        if tree[0] == tree_sel:
            text_surface = plant.render(tree[0], True, sel)
        else:
            text_surface = plant.render(tree[0], True, white)
        rect = text_surface.get_rect(center = start_center)
        screen.blit(text_surface, rect)
        tree3_rect[tree[0]] = rect
        start_center = (start_center[0], start_center[1] + 15)
        if start_center[1] >= 205:
            start_center = (start_center[0] + int(2*width/6), 85)

    # Display the control buttons
    for button_text, text_pos in control_buttons_m.items():
        if (button_text == "Next" and tree_sel == None and other_selected == False):
            text_surface = body.render(button_text, True, nsel)
        else:
            text_surface = body.render(button_text, True, white)
        rect = text_surface.get_rect(center = text_pos)
        screen.blit(text_surface, rect)
        control_buttons_m_rect[button_text] = rect
    
    # Other button
    for button_text, text_pos in tree_buttons.items():
        if button_text == ">>>":
            continue
        if (button_text == "Other" and other_selected):
            text_surface = header.render(button_text, True, sel)
        else:
            text_surface = header.render(button_text, True, white)
        rect = text_surface.get_rect(center = text_pos)
        screen.blit(text_surface, rect)
        tree_buttons_rect[button_text] = rect

    # Display the new screen
    pygame.display.flip()

#########################################################################################################
# Display moisture value for plant screen
#########################################################################################################

specific_buttons = {"Set":(int(width/8), 220), "Edit":(int(3*width/8), 220), "Back":(int(5*width/8), 220), "Cancel":(int(7*width/8), 220)}
specific_buttons_rect = {}
temp_desired_val = 0

def display_specific():

    # Erase everything on the screen
    screen.fill(black)

    # Display header for type of schedule user chose
    sched_header_surface = header.render("Moisture Sensing Mode", True, white)
    screen.blit(sched_header_surface, sched_header_surface.get_rect(center = (int(width/2), 20)))

    # Calculate the bounds and average values within those bounds
    lower_val = 0
    upper_val = 0
    if flower_selected:
        for flower in Flowers1:
            if flower[0] == flower_sel:
                lower_val = moisture_levels[flower[1]][0]
                upper_val = moisture_levels[flower[len(flower)-1]][1]
        for flower in Flowers2:
            if flower[0] == flower_sel:
                lower_val = moisture_levels[flower[1]][0]
                upper_val = moisture_levels[flower[len(flower)-1]][1]
    elif fruit_selected:
        for fruit in Fruits:
            if fruit[0] == fruit_sel:
                lower_val = moisture_levels[fruit[1]][0]
                upper_val = moisture_levels[fruit[len(fruit)-1]][1]
    elif tree_selected:
        for tree in TreesShrubs1:
            if tree[0] == tree_sel:
                lower_val = moisture_levels[tree[1]][0]
                upper_val = moisture_levels[tree[len(tree)-1]][1]
        for tree in TreesShrubs2:
            if tree[0] == tree_sel:
                lower_val = moisture_levels[tree[1]][0]
                upper_val = moisture_levels[tree[len(tree)-1]][1]
        for tree in TreesShrubs3:
            if tree[0] == tree_sel:
                lower_val = moisture_levels[tree[1]][0]
                upper_val = moisture_levels[tree[len(tree)-1]][1]

    global temp_desired_val
    temp_desired_val = int(round((lower_val + upper_val)/2))

    # Display message showing recommended value for that plant
    moisture_m1 = "The recommended soil moisture for a"
    moisture_m2 = ((tree_sel, flower_sel)[flower_selected], fruit_sel)[fruit_selected] + " is " + str(temp_desired_val) + "%"
    moisture_m1_surface = body.render(moisture_m1, True, white)
    moisture_m2_surface = body.render(moisture_m2, True, white)
    moisture_m3_surface = body.render("Click set to proceed with recommended value.", True, white)
    moisture_m4_surface = body.render("Click edit to edit this value.", True, white)
    moisture_m5_surface = body.render("Click back to go back to plant selection.", True, white)
    moisture_m6_surface = body.render("Click cancel to cancel all edits and return", True, white)
    moisture_m7_surface = body.render("to the homescreen.", True, white)
    screen.blit(moisture_m1_surface, moisture_m1_surface.get_rect(center = (int(width/2), 45)))
    screen.blit(moisture_m2_surface, moisture_m2_surface.get_rect(center = (int(width/2), 65)))
    screen.blit(moisture_m3_surface, moisture_m3_surface.get_rect(center = (int(width/2), 90)))
    screen.blit(moisture_m4_surface, moisture_m4_surface.get_rect(center = (int(width/2), 115)))
    screen.blit(moisture_m5_surface, moisture_m5_surface.get_rect(center = (int(width/2), 140)))
    screen.blit(moisture_m6_surface, moisture_m6_surface.get_rect(center = (int(width/2), 165)))
    screen.blit(moisture_m7_surface, moisture_m7_surface.get_rect(center = (int(width/2), 185)))

    # Display the control buttons
    for button_text, text_pos in specific_buttons.items():
        text_surface = body.render(button_text, True, white)
        rect = text_surface.get_rect(center = text_pos)
        screen.blit(text_surface, rect)
        specific_buttons_rect[button_text] = rect

    pygame.display.flip()

#########################################################################################################
# Display moisture value for general plant type screen
#########################################################################################################

def display_general():

    # Erase everything on the screen
    screen.fill(black)

    # Display header for type of schedule user chose
    sched_header_surface = header.render("Moisture Sensing Mode", True, white)
    screen.blit(sched_header_surface, sched_header_surface.get_rect(center = (int(width/2), 20)))

    # Display message showing recommended value for that plant type
    moisture_m1 = "The recommended soil moisture for a"
    moisture_m2 = "general " + (("tree", "flower")[flower_selected], "fruit")[fruit_selected] + " is " + str(((generalTreeShrub, generalFlower)[flower_selected], generalFruit)[fruit_selected]) + "%"
    moisture_m1_surface = body.render(moisture_m1, True, white)
    moisture_m2_surface = body.render(moisture_m2, True, white)
    moisture_m3_surface = body.render("Click set to proceed with recommended value.", True, white)
    moisture_m4_surface = body.render("Click edit to edit this value.", True, white)
    moisture_m5_surface = body.render("Click back to go back to plant selection.", True, white)
    moisture_m6_surface = body.render("Click cancel to cancel all edits and return", True, white)
    moisture_m7_surface = body.render("to the homescreen.", True, white)
    screen.blit(moisture_m1_surface, moisture_m1_surface.get_rect(center = (int(width/2), 45)))
    screen.blit(moisture_m2_surface, moisture_m2_surface.get_rect(center = (int(width/2), 65)))
    screen.blit(moisture_m3_surface, moisture_m3_surface.get_rect(center = (int(width/2), 90)))
    screen.blit(moisture_m4_surface, moisture_m4_surface.get_rect(center = (int(width/2), 115)))
    screen.blit(moisture_m5_surface, moisture_m5_surface.get_rect(center = (int(width/2), 140)))
    screen.blit(moisture_m6_surface, moisture_m6_surface.get_rect(center = (int(width/2), 165)))
    screen.blit(moisture_m7_surface, moisture_m7_surface.get_rect(center = (int(width/2), 185)))

    # Display the control buttons
    for button_text, text_pos in specific_buttons.items():
        text_surface = body.render(button_text, True, white)
        rect = text_surface.get_rect(center = text_pos)
        screen.blit(text_surface, rect)
        specific_buttons_rect[button_text] = rect

    pygame.display.flip()

#########################################################################################################
# GUI Control
#########################################################################################################

code_run = True
while code_run:
    
    ################################################
    # GUI Homescreen Functionalilty
    ################################################

    if ( screen_num == 0):

        # Get the moisture, temperature, and humidity values
        moisture = round(pm.get_wetness())
        temp = round(9*pm.get_temp()/5 + 32)
        humidity = round(pm.get_humidity())

        # Get the sunlight value
        sunlight = 0

        # Display the homescreen (with the updated values)
        display_home()

        # Reset the schedule selected variables
        # We do this in the case the the user advances to the next screen, then hits back or cancel
        # because we don't want anything to be selected when going into the second screen
        manual_selected = False
        moisture_selected = False
        intervals_selected = False

        # Check for button press. If button is pressed, perform its action
        for event in pygame.event.get():
            if ( event.type is MOUSEBUTTONUP ):
                pos = pygame.mouse.get_pos()
                x,y = pos

                for (text, rect) in home_buttons_rect.items():
                    if (rect.collidepoint(pos)):
                        # If user wants to edit the schedule, advance to the next screen
                        if (text == "Edit Schedule"):
                            print("Edit Schedule: Advancing to 'Select Mode' Screen")
                            screen_num = 1
                            stop_water()
                        # Otherwise, if the user wants to start or stop the water (and we're in manual watering mode),
                        # start/stop the water pump
                        elif (text == "Start/Stop Water"):
                            if schedule_selected == 0:
                                if currently_watering:
                                    stop_water()
                                else:
                                  start_water()

        # Water the plant for 3 seconds, wait 5 seconds, re-read moisture value, and water again if needed
        if schedule_selected == 1:
            if moisture < desired_moisture and not currently_watering:
                start_water()
            elif currently_watering and moisture > desired_moisture:
                stop_water()

        if schedule_selected == 2:
            if not currently_watering:
                if time.time() >= last_water_end + between_time_sec:
                    start_water()
            else:
                if time.time() >= last_water_start + water_time_sec:
                    stop_water()

    ################################################
    # GUI Select Mode Functionality
    ################################################

    elif ( screen_num == 1 ):

        # Display the select mode screen
        display_set_schedule1()

        own_selected = False
        flower_selected = False
        fruit_selected = False
        tree_selected = False

        # Check for button press. If button is pressed, perform its action
        for event in pygame.event.get():
            if ( event.type is MOUSEBUTTONUP ):
                pos = pygame.mouse.get_pos()
                x,y = pos

                for (text, rect) in control_buttons_rect.items():
                    if (rect.collidepoint(pos)):
                        # If the next button is hit and a mode is selected, go to the next screen
                        # If the next button is hit but a mode is not selected, stay on this screen
                        if (text == "Next"):
                            if (manual_selected or intervals_selected):
                                print("Next: Advancing to 'Set Values for Selected Mode' Screen")
                                screen_num = 2
                            if moisture_selected:
                                print("Next: Advancing to 'Select Plant' Screen")
                                screen_num = 3
                            # If intervals are selected, reset the tentative interval variables
                            # This is used in the case that the user selects intervals, changes the frequency,
                            # but cancels changes before saving. We want the initial numbers to match the current interval
                            if intervals_selected:
                                interval_b_time_selected_tent = interval_b_time_selected
                                interval_w_time_selected_tent = interval_w_time_selected
                        # If cancel is pressed, go back to the home screen
                        elif (text == "Cancel"):
                            print("Cancel: Going Back to 'Home' Screen")
                            screen_num = 0

                # Update the variables for which mode the user has tentatively selected. Set all
                # other modes to false
                for (text, rect) in sched_buttons_rect.items():
                    if (rect.collidepoint(pos)):
                        if (text == "Manual"):
                            manual_selected = True
                            moisture_selected = False
                            intervals_selected = False
                            print("Manual Mode Selected")
                        elif (text == "Moisture"):
                            manual_selected = False
                            moisture_selected = True
                            intervals_selected = False
                            print("Moisture Mode Selected")
                        elif ( text == "Intervals"):
                            manual_selected = False
                            moisture_selected = False
                            intervals_selected = True
                            print("Interval Mode Selected")

    ####################################################
    # GUI Set Values for Selected Mode Screen
    ####################################################

    elif ( screen_num == 2 ):
        display_set_schedule2()

        for event in pygame.event.get():
            if ( event.type is MOUSEBUTTONUP ):
                pos = pygame.mouse.get_pos()
                x,y = pos

                for (text, rect) in control_buttons2_rect.items():
                    if (rect.collidepoint(pos)):
                        if (text == "Set"):
                            if manual_selected:
                                screen_num = 0
                                schedule_selected = 0
                                print("Manual Mode Set, Returning to Homepage")
                            elif moisture_selected:
                                screen_num = 0
                                schedule_selected = 1
                                desired_moisture = 100*moisture_hund + 10*moisture_ten + moisture_one
                                print("Moisture Mode Selected, Returning to Homepage")
                            else:
                                if not (interval_w_time_selected_tent == interval_b_time_selected_tent and 10*interval_time_b_ten + interval_time_b_one <= 10*interval_time_w_ten + interval_time_w_one):
                                    screen_num = 0
                                    schedule_selected = 2
                                    interval_b_time = 10*interval_time_b_ten + interval_time_b_one
                                    interval_w_time = 10*interval_time_w_ten + interval_time_w_one
                                    interval_b_time_selected = interval_b_time_selected_tent
                                    interval_w_time_selected = interval_w_time_selected_tent
                                    print("Interval Mode Selected, Returning to Homepage")
                                    start_water()
                        elif (text == "Back"):
                            if moisture_selected:
                                moisture_thous = int(desired_moisture/1000)
                                moisture_hund  = int((desired_moisture - 1000*moisture_thous)/100)
                                moisture_ten   = int((desired_moisture - 1000*moisture_thous - 100*moisture_hund)/10)
                                moisture_one   = desired_moisture % 10
                            elif intervals_selected:
                                interval_time_w_ten = int(interval_w_time/10)
                                interval_time_w_one = interval_w_time % 10
                                interval_w_time_selected_tent = interval_w_time_selected
                                interval_time_b_ten = int(interval_b_time/10)
                                interval_time_b_one = interval_b_time % 10
                                interval_b_time_selected_tent = interval_b_time_selected
                            print("Going Back a Level")
                            screen_num = 1
                        elif (text == "Cancel"):
                            if moisture_selected:
                              moisture_thous = int(desired_moisture/1000)
                              moisture_hund  = int((desired_moisture - 1000*moisture_thous)/100)
                              moisture_ten   = int((desired_moisture - 1000*moisture_thous - 100*moisture_hund)/10)
                              moisture_one   = desired_moisture % 10
                            elif intervals_selected:
                                interval_time_w_ten = int(interval_w_time/10)
                                interval_time_w_one = interval_w_time % 10
                                interval_w_time_selected_tent = interval_w_time_selected
                                interval_time_b_ten = int(interval_b_time/10)
                                interval_time_b_one = interval_b_time % 10
                                interval_b_time_selected_tent = interval_b_time_selected
                            print("Canceling Edits, Returning to Homepage")
                            screen_num = 0
                
                # If we're editing the desired moisture level, have arrows increase or decrease the desired moisture level
                if moisture_selected:
                    for (text, rect) in moisture_buttons_rect.items():
                        if (rect.collidepoint(pos)):
                            if (text == "U_hund"):
                                if moisture_hund < 1:
                                    moisture_hund += 1
                                    moisture_ten = 0
                                    moisture_one = 0
                            elif (text == "U_ten"):
                                if moisture_ten < 9 and moisture_hund < 1:
                                    moisture_ten += 1
                            elif (text == "U_one"):
                                if moisture_one < 9 and moisture_hund < 1:
                                    moisture_one += 1
                            elif (text == "D_hund"):
                                if moisture_hund > 0:
                                    moisture_hund -= 1
                            elif (text == "D_ten"):
                                if moisture_ten > 0:
                                    moisture_ten -= 1
                            elif (text == "D_one"):
                                if moisture_one > 0:
                                    moisture_one -= 1

                if intervals_selected:
                    for (text, rect) in interval_arrows_rect.items():
                        if (rect.collidepoint(pos)):
                            if (text == "U_w_ten"):
                                if (interval_time_w_ten < 5):
                                    interval_time_w_ten += 1
                            elif (text == "U_w_one"):
                                if (interval_time_w_one < 9):
                                    interval_time_w_one += 1
                            elif (text == "U_w_unit"):
                                if (interval_w_time_selected_tent < 3 and ((interval_w_time_selected_tent + 1) <= interval_b_time_selected_tent)):
                                    interval_w_time_selected_tent += 1
                            elif (text == "U_b_ten"):
                                if (interval_time_b_ten < 5):
                                    interval_time_b_ten += 1
                            elif (text == "U_b_one"):
                                if (interval_time_b_one < 9):
                                    interval_time_b_one += 1
                            elif (text == "U_b_unit"):
                                if (interval_b_time_selected_tent < 3):
                                    interval_b_time_selected_tent += 1
                            elif (text == "D_w_ten"):
                                if (interval_time_w_ten > 0 and (10*interval_time_w_ten + interval_time_w_one) - 10 > 0):
                                    interval_time_w_ten -= 1
                            elif (text == "D_w_one"):
                                if (interval_time_w_one > 0 and (10*interval_time_w_ten + interval_time_w_one) - 1 > 0):
                                    interval_time_w_one -= 1
                            elif (text == "D_w_unit"):
                                if (interval_w_time_selected_tent > 0):
                                    interval_w_time_selected_tent -= 1
                            elif (text == "D_b_ten" and (10*interval_time_b_ten + interval_time_b_one) - 10 > 0):
                                if (interval_time_b_ten > 0):
                                    interval_time_b_ten -= 1
                            elif (text == "D_b_one"):
                                if (interval_time_b_one > 0 and (10*interval_time_b_ten + interval_time_b_one) - 1 > 0):
                                    interval_time_b_one -= 1
                            elif (text == "D_b_unit"):
                                if (interval_b_time_selected_tent > 0  and (interval_w_time_selected_tent <= (interval_b_time_selected_tent - 1))):
                                    interval_b_time_selected_tent -= 1
                    
                    # The time for each watering is just the watering time that the user specifies
                    water_time_sec = 10*interval_time_w_ten + interval_time_w_one
                    if interval_w_time_selected > 0:
                        water_time_sec *= 60
                    if interval_w_time_selected > 1:
                        water_time_sec *= 60
                    if interval_w_time_selected > 2:
                        water_time_sec *= 24

                    # The time between waterings is equal to the "every ___" time minus the time we want to water for
                    # For example, if we want to water the plant for 1 second every 5 seconds, we would
                    # water for 1 second, wait for 4 seconds, water for 1 second, wait for 4 seconds, etc.
                    between_time_sec = 10*interval_time_b_ten + interval_time_b_one
                    if interval_b_time_selected > 0:
                        between_time_sec *= 60
                    if interval_b_time_selected > 1:
                        between_time_sec *= 60
                    if interval_b_time_selected > 2:
                        between_time_sec *= 24
                    between_time_sec -= water_time_sec

    ####################################################
    # GUI Select Plant Type Screen
    ####################################################

    elif ( screen_num == 3 ):

        # Display the select plant type screen
        display_plant_sel()

        flower_sel = None
        fruit_sel = None
        tree_sel = None
        other_selected = False

        # Check for button press. If button is pressed, perform its action
        for event in pygame.event.get():
            if ( event.type is MOUSEBUTTONUP ):
                pos = pygame.mouse.get_pos()
                x,y = pos

                for (text, rect) in plant_type_buttons_rect.items():
                    if (rect.collidepoint(pos)):
                        if (text == "Flower"):
                            flower_selected = True
                            fruit_selected = False
                            tree_selected = False
                            own_selected = False
                        elif (text == "Fruit"):
                            flower_selected = False
                            fruit_selected = True
                            tree_selected = False
                            own_selected = False
                        elif (text == "Tree/Shrub"):
                            flower_selected = False
                            fruit_selected = False
                            tree_selected = True
                            own_selected = False
                        elif (text == "My Own Value"):
                            flower_selected = False
                            fruit_selected = False
                            tree_selected = False
                            own_selected = True

                for (text, rect) in control_buttons_m_rect.items():
                    if (rect.collidepoint(pos)):
                        if (text == "Next"):
                            # If the user has selected a mode, advance to the next screen
                            if flower_selected:
                                screen_num = 4
                            elif fruit_selected:
                                screen_num = 6
                            elif tree_selected:
                                screen_num = 7
                            elif own_selected:
                                screen_num = 2
                        elif (text == "Back"):
                            flower_selected = False
                            fruit_selected = False
                            tree_selected = False
                            own_selected = False
                            print("Going Back a Level")
                            screen_num = 1
                        elif (text == "Cancel"):
                            flower_selected = False
                            fruit_selected = False
                            tree_selected = False
                            own_selected = False
                            print("Canceling Edits, Returning to Homepage")
                            screen_num = 0

    ####################################################
    # GUI Select Flower Screen 1
    ####################################################

    elif ( screen_num == 4 ):

        # Display the select flower screen
        display_flowers1()

        # Check for button press. If button is pressed, perform its action
        for event in pygame.event.get():
            if ( event.type is MOUSEBUTTONUP ):
                pos = pygame.mouse.get_pos()
                x,y = pos

                for (text, rect) in flower1_rect.items():
                    if rect.collidepoint(pos):
                        flower_sel = text

                for (text,rect) in next_screen_rect.items():
                    if rect.collidepoint(pos):
                        if text == ">>>":
                            print("Going to next page of flowers")
                            screen_num = 5

                for (text,rect) in control_buttons_m_rect.items():
                    if rect.collidepoint(pos):
                        if text == "Next":
                            if flower_sel != None:
                                screen_num = 10
                        elif text == "Back":
                            flower_sel = None
                            screen_num = 3
                        elif text == "Cancel":
                            flower_sel = None
                            flower_selected = False
                            screen_num = 0

    ####################################################
    # GUI Select Flower Screen 2
    ####################################################

    elif ( screen_num == 5 ):

        # Display the select flower screen
        display_flowers2()

        # Check for button press. If button is pressed, perform its action
        for event in pygame.event.get():
            if ( event.type is MOUSEBUTTONUP ):
                pos = pygame.mouse.get_pos()
                x,y = pos

                for (text, rect) in flower2_rect.items():
                    if rect.collidepoint(pos):
                        flower_sel = text
                        other_selected = False

                for (text,rect) in no_ref_rect.items():
                    if rect.collidepoint(pos):
                        if text == "<<<":
                            print("Going to previous page of flowers")
                            screen_num = 4
                        elif text == "Other":
                            other_selected = True
                            flower_sel = None

                for (text,rect) in control_buttons_m_rect.items():
                    if rect.collidepoint(pos):
                        if text == "Next":
                            if flower_sel != None:
                                print("Next: Advancing to specific plant page")
                                screen_num = 10
                            elif other_selected:
                                print("Next: Advancing to general value page")
                                screen_num = 11
                        elif text == "Back":
                            flower_sel = None
                            other_selected = False
                            screen_num = 3
                        elif text == "Cancel":
                            flower_sel = None
                            flower_selected = False
                            other_selected = False
                            screen_num = 0

    ####################################################
    # GUI Select Fruit Screen
    ####################################################

    elif ( screen_num == 6 ):

        # Display the select fruit screen
        display_fruit()

        # Check for button press. If button is pressed, perform its action
        for event in pygame.event.get():
            if ( event.type is MOUSEBUTTONUP ):
                pos = pygame.mouse.get_pos()
                x,y = pos

                for (text, rect) in fruit_rect.items():
                    if rect.collidepoint(pos):
                        fruit_sel = text
                        other_selected = False

                for (text,rect) in fruit_buttons_rect.items():
                    if rect.collidepoint(pos):
                        if text == "Other":
                            other_selected = True
                            fruit_sel = None

                for (text,rect) in control_buttons_m_rect.items():
                    if rect.collidepoint(pos):
                        if text == "Next":
                            if fruit_sel != None:
                                print("Next: Advancing to specific plant page")
                                screen_num = 10
                            elif other_selected:
                                print("Next: Advancing to general value page")
                                screen_num = 11
                        elif text == "Back":
                            fruit_sel = None
                            other_selected = False
                            screen_num = 3
                        elif text == "Cancel":
                            flower_sel = None
                            flower_selected = False
                            other_selected = False
                            screen_num = 0

    ####################################################
    # GUI Select Tree/Shrub Screen 1
    ####################################################

    elif ( screen_num == 7 ):

        # Display the select fruit screen
        display_tree1()

        # Check for button press. If button is pressed, perform its action
        for event in pygame.event.get():
            if ( event.type is MOUSEBUTTONUP ):
                pos = pygame.mouse.get_pos()
                x,y = pos

                for (text, rect) in tree1_rect.items():
                    if rect.collidepoint(pos):
                        tree_sel = text
                        other_selected = False

                for (text,rect) in tree_buttons_rect.items():
                    if rect.collidepoint(pos):
                        if text == "Other":
                            other_selected = True
                            tree_sel = None
                        elif text == ">>>":
                            print("Going to next page of trees")
                            screen_num = 8

                for (text,rect) in control_buttons_m_rect.items():
                    if rect.collidepoint(pos):
                        if text == "Next":
                            if tree_sel != None:
                                print("Next: Advancing to specific plant page")
                                screen_num = 10
                            elif other_selected:
                                print("Next: Advancing to general value page")
                                screen_num = 11
                        elif text == "Back":
                            tree_sel = None
                            other_selected = False
                            screen_num = 3
                        elif text == "Cancel":
                            screen_num = 0

    ####################################################
    # GUI Select Tree/Shrub Screen 2
    ####################################################

    elif ( screen_num == 8 ):

        # Display the select fruit screen
        display_tree2()

        # Check for button press. If button is pressed, perform its action
        for event in pygame.event.get():
            if ( event.type is MOUSEBUTTONUP ):
                pos = pygame.mouse.get_pos()
                x,y = pos

                for (text, rect) in tree2_rect.items():
                    if rect.collidepoint(pos):
                        tree_sel = text
                        other_selected = False

                for (text,rect) in tree_buttons_rect.items():
                    if rect.collidepoint(pos):
                        if text == "Other":
                            other_selected = True
                            tree_sel = None
                        elif text == ">>>":
                            print("Going to next page of trees")
                            screen_num = 9
                        elif text == "<<<":
                            print("Going to previous page of trees")
                            screen_num = 7

                for (text,rect) in control_buttons_m_rect.items():
                    if rect.collidepoint(pos):
                        if text == "Next":
                            if tree_sel != None:
                                print("Next: Advancing to specific plant page")
                                screen_num = 10
                            elif other_selected:
                                print("Next: Advancing to general value page")
                                screen_num = 11
                        elif text == "Back":
                            tree_sel = None
                            other_selected = False
                            screen_num = 3
                        elif text == "Cancel":
                            screen_num = 0

    ####################################################
    # GUI Select Tree/Shrub Screen 3
    ####################################################

    elif ( screen_num == 9 ):

        # Display the select fruit screen
        display_tree3()

        # Check for button press. If button is pressed, perform its action
        for event in pygame.event.get():
            if ( event.type is MOUSEBUTTONUP ):
                pos = pygame.mouse.get_pos()
                x,y = pos

                for (text, rect) in tree3_rect.items():
                    if rect.collidepoint(pos):
                        tree_sel = text
                        other_selected = False

                for (text,rect) in tree_buttons_rect.items():
                    if rect.collidepoint(pos):
                        if text == "Other":
                            other_selected = True
                            tree_sel = None
                        elif text == "<<<":
                            print("Going to previous page of trees")
                            screen_num = 8

                for (text,rect) in control_buttons_m_rect.items():
                    if rect.collidepoint(pos):
                        if text == "Next":
                            if tree_sel != None:
                                print("Next: Advancing to specific plant page")
                                screen_num = 10
                            elif other_selected:
                                print("Next: Advancing to general value page")
                                screen_num = 11
                        elif text == "Back":
                            tree_sel = None
                            other_selected = False
                            screen_num = 3
                        elif text == "Cancel":
                            screen_num = 0

    ####################################################
    # GUI Confirm Plant Moisture Value Screen
    ####################################################

    elif ( screen_num == 10 ):

        # Display the general moisture value screen
        display_specific()

        # Check for button press. If button is pressed, perform its action
        for event in pygame.event.get():
            if ( event.type is MOUSEBUTTONUP ):
                pos = pygame.mouse.get_pos()
                x,y = pos

                for (text, rect) in specific_buttons_rect.items():
                    if rect.collidepoint(pos):
                        if text == "Set":
                            desired_moisture = temp_desired_val
                            schedule_selected = 1
                            screen_num = 0
                        elif text == "Edit":
                            moisture_hund = int((temp_desired_val / 100))
                            moisture_ten = int((temp_desired_val / 10))
                            moisture_one  = (temp_desired_val % 10)
                            screen_num = 2
                        elif text == "Back":
                            if flower_selected:
                                screen_num = 4
                            elif fruit_selected:
                                screen_num = 6
                            elif tree_selected:
                                screen_num = 7
                        elif text == "Cancel":
                            flower_selected = False
                            fruit_selected = False
                            tree_selected = False
                            flower_sel = None
                            fruit_sel = None
                            tree_sel = None
                            moisture_selected = False
                            screen_num = 0

    ####################################################
    # GUI Confirm General Plant Moisture Value Screen
    ####################################################
   
    elif ( screen_num == 11 ):

        # Display the specific moisture value screen
        display_general()

        # Check for button press. If button is pressed, perform its action
        for event in pygame.event.get():
            if ( event.type is MOUSEBUTTONUP ):
                pos = pygame.mouse.get_pos()
                x,y = pos

                for (text, rect) in specific_buttons_rect.items():
                    if rect.collidepoint(pos):
                        if text == "Set":
                            working = ((generalTreeShrub, generalFlower)[flower_selected], generalFruit)[fruit_selected]
                            desired_moisture = working
                            schedule_selected = 1
                            screen_num = 0
                        elif text == "Edit":
                            working = ((generalTreeShrub, generalFlower)[flower_selected], generalFruit)[fruit_selected]
                            moisture_hund = int(working / 100)
                            moisture_ten = int(working / 10)
                            moisture_one  = (working % 10)
                            screen_num = 2
                        elif text == "Back":
                            if flower_selected:
                                screen_num = 4
                            elif fruit_selected:
                                screen_num = 6
                            elif tree_selected:
                                screen_num = 7
                        elif text == "Cancel":
                            flower_selected = False
                            fruit_selected = False
                            tree_selected = False
                            flower_sel = None
                            fruit_sel = None
                            tree_sel = None
                            moisture_selected = False
                            screen_num = 0

# Stop the water
if currently_watering:
    stop_water()

# Nicely end the GPIO stuff
GPIO.cleanup()
