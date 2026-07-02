"""
Pruebas de metadatos de interaccion expuestos al frontend.
"""

from django.test import TestCase

from aplicaciones.formularios.api.v1.serializers import (
    OpcionRespuestaSerializer,
    PreguntaSerializer,
)
from aplicaciones.formularios.constantes_interaccion import (
    AccionInteraccionOpcion,
    ModoExclusionOpciones,
    ModoCampoTextoOtro,
    TipoSeleccionInteraccion,
)
from aplicaciones.formularios.models import (
    Formulario,
    FormularioVersion,
    OpcionRespuesta,
    Pregunta,
    SeccionFormulario,
    TipoFormulario,
    TipoPregunta,
)


class MetadatosInteraccionSerializerTests(TestCase):
    """Verifica acciones_ui y comportamiento_interaccion en la API publica."""

    @classmethod
    def setUpTestData(cls) -> None:
        formulario = Formulario.objects.create(
            codigo="form_interaccion",
            nombre="Formulario interaccion",
            descripcion="Prueba",
            tipo_formulario=TipoFormulario.ENCUESTA,
        )
        version = FormularioVersion.objects.create(
            formulario=formulario,
            numero_version=1,
            es_publicada=True,
        )
        seccion = SeccionFormulario.objects.create(
            formulario_version=version,
            codigo="sec1",
            titulo="Seccion",
            orden=1,
        )
        cls.pregunta = Pregunta.objects.create(
            seccion=seccion,
            codigo="P1",
            texto="Pregunta multiple",
            tipo_pregunta=TipoPregunta.CHECKBOX,
            es_obligatoria=True,
            permite_otro=True,
            orden=1,
        )
        cls.opcion_otro = OpcionRespuesta.objects.create(
            pregunta=cls.pregunta,
            codigo="OP_OTRO",
            etiqueta="Otros motivos, ¿cuáles?",
            valor="otros",
            orden=1,
            activa_otro=True,
        )
        cls.opcion_excluyente = OpcionRespuesta.objects.create(
            pregunta=cls.pregunta,
            codigo="OP_NO",
            etiqueta="No he sentido discriminación",
            valor="no_he_sentido",
            orden=2,
            es_excluyente=True,
        )

    def test_opcion_expone_acciones_ui(self) -> None:
        """Historia de usuario asociada: metadatos de interaccion en opciones."""
        datos = OpcionRespuestaSerializer(self.opcion_otro).data
        self.assertIn(AccionInteraccionOpcion.MOSTRAR_CAMPO_TEXTO, datos["acciones_ui"])

    def test_opcion_excluyente_expone_accion(self) -> None:
        """Historia de usuario asociada: metadatos de interaccion en opciones."""
        datos = OpcionRespuestaSerializer(self.opcion_excluyente).data
        self.assertIn(
            AccionInteraccionOpcion.EXCLUIR_OTRAS_OPCIONES,
            datos["acciones_ui"],
        )

    def test_pregunta_expone_comportamiento_interaccion(self) -> None:
        """Historia de usuario asociada: metadatos de interaccion en preguntas."""
        datos = PreguntaSerializer(self.pregunta).data
        comportamiento = datos["comportamiento_interaccion"]
        self.assertEqual(
            comportamiento["tipo_seleccion"],
            TipoSeleccionInteraccion.MULTIPLE,
        )
        self.assertEqual(
            comportamiento["campo_texto_otro"],
            ModoCampoTextoOtro.OPCIONAL,
        )
        self.assertEqual(
            comportamiento["modo_exclusion"],
            ModoExclusionOpciones.DESELECCIONAR_OTRAS,
        )

    def test_pregunta_expone_campo_texto_otro_obligatorio(self) -> None:
        """Historia de usuario asociada: texto obligatorio en opcion otro."""
        self.pregunta.texto_otro_obligatorio = True
        self.pregunta.save(update_fields=["texto_otro_obligatorio"])

        datos = PreguntaSerializer(self.pregunta).data

        self.assertEqual(
            datos["comportamiento_interaccion"]["campo_texto_otro"],
            ModoCampoTextoOtro.OBLIGATORIO,
        )
