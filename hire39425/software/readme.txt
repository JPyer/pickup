2020/9/24

1. If the device firmware's version is lower than 0.2.0 or there is no firmware in its flash,
   use CCS to load "xmodem/sg-pickup-xmodem.out' and burn .ais file via Xmodem protocol;
   otherwise, this step should be ignored.

2. Use "sg_upgrade.py" to upgrade device's firmware via network.
   Both .fw and .ais files are supported, but it's recommended to use .fw file.
   .fw files are encrypted and include product info, they are more safer than .ais files.
   Run "sg_upgrade.py --help" for more details.

3. If there's no UART1 boot switch on the board,
   it is necessary to burn the flash image "xmodem/sg-pickup-xmodem.ais"
   to disable the hardware watch dog before debugging the device with CCS.
