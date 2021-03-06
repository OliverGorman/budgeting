from datetime import datetime, timedelta
import os
import json

class MoneyIO() :
    def __init__(self) :

        self.sources = {}
        self.dateFormat = "%Y%m%d"
        self.currentStartDate = None

        if not os.path.exists("history") :
            os.mkdir("history")

    def setDataSource(self, source, dataType) :
        ''' source: object with export() (to json) method, such as a UI element.
            datatype: "subscriptions", "incomes" or "debits" 
            Note that there should only be one of each type.'''
        self.sources[dataType] = source

    def saveData(self) :
        ''' save data from all sources under the current date '''

        dateStr = self.currentStartDate.strftime(self.dateFormat)
        jsonData = {"date": dateStr}
        
        for name,source in self.sources.items() :
            jsonData[name] = source.export()

        with open(f"history/{dateStr}.json","w") as f :
            json.dump(jsonData,f,separators=(',', ':'))

    def loadData(self, startDate) :
        '''load data from file and insert into data sources'''

        self.currentStartDate = startDate
        self.graph.setData(self.getRecentRemainders(8))

        dateStr = startDate.strftime(self.dateFormat)
        path = f"history/{dateStr}.json"
        if not os.path.exists(path) :
            return

        with open(path,"r") as f :
            data = json.load(f)
            
            data.pop("date")
            for key,value in data.items() :
                self.sources[key].restore(value,startDate)
        
    def setGraph(self, graphOb) :
        self.graph = graphOb
    
    def getRecentRemainders(self, numWeeks) :
        ''' get the most recent numWeeks savings amounts '''

        remainders = []

        for w in range(numWeeks, 0, -1) :
            date = self.currentStartDate-timedelta(weeks=w)
            path = f"history/{date.strftime(self.dateFormat)}.json"
            if not os.path.exists(path) :
                # don't have data back this far
                continue

            with open(path,"r") as f :
                data = json.load(f)
                remainders.append(( (date+timedelta(days=6)).strftime("%d/%m"), MoneyIO.GetRemainder(data) ))
        
        return remainders

    def getFileDates(self) :
        dates = []
        for f in os.listdir("history") :
            if f[-5:] == ".json" and len(f) == len("YYYYMMDD.json") :
                dates.append(datetime.strptime(f[:-5], self.dateFormat))
        
        return sorted(dates)

    @classmethod
    def GetRemainder(cls, data) :
        '''calculate the remaining money as incomes - subscriptions - debits'''
        total = 0
        for i in data["incomes"] :
            total += i["hours"]*i["rate"]
        for s in data["subscriptions"].values() :
            total -= s[0]*s[1]
        for d in data["debits"] :
            total -= d["debit"]
        
        return total
class TimeManager() :
    
    def __init__(self) :
        pass

    def getRecentWeekStart(self) :
        return datetime.now()-timedelta(days=datetime.now().weekday())
