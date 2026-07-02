"""
Estructura de resultado del motor de reglas.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ResultadoReglas:
    """Resultado agregado de la evaluacion de reglas condicionales."""

    preguntas_ocultas: list[str] = field(default_factory=list)
    preguntas_visibles: list[str] = field(default_factory=list)
    preguntas_deshabilitadas: list[str] = field(default_factory=list)
    preguntas_habilitadas: list[str] = field(default_factory=list)
    preguntas_obligatorias: list[str] = field(default_factory=list)
    preguntas_opcionales: list[str] = field(default_factory=list)
    saltar_a_pregunta: str | None = None
    saltar_a_seccion: str | None = None
    finalizar_formulario: bool = False
    no_aplica_formulario: bool = False
    mensajes: list[str] = field(default_factory=list)

    def agregar_codigo_pregunta(self, codigos: list[str], codigo: str | None) -> None:
        """Agrega un codigo de pregunta a una lista si no esta repetido."""
        if codigo and codigo not in codigos:
            codigos.append(codigo)

    def agregar_mensaje(self, mensaje: str) -> None:
        """Agrega un mensaje funcional si no esta vacio."""
        texto = mensaje.strip()
        if texto and texto not in self.mensajes:
            self.mensajes.append(texto)

    def to_dict(self) -> dict[str, Any]:
        """Convierte el resultado a un diccionario serializable."""
        return {
            "preguntas_ocultas": list(self.preguntas_ocultas),
            "preguntas_visibles": list(self.preguntas_visibles),
            "preguntas_deshabilitadas": list(self.preguntas_deshabilitadas),
            "preguntas_habilitadas": list(self.preguntas_habilitadas),
            "preguntas_obligatorias": list(self.preguntas_obligatorias),
            "preguntas_opcionales": list(self.preguntas_opcionales),
            "saltar_a_pregunta": self.saltar_a_pregunta,
            "saltar_a_seccion": self.saltar_a_seccion,
            "finalizar_formulario": self.finalizar_formulario,
            "no_aplica_formulario": self.no_aplica_formulario,
            "mensajes": list(self.mensajes),
        }
