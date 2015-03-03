from __future__ import division
__author__ = 'faiz'

import sys
import pygame
import random
import time
import struct
import os
import numpy as np

# TCP/IP library
import xmlrpclib

# threading
import threading

from pygame.locals import *
import moosegesture

# for swipe lock
import Xlib
import Xlib.display


class Cognitives:
    X = 854
    Y = 480
    SCREEN_SIZE = (X, Y)
    BG_COL = (255, 255, 255)
    TEXT_COL = (0, 0, 0)
    TEXT_SIZE = 18

    # swipe related variables
    FPS = 60

    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    ORANGE = (255, 165, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    PURPLE = (153, 0, 153)

    # sensor files
    ACCEL_FILE = "/sys/devices/platform/lis3lv02d/position"
    EXTCAP_FILE = "/dev/extcap"
    SAMPLE_RATE = 0.02

    # TCP/IP variables
    HOST = "192.168.2.14"
    ACC_PORT = 65000    # accelerometer data
    BOD_PORT = 65001    # bod data

    # test variables
    TOTAL_TRIAL = 50
    COUNTDOWN = 2      # secs
    MAX_DISPLAY_TIME = 1   # secs
    TIME_REDUCTION_FACTOR = 0.5 * MAX_DISPLAY_TIME

    DATA_DIR = 'logfiles'

    def __init__(self, test_type):
        pygame.init()
        pygame.display.set_caption('N9 Cognitive Test')
        self.screen = pygame.display.set_mode(Cognitives.SCREEN_SIZE)
        self.screen.fill(Cognitives.BG_COL)
        pygame.display.flip()

        self.test_type = test_type

        # extcap file
        self.ef = open(Cognitives.EXTCAP_FILE, "r")

         # create tcp server
        svr_string = "http://%s:%s/RPC2" % (Cognitives.HOST, Cognitives.ACC_PORT)
        self.svr = xmlrpclib.ServerProxy(svr_string)

        # 1 = start screen 2 = countdown
        self.event_type = 0

        # trial result
        self.result = -1

        # trial counter
        self.counter = 0

        # stimulus type
        self.stimulus_type = 0

        # trial errors
        self.correct = 0
        self.incorrect = 0

        # SART flag
        self.sart_start = False

        # display time
        self.display_time = 0.0

        # error rate
        self.error_rate = 0.0

        # create folder
        if not os.path.exists(Cognitives.DATA_DIR):
            print 'Creating folder'
            os.mkdir(Cognitives.DATA_DIR)

        # create and open log file
        self.log_file = '%s/faiz_testdata1_%s.csv' % (Cognitives.DATA_DIR, self.test_type)
        self.f = open(self.log_file, 'w')

        # get display and window properties for swipe locking
        self.display = Xlib.display.Display()
        self.window = self.display.create_resource_object('window', pygame.display.get_wm_info()['window'])
        self.fswindow = self.display.create_resource_object('window', pygame.display.get_wm_info()['fswindow'])
        self.wmwindow = self.display.create_resource_object('window', pygame.display.get_wm_info()['wmwindow'])

        # as per Harmattan documentation (create custom region locking)
        self.customRegionAtom = self.display.intern_atom("_MEEGOTOUCH_CUSTOM_REGION")

    def swipelock(self, locked):

        if locked:
            width = Cognitives.X
            height = Cognitives.Y
        else:
            width = 0
            height = 0

        # region rectangle
        customRegion = [0, 0, width, height]

        #python-xlib Window change_property ( property, type, format, data, mode = X.PropModeReplace, onerror = None )
        self.window.change_property(self.customRegionAtom, 6, 32, customRegion)
        self.fswindow.change_property(self.customRegionAtom, 6, 32, customRegion)
        self.wmwindow.change_property(self.customRegionAtom, 6, 32, customRegion)

        # update X server
        self.display.sync()

    def init_flanker(self):
        pos = (400, 20)

        arrow_img = self.load_img('images/flanker_arrow.png')
        box_img = self.load_img('images/flanker_box.png')
        cross_img = self.load_img('images/flanker_cross.png')

        arrow_img = self.aspect_scale(arrow_img, (75, 75))
        arrow_img = pygame.transform.rotate(arrow_img, 90)

        box_img = self.aspect_scale(box_img, (75, 75))
        box_img = pygame.transform.rotate(box_img, 90)

        cross_img = self.aspect_scale(cross_img, (75, 75))
        cross_img = pygame.transform.rotate(cross_img, 90)

        pygame.display.flip()

        return arrow_img, box_img, cross_img, pos

    def change_sart_stimulus(self):
        direction = 1
        self.sart_start = False

        # 1 = non-zero; 2 = specific;
        stimulus_type = random.randint(1, 2)

        # digit sample
        dsample = []
        for x in range(1, 10):
            dsample.append(x)

        # random integer to use
        number = random.sample(dsample, 1)
        number = number[0]

        # position in the series
        pos = random.randint(1, 6)

        if stimulus_type == 1:
            self.draw_notification('Find non-zero number', Cognitives.BLACK, 45)
            time.sleep(1)

            # clear display
            self.screen.fill(Cognitives.BG_COL)

            nonzero = random.choice([True, False])

            if nonzero:
                direction = 1
                if pos == 1:
                    self.draw_text('%s00000' % number, Cognitives.BLACK, 80)
                elif pos == 2:
                    self.draw_text('0%s0000' % number, Cognitives.BLACK, 80)
                elif pos == 3:
                    self.draw_text('00%s000' % number, Cognitives.BLACK, 80)
                elif pos == 4:
                    self.draw_text('000%s00' % number, Cognitives.BLACK, 80)
                elif pos == 5:
                    self.draw_text('0000%s0' % number, Cognitives.BLACK, 80)
                elif pos == 6:
                    self.draw_text('00000%s' % number, Cognitives.BLACK, 80)
            else:
                direction = 2
                self.draw_text('000000', Cognitives.BLACK, 80)

        elif stimulus_type == 2:
            self.draw_notification('Find number %d' % number, Cognitives.BLACK, 50)
            time.sleep(1)

            # clear display
            self.screen.fill(Cognitives.BG_COL)

            # remove number to use from the sample
            for x in range(0, 8):
                if dsample[x] == number:
                    dsample.pop(x)

            # use random number from the sample
            series = []
            for y in range(0, 6):
                series.append(random.sample(dsample, 1))

            series = np.array(series)

            specific = random.choice([True, False])

            if specific:
                direction = 1
                #print 'Specific'
                if pos == 1:
                    self.draw_text('%d%d%d%d%d%d' % (number, series[0], series[1], series[2], series[3], series[4]), Cognitives.BLACK, 80)
                elif pos == 2:
                    self.draw_text('%d%d%d%d%d%d' % (series[0], number, series[1], series[2], series[3], series[4]), Cognitives.BLACK, 80)
                elif pos == 3:
                    self.draw_text('%d%d%d%d%d%d' % (series[0], series[1], number, series[2], series[3], series[4]), Cognitives.BLACK, 80)
                elif pos == 4:
                    self.draw_text('%d%d%d%d%d%d' % (series[0], series[1], series[2], number, series[3], series[4]), Cognitives.BLACK, 80)
                elif pos == 5:
                    self.draw_text('%d%d%d%d%d%d' % (series[0], series[1], series[2], series[3], number, series[4]), Cognitives.BLACK, 80)
                elif pos == 6:
                    self.draw_text('%d%d%d%d%d%d' % (series[0], series[1], series[2], series[3], series[4], number), Cognitives.BLACK, 80)
            else:
                direction = 2
                #print 'Non-specific'
                self.draw_text('%d%d%d%d%d%d' % (series[0], series[1], series[2], series[3], series[4], series[5]), Cognitives.BLACK, 80)

        self.sart_start = True
        pygame.display.flip()

        return stimulus_type, direction #nonzero, specific

    def change_stroop_stimulus(self):
        colour_strings = {1: 'Blue', 2: 'Red', 3: 'Green', 4: 'Yellow', 5: 'Black', 6: 'Purple', 7: 'Orange'}
        words = {1: 'Book', 2: 'Raid', 3: 'Grin', 4: 'Fellow', 5: 'Back', 6: 'People', 7: 'Change'}

        # default correct swipe direction
        direction = 1

        # pick random colour
        colour = random.randint(1, len(colour_strings))

        # 1 = congruent; 2 = incongruent; 3 = no-go
        stimulus_type = random.randint(1, 3)

        # clear display
        self.screen.fill(Cognitives.BG_COL)

        if stimulus_type == 1:
            direction = 1
            if colour == 1:
                self.draw_text(colour_strings[colour], Cognitives.BLUE, 80)
            elif colour == 2:
                self.draw_text(colour_strings[colour], Cognitives.RED, 80)
            elif colour == 3:
                self.draw_text(colour_strings[colour], Cognitives.GREEN, 80)
            elif colour == 4:
                self.draw_text(colour_strings[colour], Cognitives.YELLOW, 80)
            elif colour == 5:
                self.draw_text(colour_strings[colour], Cognitives.BLACK, 80)
            elif colour == 6:
                self.draw_text(colour_strings[colour], Cognitives.PURPLE, 80)
            elif colour == 7:
                self.draw_text(colour_strings[colour], Cognitives.ORANGE, 80)

        elif stimulus_type == 2:
            direction = 2
            colour_strings.pop(colour)
            word_index = random.sample(colour_strings, 1)
            word_index = word_index[0]
            incongruent_word = colour_strings[word_index]

            if colour == 1:
                self.draw_text(incongruent_word, Cognitives.BLUE, 80)
            elif colour == 2:
                self.draw_text(incongruent_word, Cognitives.RED, 80)
            elif colour == 3:
                self.draw_text(incongruent_word, Cognitives.GREEN, 80)
            elif colour == 4:
                self.draw_text(incongruent_word, Cognitives.YELLOW, 80)
            elif colour == 5:
                self.draw_text(incongruent_word, Cognitives.BLACK, 80)
            elif colour == 6:
                self.draw_text(incongruent_word, Cognitives.PURPLE, 80)
            elif colour == 7:
                self.draw_text(incongruent_word, Cognitives.ORANGE, 80)

        elif stimulus_type == 3:
            word_index = random.sample(words, 1)
            word_index = word_index[0]
            no_go_word = words[word_index]

            if colour == 1:
                self.draw_text(no_go_word, Cognitives.BLUE, 80)
            elif colour == 2:
                self.draw_text(no_go_word, Cognitives.RED, 80)
            elif colour == 3:
                self.draw_text(no_go_word, Cognitives.GREEN, 80)
            elif colour == 4:
                self.draw_text(no_go_word, Cognitives.YELLOW, 80)
            elif colour == 5:
                self.draw_text(no_go_word, Cognitives.BLACK, 80)
            elif colour == 6:
                self.draw_text(no_go_word, Cognitives.PURPLE, 80)
            elif colour == 7:
                self.draw_text(no_go_word, Cognitives.ORANGE, 80)

        pygame.display.flip()

        return stimulus_type, direction

    def draw_text(self, text, colour, size):
        labelfont = pygame.font.SysFont("Arial", size)
        label = labelfont.render(text, True, colour)
        rotatedlabel = pygame.transform.rotate(label, 90)

        textrect = rotatedlabel.get_rect()
        textrect.center = (Cognitives.X/2, Cognitives.Y/2)

        self.screen.blit(rotatedlabel, textrect)

    def change_flanker_stimulus(self, arrow_img, box_img, cross_img, pos):
        # 1 = congruent; 2 = incongruent; 3 = no-go
        stimulus_type = random.randint(1, 3)

        # direction of the arrow
        direction = random.randint(1, 2)

        # use additional flanks
        additional_flanks = random.choice([True, False])

        # change flanking arrows direction to left
        # for incongruent stimulus, the middle arrow is always in the opposite of this direction
        if direction == 2:
            arrow_img = pygame.transform.rotate(arrow_img, 180)

        # clear display
        self.screen.fill(Cognitives.BG_COL)
        pygame.display.flip()

        if stimulus_type == 1:
            self.draw_flanker_arrow(self.screen, arrow_img, pos)
            self.draw_flanker_arrow(self.screen, arrow_img, (pos[0], pos[1] + 90))
            self.draw_flanker_arrow(self.screen, arrow_img, (pos[0], pos[1] + 180))
            self.draw_flanker_arrow(self.screen, arrow_img, (pos[0], pos[1] + 270))
            self.draw_flanker_arrow(self.screen, arrow_img, (pos[0], pos[1] + 360))

            if additional_flanks:
                # top
                self.draw_flanker_arrow(self.screen, arrow_img, (pos[0] - 100, pos[1]))
                self.draw_flanker_arrow(self.screen, arrow_img, (pos[0] - 100, pos[1] + 90))
                self.draw_flanker_arrow(self.screen, arrow_img, (pos[0] - 100, pos[1] + 180))
                self.draw_flanker_arrow(self.screen, arrow_img, (pos[0] - 100, pos[1] + 270))
                self.draw_flanker_arrow(self.screen, arrow_img, (pos[0] - 100, pos[1] + 360))
                # bottom
                self.draw_flanker_arrow(self.screen, arrow_img, (pos[0] + 100, pos[1]))
                self.draw_flanker_arrow(self.screen, arrow_img, (pos[0] + 100, pos[1] + 90))
                self.draw_flanker_arrow(self.screen, arrow_img, (pos[0] + 100, pos[1] + 180))
                self.draw_flanker_arrow(self.screen, arrow_img, (pos[0] + 100, pos[1] + 270))
                self.draw_flanker_arrow(self.screen, arrow_img, (pos[0] + 100, pos[1] + 360))

        elif stimulus_type == 2:
            self.draw_flanker_arrow(self.screen, arrow_img, pos)
            self.draw_flanker_arrow(self.screen, arrow_img, (pos[0], pos[1] + 90))
            arrow_img = pygame.transform.rotate(arrow_img, 180)
            self.draw_flanker_arrow(self.screen, arrow_img, (pos[0], pos[1] + 180))
            arrow_img = pygame.transform.rotate(arrow_img, 180)
            self.draw_flanker_arrow(self.screen, arrow_img, (pos[0], pos[1] + 270))
            self.draw_flanker_arrow(self.screen, arrow_img, (pos[0], pos[1] + 360))

            if additional_flanks:
                # top
                self.draw_flanker_arrow(self.screen, arrow_img, (pos[0] - 100, pos[1]))
                self.draw_flanker_arrow(self.screen, arrow_img, (pos[0] - 100, pos[1] + 90))
                self.draw_flanker_arrow(self.screen, arrow_img, (pos[0] - 100, pos[1] + 180))
                self.draw_flanker_arrow(self.screen, arrow_img, (pos[0] - 100, pos[1] + 270))
                self.draw_flanker_arrow(self.screen, arrow_img, (pos[0] - 100, pos[1] + 360))
                # bottom
                self.draw_flanker_arrow(self.screen, arrow_img, (pos[0] + 100, pos[1]))
                self.draw_flanker_arrow(self.screen, arrow_img, (pos[0] + 100, pos[1] + 90))
                self.draw_flanker_arrow(self.screen, arrow_img, (pos[0] + 100, pos[1] + 180))
                self.draw_flanker_arrow(self.screen, arrow_img, (pos[0] + 100, pos[1] + 270))
                self.draw_flanker_arrow(self.screen, arrow_img, (pos[0] + 100, pos[1] + 360))

            # reverse the direction flag
            if direction == 1:
                direction = 2
            elif direction == 2:
                direction = 1

        elif stimulus_type == 3:
            self.draw_flanker_arrow(self.screen, box_img, pos)
            self.draw_flanker_arrow(self.screen, box_img, (pos[0], pos[1] + 90))
            self.draw_flanker_arrow(self.screen, arrow_img, (pos[0], pos[1] + 180))
            self.draw_flanker_arrow(self.screen, box_img, (pos[0], pos[1] + 270))
            self.draw_flanker_arrow(self.screen, box_img, (pos[0], pos[1] + 360))

            pygame.display.flip()

        # elif stimulus_type == 4:
        #     self.draw_flanker_arrow(self.screen, cross_img, pos)
        #     self.draw_flanker_arrow(self.screen, cross_img, (pos[0], pos[1] + 90))
        #     self.draw_flanker_arrow(self.screen, arrow_img, (pos[0], pos[1] + 180))
        #     self.draw_flanker_arrow(self.screen, cross_img, (pos[0], pos[1] + 270))
        #     self.draw_flanker_arrow(self.screen, cross_img, (pos[0], pos[1] + 360))

        pygame.display.flip()

        return stimulus_type, direction

    @staticmethod
    def load_img(file_name):
        img = pygame.image.load(file_name)
        return img

    @staticmethod
    def draw_flanker_arrow(surf, image, pos):
        surf.blit(image, pos)

    def draw_start_screen(self):
        # fill screen
        self.screen.fill(Cognitives.BG_COL)

        # text and label stuff
        label_font = pygame.font.SysFont("Arial", 40)
        button_label = label_font.render('START', True, Cognitives.BG_COL)
        instruction_text1 = label_font.render('Press the button', True, Cognitives.TEXT_COL)
        instruction_text2 = label_font.render('to start', True, Cognitives.TEXT_COL)
        button_label = pygame.transform.rotate(button_label, 90)
        instruction_text1 = pygame.transform.rotate(instruction_text1, 90)
        instruction_text2 = pygame.transform.rotate(instruction_text2, 90)

        xypos = [0, 0]
        rectoffset = [20, 20, 40, 60]
        centerxyoffset = [20, 60]

        # get rectangle from text
        text_rect = button_label.get_rect()
        text_rect.centerx = self.screen.get_rect().centerx + xypos[0]
        text_rect.centery = self.screen.get_rect().centery + xypos[1]

        # create button rectangle
        button_rect = pygame.Rect(text_rect.left - rectoffset[0], text_rect.top - rectoffset[1], text_rect.width + rectoffset[2], text_rect.height + rectoffset[3])

        # draw rectangle to screen
        pygame.draw.rect(self.screen, Cognitives.TEXT_COL, button_rect, 0)

        # blit button label to screen
        self.screen.blit(button_label, (button_rect.centerx - centerxyoffset[0], button_rect.centery - centerxyoffset[1]))

        # blit text to screen
        instruction_textrect1 = instruction_text1.get_rect()
        instruction_textrect1.topleft = (240, Cognitives.Y - 380)
        instruction_textrect2 = instruction_text2.get_rect()
        instruction_textrect2.topleft = (280, Cognitives.Y - 290)
        self.screen.blit(instruction_text1, instruction_textrect1)
        self.screen.blit(instruction_text2, instruction_textrect2)

        pygame.display.flip()

        return button_rect

    def draw_exit_screen(self):
        # fill screen
        self.screen.fill(Cognitives.BG_COL)

        label_font = pygame.font.SysFont("Arial", 60)
        theend_text = label_font.render('The End', True, Cognitives.TEXT_COL)
        theend_text = pygame.transform.rotate(theend_text, 90)

        text_rect = theend_text.get_rect()
        text_rect.centerx = self.screen.get_rect().centerx
        text_rect.centery = self.screen.get_rect().centery

        self.screen.blit(theend_text, text_rect)

        pygame.display.flip()

        time.sleep(2)

        # re-enable N9 screen swipe
        self.swipelock(False)

        pygame.quit()
        sys.exit()

    def draw_test_countdown(self, elapsed):
        # fill screen
        self.screen.fill(Cognitives.BG_COL)

        radius = elapsed * 50
        width = elapsed * 10

        pygame.draw.circle(self.screen, Cognitives.RED, (Cognitives.X/2, Cognitives.Y/2), radius, width)

        pygame.display.flip()

    def draw_notification(self, not_string, colour, size):
        # fill screen
        self.screen.fill(Cognitives.BG_COL)

        text_font = pygame.font.SysFont("Arial", size)
        not_text = text_font.render(not_string, True, colour)
        not_text = pygame.transform.rotate(not_text, 90)

        # blit text to screen
        not_textrect = not_text.get_rect()
        not_textrect.center = (Cognitives.X/2, Cognitives.Y/2)
        self.screen.blit(not_text, not_textrect)

        pygame.display.flip()
        time.sleep(1)

        # if self.counter == Cognitives.TOTAL_TRIAL and self.stimulus_type != 3:
        #     self.theend = True
        # else:
        #     self.theend = False


    @staticmethod
    def aspect_scale(img, (bx, by)):
        """ Scales 'img' to fit into box bx/by.
         This method will retain the original image's aspect ratio """
        ix, iy = img.get_size()

        if ix > iy:
            # fit to width
            scale_factor = bx / float(ix)
            sy = scale_factor * iy

            if sy > by:
                scale_factor = by / float(iy)
                sx = scale_factor * ix
                sy = by
            else:
                sx = bx
        else:
            # fit to height
            scale_factor = by / float(iy)
            sx = scale_factor * ix

            if sx > bx:
                scale_factor = bx / float(ix)
                sx = bx
                sy = scale_factor * iy
            else:
                sy = by

        return pygame.transform.scale(img, (int(sx), int(sy)))

    def read_sensor(self):
        while True:
            # bod cap
            cap_data = [0] * 24
            cap_struct = struct.Struct("<" + "H" * 24)
            data = self.ef.read(cap_struct.size)
            if data and len(data) == cap_struct.size:
                cap_data = cap_struct.unpack(data)

            # accelerometer
            with open(Cognitives.ACCEL_FILE, 'r') as af:
                rawxyz = af.read().replace('(', '').replace(')', '').replace('\n', '')
                xyz_data = map(int, rawxyz.split(","))

            # send to server for plotting/arduino sync
            # self.svr.send_data(xyz_data, cap_data, [self.stimulus_type, self.result, self.event_type, self.counter])

            event_data = [self.counter, self.test_type, self.event_type, self.stimulus_type, time.time(), self.result]

            perf_data = [self.display_time, self.error_rate]

            # just to make sure not to write after the test ends
            if self.counter <= Cognitives.TOTAL_TRIAL:
                self.writer(event_data, perf_data, xyz_data, cap_data)

            # sample rate
            time.sleep(Cognitives.SAMPLE_RATE)

    def writer(self, event_data, perf_data, accel_data, cap_data):
        towrite = []
        towrite.extend(event_data)
        towrite.extend(perf_data)
        towrite.extend(accel_data)
        towrite.extend(cap_data)

        try:
            self.f.write(','.join(map(str, towrite)) + '\n')
            self.f.flush()
        except TypeError:
            pass

    def run_read_sensor(self):
        try:
            # accelerometer thread
            sensor_thread = threading.Thread(target=self.read_sensor)
            sensor_thread.daemon = True
            sensor_thread.start()
        except:
            print 'Unable to start thread'
            pass

    @staticmethod
    def compute_time(error_rate):
        # minimum reduction
        if error_rate == 0:
            return Cognitives.TIME_REDUCTION_FACTOR
        else:
            return error_rate * Cognitives.TIME_REDUCTION_FACTOR + Cognitives.TIME_REDUCTION_FACTOR

    def run(self):
        # init flanker test
        arrow_img, box_img, cross_img, pos = self.init_flanker()

        points = []
        strokes = []
        new_trial = True
        mouse_down = False
        next_stimulus = False
        show_stimulus = False
        show_start_screen = True
        show_countdown = False
        main_clock = pygame.time.Clock()
        touchpos = (0, 0)
        start_time = 0
        self.display_time = Cognitives.MAX_DISPLAY_TIME

        # sensor thread
        self.run_read_sensor()

        # disable N9 screen swipe
        self.swipelock(True)

        while True:
            # check for events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # on mouse down, erase the previous line and start drawing a new one
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.event_type = 4
                    mouse_down = True
                    if len(points) > 2:
                        startx, starty = points[0][0], points[0][1]
                        for i in range(len(points)):
                            points[i] = (points[i][0] - startx, points[i][1] - starty)
                    points = []

                # Mouse released
                if event.type == pygame.MOUSEBUTTONUP:
                    # try to identify the gesture when the mouse dragging stops
                    mouse_down = False
                    strokes = moosegesture.getGesture(points)
                    touchpos = event.pos

                    # only detect swipe when stimulus is shown
                    if strokes and show_stimulus:
                        # congruent
                        if self.stimulus_type == 1:
                            # left/right
                            if (direction == 1 and strokes[0] == 8 or strokes[0] == 7 or strokes[0] == 9) or (direction == 2 and strokes[0] == 2 or strokes[0] == 1 or strokes[0] == 3):
                                self.result = 1
                                self.correct += 1
                            else:
                                self.incorrect += 1
                                self.result = -1

                        # incongruent
                        elif self.stimulus_type == 2:
                            # left/right
                            if (direction == 1 and strokes[0] == 8 or strokes[0] == 7 or strokes[0] == 9) or (direction == 2 and strokes[0] == 2 or strokes[0] == 1 or strokes[0] == 3):
                                self.result = 1
                                self.correct += 1
                            else:
                                self.result = -1
                                self.correct += 1

                if event.type == MOUSEMOTION and mouse_down:
                    # draw the line if the mouse is dragging
                    points.append((event.pos[0], event.pos[1]))

            if show_start_screen:
                self.event_type = 1

                if new_trial:
                    self.counter += 1

                    if self.counter >= 10:
                        self.display_time = self.compute_time(self.error_rate)

                    # compute error rate
                    self.error_rate = self.incorrect/self.counter

                    if self.counter <= Cognitives.TOTAL_TRIAL:
                        print 'trial #%d #correct = %d #incorrect = %d error rate = %.4f display time = %.4f' % (self.counter, self.correct, self.incorrect, self.error_rate, self.display_time)

                    new_trial = False

                start_button = self.draw_start_screen()

                if start_button.collidepoint(touchpos):
                    show_start_screen = False
                    show_countdown = True
                    touchpos = (0, 0)

                    # start countdown timer
                    start_time = time.time()

            if show_countdown:
                self.event_type = 2
                elapsed = time.time() - start_time

                if elapsed > Cognitives.COUNTDOWN:
                    show_countdown = False
                    next_stimulus = True
                else:
                    self.draw_test_countdown(elapsed)

            if next_stimulus:
                # test type
                if self.test_type == 1:
                    self.stimulus_type, direction = self.change_flanker_stimulus(arrow_img, box_img, cross_img, pos)

                    self.event_type = 3

                    # start timer
                    start_time = time.time()

                    next_stimulus = False
                    show_stimulus = True

                elif self.test_type == 2:
                    self.stimulus_type, direction = self.change_stroop_stimulus()

                    self.event_type = 3

                    # start timer
                    start_time = time.time()

                    next_stimulus = False
                    show_stimulus = True

                elif self.test_type == 3:
                    self.stimulus_type, direction = self.change_sart_stimulus()

                    if self.sart_start:
                        self.event_type = 3

                        # start timer
                        start_time = time.time()

                        next_stimulus = False
                        show_stimulus = True

            if show_stimulus:
                elapsed = time.time() - start_time

                # no-go
                if mouse_down and self.stimulus_type == 3:
                    self.event_type = 5
                    self.draw_notification('Incorrect', (0, 0, 0), 60)
                    self.result = -1
                    self.incorrect += 1

                    show_stimulus = False
                    show_start_screen = True
                    new_trial = True

                # no-go (response held)
                if elapsed > self.display_time and self.stimulus_type == 3:
                    self.event_type = 5
                    self.draw_notification('Correct', (0, 0, 0), 60)
                    self.result = 1
                    self.correct += 1

                    show_stimulus = False
                    show_start_screen = True
                    new_trial = True

                # incongrent/congruent
                if elapsed > self.display_time and self.stimulus_type != 3:
                    self.event_type = 5
                    self.draw_notification('Too slow. Try faster.', (0, 0, 0), 50)
                    self.result = -1
                    self.incorrect += 1

                    show_stimulus = False
                    show_start_screen = True
                    new_trial = True

                elif elapsed <= self.display_time and strokes:
                    self.event_type = 5
                    if self.result == 1:
                        self.draw_notification('Correct', (0, 0, 0), 60)
                    else:
                        self.draw_notification('Incorrect', (0, 0, 0), 60)

                    show_stimulus = False
                    show_start_screen = True
                    new_trial = True

            if self.counter > Cognitives.TOTAL_TRIAL:
                self.draw_exit_screen()

            main_clock.tick(Cognitives.FPS)