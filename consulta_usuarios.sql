-- select usuarios coordenadores de pesquisa e colaboradores por centro
SELECT 
    centro,
    COUNT(*) AS usuarios
FROM (
    -- Coordenadores de pesquisa
    SELECT 
        SUBSTRING_INDEX(C.centro, ' - ', -1) AS centro,
        CP.usuario_id
    FROM centros AS C 
    INNER JOIN departamentos AS D ON C.id = D.centroid
    INNER JOIN coordenadores_pesquisa AS CP ON CP.departamento_id = D.id
    
    UNION 
    
    -- Colaboradores
    SELECT 
        SUBSTRING_INDEX(C.centro, ' - ', -1) AS centro,
        CO.usuario_id
    FROM centros AS C 
    INNER JOIN departamentos AS D ON C.id = D.centroid
    INNER JOIN coordenadores_pesquisa AS CP ON CP.departamento_id = D.id
    INNER JOIN colaboradores AS CO ON CO.usuario_cp_id = CP.usuario_id
) AS usuarios_totais
GROUP BY centro
ORDER BY usuarios DESC;