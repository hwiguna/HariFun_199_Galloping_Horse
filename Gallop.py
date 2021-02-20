#Galloping Horse by Hari Wiguna, 2021
def main():
    import board            # Pi Pico Board GPIO pins
    import displayio        # Python's multi layer graphics
    import adafruit_displayio_ssd1306   # OLED Driver
    import busio            # Provides I2C support
    import time
    from analogio import AnalogIn

    WIDTH, HEIGHT = 128, 32  # Change to 64 if needed
    
    displayio.release_displays() # Just to be safe

    def SetupDisplay():
        # So we can communicate with our OLED via I2C
        i2c = busio.I2C(scl=board.GP3, sda=board.GP2)

        # How displayio talks to physical screen
        display_bus = displayio.I2CDisplay(i2c, device_address=0x3C) #, reset=oled_reset)

        # display represents the physical screen
        display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT)
        
        # Group is a list of TileGrids that display would render on physical screen
        group = displayio.Group(max_size=1)

        display.show(group)

        return (display, group)

    def SetupTileGrid():
        #-- Read the BMP file --
        bitmap_file = open("hari/Combined32PixelTallv2.bmp", "rb")# Do NOT use with open() here. We need the file to remain open for OnDiskBitmap() to work.
        bitmap = displayio.OnDiskBitmap(bitmap_file) # setup the file as bitmap data source
        print("bitmap ok",bitmap) # this confirms that we have an OnDiskBitmap object.

        #-- Create TileGrid --
        tileGrid = displayio.TileGrid(bitmap, pixel_shader=displayio.ColorConverter(), width=1, height=1, tile_width=47, tile_height=32)
        return tileGrid

    def SetupAnalog():
        pot0 = AnalogIn(board.A0)
        pot1 = AnalogIn(board.A1)
        return (pot0, pot1)

    def _map(x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def getMoveSpeed(pot):
        return _map(pot.value, 256, 65520, 0.1, 0.1/30)

    def getAnimSpeed(pot):
        return _map(pot.value, 256, 65520, 0.4, 0.4/10)

    #=== MAIN ===
    (mDisplay, mGroup) = SetupDisplay()
    (mTileGrid) = SetupTileGrid()
    mGroup.append(mTileGrid) #add the TileGrid to the group

    mPot0, mPot1 = SetupAnalog()

    mNextAnim = time.monotonic() + getAnimSpeed(mPot1)
    mNextMove = time.monotonic() + getMoveSpeed(mPot1)
    mCurFrame = 0
    xOffset = -47

    while True:
        if time.monotonic() >= mNextMove:
            xOffset += 1
            if xOffset > 128: xOffset = -47
            mNextMove = time.monotonic() + getMoveSpeed(mPot1)

        if time.monotonic() >= mNextAnim:
            mGroup.x = xOffset
            mTileGrid[0] = mCurFrame
            mCurFrame += 1
            if mCurFrame>14: mCurFrame=0
            mNextAnim = time.monotonic() +getAnimSpeed(mPot0)
            #print("mNextAnim=", mNextAnim, "  mCurFrame=",mCurFrame)
        
