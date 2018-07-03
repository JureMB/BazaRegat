CREATE TEMPORARY TABLE klubi_plovi AS
SELECT klub.ime AS ime_kluba, idtekmovalec, plov_idplov FROM klub JOIN clanstvo ON klub.idklub = clanstvo.klub_idklub JOIN tekmovalec ON clanstvo.tekmovalec_idtekmovalec = tekmovalec.idtekmovalec JOIN tocke_plovi ON tocke_plovi.tekmovalec_idtekmovalec = tekmovalec.idtekmovalec

-- število plovov
SELECT count(*) FROM plov WHERE regata_idregata = {}

-- tukaj bo zanka po vseh plovih
CREATE TEMPORARY TABLE plov_1 AS
SELECT sailno, ime, spol, leto_rojstva, ime_kluba, COALESCE(tocke::text, posebnosti) AS tocke_plov FROM tocke_plovi
JOIN tekmovalec ON tekmovalec_idtekmovalec = idtekmovalec
JOIN klubi_plovi ON klubi_plovi.idtekmovalec = tekmovalec.idtekmovalec AND klubi_plovi.plov_idplov = {1}
WHERE tocke_plovi.plov_idplov = {1}
ORDER BY tocke;

CREATE TEMPORARY TABLE delni2 AS
SELECT plov_1.sailno, plov_1.ime, plov_1.spol, plov_1.leto_rojstva, klubi_plovi2.ime_kluba, plov_1.tocke_plov, 
-- zanka po plovih od 2. naprej
plov_{1}.tocke_plov,
-- 
from plov_1
JOIN (SELECT klub.ime AS ime_kluba, idtekmovalec, plov_idplov, sailno FROM klub JOIN clanstvo ON klub.idklub = clanstvo.klub_idklub JOIN tekmovalec ON clanstvo.tekmovalec_idtekmovalec = tekmovalec.idtekmovalec JOIN tocke_plovi ON tocke_plovi.tekmovalec_idtekmovalec = tekmovalec.idtekmovalec)
AS klubi_plovi2 ON klubi_plovi2.sailno = plov_1.sailno
-- zanka po plovih od 2. naprej
JOIN plov_{1} ON plov_1.sailno = plov_{1}.sailno
--
;

-- število točk, ki jih dobijo neuvrščeni (za vsak plov posebej)
SELECT count(DISTINCT tocke_plov)+1 FROM plov_{0} WHERE tocke_plov~E'^\\d+$'

-- za generacijo rezultatov
SELECT DISTINCT *, (CASE WHEN prvi~E'^\\d+$' THEN prvi::integer ELSE 104 END + CASE WHEN drugi~E'^\\d+$' THEN drugi::integer ELSE 104 END + CASE WHEN tretji~E'^\\d+$' THEN tretji::integer ELSE 104 END + CASE WHEN četrti~E'^\\d+$' THEN četrti::integer ELSE 104 END) - greatest(CASE WHEN prvi~E'^\\d+$' THEN prvi::integer ELSE 104 END, CASE WHEN drugi~E'^\\d+$' THEN drugi::integer ELSE 104 END, CASE WHEN tretji~E'^\\d+$' THEN tretji::integer ELSE 104 END, CASE WHEN četrti~E'^\\d+$' THEN četrti::integer ELSE 104 END) AS net, (CASE WHEN prvi~E'^\\d+$' THEN prvi::integer ELSE 104 END + CASE WHEN drugi~E'^\\d+$' THEN drugi::integer ELSE 104 END + CASE WHEN tretji~E'^\\d+$' THEN tretji::integer ELSE 104 END + CASE WHEN četrti~E'^\\d+$' THEN četrti::integer ELSE 104 END) AS tot FROM delni2
ORDER BY net ASC, tot ASC;