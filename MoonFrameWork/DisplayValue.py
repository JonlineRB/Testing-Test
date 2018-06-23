class DisplayValue(Object):
    maxval = 0.0
    valuesum = 0.0
    minval = 0.0
    firstvalue = true
    avrgcount = 0
    unit = None

    def __init__(self, unit):
        self.unit = unit

    def aggregate(self, value):
        if self.maxval < value:
            self.maxval = value
        if self.firstvalue:
            self.minval = value
            self.firstvalue = False
        elif self.minval > value:
            self.minval = value
        self.valuesum += value
        self.avrgcount += 1

    def getavrg(self):
        try:
            return self.valuesum / float(self.avrgcount)
        except ArithmeticError:
            return 0

    def tostring(self):
        return ('\nMAX: ' + str(self.maxval) + self.unit +
                '\nAVARAGE: ' + str(self.getavrg()) + self.unit +
                '\nMIN: ' + str(self.minval) + self.unit)
