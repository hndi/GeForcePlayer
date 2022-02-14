import serial
import time
import csv
import sys
import configparser
import vlc
import math


stepScale = 16; #for 1/16 microstepping
maxAngles = [[000, 300*stepScale], [000, 300*stepScale], [000, 300*stepScale]]
damping = [1.0, 1.0, 1.0]
dampers = [0.0, 0.0, 0.0]


def getSmoothedVal2(ch):
    return dampers[ch]
    
def roundTxt(n, x):
    if n < 0:
        return str(round(n, x))
    else:
        return ' ' + str(round(n, x))

def doSend(x, y, z, utime):
    if ardConn == 1:
        ser.write(chr(255).encode('latin_1') + 
                chr(int(x / 127)).encode() + chr(int(x) % 127).encode() +
                chr(int(y / 127)).encode() + chr(int(y) % 127).encode() +
                chr(int(z / 127)).encode() + chr(int(z) % 127).encode() +
                chr(int(utime / 127)).encode() + chr(int(utime) % 127).encode())

def sendSteppers(timeDelta):
    xStep = min(max(int(getSmoothedVal2(0) *(50*stepScale) + 150*stepScale), maxAngles[0][0] *1), maxAngles[0][1] * 1)
    yStep = min(max(int(getSmoothedVal2(1) *(50*stepScale) + 150*stepScale), maxAngles[0][0] *1), maxAngles[0][1] * 1)
    zStep = min(max(int(getSmoothedVal2(2) *(50*stepScale) + 150*stepScale), maxAngles[2][0]* 1), maxAngles[2][1] * 1)
    
    barLength = 20
    text = format("#" * int((xStep - maxAngles[0][0]) * barLength / (maxAngles[0][1] - maxAngles[0][0])) + "-" * (barLength - int((xStep - maxAngles[0][0]) * barLength / (maxAngles[0][1] - maxAngles[0][0])))) + ' X:' + roundTxt(getSmoothedVal2(0), 2) + '\t'
    text += format("#" * int((yStep - maxAngles[1][0]) * barLength / (maxAngles[1][1] - maxAngles[1][0])) + "-" * (barLength - int((yStep - maxAngles[1][0]) * barLength / (maxAngles[1][1] - maxAngles[1][0])))) + ' Y:' + roundTxt(getSmoothedVal2(1), 2) + '\t'
    text += format("#" * int((zStep - maxAngles[2][0]) * barLength / (maxAngles[2][1] - maxAngles[2][0])) + "-" * (barLength - int((zStep - maxAngles[2][0]) * barLength / (maxAngles[2][1] - maxAngles[2][0])))) + ' Z:' + roundTxt(getSmoothedVal2(2), 2) 
    text += " x" + str(timeDelta)
    print (text + '\r'),
    if ardConn == 1:
        ser.write(chr(255).encode('latin_1') + 
                  chr(int(xStep / 127)).encode() + chr(int(xStep) % 127).encode() +
                  chr(int(yStep / 127)).encode() + chr(int(yStep) % 127).encode() +
                  chr(int(zStep / 127)).encode() + chr(int(zStep) % 127).encode() +
                  chr(int(timeDelta / 127)).encode() + chr(int(timeDelta) % 127).encode())

### Connect to Arduino
ardConn = 0
port = '/dev/ttyUSB11' #for windows use COM1 or so
print ('Connecting to Arduino on Port \'' + port + '\'...')
try:
    ser = serial.Serial(port, 19200)
    print ("Success!")
    ardConn = 1
except:
    print ("Error connecting!")



#global vars
chFac = [1.0, 1.0, 1.0]
chCorr = [0.0, 0.0, 0.0]
chSmooth = [0, 0, 0]
chTar = [1, 2, 3]
chSmPt = [0, 0, 0]
csvType = 0
cnt = 0
waited = 0
x = 90.0
y = 90.0
z = 90.0
t = 0.0
tOffset = 0
currT = 0
lastT = 0
factor = 1
addRow = 0

cfg = configparser.ConfigParser()

#main program
repeat = 1
while repeat == 1:
    repeat = 0
    fn = input("Enter .gf-name (enter nothing to exit) ")
    if fn == '':
        sys.exit()
    if fn == 'test':
        repeat = 1
        if ardConn == 1:
            print ("Testing servos") 
            lol = 300 * stepScale / 2
            doSend(lol, lol, lol, 0)
            
            for i in range(1500):
                roflx = lol + math.sin(i / 10) * ((i / 1500) *(lol / 2))
                rofly = lol + math.cos(i / 10) * ((i / 1500) *(lol /2))
                doSend(roflx, rofly, lol, 10)
                time.sleep(0.01)
            time.sleep(0.5)
            doSend(lol, lol, lol, 300)
            time.sleep(1)
 
 
#reading .gf file
try:
    cfg.read(fn + '.gf')
except:
    print ("Error reading " + fn + '.gf')
    sys.exit()
    
gfData      = cfg.get('gf', 'csv')
csvType     = cfg.getint('gf', 'csvtype')
mp3         = cfg.get('gf', 'mp3')
skip        = cfg.getint('gf', 'skip') 
soundOffset = cfg.getfloat('gf', 'soundoff') 

chFac[0]    = cfg.getfloat('gf', 'ch1fac')
chCorr[0]   = cfg.getfloat('gf', 'ch1corr')
chSmooth[0] = cfg.getint('gf', 'ch1smooth')
damping[0]  = cfg.getfloat('gf', 'ch1damp')
chTar[0]    = cfg.getint('gf', 'ch1tar')
chFac[1]    = cfg.getfloat('gf', 'ch2fac')
chCorr[1]   = cfg.getfloat('gf', 'ch2corr')
chSmooth[1] = cfg.getint('gf', 'ch2smooth') * 5
damping[1]  = cfg.getfloat('gf', 'ch2damp')
chTar[1]    = cfg.getint('gf', 'ch2tar')
chFac[2]    = cfg.getfloat('gf', 'ch3fac')
chCorr[2]   = cfg.getfloat('gf', 'ch3corr')
chSmooth[2] = cfg.getint('gf', 'ch3smooth')
damping[2]  = cfg.getfloat('gf', 'ch3damp')
chTar[2]    = cfg.getint('gf', 'ch3tar')
print ('Opening data file \'' + gfData + '\' and mp3 file \'' + mp3 + '\'')




if ardConn == 1:
    print ("Wating for Arduino to be ready..."),
    sys.stdout.flush()
    #while ser.read() != 'A':
    #    time.sleep(0.001)
    print (" Alive.")

print ("Waiting for VLC..."),
sys.stdout.flush()
player = vlc.MediaPlayer(mp3)
player.play()
while (vlc.libvlc_media_player_get_length(player) == 0):
    time.sleep(0.001)
player.set_position((soundOffset + skip) / vlc.libvlc_media_player_get_length(player))  
print (" Done.")


if csvType == 1:
    addRow = 1
if csvType == 2:
    factor = 10

with open(gfData) as csvfile:
    delimiter = ';'
    if csvType == 1 or csvType == 3:
        delimiter = '\t'
    readCSV = csv.reader(csvfile, delimiter=delimiter)
    timeStart = int(round(time.time() * 1000)) - skip
    for row in readCSV:
        if cnt > 0:
            
            if csvType == 2:
                if tOffset == 0:
                    tOffset = int(1000*float(row[0].replace(',', '.')))
            timeElapsed = int(round(time.time() * 1000)) - timeStart 
            waited = 0
            
            lastT = currT
            if csvType == 1:
                currT = int(row[1].replace(',', '.'))
            
            if csvType == 2:
                currT = float(row[0].replace(',', '.')) * 1000
            
            if csvType == 3 or csvType == 4:
                currT = float(row[0]) * 1000
                
            while currT - tOffset > timeElapsed:
                waited = 1
                time.sleep(0.001)
                timeElapsed = int(round(time.time() * 1000)) - timeStart 
                if csvType == 1:
                    currT = int(row[1].replace(',', '.'))
                if csvType == 2:
                    currT = int(1000 * float(row[0].replace(',', '.'))) 
                if csvType == 3:
                    currT = int(1000 * float(row[0]))
                    
            if waited == 1:
                for i in range(3):
                    if chTar[i] == 1:
                        x = (float(row[i + 1 + addRow].replace(',', '.')) + chCorr[i]) * chFac[i]  * factor
                        dampers[0] += (x - dampers[0]) / damping[0]
                    if chTar[i] == 2:
                        y = (float(row[i + 1 + addRow].replace(',', '.')) + chCorr[i]) * chFac[i] * factor
                        dampers[1] += (y - dampers[1]) / damping[1]
                    if chTar[i] == 3:
                        z = (float(row[i + 1 + addRow].replace(',', '.')) + chCorr[i]) * chFac[i] * factor
                        dampers[2] += (z - dampers[2]) / damping[2]
                        
 
                sendSteppers(currT - lastT)
                sys.stdout.flush()
        else:
            if csvType == 1:
                tOffset = int(row[1].replace(',', '.'))
        cnt += 1

print ('\r\nDone.')
