from datetime import datetime, timedelta
import os
import json

class MoneyIO() :
    def __init__(self) :

        self.sources = {}
        self.dateFormat = "%Y%m%d"

        if not os.path.exists("history") :
            os.mkdir("history")

    def setDataSource(self, source, dataType) :
        self.sources[dataType] = source

    def saveData(self, startDate) :
        dateStr = startDate.strftime(self.dateFormat)
        jsonData = {"date": dateStr}
        
        for name,source in self.sources.items() :
            jsonData[name] = source.export()

        with open(f"history/{dateStr}.json","w") as f :
            json.dump(jsonData,f)

    def loadData(self, startDate) :
        
        dateStr = startDate.strftime(self.dateFormat)
        path = f"history/{dateStr}.json"
        if not os.path.exists(path) :
            return

        with open(path,"r") as f :
            data = json.load(f)
            
            data.pop("date")
            for key,value in data.items() :
                self.sources[key].restore(value,startDate)
        
        self.graph.setData(self.getRecentRemainders(startDate, 5))
    
    def setGraph(self, graphOb) :
        self.graph = graphOb
    
    def getRecentRemainders(self, startDate, numWeeks) :

        remainders = []

        for w in range(numWeeks) :
            date = startDate-timedelta(weeks=w)
            path = f"history/{date.strftime(self.dateFormat)}.json"
            if not os.path.exists(path) :
                break

            with open(path,"r") as f :
                data = json.load(f)
                remainders.append(( (date+timedelta(days=6)).strftime("%d/%m"), MoneyIO.getRemainder(data) ))
        
        return remainders

    def getRemainder(data) :

        total = 0
        for i in data["incomes"] :
            total += i["hours"]*i["rate"]
        for s in data["subscriptions"].values() :
            total -= s[0]*s[1]
        for d in data["debits"] :
            total -= d["debit"]
        
        return total
class TimeManager() :
    
    def __init(self) :
        pass

    def getRecentWeekStart(self) :
        return datetime.now()-timedelta(datetime.now().weekday())