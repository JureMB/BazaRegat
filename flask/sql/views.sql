CREATE VIEW rezultati_nikola_1plov AS
SELECT sailno, ime, spol, leto_rojstva, ime_kluba, COALESCE(tocke::text, posebnosti) AS tocke_plov FROM tocke_plovi
JOIN tekmovalec ON tekmovalec_idtekmovalec = idtekmovalec
JOIN klubi_plovi ON klubi_plovi.idtekmovalec = tekmovalec.idtekmovalec AND klubi_plovi.plov_idplov = 1
WHERE tocke_plovi.plov_idplov = 1
ORDER BY tocke;

CREATE VIEW rezultati_nikola_2plov AS
SELECT sailno, ime, spol, leto_rojstva, ime_kluba, COALESCE(tocke::text, posebnosti) AS tocke_plov FROM tocke_plovi
JOIN tekmovalec ON tekmovalec_idtekmovalec = idtekmovalec
JOIN klubi_plovi ON klubi_plovi.idtekmovalec = tekmovalec.idtekmovalec AND klubi_plovi.plov_idplov = 2
WHERE tocke_plovi.plov_idplov = 2
ORDER BY tocke;

CREATE VIEW rezultati_nikola_3plov AS
SELECT sailno, ime, spol, leto_rojstva, ime_kluba, COALESCE(tocke::text, posebnosti) AS tocke_plov FROM tocke_plovi
JOIN tekmovalec ON tekmovalec_idtekmovalec = idtekmovalec
JOIN klubi_plovi ON klubi_plovi.idtekmovalec = tekmovalec.idtekmovalec AND klubi_plovi.plov_idplov = 3
WHERE tocke_plovi.plov_idplov = 3
ORDER BY tocke;

CREATE VIEW rezultati_nikola_4plov AS
SELECT sailno, ime, spol, leto_rojstva, ime_kluba, COALESCE(tocke::text, posebnosti) AS tocke_plov FROM tocke_plovi
JOIN tekmovalec ON tekmovalec_idtekmovalec = idtekmovalec
JOIN klubi_plovi ON klubi_plovi.idtekmovalec = tekmovalec.idtekmovalec AND klubi_plovi.plov_idplov = 4
WHERE tocke_plovi.plov_idplov = 4
ORDER BY tocke;

CREATE VIEW delni2 AS
SELECT rezultati_nikola_1plov.sailno, rezultati_nikola_1plov.ime, rezultati_nikola_1plov.spol, rezultati_nikola_1plov.leto_rojstva, klubi_plovi2.ime_kluba, rezultati_nikola_1plov.tocke_plov AS prvi, rezultati_nikola_2plov.tocke_plov AS drugi, rezultati_nikola_3plov.tocke_plov AS tretji, rezultati_nikola_4plov.tocke_plov AS četrti from rezultati_nikola_1plov
JOIN (SELECT klub.ime AS ime_kluba, idtekmovalec, plov_idplov, sailno FROM klub JOIN clanstvo ON klub.idklub = clanstvo.klub_idklub JOIN tekmovalec ON clanstvo.tekmovalec_idtekmovalec = tekmovalec.idtekmovalec JOIN tocke_plovi ON tocke_plovi.tekmovalec_idtekmovalec = tekmovalec.idtekmovalec)
 AS klubi_plovi2 ON klubi_plovi2.sailno = rezultati_nikola_1plov.sailno
JOIN rezultati_nikola_2plov ON rezultati_nikola_1plov.sailno = rezultati_nikola_2plov.sailno
JOIN rezultati_nikola_3plov ON rezultati_nikola_1plov.sailno = rezultati_nikola_3plov.sailno
JOIN rezultati_nikola_4plov ON rezultati_nikola_1plov.sailno = rezultati_nikola_4plov.sailno;

CREATE VIEW rezultati_nikola AS
SELECT DISTINCT *, (CASE WHEN prvi~E'^\\d+$' THEN prvi::integer ELSE 104 END + CASE WHEN drugi~E'^\\d+$' THEN drugi::integer ELSE 104 END + CASE WHEN tretji~E'^\\d+$' THEN tretji::integer ELSE 104 END + CASE WHEN četrti~E'^\\d+$' THEN četrti::integer ELSE 104 END) - greatest(CASE WHEN prvi~E'^\\d+$' THEN prvi::integer ELSE 104 END, CASE WHEN drugi~E'^\\d+$' THEN drugi::integer ELSE 104 END, CASE WHEN tretji~E'^\\d+$' THEN tretji::integer ELSE 104 END, CASE WHEN četrti~E'^\\d+$' THEN četrti::integer ELSE 104 END) AS net, (CASE WHEN prvi~E'^\\d+$' THEN prvi::integer ELSE 104 END + CASE WHEN drugi~E'^\\d+$' THEN drugi::integer ELSE 104 END + CASE WHEN tretji~E'^\\d+$' THEN tretji::integer ELSE 104 END + CASE WHEN četrti~E'^\\d+$' THEN četrti::integer ELSE 104 END) AS tot FROM delni2
ORDER BY net ASC, tot ASC;