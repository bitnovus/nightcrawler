def comparebyprice(a, b):
    p1 = a[0].price if (a.price == undefined) else a.price
    p1 = b[0].price if (b.price == undefined) else b.price
    return p1[:1] - p2[:1]

def comparebyarrival(a, b):
        c = a[0] if (a.departure_time == None) else a
        d = b[0] if (b.departure_time == None) else b

        a1 = timetominutes(c.departure_time)
        a2 = timetominutes(c.arrival_time)
        b1 = timetominutes(d.departure_time)
        b2 = timetominutes(d.arrival_time)
        if (a2 < a1):
            a2 = a2 + 24*60
        if (b2 < b1):
            b2 = b2 + 24*60
        return a2 - b2

def comparebydeparture(a, b):
        c = a[0] if (a.departure_time == None) else a
        d = b[0] if (b.departure_time == None) else b
        return timetominutes(c.departure_time) - timetominutes(d.departure_time)

def comparebyelapsed(a, b):
        #return getelapsedtime(a) - getelapsedtime(b);
        return a.elapsed_time - b.elapsed_time

def timetominutes(time):
        colon = time.index(":")
        hour = time[0, colon] * 1
        minute = time[colon+1, colon+3] * 1
        if (hour == 12):
            hour = 0
        if ("PM" not in time):
            hour = (hour*1) + 12
        return hour * 60 + (minute*1)

def getelapsedtime(r):
        a1 = timetominutes(getrecordtime(r, True))
        a2 = timetominutes(getrecordtime(r, False))
        c1 = a2 - a1
        if (c1 < 0):
            c1 = c1 + 24*60
        return c1

def getrecordtime(r, departure):
    if (type(r) is list):
        if (r[0].departure == None):
            # multiple legs
            return (r[0].departure_time if departure else r[0].arrival_time)
        else:
            # one leg
            return (r[0].departure_time if departure else r[r.length-1].arrival_time)
    else:
        return (r.departure_time if departure else r.arrival_time)

def initprices(x):
    for i in range(0, len(x)):
            r = x[i]
            r.elapsed_time = getelapsedtime(r);
            if (type(r) is list and r[0].price is None):
                temp_sum = 0
                for j in range(1, len(r)):
                    leg = r[j]
                    if (type(leg) is list):
                        temp_sum += float(leg[0].price[:1])
                    else:
                        temp_sum += float(leg.price[:1])
                temp_sum = str(temp_sum)
                if ("." in temp_sum):
                    dot = temp_sum.index(".")
                    if (len(temp_sum) - 2) == dot:
                        temp_sum = temp_sum + "0"
                r[0].price = "$" + temp_sum

