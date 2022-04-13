"""
Threaded bouncing boxes with frame buffer

Uses a single shot function for second core SPI handler.
This cleans itself when the function exits removing the
need for a garbage collection call.

"""
import math
from machine import Pin, SPI
import framebuf
from random import random, seed, randint
from utime import sleep_us, ticks_cpu, ticks_us
import _thread
import st7789 as st7789



class Box(object):
    """Bouncing box."""

    def __init__(self, screen_width, screen_height, size, color):
        """Initialize box.

        Args:
            screen_width (int): Width of screen.
            screen_height (int): Width of height.
            size (int): Square side length.
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
        for num in range(1, 50):
            num2 = math.sqrt(num)

    def draw(self):
        """Draw box."""
        global fbuf

        x = int(self.x)
        y = int(self.y)
        size = self.size
        fbuf.fill_rect(x, y, size, size, self.color)


# set landscape screen
screen_width = 135
screen_height = 240
screen_rotation = 1

spi = SPI(1,
          baudrate=31250000,
          polarity=1,
          phase=1,
          bits=8,
          firstbit=SPI.MSB,
          sck=Pin(10),
          mosi=Pin(11))

display = st7789.ST7789(
    spi,
    screen_width,
    screen_height,
    reset=Pin(12, Pin.OUT),
    cs=Pin(9, Pin.OUT),
    dc=Pin(8, Pin.OUT),
    backlight=Pin(13, Pin.OUT),
    rotation=screen_rotation)

print(spi)

# FrameBuffer needs 2 bytes for every RGB565 pixel
buffer_width = 240
buffer_height = 136
buffer = bytearray(buffer_width * buffer_height * 2)
fbuf = framebuf.FrameBuffer(buffer, buffer_width, buffer_height, framebuf.RGB565)

render_frame = False


def main_loop():
    """Test code."""

    global fbuf, buffer, buffer_width, buffer_height
    global render_frame

    render_frame = False

    try:

        boxes = [Box(buffer_width - 1, buffer_height - 1, randint(7, 40),
                     st7789.color565(randint(30, 256), randint(30, 256), randint(30, 256))) for i in range(25)]

        start_time = ticks_us()
        frame_count = 0
        while True:

            for b in boxes:
                b.update_pos()

            while render_frame:
                # previous frame still rendering
                pass

            for b in boxes:
                b.draw()

            # render frame to lcd
            render_frame = True
            # start spi handler on core 1
            spi_thread = _thread.start_new_thread(render_thread, ())

            frame_count += 1
            if frame_count == 100:
                frame_rate = 100 / ((ticks_us() - start_time) / 1000000)
                print(frame_rate)
                start_time = ticks_us()
                frame_count = 0


    except KeyboardInterrupt:
        pass


def render_thread():
    global fbuf, buffer, buffer_width, buffer_height, render_frame, spi
    global display, screen_width, screen_height, screen_rotation

    # No need to wait for start signal as thread only started when buffer is ready

    # render display
    display.blit_buffer(buffer, 0, 0, buffer_width, buffer_height)

    # clear buffer
    fbuf.fill(0)

    # signal finished back to main thread
    render_frame = False

    # thread will exit and self clean removing need for garbage collection


main_loop()
