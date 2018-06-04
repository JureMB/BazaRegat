
-- Rezultati za posamezen plov:
-- CREATE VIEW rezultati_plov AS
SELECT sailno, ime, spol, leto_rojstva, COALESCE(tocke::text, posebnosti) AS tocke_plov FROM tocke_plovi
JOIN tekmovalec ON tekmovalec_idtekmovalec = idtekmovalec
JOIN clanstvo ON 
WHERE plov_idplov = 1 
ORDER BY tocke;

