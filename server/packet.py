from enum import Enum

class MeasurementFunction(Enum):
    Voltage = 1
    Current = 2
    Resistance = 3
    UnImplemented = 4

class OvfStatus(Enum):
    NoOverFlow = 0
    OverFlow = 1


class Packet:
    def __init__(self, data):
        self.data = data;
        self.ovf = OvfStatus.OverFlow;

    def packetOK(self):
        if( self.data[-2] != 0xD or self.data[-1] != 0xA or len(self.data) != 11 ):
            return False
        return True

    def getDigits(self):
        dig = self.data[0:5];
        s = ""
        if( max(dig) > 10 ):
            #overflow
            self.ovf = OvfStatus.OverFlow;
        else:
            self.ovf = OvfStatus.NoOverFlow;
            for i in dig:
                if( i < 10 ):
                    s += str(i);
        return s

    
    def decodePacket(self):
        
        if not self.packetOK():
            #bad packet
            return None;
        
        s = self.getDigits();
        r = self.data[5:11]
        print "rest:", [hex(i) for i in r]

        rangeVal = r[0];
        modeVal = r[1];

        decimal = 0;
        mul = 1;
        if modeVal == 1: #DC voltage
            self.mode = MeasurementFunction.Voltage
            decimal = rangeVal
        elif modeVal == 3: #mV
            self.mode = MeasurementFunction.Voltage
            decimal = 3
            mul = 1./1000
        elif modeVal == 4: #Ohm
            self.mode = MeasurementFunction.Resistance
            decimal = (rangeVal+1)%3 + 1
            mul = 1000**((rangeVal+1)//3)
        else:
            self.mode = MeasurementFunction.UnImplemented
        
        if self.ovf == OvfStatus.NoOverFlow:
            val = float(s[:decimal] + "." + s[decimal:])
        else:
            val = 0;

        if r[3] & 0b100:
            val *= -1
        val *= mul

        self.value = val

        print self.value
        print self.mode
        print self.ovf
        return self.value