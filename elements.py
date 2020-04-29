from datetime import datetime, timedelta
from tkinter.ttk import Frame, Button, Style, Label, Entry, Treeview, Checkbutton
from tkinter import Tk, RIGHT, LEFT, BOTH, RAISED,NO,W,X, IntVar
from moneyObserve import MoneyObserver, MoneySubject

class DateDisplay(Frame) :

    def __init__(self, parent) :

        super().__init__(parent)
        self.parent = parent
        self.initUI()
    
    def initUI(self) :

        self.l1 = Label(self, text="l1",font=("Ubuntu",25))
        self.l1.pack(side=LEFT)

        lbl = Label(self,text="-->", font=("Ubuntu",25))
        lbl.pack(side=LEFT)
        self.l2 = Label(self, text="l2",font=("Ubuntu",25))
        self.l2.pack(side=LEFT)

        self.pack()

    def setStartDate(self, date) :

        self.l1["text"] = date.strftime("%d/%m")
        self.l2["text"] = (date+timedelta(days=6)).strftime("%d/%m")

class IncomeEntry(Frame, MoneySubject) :

    def __init__(self, parent) :

        super().__init__(parent)
        MoneySubject.__init__(self)
        self.parent = parent
        self.initUI()

    def initUI(self) :

        self.entries = {}
        self.records = []
        titleFrame = Frame(self, borderwidth=1)
        titleFrame.pack(fill=BOTH, expand=True)

        lbl = Label(titleFrame, text="Incomes:",font=("Ubuntu",20))
        lbl.pack(side=LEFT)

        entryFrame = Frame(self,borderwidth=1)

        for data in [("Hours",3), ("Rate",5),("Desc",15)] :
            dataFrame = Frame(entryFrame, borderwidth=2)
            lbl = Label(dataFrame, text=data[0],font=("Ubuntu",10))
            lbl.pack()
            entry = Entry(dataFrame, width=data[1])
            entry.pack()
            self.entries[data[0]] = entry

            dataFrame.pack(side=LEFT)

        okButton = Button(entryFrame,text="Submit",command=self.submitIncome)
        okButton.pack(side=LEFT)
        entryFrame.pack(fill=BOTH,expand=True)

        self.incomeList = Treeview(self,height=3)
        columns = ("Hours","Rate", "Desc", "Total")
        self.incomeList["columns"] = columns
        self.incomeList.column("#0", width=0, minwidth=0, stretch=NO)
        for field in columns :
        
            self.incomeList.column(field, width=100, stretch=NO)
            self.incomeList.heading(field, text=field,anchor=W)
        
        self.incomeList.pack(side=LEFT)

        self.pack(fill=BOTH, expand=False)

        self.incomeList.bind("<Delete>", self.keydown)

    def keydown(self, e) :
        item = self.incomeList.selection()
        if item != () :
            values = self.incomeList.item(item)['values']
            hours = float(values[0])
            rate = float(values[1])
            desc = str(values[2])
            amt = hours*rate
            self.moneyNotify({"income":-amt})
            self.incomeList.delete(item)
            self.records.remove({"hours":hours,"rate":rate,"desc":desc})

    def _emitIncome(self, hours,rate,desc) :
        values = (hours,rate,desc,f"${hours*rate:.2f}")
        self.incomeList.insert("", "end", text="", values=values)
        self.records.append({"hours":hours,"rate":rate,"desc":desc})
        self.moneyNotify({"income":hours*rate})

    def submitIncome(self) :
        # consume input in entry boxes and store in tree
        hours = float(self.entries["Hours"].get())
        rate = float(self.entries["Rate"].get())
        desc = self.entries["Desc"].get()
        self._emitIncome(hours,rate,desc)
        for entry in self.entries.values() :
            entry.delete(0, 'end')

    def clear(self) :
        
        for child in self.incomeList.get_children() :
            self.incomeList.delete(child)
        for income in self.records :
            self.moneyNotify({"income":-income["hours"]*income["rate"]})
        
        self.records = []

    def export(self) :
        return self.records

    def restore(self, incomes, startDate) :
        self.clear()
        for income in incomes :
            self._emitIncome(income["hours"],income["rate"],income["desc"])


class IncomeSummary(Frame,MoneyObserver) :

    def __init__(self, parent) :

        super().__init__(parent)
        self.initUI()

        self.income = 0
        self.subscription = 0

    def initUI(self) :

        self.incomelbl = Label(self, text="Income: $0",font=("Ubuntu",18))
        self.incomelbl.pack()
        self.availlbl = Label(self, text="Available: $0",font=("Ubuntu",18))
        self.availlbl.pack()

        self.pack()
    
    def moneyUpdate(self, monies) :
        self.income += monies.get("income", 0)
        self.subscription += monies.get("subscription", 0)
        self.incomelbl["text"] = f"Income: ${self.income:.2f}"
        self.availlbl["text"] = f"Available: ${self.income-self.subscription:.2f}"

class SubscriptionEntry(Frame,MoneySubject) :

    def __init__(self, parent) :

        super().__init__(parent)
        MoneySubject.__init__(self)
        self.initUI()

    def initUI(self) :

        titleFrame = Frame(self, borderwidth=1)
        titleFrame.pack(fill=BOTH, expand=True)
        titlelbl = Label(titleFrame, text="Subscriptions:",font=("Ubuntu",16))
        titlelbl.pack(side=LEFT)

        self.record = {}
        self.subs = {"Spotify":(1.5,None),"Phone":(5,None),"Dreamhost":(4.7,None)}
        for key in self.subs :
            self.record[key] = 0
        
        self._generateList()
        self.pack(fill=BOTH, expand=False)
    
    def _destroyList(self) :
        for frame in self.uiList :
            frame.destroy()
        self.totallbl.destroy()
        self.boxFrame.destroy()

    def _generateList(self) :

        self.boxFrame = Frame(self,borderwidth=1)
        self.uiList = []

        for entry in self.subs :
            entryFrame = Frame(self.boxFrame,borderwidth=1)
            var = IntVar()
            var.set(1*(self.record.get(entry,0) > 0))
            button = Checkbutton(entryFrame, variable=var,command=self.update)
            button.pack(side=LEFT)

            self.subs[entry] = (self.subs[entry][0], var)

            lbl = Label(entryFrame,text=entry,font=("Ubuntu",10))
            lbl.pack(side=LEFT)
            amtlbl = Label(entryFrame,text=f"${self.subs[entry][0]}",font=("Ubuntu",10))
            amtlbl.pack(side=RIGHT)
            entryFrame.pack(fill=X)
            self.uiList.append(entryFrame)

        self.totallbl = Label(self.boxFrame, text="$0",font=("Ubuntu",14))
        self.totallbl.pack(side=RIGHT)
        self.boxFrame.pack(side=LEFT,fill=BOTH)

    def update(self) :
        sum = 0
        delta = 0
        for key, value in self.subs.items() :
            state = value[1].get()
            sum += state*value[0]
            
            if state == 0 and self.record[key] > 0 :
                delta -= value[0]
            elif state == 1 and self.record[key] == 0 :
                delta += value[0]
            self.record[key] = state*value[0]

        self.moneyNotify({"subscription":delta})

        self.totallbl["text"] = f"${sum}"
    
    def export(self) :
        export = {}
        for key, value in self.record.items() :
            export[key] = (self.subs[key][0], value > 0)
        return export

    def restore(self, subs, startDate) :
        self.subs = {}
        self.record = {}
        for key in self.subs :
            self.moneyNotify({"subscription": self.record[key]})
        self._destroyList()
        for key, data in subs.items() :
            self.subs[key] = (data[0], None)
            self.record[key] = data[0]*data[1]
            self.moneyNotify({"subscription": self.record[key]})
        self._generateList()
        self.update()
        # NOTE: functions may need reorganising incl. e.g. a clear() function

class DebitList(Frame,MoneySubject,MoneyObserver) :

    def __init__(self, parent) :

        super().__init__(parent)
        MoneySubject.__init__(self)
        MoneyObserver.__init__(self)
        self.initUI()
    
    def initUI(self) :

        self.records = []

        self.debitList = Treeview(self,height=15)
        columns = ("Amount", "Desc")
        self.debitList["columns"] = columns
        self.debitList.column("#0", width=70, minwidth=70, stretch=NO)
        self.debitList.column("Amount", width=70, stretch=NO)
        self.debitList.column("Desc", width=250, stretch=NO)
        self.debitList.heading("#0", text="Date",anchor=W)
        for field in columns :
            self.debitList.heading(field, text=field,anchor=W)
        
        self.debitList.pack(side=LEFT)
        self.pack()
    
        self.debitList.bind("<Delete>", self.keydown)

    def keydown(self, e) :
        item = self.debitList.selection()
        parent = self.debitList.parent(item)
        if item != () and parent != '':
            values = self.debitList.item(item)['values']
            amount = float(values[0][1:])
            self.moneyNotify({"debit":-amount})
            self.debitList.delete(item)
            self.records.remove({"debit":amount,"desc":str(values[1]),"date":parent})

    def clear(self) :
        for debit in self.records :
            debit["debit"] *= -1
            self.moneyNotify(debit)
        self.records = []
        for child in self.debitList.get_children() :
            self.debitList.delete(child)
            
    def export(self) :
        
        return self.records

    def restore(self,debits, startDate) :

        self.clear()
        self.setStartDate(startDate)
        dateTable = {}
        for d in range(7) :
            day = startDate+timedelta(days=d)
            dateStr = day.strftime("%d/%m")
            dateTable[dateStr] = day
        for debit in debits :
            debit["date"] = dateTable[debit["date"]]
            self.moneyUpdate(debit)
            self.moneyNotify(debit)

    def moneyUpdate(self, monies) :
        if "debit" in monies :
            dateStr = monies["date"].strftime("%d/%m")

            toSave = monies
            toSave["date"] = dateStr
            self.records.append(toSave)

            values = (f"${monies['debit']}",monies["desc"])
            self.debitList.insert(dateStr,"end",text="",values=values)

    def setStartDate(self,startDate) :

        for d in range(7) :
            day = startDate+timedelta(days=d)
            dateStr = day.strftime("%d/%m")
            self.debitList.insert("", "end", id=dateStr, text=dateStr, values=("",""))

class DebitEntry(Frame,MoneySubject) :

    def __init__(self, parent) :

        super().__init__(parent)
        MoneySubject.__init__(self)
        self.initUI()
    
    def initUI(self) :

        self.entries = {}
        self.date = datetime.now()
        titleFrame = Frame(self, borderwidth=1)
        titleFrame.pack(fill=BOTH, expand=True)

        lbl = Label(titleFrame, text="Debits:",font=("Ubuntu",20))
        lbl.pack(side=LEFT)

        dateFrame = Frame(self,borderwidth=1)
        lButton = Button(dateFrame,text="<-",command=self.backDay)
        lButton.pack(side=LEFT)
        self.dateLbl = Label(dateFrame,text=self.date.strftime("%d/%m"),font=("Ubuntu",12))
        self.dateLbl.pack(side=LEFT)
        rButton = Button(dateFrame,text="->",command=self.forwardDay)
        rButton.pack(side=LEFT)
        dateFrame.pack(fill=BOTH,expand=True)

        entryFrame = Frame(self,borderwidth=1)

        for data in [("Amount",5), ("Desc",20)] :
            dataFrame = Frame(entryFrame, borderwidth=2)
            lbl = Label(dataFrame, text=data[0],font=("Ubuntu",10))
            lbl.pack()
            entry = Entry(dataFrame, width=data[1])
            entry.pack()
            self.entries[data[0]] = entry

            dataFrame.pack(side=LEFT)

        okButton = Button(entryFrame,text="Submit",command=self.submitDebit)
        okButton.pack(side=LEFT)
        entryFrame.pack(fill=BOTH,expand=True)
        self.pack(fill=BOTH, expand=False)
    
    def backDay(self) :
        
        if self.date - self.startDate >= timedelta(days=0) :
            self.date -= timedelta(days=1)

        self.dateLbl["text"] = self.date.strftime("%d/%m")
    def forwardDay(self) :
        
        if self.date - self.startDate <= timedelta(days=5) :
            self.date += timedelta(days=1)

        self.dateLbl["text"] = self.date.strftime("%d/%m")
    
    def setStartDate(self, startDate) :
        self.startDate = startDate
        self.dateLbl["text"] = self.date.strftime("%d/%m")

    def submitDebit(self) :

        amt = float(self.entries["Amount"].get())
        desc = self.entries["Desc"].get()
        self.moneyNotify({"debit":amt,"desc":desc,"date":self.date})

        for entry in self.entries.values() :
            entry.delete(0, 'end')

class TotalDisplay(Frame,MoneyObserver) :

    def __init__(self, parent) :

        super().__init__(parent)
        MoneyObserver.__init__(self)
        self.initUI()

        self.available = 0
        self.spent = 0
    
    def initUI(self) :

        titleFrame = Frame(self, borderwidth=1)
        
        lbl = Label(titleFrame, text="Remainder: ",font=("Ubuntu",14))
        lbl.pack(side=LEFT)
        self.remainLbl = Label(titleFrame,text="$0",font=("Ubuntu",14))
        self.remainLbl.pack(side=LEFT)
        titleFrame.pack(fill=BOTH, expand=True)

        percentsFrame = Frame(self,borderwidth=1)
        self.spentLbl = Label(percentsFrame,text="",font=("Ubuntu",12))
        self.spentLbl.pack()
        self.savedLbl = Label(percentsFrame,text="",font=("Ubuntu",12))
        self.savedLbl.pack()
        percentsFrame.pack()
        self.pack()
    
    def moneyUpdate(self,monies) :
        if "debit" in monies :
            self.spent += monies["debit"]
        if "income" in monies :
            self.available += monies["income"]
        if "subscription" in monies :
            self.available -= monies["subscription"]
        self.updateText()
    
    def updateText(self) :
        self.remainLbl["text"] = f"${(self.available-self.spent):.2f}"
        if self.available != 0 :
            self.spentLbl["text"] = f"{self.spent/self.available*100:.0f}% spent"
            self.savedLbl["text"] = f"{(1-self.spent/self.available)*100:.0f}% saved"
        else :
            self.spentLbl["text"] = ""
            self.savedLbl["text"] = ""