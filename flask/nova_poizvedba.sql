SELECT tekmovalec.sailno, tekmovalec.ime, tekmovalec.spol, tekmovalec.leto_rojstva, ime_kluba, 
array_to_string(array_agg(coalesce(tocke::text, posebnosti) ORDER BY st_plova ASC), ',') AS tocke_plovi, 
(sum(efektivne_tocke) - max(efektivne_tocke))::int AS net,
sum(efektivne_tocke)::int AS tot
FROM efektivne_tocke JOIN plov ON plov_idplov = plov.idplov
JOIN tekmovalec ON tekmovalec_idtekmovalec = idtekmovalec
JOIN klubi_plovi ON klubi_plovi.idtekmovalec = tekmovalec_idtekmovalec AND klubi_plovi.plov_idplov = plov.idplov
WHERE regata_idregata = 1
GROUP BY tekmovalec_idtekmovalec, ime_kluba, tekmovalec.sailno, tekmovalec.ime, tekmovalec.spol, tekmovalec.leto_rojstva
ORDER BY net ASC, tot ASC,
array_agg(efektivne_tocke ORDER BY st_plova ASC) ASC, array_agg(coalesce(tocke::text, posebnosti) ORDER BY st_plova ASC) ASC