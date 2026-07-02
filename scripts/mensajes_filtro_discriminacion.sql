-- Configura los mensajes de no elegibilidad de las preguntas filtro
-- de la Encuesta de Discriminacion (parametrizable por formulario).
SET NAMES utf8mb4;

-- Restriccion de edad (preguntas con codigo P1: fecha de nacimiento y edad)
UPDATE formularios_pregunta p
JOIN formularios_seccionformulario s ON p.seccion_id = s.id
JOIN formularios_formularioversion v ON s.formulario_version_id = v.id
JOIN formularios_formulario f ON v.formulario_id = f.id
SET p.mensaje_no_cumple = 'Para participar en esta encuesta debes ser mayor de 18 años.'
WHERE f.uuid = '1b5f64f9cd6648f6b210ce6b371bb8fb'
  AND p.es_pregunta_filtro = 1
  AND p.codigo = 'P1';

-- Restriccion de residencia en Colombia (codigo P2)
UPDATE formularios_pregunta p
JOIN formularios_seccionformulario s ON p.seccion_id = s.id
JOIN formularios_formularioversion v ON s.formulario_version_id = v.id
JOIN formularios_formulario f ON v.formulario_id = f.id
SET p.mensaje_no_cumple = 'Para participar en esta encuesta debes haber vivido en Colombia durante los últimos 5 años.'
WHERE f.uuid = '1b5f64f9cd6648f6b210ce6b371bb8fb'
  AND p.es_pregunta_filtro = 1
  AND p.codigo = 'P2';
