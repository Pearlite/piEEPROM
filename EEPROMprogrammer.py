# Read from/write to EEPROM using a Raspberry Pi
# Use LS595 shift registers for address lines
import atexit
import time
import RPi.GPIO as GPIO


def setup():
    '''Define I/O pins and set initial states'''
    GPIO.setmode(GPIO.BCM)  # Use BCM numbering scheme

    # Define EEPROM data pins
    global datapins
    datapins = [14, 15, 18, 23, 24, 25, 8, 7]
    # Setup as I or O is done in write/read/erase functions

    # Set up EEPROM control pins and set EEPROM in standby mode
    GPIO.setup(2, GPIO.OUT, initial=GPIO.HIGH)  # CE, active low
    GPIO.setup(3, GPIO.OUT, initial=GPIO.HIGH)  # OE, active low
    GPIO.setup(4, GPIO.OUT, initial=GPIO.HIGH)  # WE, active low

    # Set up shift register control pins
    # (tied together for both shift registers)
    GPIO.setup(17, GPIO.OUT, initial=GPIO.LOW)  # SER
    GPIO.setup(27, GPIO.OUT)  # SCK
    GPIO.setup(22, GPIO.OUT, inital=GPIO.HIGH)  # SRCLR, active low


def read_contents(num):
    '''Read first x addresses and print their contents'''

    GPIO.setup(datapins, GPIO.IN)  # Set up data pins
    GPIO.output(2, 0)  # CE - enable

    print('Reading first {} addresses...\n'.format(num))
    D_hex = []
    for i in range(num):  # Read first num addresses
        # Fill shift register with binary representation of address
        fill_shift_register(i)

        GPIO.output(3, 0)  # OE - enable
        time.sleep(0.001)

        # Read data from data pins
        D = []
        for bit, datapin in enumerate(datapins):
            D[bit] = GPIO.input(datapin)

        D_hex[i] = hex(int(D.join('')))

        GPIO.output(3, 1)  # OE - disable

        # Clear shift registers
        GPIO.output(22, 0)
        time.sleep(0.001)
        GPIO.output(22, 1)

        # Display every 16th address + 16 EEPROM contents, in hex:
        if(i % 16 == 0) & (i != 0):
            print('''0x{:03x}:
                  {:02x} {:02x} {:02x} {:02x} {:02x} {:02x} {:02x} {:02x}\t
                  {:02x} {:02x} {:02x} {:02x} {:02x} {:02x} {:02x} {:02x}\n'''
                  .format(hex(i), D_hex[i-15:i]))

    GPIO.output(2, 1)  # CE - disable


def erase():
    '''Overwrite all EEPROM contents with ones'''

    print('Overwriting EEPROM contents...')

    GPIO.setup(datapins, GPIO.OUT, initial=GPIO.HIGH)  # Set up data pins
    GPIO.output(2, 0)  # CE - enable

    # Loop over all addresses; write ones
    for i in range(2**10):  # EEPROM has 10 address pins
        fill_shift_register(i)
        GPIO.output(4, 0)  # WE - enable
        time.sleep(0.001)
        GPIO.output(4, 1)  # WE - disable

        if i % 64 == 0:
            print('.')  # Progress indicator

        # Clear shift registers
        GPIO.output(22, 0)
        time.sleep(0.001)
        GPIO.output(22, 1)

    GPIO.output(2, 1)  # CE - disable
    print('Done.')


def write_7seg():
    '''Write binary-to-7 segment display mapping to the EEPROM'''

    print('Writing 7-segment display mapping...')

    GPIO.setup(datapins, GPIO.OUT)  # Set up data pins
    GPIO.output(2, 0)  # CE - enable

    # Loop over all addresses; write appropriate data
    for i in range(2**10):  # EEPROM has 10 address pins
        fill_shift_register(i)
        # TODO: determine which contents the EEPROM needs, based on the connections to the 7-segment display

    GPIO.output(2, 1)  # CE - disable
    print('Done.')


def fill_shift_register(i):
    '''Fill shift register with binary representation of address'''
    address = list(map(int, bin(i)[2:].zfill(10)))

    for i in range(9):
        # Load memory address into shift register
        GPIO.output(17, address(i))  # Output on serial

        # Pulse SR clock to advance one bit
        GPIO.output(27, 1)
        time.sleep(0.001)
        GPIO.output(27, 0)


def main():
    atexit.register(GPIO.cleanup())  # Ensure cleanup runs at exit or interrupt

    setup()
    read_contents(255)  # Read first 255 addresses and print contents
    quit()


if __name__ == '__main__':
    main()
