"""

Threaded version of bouncing boxes with frame buffer

Using simple flag for thread synchronisation.

"""
import math
import time
from time import sleep
from ili9341 import Display, color565
from machine import Pin, SPI
import machine
import framebuf
from random import random, seed, randint
from utime import sleep_us, ticks_cpu, ticks_us
import gc
import os
import _thread


class Box(object):
    """Bouncing box."""

    def __init__(self, screen_width, screen_height, size, color):
        """Initialize box.

        Args:
            screen_width (int): Width of screen.
            screen_height (int): Width of height.
            size (int): Square side length.
            display (ILI9341): display object.
            color (int): RGB565 color value.
        """
        self.size = size
        self.w = screen_width
        self.h = screen_height
        self.color = color
        # Generate non-zero random speeds between -5.0 and 5.0
        seed(ticks_cpu())
        r = random() * 10.0
        self.x_speed = r - 5
        r = random() * 10.0
        self.y_speed = r - 5

        self.x = self.w / 2
        self.y = self.h / 2

    def update_pos(self):
        """Update box position and speed."""

        # update position
        self.x += self.x_speed
        self.y += self.y_speed

        # limit checking
        if self.x < 0:
            self.x = 0
            self.x_speed = -self.x_speed
        elif self.x > (self.w - self.size):
            self.x = self.w - self.size
            self.x_speed = -self.x_speed
        if self.y < 0:
            self.y = 0
            self.y_speed = -self.y_speed
        elif self.y > (self.h - self.size):
            self.y = self.h - self.size
            self.y_speed = -self.y_speed

        # extra processing load
        # for num in range(1, 25):
        #     num2 = math.sqrt(num)

    def draw(self):
        """Draw box."""
        global fbuf

        x = int(self.x)
        y = int(self.y)
        size = self.size
        fbuf.fill_rect(x, y, size, size, self.color)


def free(full=False):
    gc.collect()
    F = gc.mem_free()
    A = gc.mem_alloc()
    T = F + A
    P = '{0:.2f}%'.format(F / T * 100)
    if not full:
        return P
    else:
        return ('Total:{0} Free:{1} ({2})'.format(T, F, P))


# set landscape screen
screen_width = 320
screen_height = 240
screen_rotation = 90

spi = SPI(0,
          baudrate=31250000,
          polarity=1,
          phase=1,
          bits=8,
          firstbit=SPI.MSB,
          sck=Pin(18),
          mosi=Pin(19),
          miso=Pin(16))

display = Display(spi, dc=Pin(15), cs=Pin(17), rst=Pin(14),
                  width=screen_width, height=screen_height,
                  rotation=screen_rotation)

print(spi)

# FrameBuffer needs 2 bytes for every RGB565 pixel
buffer_width = 240
buffer_height = 136
buffer = bytearray(buffer_width * buffer_height * 2)
fbuf = framebuf.FrameBuffer(buffer, buffer_width, buffer_height, framebuf.RGB565)

render_frame = False


def main_loop():

    global fbuf, buffer, buffer_width, buffer_height
    global render_frame

    try:

        boxes = [Box(buffer_width - 1, buffer_height - 1, randint(7, 40),
                     color565(randint(30, 256), randint(30, 256), randint(30, 256))) for i in range(100)]

        print(free(True))

        start_time = ticks_us()
        frame_count = 0
        while True:

            for b in boxes:
                b.update_pos()

            while render_frame:
                # previous frame still rendering to lcd
                pass

            for b in boxes:
                b.draw()

            # ask spi handler to render frame to LCD
            render_frame = True

            frame_count += 1
            if frame_count == 100:
                frame_rate = 100 / ((ticks_us() - start_time) / 1000000)
                print(frame_rate)
                start_time = ticks_us()
                frame_count = 0


    except KeyboardInterrupt:
        pass


def render_thread(id):
    global fbuf, buffer, buffer_width, buffer_height, render_frame, spi
    global display, screen_width, screen_height, screen_rotation

    while True:
        # wait for main_loop to ask for frame render
        while not render_frame:
           pass

        # render display
        display.block(int((320 - buffer_width) / 2), int((240 - buffer_height) / 2),
                      int((320 - buffer_width) / 2) + buffer_width - 1,
                      int((240 - buffer_height) / 2) + buffer_height - 1, buffer)
        # clear buffer
        fbuf.fill(0)
        render_frame = False

        gc.collect()  # run garbage collection to clean unused memory


spi_thread = _thread.start_new_thread(render_thread, (2,))
main_loop()
