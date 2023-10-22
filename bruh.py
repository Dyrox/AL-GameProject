def expression(n):
    
    
     return (7*n+12)/(2*n+3)

sum = []

for i in range(-100,1000099):
    
    ok = expression(i)
    print(i)
    # print(i,ok)
    if ok.is_integer():
        print(ok)
        sum +=[i,ok]

print(sum)

