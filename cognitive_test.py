__author__ = 'faiz'

import sys
import pygame
import random
import time

from pygame.locals import *
import moosegesture

class Cogtest:
    X = 854
    Y = 480
    SCREEN_SIZE = (X, Y)
    BG_COL = (255, 255, 255)
    TEXT_COL = (0, 0, 0)
    TEXT_SIZE = 18

    # swipe related variables
    FPS = 60

    TEXTCOLOR = (255, 255, 255) # white
    BACKGROUNDCOLOR = (0, 0, 0)# black
    POINTSCOLOR = (255, 0, 0) # red
    LINECOLOR = (255, 165, 0) # orange
    CARDINALCOLOR = (0, 255, 0) # green
    DIAGONALCOLOR = (0, 0, 255) # blue

    def __init__(self):
        pygame.init()
        pygame.display.set_caption('N9 Cognitive Test')
        self.screen = pygame.display.set_mode(Cogtest.SCREEN_SIZE)
        self.screen.fill(Cogtest.BG_COL)
        pygame.display.flip()

    @staticmethod
    def draw_text(surf, text, xpos, ypos):
        labelfont = pygame.font.SysFont("Arial", Cogtest.TEXT_SIZE)
        label = labelfont.render(text, True, Cogtest.TEXT_COL)
        rotatedlabel = pygame.transform.rotate(label, 90)
        surf.blit(rotatedlabel, (xpos, ypos))

    def flanker(self):
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

    def change_stimulus(self, arrow_img, box_img, cross_img, pos):

        stimulus_type = random.randint(1, 4)
        direction = random.randint(1, 2)

        # change flanking arrows direction to left
        # for incongruent stimulus, the middle is always the opposite of this direction
        if direction == 2:
            arrow_img = pygame.transform.rotate(arrow_img, 180)

        # clear display
        self.screen.fill(Cogtest.BG_COL)
        pygame.display.flip()

        if stimulus_type == 1:
            self.draw_flanker_arrow(self.screen, arrow_img, pos)
            self.draw_flanker_arrow(self.screen, arrow_img, (pos[0], pos[1] + 90))
            self.draw_flanker_arrow(self.screen, arrow_img, (pos[0], pos[1] + 180))
            self.draw_flanker_arrow(self.screen, arrow_img, (pos[0], pos[1] + 270))
            self.draw_flanker_arrow(self.screen, arrow_img, (pos[0], pos[1] + 360))

            pygame.display.flip()

        elif stimulus_type == 2:
            self.draw_flanker_arrow(self.screen, arrow_img, pos)
            self.draw_flanker_arrow(self.screen, arrow_img, (pos[0], pos[1] + 90))
            arrow_img = pygame.transform.rotate(arrow_img, 180)
            self.draw_flanker_arrow(self.screen, arrow_img, (pos[0], pos[1] + 180))
            arrow_img = pygame.transform.rotate(arrow_img, 180)
            self.draw_flanker_arrow(self.screen, arrow_img, (pos[0], pos[1] + 270))
            self.draw_flanker_arrow(self.screen, arrow_img, (pos[0], pos[1] + 360))

            # reverse the direction flag
            if direction == 1:
                direction = 2
            elif direction == 2:
                direction = 1

            pygame.display.flip()

        elif stimulus_type == 3:
            self.draw_flanker_arrow(self.screen, box_img, pos)
            self.draw_flanker_arrow(self.screen, box_img, (pos[0], pos[1] + 90))
            self.draw_flanker_arrow(self.screen, arrow_img, (pos[0], pos[1] + 180))
            self.draw_flanker_arrow(self.screen, box_img, (pos[0], pos[1] + 270))
            self.draw_flanker_arrow(self.screen, box_img, (pos[0], pos[1] + 360))

            pygame.display.flip()

        elif stimulus_type == 4:
            self.draw_flanker_arrow(self.screen, cross_img, pos)
            self.draw_flanker_arrow(self.screen, cross_img, (pos[0], pos[1] + 90))
            self.draw_flanker_arrow(self.screen, arrow_img, (pos[0], pos[1] + 180))
            self.draw_flanker_arrow(self.screen, cross_img, (pos[0], pos[1] + 270))
            self.draw_flanker_arrow(self.screen, cross_img, (pos[0], pos[1] + 360))

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
        self.screen.fill(Cogtest.BG_COL)

        # text and label stuff
        label_font = pygame.font.SysFont("Arial", 40)
        button_label = label_font.render('START', True, Cogtest.BG_COL)
        instruction_text1 = label_font.render('Press the button', True, Cogtest.TEXT_COL)
        instruction_text2 = label_font.render('to start', True, Cogtest.TEXT_COL)
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
        pygame.draw.rect(self.screen, Cogtest.TEXT_COL, button_rect, 0)

        # blit button label to screen
        self.screen.blit(button_label, (button_rect.centerx - centerxyoffset[0], button_rect.centery - centerxyoffset[1]))

        # blit text to screen
        instruction_textrect1 = instruction_text1.get_rect()
        instruction_textrect1.topleft = (240, Cogtest.Y - 380)
        instruction_textrect2 = instruction_text2.get_rect()
        instruction_textrect2.topleft = (280, Cogtest.Y - 290)
        self.screen.blit(instruction_text1, instruction_textrect1)
        self.screen.blit(instruction_text2, instruction_textrect2)

        pygame.display.flip()

        return button_rect

    def draw_test_countdown(self, elapsed):
        colour = (0, 0, 0)

        # fill screen
        self.screen.fill(Cogtest.BG_COL)

        radius = elapsed * 50
        width = elapsed * 10

        pygame.draw.circle(self.screen, colour, (Cogtest.X/2, Cogtest.Y/2), radius, width)

        pygame.display.flip()

    def draw_notification(self, not_string, offset, colour, size):

        # fill screen
        self.screen.fill(Cogtest.BG_COL)

        text_font = pygame.font.SysFont("Arial", size)
        not_text = text_font.render(not_string, True, colour)
        not_text = pygame.transform.rotate(not_text, 90)

        # blit text to screen
        not_textrect = not_text.get_rect()
        not_textrect.topleft = (offset[0], Cogtest.Y - offset[1])
        self.screen.blit(not_text, not_textrect)

        pygame.display.flip()

        time.sleep(1)


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

    def run(self):
        arrow_img, box_img, cross_img, pos = self.flanker()

        points = []
        mouse_down = False
        next_stimulus = False
        show_stimulus = False
        show_start_screen = True
        show_countdown = False
        main_clock = pygame.time.Clock()
        touchpos = (0, 0)
        start_time = 0
        result = False

        while True:
            # check for events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # on mouse down, erase the previous line and start drawing a new one
                if event.type == pygame.MOUSEBUTTONDOWN:
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
                    segments = moosegesture.getSegments(points)

                    touchpos = event.pos

                    # only when stimulus is shown
                    if len(strokes) > 0 and show_stimulus:

                        if stimulus_type == 1:
                            # left/right
                            if (direction == 1 and strokes[0] == 8) or (direction == 2 and strokes[0] == 2):
                                result = True
                            else:
                                result = False

                        if stimulus_type == 2:
                            # left/right
                            if (direction == 1 and strokes[0] == 8) or (direction == 2 and strokes[0] == 2):
                                result = True
                            else:
                                result = False

                        if stimulus_type == 3:
                            # up
                            if strokes[0] == 4:
                                result = True
                            else:
                                result = False

                        if stimulus_type == 4:
                            # down
                            if strokes[0] == 6:
                                result = True
                            else:
                                result = False

                if event.type == MOUSEMOTION and mouse_down:
                    # draw the line if the mouse is dragging
                    points.append((event.pos[0], event.pos[1]))

            # draw points
            #for x, y in points:
            #    pygame.draw.circle(self.screen, Cogtest.POINTSCOLOR, (x, y), 2)

            if show_start_screen:
                start_button = self.draw_start_screen()

                if start_button.collidepoint(touchpos):
                    show_start_screen = False
                    show_countdown = True
                    touchpos = (0, 0)

                    # start countdown timer
                    start_time = time.time()

            if show_countdown:
                elapsed = time.time() - start_time

                if elapsed > 3:
                    show_countdown = False
                    next_stimulus = True
                else:
                    self.draw_test_countdown(elapsed)

            if next_stimulus:
                next_stimulus = False
                stimulus_type, direction = self.change_stimulus(arrow_img, box_img, cross_img, pos)

                # start timer
                start_time = time.time()

                show_stimulus = True

            if show_stimulus:
                elapsed = time.time() - start_time

                if elapsed > 3:
                    self.draw_notification('Too slow. Try faster.', (350, 410), (0, 0, 0), 40)
                    show_stimulus = False
                    show_start_screen = True
                elif elapsed <= 3 and len(strokes) > 0:
                    if result:
                        self.draw_notification('Correct', (350, 320), (0, 0, 255), 60)
                        show_stimulus = False
                        show_start_screen = True
                    else:
                        self.draw_notification('Incorrect', (350, 350), (255, 0, 0), 60)
                        show_stimulus = False
                        show_start_screen = True

            if mouse_down:
                # draw strokes as unidentified while dragging the mouse
                if len(points) > 1:
                    pygame.draw.lines(self.screen, Cogtest.LINECOLOR, False, points, 2)
            else:
                # draw the identified strokes
                segNum = 0
                curColor = Cogtest.LINECOLOR
                for p in range(len(points)-1):

                    if segNum < len(segments) and segments[segNum][0] == p:
                        # start of new stroke
                        if strokes[segNum] in [2, 4, 6, 8]:
                            curColor = Cogtest.CARDINALCOLOR
                        elif strokes[segNum] in [1, 3, 7, 9]:
                            curColor = Cogtest.DIAGONALCOLOR
                    pygame.draw.line(self.screen, curColor, points[p], points[p+1], 2)

                    if segNum < len(segments) and segments[segNum][1] == p:
                        # end of a stroke
                        curColor = Cogtest.LINECOLOR
                        segNum += 1

            #pygame.display.update()
            main_clock.tick(Cogtest.FPS)