'''from utilites import card_template_parser
s1 = "<aaa >$login$ $pass$</zomg> $uid$<aa$aaa $lol pass$>"
print card_template_parser(s1, {"login":"ylt", "pass":"pswd", "uid":"3453432"})

print s1'''
import time
#zlst = range(10000)
a = time.time()

d = 0
for i in range(1000):
    zlst = range(100000)
    for zv in zlst:
        d= d + zv
print time.time() - a

#zlst = range(10000)
a = time.time()
d = 0
for i in range(1000):
    zlst = range(100000)
    for zi in range(len(zlst)):
        d = d+ zlst.pop()
print time.time() - a        
zlst = range(10000)
a = time.time()
d = 0
for i in range(1000):
    zlst = range(100000)
    try:
        while True:
            d = d+ zlst.pop()
    except:
        pass
print time.time() - a