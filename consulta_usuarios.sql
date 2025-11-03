-- select usuarios coordenadores de pesquisa
SELECT C.centro FROM centros AS C 
INNER JOIN departamentos AS D ON C.id = D.centroid
INNER JOIN coordenadores_pesquisa AS CP ON CP.departamento_id = D.id;

-- select usuarios colaboradores
SELECT C.centro FROM centros AS C 
INNER JOIN departamentos AS D ON C.id = D.centroid
INNER JOIN coordenadores_pesquisa AS CP ON CP.departamento_id = D.id
INNER JOIN colaboradores AS CO ON CO.usuario_cp_id = CP.usuario_id;