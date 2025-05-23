from collections import UserDict, UserList, UserString


class LookUpKeyDict(UserDict):
    def lookup_key(self, value):
        keys = []
        for (k, v) in self.data.items():
            if v == value:
                keys.append(k)
        return keys
    
d = LookUpKeyDict()
d['a'] = 1
d['b'] = 2
d['c'] = 1

print(d.lookup_key(0))
print(d.lookup_key(1))
print(d.lookup_key(2))

class AmountPaymentList(UserList):

    def amount_payment(self):
        s = 0
        for a in self.data:
            if a > 0:
                s += a
        return s
    
pl = AmountPaymentList([1, -1, 2])
print(pl.amount_payment())

class NumberString(UserString):
    def number_count(self):
        cnt = 0
        for c in self.data:
            if c.isdigit():
                cnt += 1
        return cnt
    
nstr = NumberString('hjhhfkfds')
print(nstr.number_count())
nstr = NumberString('hjhhf9kf0ds')
print(nstr.number_count())