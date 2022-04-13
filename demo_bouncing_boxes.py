"""ILI9341 demo (bouncing boxes)."""
import machine
from machine import Pin, SPI
from random import random, seed
from ili9341 import Display, color565
from random import random, seed, randint
from utime import sleep_us, ticks_cpu, ticks_us, ticks_diff


class Box(object):
    """Bouncing box."""

    def __init__(self, screen_width, screen_height, size, display, color):
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
        self.display = display
        self.color = color
        # Generate non-zero random speeds between -5.0 and 5.0
        seed(ticks_cpu())
        r = random() * 10.0
        self.x_speed = r - 5
        r = random() * 10.0
        self.y_speed = r - 5

        self.x = self.w / 2
        self.y = self.h / 2

        self.prev_x = self.x
        self.prev_y = self.y


    def update_pos(self):
        """Update box position and speed."""
        # store current position
        self.prev_x = self.x
        self.prev_y = self.y

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

    def draw(self):
        """Draw box."""
        x = int(self.x)
        y = int(self.y)
        size = self.size
        prev_x = int(self.prev_x)
        prev_y = int(self.prev_y)
        self.display.fill_hrect(prev_x,
                                prev_y,
                                size, size, 0)
        self.display.fill_hrect(x,
                                y,
                                size, size, self.color)


def test():
    """Bouncing box."""

    # set landscape screen
    screen_width = 320
    screen_height = 240
    screen_rotation = 90

    try:
        # Baud rate of 31250000 is max at standard clock speed
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
        display.clear()

        # generate boxes
        boxes = [Box(319, 239, randint(7, 40), display,
                     color565(randint(30, 256), randint(30, 256), randint(30, 256))) for i in range(75)]


        start_time = ticks_us()
        frame_count = 0

        while True:
            timer = ticks_us()
            for b in boxes:
                b.update_pos()
                b.draw()

            frame_count += 1
            if frame_count == 100:
                frame_rate = 100 / ((ticks_us() - start_time) / 1000000)
                print(frame_rate)
                start_time = ticks_us()
                frame_count = 0

    except KeyboardInterrupt:
        display.cleanup()


test()
