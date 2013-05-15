def initializeprices(x):
    for (var i = 0; i < x.length; i++):
            r = x[i];
            r.elapsed_time = getelapsedtime(r);
            console.log(r);
            if (r instanceof Array && r[0].price == undefined):
                var temp_sum = 0;
                for (var j = 1; j < r.length; j++):
                    var leg = r[j];
                    if (leg instanceof Array):
                        temp_sum += parseFloat(leg[0].price.substring(1));
                    else:
                        temp_sum += parseFloat(leg.price.substring(1));
                temp_sum = temp_sum.toString();
                dot = temp_sum.indexOf(".");
                if (dot != -1 && dot == temp_sum.length - 2):
                    temp_sum = temp_sum + "0";
                r[0].price = "$" + temp_sum;

def comparebyprice(a, b):
    p1 = (a.price == undefined) ? a[0].price : a.price;
    p2 = (b.price == undefined) ? b[0].price : b.price;

    p1 = a[0].price if (a.price == undefined) else a.price
    p1 = b[0].price if (b.price == undefined) else b.price
    return p1.substring(1) - p2.substring(1);

def timetominutes(time):
        colon = time.index(":")
        hour = time[0, colon] * 1;
        minute = time[colon+1, colon+3] * 1;
        if (hour == 12):
            hour = 0;
        if ("PM" not in time):
            hour = (hour*1) + 12;
        return hour * 60 + (minute*1);

def comparebyarrival(a, b):
        c = (a.departure_time == undefined) ? a[0] : a;
        d = (b.departure_time == undefined) ? b[0] : b;
        a1 = timetominutes(c.departure_time);
        a2 = timetominutes(c.arrival_time);
        b1 = timetominutes(d.departure_time);
        b2 = timetominutes(d.arrival_time);
        if (a2 < a1):
            a2 = a2 + 24*60;
        if (b2 < b1):
            b2 = b2 + 24*60;
        return a2 - b2;

def comparebydeparture(a, b):
        c = (a.departure_time == undefined) ? a[0] : a;
        d = (b.departure_time == undefined) ? b[0] : b;
        return timetominutes(c.departure_time) - timetominutes(d.departure_time);

def comparebyelapsed(a, b):
        #return getelapsedtime(a) - getelapsedtime(b);
        return a.elapsed_time - b.elapsed_time;

def getelapsedtime(r):
        a1 = timetominutes(getrecordtime(r, true));
        a2 = timetominutes(getrecordtime(r, false));
        c1 = a2 - a1;
        if (c1 < 0):
            c1 = c1 + 24*60;
        return c1;

def getrecordtime(r, departure):
    if (r instanceof Array):
        if (r[0].departure == undefined):
            # multiple legs
            return (departure ? r[0].departure_time : r[0].arrival_time);
        else:
            # one leg
            return (departure ? r[0].departure_time : r[r.length-1].arrival_time);
    else:
        return (departure ? r.departure_time : r.arrival_time);

