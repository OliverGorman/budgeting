from datetime import datetime, timedelta
import os
import json

class MoneyIO() :
    # TODO: change to specifying the type of each data source for more robust storage
    def __init__(self) :

        self.sources = {}
        self.dateFormat = "%Y%m%d"

    def setDataSource(self, source, dataType) :
        self.sources[dataType] = source

    def saveData(self, startDate) :
        dateStr = startDate.strftime(self.dateFormat)
        jsonData = {"date": dateStr}
        
        for name,source in self.sources.items() :
            jsonData[name] = source.export()

        with open(f"{dateStr}.json","w") as f :
            json.dump(jsonData,f)

    def loadData(self, startDate) :
        
        dateStr = startDate.strftime(self.dateFormat)
        path = f"{dateStr}.json"
        if not os.path.exists(path) :
            return

        with open(path,"r") as f :
            data = json.load(f)
            
            data.pop("date")
            for key,value in data.items() :
                self.sources[key].restore(value,startDate)
        
class TimeManager() :
    
    def __init(self) :
        pass

    def getRecentWeekStart(self) :
        return datetime.now()-timedelta(datetime.now().weekday())