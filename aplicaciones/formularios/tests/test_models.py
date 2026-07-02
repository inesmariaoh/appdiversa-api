"""
Pruebas de los modelos del motor de formularios parametrizables.
"""

from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from aplicaciones.formularios.models import (
    AccionRegla,
    CatalogoGeografico,
    EstadoFormulario,
    Formulario,
    FormularioVersion,
    MensajesValidacion,
    OpcionRespuesta,
    OperadorRegla,
    Pregunta,
    ReglaPregunta,
    SeccionFormulario,
    TextoFormulario,
    TipoCatalogoGeografico,
    TipoFormulario,
    TipoPregunta,
    TipoTextoFormulario,
)


class FormularioModelTests(TestCase):
    """Pruebas del modelo Formulario."""

    def test_crear_formulario_exitoso(self) -> None:
        formulario = Formulario.objects.create(
            codigo="form_demo",
            nombre="Formulario demo",
            tipo_formulario=TipoFormulario.ENCUESTA,
        )

        self.assertEqual(formulario.codigo, "form_demo")
        self.assertEqual(formulario.estado, EstadoFormulario.BORRADOR)
        self.assertTrue(formulario.permite_anonimo)
        self.assertIsNotNone(formulario.uuid)

    def test_fechas_invalidas_generan_error(self) -> None:
        ahora = timezone.now()
        formulario = Formulario(
            codigo="form_fechas",
            nombre="Formulario fechas",
            tipo_formulario=TipoFormulario.REGISTRO,
            fecha_inicio=ahora + timedelta(days=1),
            fecha_fin=ahora,
        )

        with self.assertRaises(ValidationError) as contexto:
            formulario.full_clean()

        self.assertIn("fecha_fin", contexto.exception.message_dict)
        self.assertEqual(
            contexto.exception.message_dict["fecha_fin"][0],
            MensajesValidacion.FECHA_INICIO_MAYOR_FIN,
        )


class FormularioVersionModelTests(TestCase):
    """Pruebas del modelo FormularioVersion."""

    def setUp(self) -> None:
        self.formulario = Formulario.objects.create(
            codigo="form_version",
            nombre="Formulario version",
            tipo_formulario=TipoFormulario.CENSO,
        )

    def test_crear_version_exitoso(self) -> None:
        version = FormularioVersion.objects.create(
            formulario=self.formulario,
            numero_version=1,
            estado=EstadoFormulario.BORRADOR,
        )

        self.assertEqual(version.numero_version, 1)
        self.assertFalse(version.es_publicada)

    def test_version_publicada_requiere_estado_publicado(self) -> None:
        version = FormularioVersion(
            formulario=self.formulario,
            numero_version=2,
            estado=EstadoFormulario.BORRADOR,
            es_publicada=True,
        )

        with self.assertRaises(ValidationError) as contexto:
            version.full_clean()

        self.assertIn("estado", contexto.exception.message_dict)

    def test_constraint_unico_formulario_numero_version(self) -> None:
        FormularioVersion.objects.create(
            formulario=self.formulario,
            numero_version=3,
        )

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                FormularioVersion.objects.create(
                    formulario=self.formulario,
                    numero_version=3,
                )


class SeccionPreguntaModelTests(TestCase):
    """Pruebas de secciones y preguntas."""

    def setUp(self) -> None:
        formulario = Formulario.objects.create(
            codigo="form_seccion",
            nombre="Formulario seccion",
            tipo_formulario=TipoFormulario.EVALUACION,
        )
        self.version = FormularioVersion.objects.create(
            formulario=formulario,
            numero_version=1,
        )
        self.seccion = SeccionFormulario.objects.create(
            formulario_version=self.version,
            codigo="sec_01",
            titulo="Seccion inicial",
            orden=1,
        )

    def test_crear_seccion_exitoso(self) -> None:
        self.assertEqual(self.seccion.codigo, "sec_01")
        self.assertTrue(self.seccion.esta_activo)

    def test_crear_pregunta_exitoso(self) -> None:
        pregunta = Pregunta.objects.create(
            seccion=self.seccion,
            codigo="preg_01",
            texto="Texto de la pregunta",
            tipo_pregunta=TipoPregunta.TEXTO_CORTO,
            orden=1,
        )

        self.assertEqual(pregunta.codigo, "preg_01")
        self.assertTrue(pregunta.esta_activa)

    def test_longitudes_invalidas_generan_error(self) -> None:
        pregunta = Pregunta(
            seccion=self.seccion,
            codigo="preg_long",
            texto="Pregunta con longitudes invalidas",
            tipo_pregunta=TipoPregunta.TEXTO_CORTO,
            orden=2,
            longitud_minima=100,
            longitud_maxima=10,
        )

        with self.assertRaises(ValidationError) as contexto:
            pregunta.full_clean()

        self.assertIn("longitud_maxima", contexto.exception.message_dict)

    def test_valores_numericos_invalidos_generan_error(self) -> None:
        pregunta = Pregunta(
            seccion=self.seccion,
            codigo="preg_num",
            texto="Pregunta numerica",
            tipo_pregunta=TipoPregunta.NUMERO,
            orden=3,
            valor_minimo=Decimal("100.00"),
            valor_maximo=Decimal("10.00"),
        )

        with self.assertRaises(ValidationError) as contexto:
            pregunta.full_clean()

        self.assertIn("valor_maximo", contexto.exception.message_dict)

    def test_constraint_unico_seccion_codigo(self) -> None:
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                SeccionFormulario.objects.create(
                    formulario_version=self.version,
                    codigo="sec_01",
                    titulo="Duplicada",
                    orden=2,
                )

    def test_constraint_unico_pregunta_codigo(self) -> None:
        Pregunta.objects.create(
            seccion=self.seccion,
            codigo="preg_dup",
            texto="Original",
            tipo_pregunta=TipoPregunta.RADIO,
            orden=4,
        )

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Pregunta.objects.create(
                    seccion=self.seccion,
                    codigo="preg_dup",
                    texto="Duplicada",
                    tipo_pregunta=TipoPregunta.RADIO,
                    orden=5,
                )


class OpcionRespuestaModelTests(TestCase):
    """Pruebas del modelo OpcionRespuesta."""

    def setUp(self) -> None:
        formulario = Formulario.objects.create(
            codigo="form_opcion",
            nombre="Formulario opcion",
            tipo_formulario=TipoFormulario.INSCRIPCION,
        )
        version = FormularioVersion.objects.create(
            formulario=formulario,
            numero_version=1,
        )
        seccion = SeccionFormulario.objects.create(
            formulario_version=version,
            codigo="sec_opc",
            titulo="Seccion opciones",
            orden=1,
        )
        self.pregunta = Pregunta.objects.create(
            seccion=seccion,
            codigo="preg_opc",
            texto="Seleccione una opcion",
            tipo_pregunta=TipoPregunta.SELECT,
            orden=1,
        )

    def test_crear_opcion_exitoso(self) -> None:
        opcion = OpcionRespuesta.objects.create(
            pregunta=self.pregunta,
            codigo="opc_01",
            etiqueta="Opcion uno",
            valor="1",
            orden=1,
        )

        self.assertEqual(opcion.codigo, "opc_01")
        self.assertTrue(opcion.esta_activa)

    def test_constraint_unico_opcion_codigo(self) -> None:
        OpcionRespuesta.objects.create(
            pregunta=self.pregunta,
            codigo="opc_dup",
            etiqueta="Original",
            valor="1",
            orden=2,
        )

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                OpcionRespuesta.objects.create(
                    pregunta=self.pregunta,
                    codigo="opc_dup",
                    etiqueta="Duplicada",
                    valor="2",
                    orden=3,
                )


class CatalogoGeograficoModelTests(TestCase):
    """Pruebas del catalogo geografico."""

    def test_constraint_unico_tipo_codigo(self) -> None:
        CatalogoGeografico.objects.create(
            tipo=TipoCatalogoGeografico.PAIS,
            codigo="CO",
            nombre="Colombia",
        )

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                CatalogoGeografico.objects.create(
                    tipo=TipoCatalogoGeografico.PAIS,
                    codigo="CO",
                    nombre="Colombia duplicada",
                )


class TextoFormularioModelTests(TestCase):
    """Pruebas del modelo TextoFormulario."""

    def test_crear_texto_formulario(self) -> None:
        formulario = Formulario.objects.create(
            codigo="form_texto",
            nombre="Formulario texto",
            tipo_formulario=TipoFormulario.CARACTERIZACION,
        )
        version = FormularioVersion.objects.create(
            formulario=formulario,
            numero_version=1,
        )
        texto = TextoFormulario.objects.create(
            formulario_version=version,
            tipo=TipoTextoFormulario.INTRODUCCION,
            contenido="Contenido de introduccion",
            orden=1,
        )

        self.assertEqual(texto.tipo, TipoTextoFormulario.INTRODUCCION)
        self.assertTrue(texto.esta_activo)


class ReglaPreguntaModelTests(TestCase):
    """Pruebas del modelo ReglaPregunta."""

    def test_crear_regla_pregunta(self) -> None:
        formulario = Formulario.objects.create(
            codigo="form_regla",
            nombre="Formulario regla",
            tipo_formulario=TipoFormulario.ENCUESTA,
        )
        version = FormularioVersion.objects.create(
            formulario=formulario,
            numero_version=1,
        )
        seccion = SeccionFormulario.objects.create(
            formulario_version=version,
            codigo="sec_reg",
            titulo="Seccion regla",
            orden=1,
        )
        pregunta_origen = Pregunta.objects.create(
            seccion=seccion,
            codigo="preg_orig",
            texto="Pregunta origen",
            tipo_pregunta=TipoPregunta.RADIO,
            orden=1,
        )
        pregunta_destino = Pregunta.objects.create(
            seccion=seccion,
            codigo="preg_dest",
            texto="Pregunta destino",
            tipo_pregunta=TipoPregunta.TEXTO_CORTO,
            orden=2,
        )
        regla = ReglaPregunta.objects.create(
            pregunta_origen=pregunta_origen,
            operador=OperadorRegla.EQUALS,
            valor_esperado={"valor": "si"},
            pregunta_destino=pregunta_destino,
            accion=AccionRegla.MOSTRAR,
        )

        self.assertEqual(regla.accion, AccionRegla.MOSTRAR)
        self.assertTrue(regla.esta_activa)
