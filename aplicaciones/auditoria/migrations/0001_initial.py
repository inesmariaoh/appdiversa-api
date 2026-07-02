# Generated manually for auditoria transversal

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="RegistroAuditoria",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("entidad", models.CharField(max_length=150)),
                ("entidad_id", models.CharField(max_length=100)),
                (
                    "accion",
                    models.CharField(
                        choices=[
                            ("crear", "Crear"),
                            ("editar", "Editar"),
                            ("eliminar", "Eliminar"),
                            ("restaurar", "Restaurar"),
                            ("publicar", "Publicar"),
                            ("cerrar", "Cerrar"),
                            ("archivar", "Archivar"),
                            ("consultar", "Consultar"),
                            ("exportar", "Exportar"),
                            ("iniciar_sesion", "Iniciar sesion"),
                            ("finalizar_formulario", "Finalizar formulario"),
                            ("sincronizar", "Sincronizar"),
                        ],
                        max_length=30,
                    ),
                ),
                (
                    "identificador_keycloak",
                    models.CharField(blank=True, max_length=255),
                ),
                (
                    "uuid_sesion_anonima",
                    models.CharField(blank=True, max_length=100),
                ),
                ("ip", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.TextField(blank=True)),
                ("valor_anterior", models.JSONField(blank=True, null=True)),
                ("valor_nuevo", models.JSONField(blank=True, null=True)),
                ("descripcion", models.TextField(blank=True)),
                ("fecha_accion", models.DateTimeField(auto_now_add=True)),
                (
                    "usuario",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Registro de auditoria",
                "verbose_name_plural": "Registros de auditoria",
                "ordering": ["-fecha_accion"],
                "indexes": [
                    models.Index(
                        fields=["entidad", "entidad_id"],
                        name="auditoria_entidad_entidad_id_idx",
                    ),
                    models.Index(
                        fields=["accion"],
                        name="auditoria_accion_idx",
                    ),
                    models.Index(
                        fields=["usuario"],
                        name="auditoria_usuario_idx",
                    ),
                    models.Index(
                        fields=["identificador_keycloak"],
                        name="auditoria_keycloak_idx",
                    ),
                    models.Index(
                        fields=["uuid_sesion_anonima"],
                        name="auditoria_uuid_sesion_idx",
                    ),
                    models.Index(
                        fields=["fecha_accion"],
                        name="auditoria_fecha_accion_idx",
                    ),
                ],
            },
        ),
    ]
