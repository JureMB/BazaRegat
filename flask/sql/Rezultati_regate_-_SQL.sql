-- Rezultati regate (Sv. Nikola)
-- pomozno
CREATE VIEW delni1 AS
SELECT rezultati_nikola_1plov.sailno, rezultati_nikola_1plov.ime, rezultati_nikola_1plov.spol, rezultati_nikola_1plov.leto_rojstva, rezultati_nikola_1plov.tocke_plov AS prvi, rezultati_nikola_2plov.tocke_plov AS drugi, rezultati_nikola_3plov.tocke_plov AS tretji, rezultati_nikola_4plov.tocke_plov AS četrti from rezultati_nikola_1plov
JOIN rezultati_nikola_2plov ON rezultati_nikola_1plov.sailno = rezultati_nikola_2plov.sailno
JOIN rezultati_nikola_3plov ON rezultati_nikola_1plov.sailno = rezultati_nikola_3plov.sailno
JOIN rezultati_nikola_4plov ON rezultati_nikola_1plov.sailno = rezultati_nikola_4plov.sailno;

-- za generacijo rezultatov, ^\\d+$ = :
SELECT *, (CASE WHEN prvi~E'^\\d+$' THEN prvi::integer ELSE 104 END + CASE WHEN drugi~E'^\\d+$' THEN drugi::integer ELSE 104 END + CASE WHEN tretji~E'^\\d+$' THEN tretji::integer ELSE 104 END + CASE WHEN četrti~E'^\\d+$' THEN četrti::integer ELSE 104 END) - greatest(CASE WHEN prvi~E'^\\d+$' THEN prvi::integer ELSE 104 END, CASE WHEN drugi~E'^\\d+$' THEN drugi::integer ELSE 104 END, CASE WHEN tretji~E'^\\d+$' THEN tretji::integer ELSE 104 END, CASE WHEN četrti~E'^\\d+$' THEN četrti::integer ELSE 104 END) AS net, (CASE WHEN prvi~E'^\\d+$' THEN prvi::integer ELSE 104 END + CASE WHEN drugi~E'^\\d+$' THEN drugi::integer ELSE 104 END + CASE WHEN tretji~E'^\\d+$' THEN tretji::integer ELSE 104 END + CASE WHEN četrti~E'^\\d+$' THEN četrti::integer ELSE 104 END) AS tot FROM delni1
ORDER BY net ASC, tot ASC; 

-- dodajanje stolpca s klubom preko tabele članstvo, za vsakega jadralca (sailno) vrnemo ime njegovega kluba

