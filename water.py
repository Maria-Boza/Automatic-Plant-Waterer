# Ashley Heckman (agh93) & Maria Boza (mib57)
# Wednesday Lab, Team 6
# ECE 5725 Final Project
# water.py

import time
import pygame
import os
from pygame.locals import*
import RPi.GPIO as GPIO

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

    # Print
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

    # Print
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
    stop_water()

GPIO.add_event_detect(27, GPIO.FALLING, callback = GPIO27_callback, bouncetime = 300)

#########################################################################################################
# Watering Modes
#########################################################################################################

schedule_type = ["Manual", "Moisture Sensor", "Intervals"]
schedule_selected = 0
desired_moisture = 0

# Setup the soil moisture sensor
moisture = 0

# Setup the temperature sensor
temp = 0

# Setup the humidity sensor
humidity = 0

# Setup the sunlight sensor
sunlight = 0

# Setup the camera

# Get the sensor readings
def get_sensor_values():
    return

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

    # Display sunlight
    sunlight_text = "Sunlight Today: " + str(sunlight) + " hours"
    sunlight_text_surface = body.render(sunlight_text, True, white)
    sunlight_rect = sunlight_text_surface.get_rect(center = (int(width/2), 90))
    screen.blit(sunlight_text_surface, sunlight_rect)

    # Display time the plant was last watered header
    water_header_text = "Last Watered"
    water_header_text_surface = header.render(water_header_text, True, white)
    water_header_rect = water_header_text_surface.get_rect(center = (int(width/2), 120))
    screen.blit(water_header_text_surface, water_header_rect)

    # Display time the plant was last watered
    if not currently_watering:
        last_water_start_text = str(time.localtime(last_water_start)[1]) + "/" + str(time.localtime(last_water_start)[2]) + " " + str((time.localtime(last_water_start)[3], time.localtime(last_water_start)[3] - 12)[time.localtime(last_water_start)[3] > 12]) + (":", ":0")[time.localtime(last_water_start)[4] < 10] + str(time.localtime(last_water_start)[4]) + (" am", " pm")[time.localtime(last_water_start)[3] > 12]
        last_water_end_text = str(time.localtime(last_water_end)[1]) + "/" + str(time.localtime(last_water_end)[2]) + " " + str((time.localtime(last_water_end)[3], time.localtime(last_water_end)[3] - 12)[time.localtime(last_water_end)[3] > 12]) + (":", ":0")[time.localtime(last_water_end)[4] < 10] + str(time.localtime(last_water_end)[4]) + (" am", " pm")[time.localtime(last_water_end)[3] > 12]
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

#########################################################################################################
# GUI Control
#########################################################################################################

code_run = True
while code_run:
    
    ################################################
    # GUI Homescreen Functionalilty
    ################################################

    if ( screen_num == 0):

        # Display the homescreen
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
                            if (manual_selected or moisture_selected or intervals_selected):
                                print("Next: Advancing to 'Set Values for Selected Mode' Screen")
                                screen_num = 2
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

# Nicely end the GPIO stuff
GPIO.cleanup()
