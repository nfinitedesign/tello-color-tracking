import cv2
import pygame
import numpy as np
import time

from djitellopy import Tello
from pygame.locals import *


#
#        8888888          d8b 888    d8b          888 d8b                   888    d8b
#          888            Y8P 888    Y8P          888 Y8P                   888    Y8P
#          888                888                 888                       888
#          888   88888b.  888 888888 888  8888b.  888 888 .d8888b   8888b.  888888 888  .d88b.  88888b.
#          888   888 "88b 888 888    888     "88b 888 888 88K          "88b 888    888 d88""88b 888 "88b
#          888   888  888 888 888    888 .d888888 888 888 "Y8888b. .d888888 888    888 888  888 888  888
#          888   888  888 888 Y88b.  888 888  888 888 888      X88 888  888 Y88b.  888 Y88..88P 888  888
#        8888888 888  888 888  "Y888 888 "Y888888 888 888  88888P' "Y888888  "Y888 888  "Y88P"  888  888
#


class FrontEnd(object):
    """ Maintains the Tello display and moves it through the keyboard keys.
        Press escape key to quit.
        The controls are:
            - Tab:      Takeoff
            - Shift:    Land
            - Space:    Emergency Shutdown
            - WASD:     Forward, backward, left and right
            - Q and E:  Counter clockwise and clockwise rotations
            - R and F:  Up and down
            - T:        Start/Stop tracking
            - C:        Select central pixel value as new color for tracking
            - #:        Switch controllable parameter
            - + and -:  Raise or Lower controllable parameter
    """

    def __init__(self):
        # Init pygame
        pygame.init()

        # Init Tello object that interacts with the Tello drone
        self.tello = Tello()

        # general config
        self.internalSpeed = 100
        self.FPS = 20
        self.hud_size = (800, 600)


        # config of controllable parameters
        self.controll_params = {
            'Speed': 100,
            'Color': 0,
        }
        self.controll_params_d = {
            'Speed': 10,
            'Color': 1,
        }
        self.controll_params_m = {
            'Speed': 100,
            'Color': 2,
        }

        # tracker config
        self.color_lower = {
            'blue':     (100, 200, 50),
            'red':      (0, 200, 100),
            'yellow':   (20, 200, 130),
        }
        self.color_upper = {
            'blue':     (140, 255, 255),
            'red':      (20, 255, 255),
            'yellow':   (40, 255, 255),
        }

        self.current_color = np.array(self.color_lower['blue']) + np.array(self.color_upper['blue'])
        for i in range(0,3): self.current_color[i] = self.current_color[i] / 2
        self.crange = (10, 50, 50)

        # other params (no need to config)
        self.current_parameter = 0
        self.param_keys = list(self.controll_params.keys())
        self.color_keys = list(self.color_lower.keys())
        self.central_color = (0,0,0)
        self.midx = int(self.hud_size[0] / 2)
        self.midy = int(self.hud_size[1] / 2)
        self.xoffset = 0
        self.yoffset = 0
        self.target_radius = 120
        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0
        self.send_rc_control = False
        self.isTracking = False

         # Creat pygame window
        pygame.display.set_caption("Tello video stream")
        self.screen = pygame.display.set_mode(self.hud_size)

        # create update timer
        pygame.time.set_timer(USEREVENT + 1, 50)


#
#      888b     d888          d8b               888
#      8888b   d8888          Y8P               888
#      88888b.d88888                            888
#      888Y88888P888  8888b.  888 88888b.       888      .d88b.   .d88b.  88888b.
#      888 Y888P 888     "88b 888 888 "88b      888     d88""88b d88""88b 888 "88b
#      888  Y8P  888 .d888888 888 888  888      888     888  888 888  888 888  888
#      888   "   888 888  888 888 888  888      888     Y88..88P Y88..88P 888 d88P
#      888       888 "Y888888 888 888  888      88888888 "Y88P"   "Y88P"  88888P"
#                                                                         888
#                                                                         888
#                                                                         888
#


    def run(self):
        """
        Main loop.
        Contains reading the incoming frames, the call for tracking and basic keyboard stuff.
        """

        if not self.tello.connect():
            print("Tello not connected")
            return

        if not self.tello.set_speed(self.internalSpeed):
            print("Not set speed to lowest possible")
            return

        # In case streaming is on. This happens when we quit this program without the escape key.
        if not self.tello.streamoff():
            print("Could not stop video stream")
            return

        if not self.tello.streamon():
            print("Could not start video stream")
            return

        frame_read = self.tello.get_frame_read()

        self.should_stop = False
        while not self.should_stop:

            # read frame
            img = cv2.cvtColor(frame_read.frame, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, self.hud_size, interpolation=cv2.INTER_AREA)

            # get output from tracking
            if self.isTracking:
                self.track(img)

            # produce hud
            self.frame = self.write_hud(img.copy())
            self.frame = np.fliplr(self.frame)
            self.frame = np.rot90(self.frame)
            self.frame = pygame.surfarray.make_surface(self.frame)
            self.screen.fill([0, 0, 0])
            self.screen.blit(self.frame, (0, 0))
            pygame.display.update()

            # handle input from dronet or user
            for event in pygame.event.get():
                if event.type == USEREVENT + 1:
                    self.send_input()
                elif event.type == QUIT:
                    self.should_stop = True
                elif event.type == KEYDOWN:
                    if (event.key == K_ESCAPE) or (event.key == K_BACKSPACE):
                        self.should_stop = True
                    else:
                        self.keydown(event.key)
                elif event.type == KEYUP:
                        self.keyup(event.key)

                # shutdown stream
                if frame_read.stopped:
                    frame_read.stop()
                    break

            # wait a little
            time.sleep(1 / self.FPS)

        # always call before finishing to deallocate resources
        self.tello.end()


    def track(self, frame):
        """
        HSV color space tracking.
        """
        # resize the frame, blur it, and convert it to the HSV
        # color space
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_RGB2HSV)
        self.central_color = hsv[self.midy,self.midx,:]

        # construct a mask for the color then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        mask = cv2.inRange(hsv, self.current_color - self.crange, self.current_color + self.crange)
        mask = cv2.erode(mask, None, iterations=3)
        mask = cv2.dilate(mask, None, iterations=3)

        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        image, cnts, hierarchy  = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)

        center = None

        radius = 0
        velocity = 0
        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # update color from mean color
            mask_upstate = cv2.bitwise_and(hsv, hsv, mask=mask)
            mean = cv2.mean(mask_upstate)
            multiplier = float(mask.size)/(cv2.countNonZero(mask)+0.001)
            mean = np.array([multiplier * x for x in mean])

            self.update_color(mean)
            print(self.current_color)

            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(cnts, key=cv2.contourArea)

            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)

            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            # only proceed if the radius meets a minimum size
            if radius > 40:
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                cv2.circle(frame, (int(x), int(y)), int(radius),
                           (0, 255, 0), 2)

                self.xoffset = int(center[0] - self.midx)
                self.yoffset = int(self.midy - center[1])
                velocity = clamp(self.target_radius - radius, -40, 60) / 100 * self.controll_params['Speed']
            else:
                self.xoffset = 0
                self.yoffset = 0
                velocity = 0
        else:
            self.xoffset = 0
            self.yoffset = 0
            velocity = 0

        xfact = self.xoffset / self.hud_size[0] * self.controll_params['Speed'] * 2
        yfact = self.yoffset / self.hud_size[0] * self.controll_params['Speed'] * 2

        self.for_back_velocity = int(velocity)
        self.yaw_velocity = int(xfact)
        self.up_down_velocity = int(yfact)


#
#      8888888                            888         888b     d888          888    888                    888
#        888                              888         8888b   d8888          888    888                    888
#        888                              888         88888b.d88888          888    888                    888
#        888   88888b.  88888b.  888  888 888888      888Y88888P888  .d88b.  888888 88888b.   .d88b.   .d88888 .d8888b
#        888   888 "88b 888 "88b 888  888 888         888 Y888P 888 d8P  Y8b 888    888 "88b d88""88b d88" 888 88K
#        888   888  888 888  888 888  888 888         888  Y8P  888 88888888 888    888  888 888  888 888  888 "Y8888b.
#        888   888  888 888 d88P Y88b 888 Y88b.       888   "   888 Y8b.     Y88b.  888  888 Y88..88P Y88b 888      X88
#      8888888 888  888 88888P"   "Y88888  "Y888      888       888  "Y8888   "Y888 888  888  "Y88P"   "Y88888  88888P'
#                       888
#                       888
#                       888
#


    def keydown(self, key):
        """ Update velocities based on key pressed
        Arguments:
            key: pygame key
        """
        if key == pygame.K_w:           # set forward velocity
            self.isTracking = False
            self.for_back_velocity = self.controll_params['Speed']
        elif key == pygame.K_s:         # set backward velocity
            self.isTracking = False
            self.for_back_velocity = -self.controll_params['Speed']
        elif key == pygame.K_a:         # set left velocity
            self.isTracking = False
            self.left_right_velocity = -self.controll_params['Speed']
        elif key == pygame.K_d:         # set right velocity
            self.isTracking = False
            self.left_right_velocity = self.controll_params['Speed']
        elif key == pygame.K_r:         # set up velocity
            self.isTracking = False
            self.up_down_velocity = self.controll_params['Speed']
        elif key == pygame.K_f:         # set down velocity
            self.isTracking = False
            self.up_down_velocity = -self.controll_params['Speed']
        elif key == pygame.K_e:         # set yaw clockwise velocity
            self.isTracking = False
            self.yaw_velocity = self.controll_params['Speed']
        elif key == pygame.K_q:         # set yaw counter clockwise velocity
            self.isTracking = False
            self.yaw_velocity = -self.controll_params['Speed']
        elif key == pygame.K_TAB:       # takeoff
            self.tello.takeoff()
            self.send_rc_control = True
        elif key == pygame.K_LSHIFT:    # land
            self.isTracking = False
            self.tello.land()
            self.send_rc_control = False
        elif key == pygame.K_SPACE:     # emergency shutdown
            self.isTracking = False
            self.tello.emergency()
            self.send_rc_control = False
            self.should_stop = True
        elif key == pygame.K_BACKSPACE:     # emergency shutdown
            self.isTracking = False
            self.send_rc_control = False
            self.should_stop = True
        elif key == pygame.K_t:      # arm tracking
            self.isTracking = not self.isTracking
            self.for_back_velocity = 0
            self.yaw_velocity = 0
            self.up_down_velocity = 0
        elif key == pygame.K_c:      # get new color
            self.set_color(self.central_color)
            self.for_back_velocity = 0
            self.yaw_velocity = 0
            self.up_down_velocity = 0
        elif key == pygame.K_HASH:         # switch parameters
            if self.current_parameter == 0:
                self.current_parameter = 1
            else:
                self.current_parameter = 0
        elif key == pygame.K_PLUS:      # raise current parameter
            what = self.param_keys[self.current_parameter]
            if self.controll_params[what] < self.controll_params_m[what] - 0.01:
                self.controll_params[what] = self.controll_params[what] + self.controll_params_d[what]
                if (what == 'Color'):
                    self.reset_color()
        elif key == pygame.K_MINUS:     # lower current parameter
            what = self.param_keys[self.current_parameter]
            if self.controll_params[what] > 0.01:
                self.controll_params[what] = self.controll_params[what] - self.controll_params_d[what]
                if (what == 'Color'):
                    self.reset_color()


    def keyup(self, key):
        """ Update velocities based on key released
        Arguments:
            key: pygame key
        """
        if key == pygame.K_w or key == pygame.K_s:      # set zero forward/backward velocity
            self.for_back_velocity = 0
        elif key == pygame.K_a or key == pygame.K_d:    # set zero left/right velocity
            self.left_right_velocity = 0
        elif key == pygame.K_r or key == pygame.K_f:    # set zero up/down velocity
            self.up_down_velocity = 0
        elif key == pygame.K_q or key == pygame.K_e:    # set zero yaw velocity
            self.yaw_velocity = 0


    def send_input(self):
        """ Update routine. Send velocities to Tello."""
        #print("V: " + str(self.for_back_velocity) + "; Y: " + str(self.yaw_velocity))
        if self.send_rc_control:
            self.tello.send_rc_control(self.left_right_velocity, self.for_back_velocity, self.up_down_velocity,
                                       self.yaw_velocity)


#
#        888    888          888                                888b     d888          888    888                    888
#        888    888          888                                8888b   d8888          888    888                    888
#        888    888          888                                88888b.d88888          888    888                    888
#        8888888888  .d88b.  888 88888b.   .d88b.  888d888      888Y88888P888  .d88b.  888888 88888b.   .d88b.   .d88888 .d8888b
#        888    888 d8P  Y8b 888 888 "88b d8P  Y8b 888P"        888 Y888P 888 d8P  Y8b 888    888 "88b d88""88b d88" 888 88K
#        888    888 88888888 888 888  888 88888888 888          888  Y8P  888 88888888 888    888  888 888  888 888  888 "Y8888b.
#        888    888 Y8b.     888 888 d88P Y8b.     888          888   "   888 Y8b.     Y88b.  888  888 Y88..88P Y88b 888      X88
#        888    888  "Y8888  888 88888P"   "Y8888  888          888       888  "Y8888   "Y888 888  888  "Y88P"   "Y88888  88888P'
#                                888
#                                888
#                                888
#


    def update_color(self, val):
        """
        Adjusts the currently tracked color to input.
        """
        if (cv2.mean(val) != 0):
            for i in range(0,2):
                self.current_color[i] = clamp(val[i],
                                       self.color_lower[self.color_keys[self.controll_params['Color']]][i],
                                       self.color_upper[self.color_keys[self.controll_params['Color']]][i])

    def set_color(self, val):
        self.current_color = np.array(val)
        print(val)

    def reset_color(self):
        self.current_color = np.array(self.color_lower[self.color_keys[self.controll_params['Color']]]) + np.array(self.color_upper[self.color_keys[self.controll_params['Color']]])
        for i in range(0,3): self.current_color[i] = self.current_color[i] / 2

    def write_hud(self, frame):
        """Draw drone info and record on frame"""
        stats = ["TelloTracker"]
        if self.isTracking:
            stats.append("Tracking active.")
            stats.append("Speed: {:03d}".format(self.controll_params['Speed']))
            stats.append("Color: " + self.color_keys[self.controll_params['Color']])
            self.draw_arrows(frame)
        else:
            stats.append("Tracking disabled.")
            img = cv2.circle(frame, (self.midx, self.midy), 10, (0,0,255), 1)

        stats.append(self.param_keys[self.current_parameter] + ": {:4.1f}".format(self.controll_params[self.param_keys[self.current_parameter]]))
        for idx, stat in enumerate(stats):
            text = stat.lstrip()
            cv2.putText(frame, text, (0, 30 + (idx * 30)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.0, (255, 0, 0), lineType=30)
        return frame

    def draw_arrows(self, frame):
        """Show the direction vector output in the cv2 window"""
        #cv2.putText(frame,"Color:", (0, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, 255, thickness=2)
        cv2.arrowedLine(frame, (self.midx, self.midy),
                        (self.midx + self.xoffset, self.midy - self.yoffset),
                        (255, 0, 0), 5)
        return frame

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

def main():
    frontend = FrontEnd()

    # run frontend
    frontend.run()


if __name__ == '__main__':
    main()
