class MoneyObserver() :

    def moneyUpdate(self, monies) :
        ''' provide a money delta '''
        pass

    def reset(self) :
        ''' clear data '''
        pass

class MoneySubject() :

    def __init__(self) :

        self.observers = []
    
    def attachObserver(self, ob) :
        self.observers.append(ob)

    def moneyNotify(self, monies) :
        for ob in self.observers :
            ob.moneyUpdate(monies)