"""
Serializers de la API publica de formularios.
"""

from typing import Any

from rest_framework import serializers

from aplicaciones.catalogos.models import Catalogo
from aplicaciones.formularios.api.util_media import construir_url_imagen_campo
from aplicaciones.formularios.models import (
    Formulario,
    FormularioVersion,
    OpcionRespuesta,
    Pregunta,
    PreguntaMatrizColumna,
    PreguntaMatrizFila,
    ReglaPregunta,
    SeccionFormulario,
    TextoFormulario,
)
from aplicaciones.formularios.servicios_interaccion_opciones import (
    construir_acciones_ui_opcion,
    construir_comportamiento_interaccion,
)
from aplicaciones.formularios.utilidades_opcion_excluyente import resolver_es_excluyente
from aplicaciones.formularios.utilidades_opcion_otro import resolver_activa_otro
from aplicaciones.formularios.validadores_tooltip import tooltip_visible_en_api
from aplicaciones.formularios.catalogo_geografico import (
    es_pregunta_catalogo_geografico,
    obtener_dependientes_geograficos_ordenados,
)
from aplicaciones.formularios.disponibilidad import calcular_metadatos_disponibilidad
from aplicaciones.formularios.filtros.evaluador import construir_metadata_validacion_filtro
from aplicaciones.formularios.selectores import FormularioEstructuraDatos
from aplicaciones.formularios.servicios import obtener_fuente_opciones_pregunta
from aplicaciones.internacionalizacion.api.mixins import TraduccionSerializerMixin
from aplicaciones.internacionalizacion.servicios import (
    aplicar_texto_traducido,
    construir_mapa_traducciones,
    normalizar_codigo_idioma,
    recolectar_uuids_estructura_formulario,
    resolver_uuid_entidad,
)

PREFIJO_API_CATALOGOS = "/api/v1/catalogos/"


class FormularioDisponibleSerializer(
    TraduccionSerializerMixin,
    serializers.ModelSerializer,
):
    """Serializer resumido para formularios disponibles."""

    nombre_entidad = "Formulario"
    imagen_portada = serializers.SerializerMethodField()
    estado_disponibilidad = serializers.SerializerMethodField()
    puede_iniciar = serializers.SerializerMethodField()
    etiqueta_estado = serializers.SerializerMethodField()

    class Meta:
        model = Formulario
        fields = (
            "uuid",
            "codigo",
            "nombre",
            "descripcion",
            "tipo_formulario",
            "orden",
            "tiempo_estimado_minutos",
            "fecha_inicio",
            "fecha_fin",
            "estado_disponibilidad",
            "puede_iniciar",
            "etiqueta_estado",
            "permite_anonimo",
            "permite_registro_final",
            "permite_multiples_respuestas",
            "permite_offline",
            "imagen_portada",
        )

    def get_imagen_portada(self, instancia: Formulario) -> str | None:
        """Retorna la URL de la imagen de portada si existe."""
        return construir_url_imagen_campo(
            instancia,
            "imagen_portada",
            self.context.get("request"),
            campo_repositorio="imagen_portada_repositorio",
        )

    def _metadatos_disponibilidad(self, instancia: Formulario) -> dict[str, str | bool]:
        """Retorna metadatos de disponibilidad calculados para la instancia."""
        return calcular_metadatos_disponibilidad(instancia)

    def get_estado_disponibilidad(self, instancia: Formulario) -> str:
        """Retorna el codigo de estado de disponibilidad publica."""
        return str(self._metadatos_disponibilidad(instancia)["estado_disponibilidad"])

    def get_puede_iniciar(self, instancia: Formulario) -> bool:
        """Indica si el formulario puede iniciar sesion en el instante actual."""
        valor = self._metadatos_disponibilidad(instancia)["puede_iniciar"]
        return bool(valor)

    def get_etiqueta_estado(self, instancia: Formulario) -> str:
        """Retorna la etiqueta visible del estado de disponibilidad."""
        return str(self._metadatos_disponibilidad(instancia)["etiqueta_estado"])

    def to_representation(self, instancia: Formulario) -> dict[str, Any]:
        """Serializa el formulario aplicando traducciones si existen."""
        datos = super().to_representation(instancia)
        return self.aplicar_traducciones_campos(
            instancia,
            datos,
            ("nombre", "descripcion"),
        )


class TextoFormularioSerializer(
    TraduccionSerializerMixin,
    serializers.ModelSerializer,
):
    """Serializer para textos parametrizables de una version."""

    nombre_entidad = "TextoFormulario"

    class Meta:
        model = TextoFormulario
        fields = ("tipo", "titulo", "contenido", "orden")

    def to_representation(self, instancia: TextoFormulario) -> dict[str, Any]:
        """Serializa el texto aplicando traducciones si existen."""
        datos = super().to_representation(instancia)
        datos = self.aplicar_traducciones_campos(
            instancia,
            datos,
            ("titulo", "contenido"),
        )
        datos["contenido_accesible"] = self.construir_contenido_accesible_campos(
            instancia,
            ("contenido",),
        )
        return datos


class OpcionRespuestaSerializer(
    TraduccionSerializerMixin,
    serializers.ModelSerializer,
):
    """Serializer para opciones de respuesta."""

    nombre_entidad = "OpcionRespuesta"
    acciones_ui = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
    )

    class Meta:
        model = OpcionRespuesta
        fields = (
            "codigo",
            "etiqueta",
            "valor",
            "tooltip",
            "tiene_tooltip",
            "orden",
            "es_excluyente",
            "activa_otro",
            "acciones_ui",
        )

    def to_representation(self, instancia: OpcionRespuesta) -> dict[str, Any]:
        """Serializa la opcion aplicando traducciones si existen."""
        datos = super().to_representation(instancia)
        datos = self.aplicar_traducciones_campos(
            instancia,
            datos,
            ("etiqueta", "tooltip"),
        )
        datos["activa_otro"] = resolver_activa_otro(
            bool(datos.get("activa_otro")),
            instancia.pregunta.permite_otro,
            str(datos.get("etiqueta", "")),
        )
        datos["es_excluyente"] = resolver_es_excluyente(
            bool(datos.get("es_excluyente")),
            instancia.pregunta.tipo_pregunta,
            str(datos.get("etiqueta", "")),
        )
        datos["acciones_ui"] = construir_acciones_ui_opcion(
            bool(datos["activa_otro"]),
            bool(datos["es_excluyente"]),
            instancia.pregunta.tipo_pregunta,
        )
        datos["tooltip"] = tooltip_visible_en_api(
            bool(instancia.tiene_tooltip),
            str(datos.get("tooltip", "")),
        )
        return datos


class PreguntaMatrizFilaSerializer(serializers.ModelSerializer):
    """Serializer para filas de preguntas tipo matriz."""

    class Meta:
        model = PreguntaMatrizFila
        fields = ("codigo", "etiqueta", "orden")


class PreguntaMatrizColumnaSerializer(serializers.ModelSerializer):
    """Serializer para columnas de preguntas tipo matriz."""

    class Meta:
        model = PreguntaMatrizColumna
        fields = ("codigo", "etiqueta", "valor", "orden")


class ReglaPreguntaSerializer(
    TraduccionSerializerMixin,
    serializers.ModelSerializer,
):
    """Serializer para reglas condicionales de preguntas."""

    nombre_entidad = "ReglaPregunta"
    pregunta_destino_codigo = serializers.SerializerMethodField()
    seccion_destino_codigo = serializers.SerializerMethodField()

    class Meta:
        model = ReglaPregunta
        fields = (
            "operador",
            "valor_esperado",
            "accion",
            "mensaje",
            "pregunta_destino_codigo",
            "seccion_destino_codigo",
        )

    def get_pregunta_destino_codigo(self, regla: ReglaPregunta) -> str | None:
        """Retorna el codigo de la pregunta destino si existe."""
        if regla.pregunta_destino is None:
            return None
        return regla.pregunta_destino.codigo

    def get_seccion_destino_codigo(self, regla: ReglaPregunta) -> str | None:
        """Retorna el codigo de la seccion destino si existe."""
        if regla.seccion_destino is None:
            return None
        return regla.seccion_destino.codigo

    def to_representation(self, instancia: ReglaPregunta) -> dict[str, Any]:
        """Serializa la regla aplicando traducciones si existen."""
        datos = super().to_representation(instancia)
        return self.aplicar_traducciones_campos(instancia, datos, ("mensaje",))


class PreguntaSerializer(
    TraduccionSerializerMixin,
    serializers.ModelSerializer,
):
    """Serializer para preguntas con relaciones anidadas."""

    nombre_entidad = "Pregunta"
    opciones = OpcionRespuestaSerializer(many=True, read_only=True)
    comportamiento_interaccion = serializers.DictField(read_only=True)
    filas_matriz = PreguntaMatrizFilaSerializer(many=True, read_only=True)
    columnas_matriz = PreguntaMatrizColumnaSerializer(many=True, read_only=True)
    reglas_origen = ReglaPreguntaSerializer(many=True, read_only=True)
    catalogo_asociado = serializers.SerializerMethodField()
    pregunta_padre_catalogo = serializers.SerializerMethodField()
    es_pregunta_geografica = serializers.SerializerMethodField()
    preguntas_dependientes_geograficas = serializers.SerializerMethodField()
    catalogo_departamento = serializers.SerializerMethodField()
    pregunta_origen_flujo_codigo = serializers.SerializerMethodField()
    validacion_filtro = serializers.SerializerMethodField()
    fuente_opciones = serializers.SerializerMethodField()

    class Meta:
        model = Pregunta
        fields = (
            "codigo",
            "texto",
            "descripcion",
            "tooltip",
            "tiene_tooltip",
            "tipo_pregunta",
            "es_obligatoria",
            "es_pregunta_filtro",
            "tipo_validacion_filtro",
            "valor_filtro_esperado",
            "bloquea_continuacion_si_no_cumple",
            "mensaje_no_cumple",
            "validacion_filtro",
            "permite_otro",
            "permite_observacion",
            "orden",
            "longitud_minima",
            "longitud_maxima",
            "valor_minimo",
            "valor_maximo",
            "expresion_regular",
            "mensaje_error",
            "usa_catalogo",
            "catalogo_asociado",
            "pregunta_padre_catalogo",
            "es_pregunta_geografica",
            "preguntas_dependientes_geograficas",
            "catalogo_departamento",
            "visible_por_defecto",
            "limpiar_respuesta_al_ocultar",
            "pregunta_origen_flujo_codigo",
            "codigo_catalogo_departamento",
            "permite_busqueda_catalogo",
            "limite_items_catalogo",
            "fuente_opciones",
            "opciones",
            "filas_matriz",
            "columnas_matriz",
            "reglas_origen",
            "comportamiento_interaccion",
        )

    def get_catalogo_asociado(self, pregunta: Pregunta) -> dict[str, str] | None:
        """Retorna metadata del catalogo asociado para consumo del frontend."""
        if not pregunta.usa_catalogo or pregunta.catalogo_asociado is None:
            return None

        catalogo = pregunta.catalogo_asociado
        mapa_traducciones = self.context.get("mapa_traducciones", {})
        nombre_catalogo = catalogo.nombre
        if mapa_traducciones:
            uuid_catalogo = resolver_uuid_entidad(catalogo, "Catalogo")
            nombre_catalogo = aplicar_texto_traducido(
                mapa_traducciones,
                "Catalogo",
                uuid_catalogo,
                "nombre",
                nombre_catalogo,
            )

        return {
            "codigo": catalogo.codigo,
            "nombre": nombre_catalogo,
            "tipo_catalogo": catalogo.tipo_catalogo,
            "endpoint_items": f"{PREFIJO_API_CATALOGOS}{catalogo.codigo}/items/",
        }

    def get_es_pregunta_geografica(self, pregunta: Pregunta) -> bool:
        """Indica si la pregunta pertenece a una jerarquia geografica parametrizable."""
        return es_pregunta_catalogo_geografico(pregunta)

    def get_preguntas_dependientes_geograficas(
        self,
        pregunta: Pregunta,
    ) -> list[dict[str, str]]:
        """Retorna metadata de preguntas geograficas dependientes directas o en cadena."""
        dependientes = obtener_dependientes_geograficos_ordenados(pregunta)
        mapa_traducciones = self.context.get("mapa_traducciones", {})
        resultado: list[dict[str, str]] = []

        for dependiente in dependientes:
            texto = dependiente.texto
            if mapa_traducciones:
                uuid_dependiente = resolver_uuid_entidad(dependiente, "Pregunta")
                texto = aplicar_texto_traducido(
                    mapa_traducciones,
                    "Pregunta",
                    uuid_dependiente,
                    "texto",
                    texto,
                )
            resultado.append(
                {
                    "codigo": dependiente.codigo,
                    "texto": texto,
                },
            )

        return resultado

    def get_catalogo_departamento(self, pregunta: Pregunta) -> dict[str, str] | None:
        """Retorna metadata del catalogo de departamentos para ubicacion geografica."""
        codigo_catalogo = pregunta.codigo_catalogo_departamento.strip()
        if not codigo_catalogo:
            return None

        catalogo = Catalogo.objects.filter(
            codigo=codigo_catalogo,
            esta_activo=True,
            esta_eliminado=False,
        ).first()
        if catalogo is None:
            return None

        return {
            "codigo": catalogo.codigo,
            "nombre": catalogo.nombre,
            "tipo_catalogo": catalogo.tipo_catalogo,
            "endpoint_items": f"{PREFIJO_API_CATALOGOS}{catalogo.codigo}/items/",
        }

    def get_pregunta_origen_flujo_codigo(self, pregunta: Pregunta) -> str | None:
        """Retorna el codigo de la pregunta origen del flujo visual si existe."""
        if pregunta.pregunta_origen_flujo_id is None:
            return None
        return pregunta.pregunta_origen_flujo.codigo

    def get_validacion_filtro(self, pregunta: Pregunta) -> dict[str, Any] | None:
        """Retorna metadata de validacion para preguntas filtro/preliminares."""
        return construir_metadata_validacion_filtro(pregunta)

    def get_pregunta_padre_catalogo(self, pregunta: Pregunta) -> dict[str, str] | None:
        """Retorna metadata de la pregunta padre de catalogo si existe."""
        if pregunta.pregunta_padre_catalogo is None:
            return None

        padre = pregunta.pregunta_padre_catalogo
        texto_padre = padre.texto
        mapa_traducciones = self.context.get("mapa_traducciones", {})
        if mapa_traducciones:
            uuid_padre = resolver_uuid_entidad(padre, "Pregunta")
            texto_padre = aplicar_texto_traducido(
                mapa_traducciones,
                "Pregunta",
                uuid_padre,
                "texto",
                texto_padre,
            )

        return {
            "codigo": padre.codigo,
            "texto": texto_padre,
        }

    def get_fuente_opciones(self, pregunta: Pregunta) -> str:
        """Retorna el origen de opciones de la pregunta."""
        return obtener_fuente_opciones_pregunta(pregunta)

    def to_representation(self, instancia: Pregunta) -> dict[str, Any]:
        """Serializa la pregunta aplicando traducciones si existen."""
        datos = super().to_representation(instancia)
        datos = self.aplicar_traducciones_campos(
            instancia,
            datos,
            ("texto", "descripcion", "tooltip", "mensaje_error"),
        )
        datos["contenido_accesible"] = self.construir_contenido_accesible_campos(
            instancia,
            ("texto", "tooltip"),
        )
        opciones = datos.get("opciones", [])
        datos["comportamiento_interaccion"] = construir_comportamiento_interaccion(
            instancia.tipo_pregunta,
            instancia.permite_otro,
            opciones,
        )
        datos["tooltip"] = tooltip_visible_en_api(
            bool(instancia.tiene_tooltip),
            str(datos.get("tooltip", "")),
        )
        return datos


class SeccionFormularioSerializer(
    TraduccionSerializerMixin,
    serializers.ModelSerializer,
):
    """Serializer para secciones con preguntas anidadas."""

    nombre_entidad = "SeccionFormulario"
    preguntas = PreguntaSerializer(many=True, read_only=True)

    class Meta:
        model = SeccionFormulario
        fields = (
            "codigo",
            "titulo",
            "descripcion",
            "texto_ayuda",
            "orden",
            "preguntas",
        )

    def to_representation(self, instancia: SeccionFormulario) -> dict[str, Any]:
        """Serializa la seccion aplicando traducciones si existen."""
        datos = super().to_representation(instancia)
        return self.aplicar_traducciones_campos(
            instancia,
            datos,
            ("titulo", "descripcion", "texto_ayuda"),
        )


class FormularioVersionResumenSerializer(serializers.ModelSerializer):
    """Serializer resumido de la version publicada."""

    class Meta:
        model = FormularioVersion
        fields = ("id", "numero_version")


class FormularioEstructuraSerializer(serializers.Serializer):
    """Serializer de la estructura completa de un formulario publicado."""

    uuid = serializers.UUIDField(read_only=True)
    codigo = serializers.CharField(read_only=True)
    nombre = serializers.CharField(read_only=True)
    descripcion = serializers.CharField(read_only=True)
    introduccion = serializers.CharField(read_only=True)
    objetivo = serializers.CharField(read_only=True)
    tipo_formulario = serializers.CharField(read_only=True)
    imagen_portada = serializers.CharField(read_only=True, allow_null=True)
    version = FormularioVersionResumenSerializer(read_only=True)
    textos = TextoFormularioSerializer(many=True, read_only=True)
    secciones = SeccionFormularioSerializer(many=True, read_only=True)

    def to_representation(
        self,
        instancia: FormularioEstructuraDatos,
    ) -> dict[str, object]:
        """Serializa el formulario con su version publicada y estructura anidada."""
        formulario = instancia.formulario
        version = instancia.version
        textos = getattr(version, "textos_activos", version.textos.all())
        secciones = getattr(version, "secciones_activas", version.secciones.all())

        codigo_idioma = normalizar_codigo_idioma(self.context.get("idioma"))
        uuids_estructura = recolectar_uuids_estructura_formulario(instancia)
        mapa_traducciones = construir_mapa_traducciones(
            codigo_idioma,
            uuids_estructura,
        )
        contexto_traduccion = {
            **self.context,
            "mapa_traducciones": mapa_traducciones,
            "idioma": codigo_idioma,
        }

        uuid_formulario = resolver_uuid_entidad(formulario, "Formulario")
        solicitud = self.context.get("request")

        return {
            "uuid": formulario.uuid,
            "codigo": formulario.codigo,
            "imagen_portada": construir_url_imagen_campo(
                formulario,
                "imagen_portada",
                solicitud,
                campo_repositorio="imagen_portada_repositorio",
            ),
            "nombre": aplicar_texto_traducido(
                mapa_traducciones,
                "Formulario",
                uuid_formulario,
                "nombre",
                formulario.nombre,
            ),
            "descripcion": aplicar_texto_traducido(
                mapa_traducciones,
                "Formulario",
                uuid_formulario,
                "descripcion",
                formulario.descripcion,
            ),
            "introduccion": aplicar_texto_traducido(
                mapa_traducciones,
                "Formulario",
                uuid_formulario,
                "introduccion",
                formulario.introduccion,
            ),
            "objetivo": aplicar_texto_traducido(
                mapa_traducciones,
                "Formulario",
                uuid_formulario,
                "objetivo",
                formulario.objetivo,
            ),
            "tipo_formulario": formulario.tipo_formulario,
            "version": FormularioVersionResumenSerializer(version).data,
            "textos": TextoFormularioSerializer(
                textos,
                many=True,
                context=contexto_traduccion,
            ).data,
            "secciones": SeccionFormularioSerializer(
                secciones,
                many=True,
                context=contexto_traduccion,
            ).data,
        }
