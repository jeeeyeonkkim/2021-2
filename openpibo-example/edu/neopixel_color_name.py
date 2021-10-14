import os, sys, time

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utils.config import Config as cfg

sys.path.append(cfg.OPENPIBO_PATH + '/edu')
from pibo import Edu_Pibo

def color_name_test():
    pibo = Edu_Pibo()
    ret=pibo.eye_on('aqua', 'purple')
    print(ret)
    time.sleep(1)
    
    ret2=pibo.eye_on('pink')
    print(ret2)
    time.sleep(1)
    pibo.eye_off()

if __name__ == "__main__":
    color_name_test()
'''
    # [Neopixel] - LED ON
    def eye_on(self, *color):
        if len(color) == 0:
            return self.return_msg(False, "Argument error", "RGB or Color is required", None)
        try:
            if self.isAlpha(*color) == False:
                for i in color:
                    if i < 0 or i > 255:
                        return self.return_msg(False, "Range error", "RGB value should be 0~255", None)
                if len(color) == 3:
                    cmd = "#20:{}!".format(",".join(str(p) for p in color))
                elif len(color) == 6:
                    cmd = "#23:{}!".format(",".join(str(p) for p in color))
                else:
                    return self.return_msg(False, "Syntax error", "Only 3 or 6 values can be entered", None)
            else:
                if len(color) == 1:
                    color = color[-1].lower()
                    if color not in self.colordb.keys():
                        return self.return_msg(False, "NotFound error", "{} does not exist in the colordb".format(color), None)
                    else:
                        color = self.colordb[color]
                        cmd = "#20:{}!".format(",".join(str(p) for p in color))
                elif len(color) == 2:
                    l_color, r_color = color[0].lower(), color[1].lower()
                    if l_color in self.colordb.keys() and r_color in self.colordb.keys():
                        l_color = self.colordb[l_color]
                        r_color = self.colordb[r_color]
                        color = l_color + r_color
                        cmd = "#23:{}!".format(",".join(str(p) for p in color))
                    else:
                        if l_color not in self.colordb.keys():
                            return self.return_msg(False, "NotFound error", "{} does not exist in the colordb".format(color[0]), None)
                        return self.return_msg(False, "NotFound error", "{} does not exist in the colordb".format(color[1]), None)
                else:
                    return self.return_msg(False, "Syntax error", "Only 2 colors can be entered", None)
            if self.check:
                self.que.put(cmd)
            else:
                self.device.send_raw(cmd)
            return self.return_msg(True, "Success", "Success", None)
        except Exception as e:
            return self.return_msg(False, "Exception error", e, None)


    # [Neopixel] - LED OFF
    def eye_off(self):
        try:
            cmd = "#20:0,0,0!"
            if self.check:
                self.que.put(cmd)
            else:
                self.device.send_raw(cmd)
            return self.return_msg(True, "Success", "Success", None)
        except Exception as e:
            return self.return_msg(False, "Exception error", e, None)
'''
