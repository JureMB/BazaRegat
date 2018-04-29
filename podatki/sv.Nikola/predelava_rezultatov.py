def predelaj_rezultate(dat):
    """stolpci: mesto na regati, sailno, ime in priimek, subgroup, color, klub, plovi"""

    with open(dat, 'r', encoding='utf8') as f:
        data = f.readlines()

    sailno = []
    sailor = []
    spol = []
    club = []
    plovi = []
    i = 0
    for line in data[1:]:  # brez prve
        l = line.split("\t")  # razdelimo
        sailno.append(l[1])
        sailor.append(l[2])
        spol.append(l[3])
        club.append(l[5])
        plovi.append(l[6:-1])
        # print(sailno[i], '\t', sailor[i], '\t', spol[i], '\t', club[i], '\t', plovi[i])
        i += 1

    klub = []
    j = 0
    for s in club:
        s = s.replace('È', 'Č')
        klub.append(s.upper())

    spoli = []
    for s in spol:
        if 'Girl' in s:
            spoli.append('F')
        else:
            spoli.append('M')

    with open('nikola_jadralci.txt', 'w', encoding='utf8') as f:
        i = 0
        for sailor_i in sailor:
            f.write(sailor_i + '\t' + sailno[i] + '\t' + spoli[i] + '\t' + klub[i] + '\n')
            i += 1
    # print(plovi[0])
    st_plovov = len(plovi[0])
    print('Število plovov: ' + str(st_plovov))
    p = [[0 for i in range(len(plovi))] for j in range(st_plovov)]

    i = 0
    for line in plovi:
        for e in range(st_plovov):
            p[e][i] = line[e]
        i += 1

    # print(p)
    def is_number(s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    for plov in p:
        i = 0
        for tocka in plov:
            plov[i] = plov[i].replace('(', '')
            plov[i] = plov[i].replace(')', '')
            if not is_number(plov[i]):
                plov[i] = plov[i][4:]
            i += 1

    with open('nikola_plovi.txt', 'w', encoding='utf8') as f:
        i = 0
        for sailno_i in sailno:
            tocke = ''
            for plov in p:
                tocke += '\t' + plov[i]
            f.write(sailno_i + tocke + '\n')
            i += 1

    club = list(set(klub))
    with open('nikola_klubi.txt', 'w', encoding='utf8') as f:
        for club_i in club:
            f.write(club_i + '\n')

    return sailno, sailor, spoli, club, p

predelaj_rezultate("nikola.txt")