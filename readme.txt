G-Force playback device

This is the source code for the arduino sketch used with an ESP8266, but it might also work with an arduino, and the python script that is reading, calculating and sending the geforce data to the microcontroller via USB serial connection.

Please excuse my coding stile, i didn't expect that anyone would ask for the source code :D So it is really ugly, just wanted to get it working quickly.

You need a .gf file that is read by the python script, and this .gf file contains all data for your recording, such as the mp3/video file (played back by VLC), the geforce data file in the CSV format and some settings like time offset and smoothing for each channel.

The script can read different CSV formats, you can specify your format in the .gf-file. csvtype=4 for example is semicolon separated, decimal point with timing on column 1, x y z on the following columns. I used and recommend the app "phyphox" for recording. I provided an example CSV and MP3 file

The ESP starts to crash and keep rebooting for some reason after sending a few packets of data. Uploading the sketch again seems to help for the moment. Maybe someone findes the problem :)
