"""
Modelos del motor de formularios parametrizables.
"""

import uuid

from django.core.exceptions import ValidationError
from django.db import models

from aplicaciones.auditoria.models import AuditoriaModeloAbstracto


class MensajesValidacion:
    """Mensajes centralizados para validaciones de modelos de formularios."""

    FECHA_INICIO_MAYOR_FIN = (
        "La fecha de inicio no puede ser posterior a la fecha de fin."
    )
    LONGITUD_MINIMA_MAYOR_MAXIMA = (
        "La longitud mínima no puede ser mayor que la longitud máxima."
    )
    VALOR_MINIMO_MAYOR_MAXIMO = (
        "El valor mínimo no puede ser mayor que el valor máximo."
    )
    VERSION_PUBLICADA_REQUIERE_ESTADO = (
        "Una versión publicada debe tener estado publicado."
    )
    CATALOGO_OBLIGATORIO = (
        "El catálogo asociado es obligatorio cuando la pregunta usa catálogo."
    )
    TIPO_PREGUNTA_NO_PERMITE_CATALOGO = (
        "El tipo de pregunta no permite asociar un catálogo parametrizable."
    )
    PREGUNTA_PADRE_OTRA_VERSION = (
        "La pregunta padre de catálogo debe pertenecer a la misma versión del formulario."
    )
    PREGUNTA_PADRE_REQUIERE_CATALOGO = (
        "La pregunta padre de catálogo requiere que la pregunta use catálogo."
    )
    PREGUNTA_PADRE_CATALOGO_OBLIGATORIO = (
        "La pregunta padre de catálogo requiere un catálogo asociado."
    )
    PREGUNTA_PADRE_ES_LA_MISMA = (
        "La pregunta no puede depender de sí misma como padre de catálogo."
    )
    TOOLTIP_TEXTO_OBLIGATORIO = (
        "El texto del tooltip es obligatorio cuando está activado."
    )


class EstadoFormulario(models.TextChoices):
    """Estados posibles de un formulario y sus versiones."""

    BORRADOR = "borrador", "Borrador"
    PUBLICADO = "publicado", "Publicado"
    CERRADO = "cerrado", "Cerrado"
    ARCHIVADO = "archivado", "Archivado"
    INACTIVO = "inactivo", "Inactivo"


class TipoFormulario(models.TextChoices):
    """Tipos de formulario soportados por el motor."""

    ENCUESTA = "encuesta", "Encuesta"
    CARACTERIZACION = "caracterizacion", "Caracterización"
    INSCRIPCION = "inscripcion", "Inscripción"
    REGISTRO = "registro", "Registro"
    CENSO = "censo", "Censo"
    EVALUACION = "evaluacion", "Evaluación"


class TipoTextoFormulario(models.TextChoices):
    """Tipos de texto asociados a una version de formulario."""

    INTRODUCCION = "introduccion", "Introducción"
    DEFINICION = "definicion", "Definición"
    CONSENTIMIENTO = "consentimiento", "Consentimiento"
    TERMINOS = "terminos", "Términos"
    AGRADECIMIENTO = "agradecimiento", "Agradecimiento"
    AYUDA = "ayuda", "Ayuda"
    CIERRE = "cierre", "Cierre"
    CONSENTIMIENTO_DATOS = "consentimiento_datos", "Consentimiento de datos"
    CONFIRMACION_ENVIO = "confirmacion_envio", "Confirmación de envío"
    VERIFICACION_EXITOSA = "verificacion_exitosa", "Verificación exitosa"
    AUTORIZACION_DATOS = "autorizacion_datos", "Autorización de datos"
    RESUMEN_RESPUESTAS = "resumen_respuestas", "Resumen de respuestas"
    REGISTRO_OPCIONAL = "registro_opcional", "Registro opcional"
    ENVIO_CORREO = "envio_correo", "Envío de correo"
    CONTACTO = "contacto", "Contacto"
    AYUDA_ACCESIBILIDAD = "ayuda_accesibilidad", "Ayuda de accesibilidad"
    NO_CUMPLE_CONDICIONES = "no_cumple_condiciones", "No cumple condiciones"


class TipoPregunta(models.TextChoices):
    """Tipos de pregunta soportados por el motor."""

    TEXTO_CORTO = "texto_corto", "Texto corto"
    TEXTO_LARGO = "texto_largo", "Texto largo"
    NUMERO = "numero", "Número"
    FECHA = "fecha", "Fecha"
    HORA = "hora", "Hora"
    FECHA_HORA = "fecha_hora", "Fecha y hora"
    RADIO = "radio", "Radio"
    CHECKBOX = "checkbox", "Checkbox"
    SELECT = "select", "Select"
    SELECT_MULTIPLE = "select_multiple", "Select múltiple"
    AUTOCOMPLETE = "autocomplete", "Autocomplete"
    LIKERT = "likert", "Likert"
    MATRIZ = "matriz", "Matriz"
    ARCHIVO = "archivo", "Archivo"
    FIRMA = "firma", "Firma"
    GEOLOCALIZACION = "geolocalizacion", "Geolocalización"
    UBICACION_GEOGRAFICA = "ubicacion_geografica", "Ubicación geográfica"
    AUDIO = "audio", "Audio"
    VIDEO = "video", "Video"


class TipoValidacionFiltro(models.TextChoices):
    """Tipos de validacion para preguntas filtro/preliminares."""

    RANGO_EDAD = "rango_edad", "Rango de edad"
    OPCION_EXACTA = "opcion_exacta", "Opción exacta"
    LISTA_OPCIONES = "lista_opciones", "Lista de opciones"
    RANGO_NUMERICO = "rango_numerico", "Rango numérico"
    BOOLEANO = "booleano", "Booleano"


class OperadorRegla(models.TextChoices):
    """Operadores para reglas condicionales entre preguntas."""

    EQUALS = "equals", "Equals"
    NOT_EQUALS = "not_equals", "Not equals"
    CONTAINS = "contains", "Contains"
    GT = "gt", "Greater than"
    LT = "lt", "Less than"
    IN = "in", "In"


class AccionRegla(models.TextChoices):
    """Acciones ejecutables por reglas condicionales."""

    MOSTRAR = "mostrar", "Mostrar"
    OCULTAR = "ocultar", "Ocultar"
    HABILITAR = "habilitar", "Habilitar"
    DESHABILITAR = "deshabilitar", "Deshabilitar"
    HACER_OBLIGATORIA = "hacer_obligatoria", "Hacer obligatoria"
    HACER_OPCIONAL = "hacer_opcional", "Hacer opcional"
    SALTAR_A_PREGUNTA = "saltar_a_pregunta", "Saltar a pregunta"
    SALTAR_A_SECCION = "saltar_a_seccion", "Saltar a sección"
    FINALIZAR_FORMULARIO = "finalizar_formulario", "Finalizar formulario"
    NO_APLICA_FORMULARIO = "no_aplica_formulario", "No aplica formulario"


TIPOS_PREGUNTA_CATALOGO = frozenset(
    {
        TipoPregunta.RADIO,
        TipoPregunta.CHECKBOX,
        TipoPregunta.SELECT,
        TipoPregunta.SELECT_MULTIPLE,
        TipoPregunta.AUTOCOMPLETE,
    },
)


class Formulario(AuditoriaModeloAbstracto):
    """Formulario parametrizable del motor AppDiversa."""

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    introduccion = models.TextField(blank=True)
    objetivo = models.TextField(blank=True)
    tipo_formulario = models.CharField(
        max_length=30,
        choices=TipoFormulario.choices,
    )
    tiempo_estimado_minutos = models.PositiveIntegerField(null=True, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=EstadoFormulario.choices,
        default=EstadoFormulario.BORRADOR,
    )
    version_actual = models.PositiveIntegerField(default=1)
    permite_anonimo = models.BooleanField(default=True)
    permite_registro_final = models.BooleanField(default=True)
    permite_multiples_respuestas = models.BooleanField(default=False)
    permite_offline = models.BooleanField(default=True)
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    orden = models.PositiveIntegerField(default=1)
    imagen_portada = models.ImageField(
        upload_to="formularios/portadas/",
        null=True,
        blank=True,
    )
    imagen_portada_repositorio = models.ForeignKey(
        "archivos.ArchivoRepositorio",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="formularios_portada",
    )

    class Meta:
        ordering = ["orden", "nombre"]
        indexes = [
            models.Index(fields=["estado"]),
            models.Index(fields=["codigo"]),
            models.Index(fields=["tipo_formulario"]),
            models.Index(fields=["orden"]),
        ]
        verbose_name = "Formulario"
        verbose_name_plural = "Formularios"

    def __str__(self) -> str:
        return f"{self.codigo} - {self.nombre}"

    def clean(self) -> None:
        super().clean()
        if self.fecha_inicio and self.fecha_fin and self.fecha_inicio > self.fecha_fin:
            raise ValidationError(
                {"fecha_fin": MensajesValidacion.FECHA_INICIO_MAYOR_FIN}
            )


class FormularioVersion(AuditoriaModeloAbstracto):
    """Version historica de un formulario parametrizable."""

    formulario = models.ForeignKey(
        Formulario,
        on_delete=models.CASCADE,
        related_name="versiones",
    )
    numero_version = models.PositiveIntegerField()
    estado = models.CharField(
        max_length=20,
        choices=EstadoFormulario.choices,
        default=EstadoFormulario.BORRADOR,
    )
    descripcion_cambio = models.TextField(blank=True)
    es_publicada = models.BooleanField(default=False)
    fecha_publicacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["formulario", "numero_version"]
        constraints = [
            models.UniqueConstraint(
                fields=["formulario", "numero_version"],
                name="uq_formulario_version_numero",
            ),
        ]
        indexes = [
            models.Index(fields=["estado"]),
        ]
        verbose_name = "Versión de formulario"
        verbose_name_plural = "Versiones de formulario"

    def __str__(self) -> str:
        return f"{self.formulario.codigo} v{self.numero_version}"

    def clean(self) -> None:
        super().clean()
        if self.es_publicada and self.estado != EstadoFormulario.PUBLICADO:
            raise ValidationError(
                {"estado": MensajesValidacion.VERSION_PUBLICADA_REQUIERE_ESTADO}
            )


class TextoFormulario(AuditoriaModeloAbstracto):
    """Texto parametrizable asociado a una version de formulario."""

    formulario_version = models.ForeignKey(
        FormularioVersion,
        on_delete=models.CASCADE,
        related_name="textos",
    )
    tipo = models.CharField(max_length=30, choices=TipoTextoFormulario.choices)
    titulo = models.CharField(max_length=255, blank=True)
    contenido = models.TextField()
    orden = models.PositiveIntegerField(default=1)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["orden"]
        indexes = [
            models.Index(fields=["orden"]),
            models.Index(fields=["esta_activo"]),
        ]
        verbose_name = "Texto de formulario"
        verbose_name_plural = "Textos de formulario"

    def __str__(self) -> str:
        return f"{self.formulario_version} - {self.tipo}"


class SeccionFormulario(AuditoriaModeloAbstracto):
    """Seccion dentro de una version de formulario."""

    formulario_version = models.ForeignKey(
        FormularioVersion,
        on_delete=models.CASCADE,
        related_name="secciones",
    )
    codigo = models.CharField(max_length=50)
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    texto_ayuda = models.TextField(blank=True)
    orden = models.PositiveIntegerField()
    es_visible = models.BooleanField(default=True)
    esta_activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["orden"]
        constraints = [
            models.UniqueConstraint(
                fields=["formulario_version", "codigo"],
                name="uq_seccion_formulario_version_codigo",
            ),
        ]
        indexes = [
            models.Index(fields=["orden"]),
            models.Index(fields=["esta_activo"]),
        ]
        verbose_name = "Sección de formulario"
        verbose_name_plural = "Secciones de formulario"

    def __str__(self) -> str:
        return f"{self.formulario_version} - {self.codigo}"


class Pregunta(AuditoriaModeloAbstracto):
    """Pregunta parametrizable dentro de una seccion."""

    seccion = models.ForeignKey(
        SeccionFormulario,
        on_delete=models.CASCADE,
        related_name="preguntas",
    )
    codigo = models.CharField(max_length=50)
    texto = models.TextField()
    descripcion = models.TextField(blank=True)
    tooltip = models.TextField(blank=True)
    tiene_tooltip = models.BooleanField(default=False)
    tipo_pregunta = models.CharField(max_length=30, choices=TipoPregunta.choices)
    es_obligatoria = models.BooleanField(default=False)
    es_pregunta_filtro = models.BooleanField(default=False)
    tipo_validacion_filtro = models.CharField(
        max_length=30,
        choices=TipoValidacionFiltro.choices,
        blank=True,
        default="",
    )
    valor_filtro_esperado = models.JSONField(null=True, blank=True)
    bloquea_continuacion_si_no_cumple = models.BooleanField(
        default=True,
        help_text="Indica si el incumplimiento del filtro bloquea el ingreso al formulario.",
    )
    mensaje_no_cumple = models.TextField(
        blank=True,
        help_text="Mensaje visible cuando la respuesta no cumple la condicion del filtro.",
    )
    permite_otro = models.BooleanField(default=False)
    texto_otro_obligatorio = models.BooleanField(
        default=False,
        help_text=(
            "Indica si el texto libre asociado a una opcion tipo otro es "
            "obligatorio cuando dicha opcion resulta seleccionada."
        ),
    )
    permite_observacion = models.BooleanField(default=False)
    orden = models.PositiveIntegerField()
    longitud_minima = models.PositiveIntegerField(null=True, blank=True)
    longitud_maxima = models.PositiveIntegerField(null=True, blank=True)
    valor_minimo = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
    )
    valor_maximo = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
    )
    expresion_regular = models.CharField(max_length=500, blank=True)
    mensaje_error = models.TextField(blank=True)
    esta_activa = models.BooleanField(default=True)
    usa_catalogo = models.BooleanField(default=False)
    catalogo_asociado = models.ForeignKey(
        "catalogos.Catalogo",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="preguntas",
    )
    pregunta_padre_catalogo = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="preguntas_dependientes_catalogo",
    )
    campo_codigo_padre_catalogo = models.CharField(
        max_length=100,
        blank=True,
        default="codigo",
    )
    permite_busqueda_catalogo = models.BooleanField(default=False)
    limite_items_catalogo = models.PositiveIntegerField(null=True, blank=True)
    visible_por_defecto = models.BooleanField(
        default=True,
        help_text="Indica si la pregunta se muestra sin una regla de visibilidad.",
    )
    limpiar_respuesta_al_ocultar = models.BooleanField(
        default=True,
        help_text="Indica si se elimina la respuesta cuando la pregunta queda oculta.",
    )
    pregunta_origen_flujo = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="preguntas_dependientes_flujo",
        help_text="Pregunta tras la cual se inserta visualmente cuando es visible.",
    )
    codigo_catalogo_departamento = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="Código del catálogo de departamentos para ubicación geográfica.",
    )

    class Meta:
        ordering = ["orden"]
        constraints = [
            models.UniqueConstraint(
                fields=["seccion", "codigo"],
                name="uq_pregunta_seccion_codigo",
            ),
        ]
        indexes = [
            models.Index(fields=["tipo_pregunta"]),
            models.Index(fields=["esta_activa"]),
            models.Index(fields=["orden"]),
        ]
        verbose_name = "Pregunta"
        verbose_name_plural = "Preguntas"

    def __str__(self) -> str:
        return f"{self.seccion.codigo} - {self.codigo}"

    def clean(self) -> None:
        super().clean()
        self._validar_longitudes()
        self._validar_valores_numericos()
        self._validar_configuracion_catalogo()
        self._validar_tooltip()

    def _validar_tooltip(self) -> None:
        from aplicaciones.formularios.validadores_tooltip import (
            validar_tooltip_configurado,
        )

        validar_tooltip_configurado(self.tiene_tooltip, self.tooltip)

    def _validar_configuracion_catalogo(self) -> None:
        if self.usa_catalogo:
            self._validar_catalogo_obligatorio()
            self._validar_tipo_pregunta_catalogo()
            self._validar_pregunta_padre_catalogo()

    def _validar_catalogo_obligatorio(self) -> None:
        if self.catalogo_asociado_id is None:
            raise ValidationError(
                {"catalogo_asociado": MensajesValidacion.CATALOGO_OBLIGATORIO},
            )

    def _validar_tipo_pregunta_catalogo(self) -> None:
        if self.tipo_pregunta not in TIPOS_PREGUNTA_CATALOGO:
            raise ValidationError(
                {"tipo_pregunta": MensajesValidacion.TIPO_PREGUNTA_NO_PERMITE_CATALOGO},
            )

    def _validar_pregunta_padre_catalogo(self) -> None:
        if self.pregunta_padre_catalogo is None:
            return

        if self.pk is not None and self.pregunta_padre_catalogo_id == self.pk:
            raise ValidationError(
                {"pregunta_padre_catalogo": MensajesValidacion.PREGUNTA_PADRE_ES_LA_MISMA},
            )

        if self.pregunta_padre_catalogo.seccion.formulario_version_id != (
            self.seccion.formulario_version_id
        ):
            raise ValidationError(
                {
                    "pregunta_padre_catalogo": (
                        MensajesValidacion.PREGUNTA_PADRE_OTRA_VERSION
                    ),
                },
            )

        if not self.usa_catalogo:
            raise ValidationError(
                {
                    "pregunta_padre_catalogo": (
                        MensajesValidacion.PREGUNTA_PADRE_REQUIERE_CATALOGO
                    ),
                },
            )

        if self.catalogo_asociado_id is None:
            raise ValidationError(
                {
                    "pregunta_padre_catalogo": (
                        MensajesValidacion.PREGUNTA_PADRE_CATALOGO_OBLIGATORIO
                    ),
                },
            )

    def _validar_longitudes(self) -> None:
        if (
            self.longitud_minima is not None
            and self.longitud_maxima is not None
            and self.longitud_minima > self.longitud_maxima
        ):
            raise ValidationError(
                {"longitud_maxima": MensajesValidacion.LONGITUD_MINIMA_MAYOR_MAXIMA}
            )

    def _validar_valores_numericos(self) -> None:
        if (
            self.valor_minimo is not None
            and self.valor_maximo is not None
            and self.valor_minimo > self.valor_maximo
        ):
            raise ValidationError(
                {"valor_maximo": MensajesValidacion.VALOR_MINIMO_MAYOR_MAXIMO}
            )


class OpcionRespuesta(AuditoriaModeloAbstracto):
    """Opcion de respuesta para preguntas de seleccion."""

    pregunta = models.ForeignKey(
        Pregunta,
        on_delete=models.CASCADE,
        related_name="opciones",
    )
    codigo = models.CharField(max_length=50)
    etiqueta = models.CharField(max_length=500)
    valor = models.CharField(max_length=255)
    tooltip = models.TextField(blank=True)
    tiene_tooltip = models.BooleanField(default=False)
    orden = models.PositiveIntegerField()
    es_excluyente = models.BooleanField(default=False)
    activa_otro = models.BooleanField(default=False)
    esta_activa = models.BooleanField(default=True)

    class Meta:
        ordering = ["orden"]
        constraints = [
            models.UniqueConstraint(
                fields=["pregunta", "codigo"],
                name="uq_opcion_respuesta_pregunta_codigo",
            ),
        ]
        indexes = [
            models.Index(fields=["orden"]),
            models.Index(fields=["esta_activa"]),
        ]
        verbose_name = "Opción de respuesta"
        verbose_name_plural = "Opciones de respuesta"

    def __str__(self) -> str:
        return f"{self.pregunta.codigo} - {self.codigo}"

    def clean(self) -> None:
        super().clean()
        from aplicaciones.formularios.validadores_tooltip import (
            validar_tooltip_configurado,
        )

        validar_tooltip_configurado(self.tiene_tooltip, self.tooltip)


class PreguntaMatrizFila(AuditoriaModeloAbstracto):
    """Fila de una pregunta tipo matriz."""

    pregunta = models.ForeignKey(
        Pregunta,
        on_delete=models.CASCADE,
        related_name="filas_matriz",
    )
    codigo = models.CharField(max_length=50)
    etiqueta = models.CharField(max_length=500)
    orden = models.PositiveIntegerField()
    esta_activa = models.BooleanField(default=True)

    class Meta:
        ordering = ["orden"]
        constraints = [
            models.UniqueConstraint(
                fields=["pregunta", "codigo"],
                name="uq_matriz_fila_pregunta_codigo",
            ),
        ]
        indexes = [
            models.Index(fields=["orden"]),
            models.Index(fields=["esta_activa"]),
        ]
        verbose_name = "Fila de matriz"
        verbose_name_plural = "Filas de matriz"

    def __str__(self) -> str:
        return f"{self.pregunta.codigo} - fila {self.codigo}"


class PreguntaMatrizColumna(AuditoriaModeloAbstracto):
    """Columna de una pregunta tipo matriz."""

    pregunta = models.ForeignKey(
        Pregunta,
        on_delete=models.CASCADE,
        related_name="columnas_matriz",
    )
    codigo = models.CharField(max_length=50)
    etiqueta = models.CharField(max_length=500)
    valor = models.CharField(max_length=100)
    orden = models.PositiveIntegerField()
    esta_activa = models.BooleanField(default=True)

    class Meta:
        ordering = ["orden"]
        constraints = [
            models.UniqueConstraint(
                fields=["pregunta", "codigo"],
                name="uq_matriz_columna_pregunta_codigo",
            ),
        ]
        indexes = [
            models.Index(fields=["orden"]),
            models.Index(fields=["esta_activa"]),
        ]
        verbose_name = "Columna de matriz"
        verbose_name_plural = "Columnas de matriz"

    def __str__(self) -> str:
        return f"{self.pregunta.codigo} - columna {self.codigo}"


class ReglaPregunta(AuditoriaModeloAbstracto):
    """Regla condicional entre preguntas o secciones."""

    pregunta_origen = models.ForeignKey(
        Pregunta,
        on_delete=models.CASCADE,
        related_name="reglas_origen",
    )
    operador = models.CharField(max_length=20, choices=OperadorRegla.choices)
    valor_esperado = models.JSONField()
    pregunta_destino = models.ForeignKey(
        Pregunta,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="reglas_destino",
    )
    seccion_destino = models.ForeignKey(
        SeccionFormulario,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="reglas_destino",
    )
    accion = models.CharField(max_length=30, choices=AccionRegla.choices)
    mensaje = models.TextField(blank=True)
    esta_activa = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["esta_activa"]),
        ]
        verbose_name = "Regla de pregunta"
        verbose_name_plural = "Reglas de pregunta"

    def __str__(self) -> str:
        return f"Regla {self.pregunta_origen.codigo} -> {self.accion}"
