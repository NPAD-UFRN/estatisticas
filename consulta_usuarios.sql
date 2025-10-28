-- select usuarios coordenadores de pesquisa
SELECT U.username, C.centro, D.departamento FROM centros AS C 
INNER JOIN departamentos AS D ON C.id = D.centroid
INNER JOIN coordenadores_pesquisa AS CP ON CP.departamento_id = D.id
INNER JOIN usuarios AS U ON U.id = CP.usuario_id;

-- select usuarios colaboradores
SELECT U.username, C.centro, D.departamento FROM centros AS C 
INNER JOIN departamentos AS D ON C.id = D.centroid
INNER JOIN coordenadores_pesquisa AS CP ON CP.departamento_id = D.id
INNER JOIN colaboradores AS CO ON CO.usuario_cp_id = CP.usuario_id
INNER JOIN usuarios AS U ON U.id = CP.usuario_id; 
