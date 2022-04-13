"""
Test to get frame buffer working on ILI9341

Adjust buffer screen size to check memory usage

Times 60 frames to give idea of max frame rate

"""
import time
from time import sleep
from ili9341 import Display, color565
from machine import Pin, SPI
import machine
import framebuf




def test():
    """Test code."""
    # Baud rate of 31250000 is max
    colors = [color565(255, 0, 0),
              color565(0, 255, 0),
              color565(0, 0, 255),
              color565(255, 255, 0),
              color565(0, 255, 255),
              color565(255, 0, 255)]

    spi = SPI(0,
              baudrate=31250000,
              polarity=1,
              phase=1,
              bits=8,
              firstbit=SPI.MSB,
              sck=Pin(18),
              mosi=Pin(19),
              miso=Pin(16))
    display = Display(spi, dc=Pin(15), cs=Pin(17), rst=Pin(14), width=320, height=240, rotation=90)

    print(spi)

    # FrameBuffer needs 2 bytes for every RGB565 pixel
    buffer_width = 240
    buffer_height = 140
    buffer = bytearray(buffer_width * buffer_height * 2)
    fbuf = framebuf.FrameBuffer(buffer, buffer_width, buffer_height, framebuf.RGB565)

    start_time = time.ticks_us()
    colour = 0
    for count in range(60):
        fbuf.fill(colors[colour])
        display.block(int((320 - buffer_width) / 2), int((240 - buffer_height) / 2),
                      int((320 - buffer_width) / 2) + buffer_width-1,
                      int((240 - buffer_height) / 2) + buffer_height-1, buffer)
        colour = (colour + 1) % 6
        sleep(1)
    print(time.ticks_diff(time.ticks_us(), start_time))
    display.display_off()


# machine.freq(250000000)
test()
