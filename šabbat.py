import wx, urllib3, threading
from wx import adv

def get_sabbat(geotag: int = 281184, shabat_min: int = 50, d = None, m = None, y = None):
    if geotag == 0:
        geotag = 281184
    if d and m and y:
        raw_data = urllib3.PoolManager().request('GET',f'https://www.hebcal.com/shabbat/?cfg=json&geonameid={geotag}&m={shabat_min}&gy={y}&gm={m}&gd={d}').data.decode()
    else:
        raw_data = urllib3.PoolManager().request('GET',f'https://www.hebcal.com/shabbat/?cfg=json&geonameid={geotag}&m={shabat_min}').data.decode()
    data =[i for i in  eval(raw_data)['items'] if i["category"] == "havdalah" or i["category"] == "candles"]
    return [data[0]['title'],data[-1]['title']]

def get_in(geotag: int = 281184, shabat_min: int = 72, d = None, m = None, y = None):
    return get_sabbat(geotag, shabat_min, d, m, y)[0][get_sabbat()[0].find(r":")+2:]

def get_out(geotag: int = 281184, shabat_min: int = 72, d = None, m = None, y = None):
    return get_sabbat(geotag, shabat_min, d, m, y)[-1][get_sabbat(geotag, shabat_min, d, m, y)[-1].find(r":")+2:]

def convert_time(time: str):
    if eval(time.split(":")[0]) > 12 or time.find("m") < 0:
        return time
    if time.find("am") > -1:
        return time.split("am")[0]
    time = time.split("pm")[0]
    time = str(eval(time.split(":")[0])+12) + ":" + time.split(":")[1]
    return time

cities = {"מודיעין":282926,"מודיעין־מכבים־רעות":282926,"תל־אביב–יפו":293397,"ירושלים":281184,"חיפה":294801,"בחר עיר":0}
cit = sorted(list(cities.keys()))


class dater(adv.DatePickerCtrl):
    def __init__(self, parent, dt=wx.DateTime.Now(), style=adv.DP_DROPDOWN):
        super().__init__(parent, dt=dt, style=style)
        

class Panel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.Sizer = wx.GridSizer(3, 2, wx.Size(50,50))
        self.Sizer.Add(wx.StaticText(self,label="זמן כניסת השבת:\t"))
        self.s_in = wx.TextCtrl(self)
        self.s_in.Value = convert_time(get_in())
        self.s_in.SetEditable(False)
        self.Sizer.Add(self.s_in)
        self.Sizer.Add(wx.StaticText(self,label="זמן יציאת השבת:\t"))
        self.s_out = wx.TextCtrl(self)
        self.s_out.SetEditable(False)
        self.s_out.Value = convert_time(get_out())
        self.Sizer.Add(self.s_out)
        self.city = wx.ComboBox(self,choices = cit, value = "בחר עיר")
        self.city.Bind(wx.EVT_COMBOBOX_CLOSEUP,self.choose)
        self.city.Bind(wx.EVT_KEY_DOWN, self.choose_enter)
        self.Sizer.Add(self.city)
        self.date = dater(self)
        self.date.Bind(adv.EVT_DATE_CHANGED, self.date_change)
        self.Sizer.Add(self.date)
        self.dy , self.dm , self.dd = str(self.date.Value).split(" ")[0].split("/")[2] , str(self.date.Value).split(" ")[0].split("/")[1] , str(self.date.Value).split(" ")[0].split("/")[0]
        
    def choose(self, event: wx.Event):
        self.set_values()
        event.Skip()
    
    def choose_enter(self, event: wx.KeyEvent):
        self.set_values()
        event.Skip()
        
    def date_change(self, event: adv.DateEvent):
        self.dy , self.dm , self.dd = str(self.date.Value).split(" ")[0].split("/")[2] , str(self.date.Value).split(" ")[0].split("/")[1] , str(self.date.Value).split(" ")[0].split("/")[0]
        self.set_values()
        event.Skip()
        
    def set_values(self):
        self.s_in.Value = convert_time(get_in(cities[self.city.Value],d = self.dd, y = self.dy , m = self.dm))
        self.s_out.Value = convert_time(get_out(cities[self.city.Value],d = self.dd, y = self.dy , m = self.dm))
        
class Frame(wx.Frame):
    def __init__(self, parent, title=""):
        super().__init__(parent, title=title)
        self.panel = Panel(self)
        
class App(wx.App):
    def OnInit(self):
        self.frame = Frame(None, "שבת")
        self.frame.Show()
        return True
    
if __name__ == "__main__":
    app = App()
    app.MainLoop()