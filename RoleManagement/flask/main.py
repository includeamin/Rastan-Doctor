

b =[[0.234235,2.23252,2.235235],
 [2.235235,2.2352352,2.235235235]]






def update(a):
    for i in range(0, len(a)):
        for j in range(0, len(a[i])):
            a[i][j] = round(a[i][j], 2)
    return  a


logging.warning(update(b))