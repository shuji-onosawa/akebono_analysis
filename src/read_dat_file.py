with open('y1990.dat', 'r') as f:
    lines = f.readlines()
    data = [line.strip().split() for line in lines]

for i in range(len(data)):
    if data[i][0] == '900211':
        print('---')
        print(data[i][1])
        logNH = float(data[i][26])
        logNHe = float(data[i][27])
        logNO = float(data[i][29])
        print('H+ density: '+str(1e-6*10**logNH)+' [cm^-3]')
        print('He+ density: '+str(1e-6*10**logNHe)+' [cm^-3]')
        print('O+ density: '+str(1e-6*10**logNO)+' [cm^-3]')
        total = 10**logNH + 10**logNHe + 10**logNO
        print('ratio: H+ = '+str(10**logNH/total)+', He+ = '+str(10**logNHe/total)+', O+ = '+str(10**logNO/total))
        print('---')