from tkinter import Tk,Label, Button, Entry, Frame, LEFT, RIGHT
from datetime import datetime
from elements import IncomeEntry, DateDisplay, IncomeSummary, SubscriptionEntry, DebitList, DebitEntry, TotalDisplay, MoneyGraph
from environment import MoneyIO, TimeManager

class App(Tk) :

    def __init__(self) :
        super().__init__()
        self.initUI()

    def initUI(self) :

        self.fileManager = MoneyIO()

        leftFrame = Frame(self, borderwidth=1)
        dateDisplay = DateDisplay(leftFrame)
        incomeEntry = IncomeEntry(leftFrame)
        subscriptionEntry = SubscriptionEntry(leftFrame)
        debitEntry = DebitEntry(leftFrame)
        leftFrame.pack(side=LEFT)

        rightFrame = Frame(self,borderwidth=1)
        incomeSummary = IncomeSummary(rightFrame)
        debitList = DebitList(rightFrame)
        totalDisplay = TotalDisplay(rightFrame)
        moneyGraph = MoneyGraph(rightFrame)
        rightFrame.pack(side=RIGHT)

        incomeEntry.attachObserver(incomeSummary)
        subscriptionEntry.attachObserver(incomeSummary)
        debitEntry.attachObserver(debitList)

        incomeEntry.attachObserver(totalDisplay)
        subscriptionEntry.attachObserver(totalDisplay)
        debitEntry.attachObserver(totalDisplay)
        debitList.attachObserver(totalDisplay)

        timeManager = TimeManager()
        self.lastSunday = timeManager.getRecentWeekStart()
        dateDisplay.setStartDate(self.lastSunday)
        debitList.setStartDate(self.lastSunday)
        debitEntry.setStartDate(self.lastSunday)

        for src in [(incomeEntry,"incomes"),(subscriptionEntry,"subscriptions"),(debitList,"debits")] :
            self.fileManager.setDataSource(src[0],src[1])
            
        self.fileManager.setGraph(moneyGraph)
        self.fileManager.loadData(self.lastSunday)

    def mainloop(self) :
        super().mainloop()
        self.fileManager.saveData(self.lastSunday)

def main() :
    app = App()
    app.title("Budget")
    app.mainloop()

if __name__ == '__main__':
    main()