-- MySQL dump 10.13  Distrib 8.0.45, for Linux (x86_64)
--
-- Host: localhost    Database: appdiversa
-- ------------------------------------------------------
-- Server version	8.0.45

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `archivos_archivorepositorio`
--

DROP TABLE IF EXISTS `archivos_archivorepositorio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `archivos_archivorepositorio` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_modificacion` datetime(6) NOT NULL,
  `fecha_eliminacion` datetime(6) DEFAULT NULL,
  `esta_eliminado` tinyint(1) NOT NULL,
  `uuid` char(32) NOT NULL,
  `nombre_original` varchar(300) NOT NULL,
  `nombre_fisico` varchar(300) NOT NULL,
  `extension` varchar(20) NOT NULL,
  `mime_type` varchar(150) NOT NULL,
  `tamano_bytes` bigint unsigned NOT NULL,
  `checksum_sha256` varchar(64) NOT NULL,
  `tipo_archivo` varchar(30) NOT NULL,
  `ruta_relativa` varchar(500) NOT NULL,
  `url_publica` varchar(500) NOT NULL,
  `es_publico` tinyint(1) NOT NULL,
  `origen` varchar(30) NOT NULL,
  `estado` varchar(20) NOT NULL,
  `descripcion` longtext NOT NULL,
  `metadatos` json DEFAULT NULL,
  `fecha_carga` datetime(6) NOT NULL,
  `usuario_keycloak` varchar(255) NOT NULL,
  `uuid_sesion` char(32) DEFAULT NULL,
  `creado_por_id` int DEFAULT NULL,
  `eliminado_por_id` int DEFAULT NULL,
  `modificado_por_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `archivos_archivorepo_creado_por_id_bc9909a5_fk_auth_user` (`creado_por_id`),
  KEY `archivos_archivorepo_eliminado_por_id_813decfb_fk_auth_user` (`eliminado_por_id`),
  KEY `archivos_archivorepo_modificado_por_id_76f3e83a_fk_auth_user` (`modificado_por_id`),
  KEY `archivos_ar_uuid_6cc166_idx` (`uuid`),
  KEY `archivos_ar_tipo_ar_4640ec_idx` (`tipo_archivo`),
  KEY `archivos_ar_estado_d74829_idx` (`estado`),
  KEY `archivos_ar_origen_62694c_idx` (`origen`),
  KEY `archivos_ar_checksu_ccb13b_idx` (`checksum_sha256`),
  KEY `archivos_ar_fecha_c_a26944_idx` (`fecha_carga`),
  CONSTRAINT `archivos_archivorepo_creado_por_id_bc9909a5_fk_auth_user` FOREIGN KEY (`creado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `archivos_archivorepo_eliminado_por_id_813decfb_fk_auth_user` FOREIGN KEY (`eliminado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `archivos_archivorepo_modificado_por_id_76f3e83a_fk_auth_user` FOREIGN KEY (`modificado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `archivos_archivorepositorio_chk_1` CHECK ((`tamano_bytes` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `archivos_archivorepositorio`
--

LOCK TABLES `archivos_archivorepositorio` WRITE;
/*!40000 ALTER TABLE `archivos_archivorepositorio` DISABLE KEYS */;
/*!40000 ALTER TABLE `archivos_archivorepositorio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auditoria_registroauditoria`
--

DROP TABLE IF EXISTS `auditoria_registroauditoria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auditoria_registroauditoria` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `entidad` varchar(150) NOT NULL,
  `entidad_id` varchar(100) NOT NULL,
  `accion` varchar(30) NOT NULL,
  `identificador_keycloak` varchar(255) NOT NULL,
  `uuid_sesion_anonima` varchar(100) NOT NULL,
  `ip` char(39) DEFAULT NULL,
  `user_agent` longtext NOT NULL,
  `valor_anterior` json DEFAULT NULL,
  `valor_nuevo` json DEFAULT NULL,
  `descripcion` longtext NOT NULL,
  `fecha_accion` datetime(6) NOT NULL,
  `usuario_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `auditoria_r_entidad_0cbcba_idx` (`entidad`,`entidad_id`),
  KEY `auditoria_r_accion_dae68a_idx` (`accion`),
  KEY `auditoria_r_usuario_5ab20b_idx` (`usuario_id`),
  KEY `auditoria_r_identif_885d7e_idx` (`identificador_keycloak`),
  KEY `auditoria_r_uuid_se_b64bae_idx` (`uuid_sesion_anonima`),
  KEY `auditoria_r_fecha_a_82c07a_idx` (`fecha_accion`),
  CONSTRAINT `auditoria_registroauditoria_usuario_id_5900964c_fk_auth_user_id` FOREIGN KEY (`usuario_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auditoria_registroauditoria`
--

LOCK TABLES `auditoria_registroauditoria` WRITE;
/*!40000 ALTER TABLE `auditoria_registroauditoria` DISABLE KEYS */;
INSERT INTO `auditoria_registroauditoria` VALUES (1,'SesionAnonima','1','iniciar_sesion','','','172.20.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36',NULL,'{\"id\": 1, \"estado\": \"iniciada\", \"idioma\": \"es-CO\", \"creado_por\": null, \"es_offline\": false, \"formulario\": \"1\", \"user_agent\": \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36\", \"uuid_sesion\": \"11111111-1111-1111-1111-111111111111\", \"direccion_ip\": \"172.20.0.1\", \"fecha_inicio\": \"2026-06-28T17:30:43.229537+00:00\", \"zona_horaria\": \"America/Bogota\", \"eliminado_por\": null, \"esta_eliminado\": false, \"fecha_creacion\": \"2026-06-28T17:30:43.229500+00:00\", \"modificado_por\": null, \"fecha_eliminacion\": null, \"fecha_modificacion\": \"2026-06-28T17:30:43.229515+00:00\", \"version_formulario\": \"1\", \"fecha_sincronizacion\": null, \"fecha_ultima_actividad\": \"2026-06-28T17:30:43.229144+00:00\"}','','2026-06-28 17:30:43.236910',NULL),(2,'Respuesta','1','crear','','','172.20.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36',NULL,'{\"id\": 1, \"sesion\": \"1\", \"latitud\": null, \"longitud\": null, \"pregunta\": \"1\", \"creado_por\": null, \"valor_hora\": null, \"valor_json\": null, \"observacion\": \"\", \"valor_fecha\": null, \"valor_texto\": \"\", \"archivo_ruta\": \"\", \"valor_numero\": \"25\", \"eliminado_por\": null, \"archivo_nombre\": \"\", \"esta_eliminado\": false, \"fecha_creacion\": \"2026-06-28T17:31:19.657955+00:00\", \"modificado_por\": null, \"valor_booleano\": null, \"origen_respuesta\": \"web\", \"precision_metros\": null, \"valor_fecha_hora\": null, \"fecha_eliminacion\": null, \"version_respuesta\": 1, \"fecha_modificacion\": \"2026-06-28T17:31:19.657976+00:00\", \"fecha_respuesta_cliente\": null, \"requiere_sincronizacion\": false, \"fecha_respuesta_servidor\": \"2026-06-28T17:31:19.658095+00:00\"}','','2026-06-28 17:31:19.659434',NULL),(3,'Respuesta','2','crear','','','172.20.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36',NULL,'{\"id\": 2, \"sesion\": \"1\", \"latitud\": null, \"longitud\": null, \"pregunta\": \"2\", \"creado_por\": null, \"valor_hora\": null, \"valor_json\": null, \"observacion\": \"\", \"valor_fecha\": null, \"valor_texto\": \"Mujer\", \"archivo_ruta\": \"\", \"valor_numero\": null, \"eliminado_por\": null, \"archivo_nombre\": \"\", \"esta_eliminado\": false, \"fecha_creacion\": \"2026-06-28T17:31:46.823593+00:00\", \"modificado_por\": null, \"valor_booleano\": null, \"origen_respuesta\": \"web\", \"precision_metros\": null, \"valor_fecha_hora\": null, \"fecha_eliminacion\": null, \"version_respuesta\": 1, \"fecha_modificacion\": \"2026-06-28T17:31:46.823628+00:00\", \"fecha_respuesta_cliente\": null, \"requiere_sincronizacion\": false, \"fecha_respuesta_servidor\": \"2026-06-28T17:31:46.823684+00:00\"}','','2026-06-28 17:31:46.824488',NULL),(4,'SesionAnonima','1','consultar','','','172.20.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36',NULL,'{\"estado\": \"en_proceso\", \"es_valido\": true, \"uuid_sesion\": \"11111111-1111-1111-1111-111111111111\", \"total_pendientes\": 0}','Validacion de finalizacion de formulario.','2026-06-28 17:33:03.338661',NULL),(5,'SesionAnonima','1','finalizar_formulario','','','172.20.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36',NULL,'{\"estado\": \"finalizada\", \"uuid_sesion\": \"11111111-1111-1111-1111-111111111111\", \"total_respuestas\": 2}','El formulario fue finalizado correctamente.','2026-06-28 17:33:29.221708',NULL),(6,'ConfiguracionInterfaz','1','editar','','','172.20.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36','{\"id\": 1, \"favicon\": null, \"creado_por\": null, \"esta_activa\": true, \"color_acento\": \"\", \"nombre_corto\": \"AppDiversa\", \"eliminado_por\": null, \"color_primario\": \"\", \"esta_eliminado\": false, \"fecha_creacion\": \"2026-06-28T16:32:07.169636+00:00\", \"logo_principal\": \"interfaz/logos/Propuesta_2.jpg\", \"modificado_por\": null, \"logo_secundario\": null, \"color_secundario\": \"\", \"texto_pie_pagina\": \"Pie de Página App Diversa\", \"fecha_eliminacion\": null, \"nombre_aplicativo\": \"App Diversa\", \"fecha_modificacion\": \"2026-06-28T16:32:07.169660+00:00\", \"logo_institucional\": \"interfaz/logos/Logo_DANE_color_Horizontal.png\", \"descripcion_aplicativo\": \"Descripción App Diversa\"}','{\"id\": 1, \"favicon\": null, \"creado_por\": null, \"esta_activa\": true, \"color_acento\": \"\", \"nombre_corto\": \"AppDiversa\", \"eliminado_por\": null, \"color_primario\": \"\", \"esta_eliminado\": false, \"fecha_creacion\": \"2026-06-28T16:32:07.169636+00:00\", \"logo_principal\": \"interfaz/logos/Propuesta_2.jpg\", \"modificado_por\": \"1\", \"logo_secundario\": null, \"color_secundario\": \"\", \"texto_pie_pagina\": \"Pie de Página App Diversa\", \"fecha_eliminacion\": null, \"nombre_aplicativo\": \"App Diversa\", \"fecha_modificacion\": \"2026-06-28T18:12:45.442727+00:00\", \"logo_institucional\": \"interfaz/logos/logos_dane_sen_qXXFwQI.png\", \"descripcion_aplicativo\": \"Descripción App Diversa\"}','','2026-06-28 18:12:45.469883',1),(7,'LogoInterfaz','3','editar','','','172.20.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36','{\"id\": 3, \"orden\": 3, \"codigo\": \"logo_institucional\", \"imagen\": \"interfaz/logos/logos_dane_sen_qXXFwQI.png\", \"nombre\": \"Logo institucional\", \"creado_por\": null, \"esta_activo\": true, \"eliminado_por\": null, \"esta_eliminado\": false, \"fecha_creacion\": \"2026-06-28T21:28:33.877327+00:00\", \"modificado_por\": null, \"fecha_eliminacion\": null, \"texto_alternativo\": \"\", \"fecha_modificacion\": \"2026-06-28T21:28:33.877341+00:00\", \"archivo_repositorio\": null, \"configuracion_interfaz\": \"1\"}','{\"id\": 3, \"orden\": 3, \"codigo\": \"logo_institucional\", \"imagen\": \"interfaz/logos/logos_dane_sen_qXXFwQI.png\", \"nombre\": \"Logo institucional\", \"creado_por\": null, \"esta_activo\": true, \"eliminado_por\": null, \"esta_eliminado\": false, \"fecha_creacion\": \"2026-06-28T21:28:33.877327+00:00\", \"modificado_por\": \"1\", \"fecha_eliminacion\": null, \"texto_alternativo\": \"Logo DANE - SEN\", \"fecha_modificacion\": \"2026-06-28T21:31:20.385088+00:00\", \"archivo_repositorio\": null, \"configuracion_interfaz\": \"1\"}','','2026-06-28 21:31:20.386146',1),(8,'LogoInterfaz','2','editar','','','172.20.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36','{\"id\": 2, \"orden\": 1, \"codigo\": \"logo_principal\", \"imagen\": \"interfaz/logos/Propuesta_2.jpg\", \"nombre\": \"Logo principal\", \"creado_por\": null, \"esta_activo\": true, \"eliminado_por\": null, \"esta_eliminado\": false, \"fecha_creacion\": \"2026-06-28T21:28:33.874313+00:00\", \"modificado_por\": null, \"fecha_eliminacion\": null, \"texto_alternativo\": \"\", \"fecha_modificacion\": \"2026-06-28T21:28:33.874330+00:00\", \"archivo_repositorio\": null, \"configuracion_interfaz\": \"1\"}','{\"id\": 2, \"orden\": 1, \"codigo\": \"logo_principal\", \"imagen\": \"interfaz/logos/Propuesta_2.jpg\", \"nombre\": \"Logo principal\", \"creado_por\": null, \"esta_activo\": true, \"eliminado_por\": null, \"esta_eliminado\": false, \"fecha_creacion\": \"2026-06-28T21:28:33.874313+00:00\", \"modificado_por\": \"1\", \"fecha_eliminacion\": null, \"texto_alternativo\": \"Logo Mi Dato Cuenta\", \"fecha_modificacion\": \"2026-06-28T21:31:35.781817+00:00\", \"archivo_repositorio\": null, \"configuracion_interfaz\": \"1\"}','','2026-06-28 21:31:35.782755',1),(9,'LogoInterfaz','2','editar','','','172.20.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36','{\"id\": 2, \"orden\": 1, \"codigo\": \"logo_principal\", \"imagen\": \"interfaz/logos/Propuesta_2.jpg\", \"nombre\": \"Logo principal\", \"creado_por\": null, \"esta_activo\": true, \"eliminado_por\": null, \"esta_eliminado\": false, \"fecha_creacion\": \"2026-06-28T21:28:33.874313+00:00\", \"modificado_por\": \"1\", \"fecha_eliminacion\": null, \"texto_alternativo\": \"Logo Mi Dato Cuenta\", \"fecha_modificacion\": \"2026-06-28T21:31:35.781817+00:00\", \"archivo_repositorio\": null, \"configuracion_interfaz\": \"1\"}','{\"id\": 2, \"orden\": 1, \"codigo\": \"logo_principal\", \"imagen\": \"interfaz/logos/Propuesta_2.jpg\", \"nombre\": \"Logo principal\", \"creado_por\": null, \"esta_activo\": true, \"eliminado_por\": null, \"esta_eliminado\": false, \"fecha_creacion\": \"2026-06-28T21:28:33.874313+00:00\", \"modificado_por\": \"1\", \"fecha_eliminacion\": null, \"texto_alternativo\": \"Logo Mi Dato Cuenta\", \"fecha_modificacion\": \"2026-06-28T21:31:55.721166+00:00\", \"archivo_repositorio\": null, \"configuracion_interfaz\": \"1\"}','','2026-06-28 21:31:55.721941',1),(10,'LogoInterfaz','1','eliminar','','','172.20.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36','{\"id\": 1, \"orden\": 3, \"codigo\": \"logo_institucional\", \"imagen\": \"interfaz/logos/logo_institucional_umQ3lNf.png\", \"nombre\": \"Logo institucional\", \"creado_por\": null, \"esta_activo\": true, \"eliminado_por\": null, \"esta_eliminado\": false, \"fecha_creacion\": \"2026-06-28T21:28:33.873160+00:00\", \"modificado_por\": null, \"fecha_eliminacion\": null, \"texto_alternativo\": \"\", \"fecha_modificacion\": \"2026-06-28T21:28:33.873178+00:00\", \"archivo_repositorio\": null, \"configuracion_interfaz\": \"2\"}',NULL,'Eliminacion logica del registro.','2026-06-28 21:32:05.008143',1),(11,'Formulario','2','crear','','','172.20.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36',NULL,'{\"id\": 2, \"uuid\": \"efe7bf97-dec4-4b02-a774-d49dbd2303db\", \"codigo\": \"SERV-01\", \"estado\": \"borrador\", \"nombre\": \"Encuesta de Acceso y Prestación de Servicios\", \"objetivo\": \"Objetivo: Encuesta de Acceso y Prestación de Servicios\", \"fecha_fin\": null, \"creado_por\": \"1\", \"descripcion\": \"Descripción Encuesta de Acceso y Prestación de Servicios\", \"fecha_inicio\": null, \"introduccion\": \"Introducción Encuesta de Acceso y Prestación de Servicios\", \"eliminado_por\": null, \"esta_eliminado\": false, \"fecha_creacion\": \"2026-06-29T14:41:42.256077+00:00\", \"imagen_portada\": \"formularios/portadas/image_proxma_enc.png\", \"modificado_por\": \"1\", \"version_actual\": 1, \"permite_anonimo\": true, \"permite_offline\": true, \"tipo_formulario\": \"encuesta\", \"fecha_eliminacion\": null, \"fecha_modificacion\": \"2026-06-29T14:41:42.256108+00:00\", \"permite_registro_final\": true, \"tiempo_estimado_minutos\": 5, \"imagen_portada_repositorio\": null, \"permite_multiples_respuestas\": false}','','2026-06-29 14:41:42.287995',1),(12,'Formulario','2','editar','','','172.20.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36','{\"id\": 2, \"uuid\": \"efe7bf97-dec4-4b02-a774-d49dbd2303db\", \"codigo\": \"SERV-01\", \"estado\": \"borrador\", \"nombre\": \"Encuesta de Acceso y Prestación de Servicios\", \"objetivo\": \"Objetivo: Encuesta de Acceso y Prestación de Servicios\", \"fecha_fin\": null, \"creado_por\": \"1\", \"descripcion\": \"Descripción Encuesta de Acceso y Prestación de Servicios\", \"fecha_inicio\": null, \"introduccion\": \"Introducción Encuesta de Acceso y Prestación de Servicios\", \"eliminado_por\": null, \"esta_eliminado\": false, \"fecha_creacion\": \"2026-06-29T14:41:42.256077+00:00\", \"imagen_portada\": \"formularios/portadas/image_proxma_enc.png\", \"modificado_por\": \"1\", \"version_actual\": 1, \"permite_anonimo\": true, \"permite_offline\": true, \"tipo_formulario\": \"encuesta\", \"fecha_eliminacion\": null, \"fecha_modificacion\": \"2026-06-29T14:41:42.256108+00:00\", \"permite_registro_final\": true, \"tiempo_estimado_minutos\": 5, \"imagen_portada_repositorio\": null, \"permite_multiples_respuestas\": false}','{\"id\": 2, \"uuid\": \"efe7bf97-dec4-4b02-a774-d49dbd2303db\", \"codigo\": \"SERV-01\", \"estado\": \"publicado\", \"nombre\": \"Encuesta de Acceso y Prestación de Servicios\", \"objetivo\": \"Objetivo: Encuesta de Acceso y Prestación de Servicios\", \"fecha_fin\": null, \"creado_por\": \"1\", \"descripcion\": \"Descripción Encuesta de Acceso y Prestación de Servicios\", \"fecha_inicio\": null, \"introduccion\": \"Introducción Encuesta de Acceso y Prestación de Servicios\", \"eliminado_por\": null, \"esta_eliminado\": false, \"fecha_creacion\": \"2026-06-29T14:41:42.256077+00:00\", \"imagen_portada\": \"formularios/portadas/image_proxma_enc.png\", \"modificado_por\": \"1\", \"version_actual\": 1, \"permite_anonimo\": true, \"permite_offline\": true, \"tipo_formulario\": \"encuesta\", \"fecha_eliminacion\": null, \"fecha_modificacion\": \"2026-06-29T14:42:30.526226+00:00\", \"permite_registro_final\": true, \"tiempo_estimado_minutos\": 5, \"imagen_portada_repositorio\": null, \"permite_multiples_respuestas\": false}','','2026-06-29 14:42:30.527625',1),(13,'Formulario','1','editar','','','172.20.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36','{\"id\": 1, \"uuid\": \"1b5f64f9-cd66-48f6-b210-ce6b371bb8fb\", \"codigo\": \"DISC-001\", \"estado\": \"publicado\", \"nombre\": \"Encuesta de Discriminación\", \"objetivo\": \"Objetivo Encuesta de Discriminación\", \"fecha_fin\": null, \"creado_por\": null, \"descripcion\": \"Descripción Encuesta de Discriminación\", \"fecha_inicio\": null, \"introduccion\": \"Introducción Encuesta de Discriminación\", \"eliminado_por\": null, \"esta_eliminado\": false, \"fecha_creacion\": \"2026-06-28T15:28:46.339357+00:00\", \"imagen_portada\": null, \"modificado_por\": null, \"version_actual\": 1, \"permite_anonimo\": true, \"permite_offline\": true, \"tipo_formulario\": \"encuesta\", \"fecha_eliminacion\": null, \"fecha_modificacion\": \"2026-06-28T15:28:46.339376+00:00\", \"permite_registro_final\": true, \"tiempo_estimado_minutos\": 10, \"imagen_portada_repositorio\": null, \"permite_multiples_respuestas\": false}','{\"id\": 1, \"uuid\": \"1b5f64f9-cd66-48f6-b210-ce6b371bb8fb\", \"codigo\": \"DISC-001\", \"estado\": \"publicado\", \"nombre\": \"Encuesta de Discriminación\", \"objetivo\": \"Objetivo Encuesta de Discriminación\", \"fecha_fin\": null, \"creado_por\": null, \"descripcion\": \"Descripción Encuesta de Discriminación\", \"fecha_inicio\": null, \"introduccion\": \"Introducción Encuesta de Discriminación\", \"eliminado_por\": null, \"esta_eliminado\": false, \"fecha_creacion\": \"2026-06-28T15:28:46.339357+00:00\", \"imagen_portada\": \"formularios/portadas/image_ecu_disponible.png\", \"modificado_por\": \"1\", \"version_actual\": 1, \"permite_anonimo\": true, \"permite_offline\": true, \"tipo_formulario\": \"encuesta\", \"fecha_eliminacion\": null, \"fecha_modificacion\": \"2026-06-29T14:43:25.740388+00:00\", \"permite_registro_final\": true, \"tiempo_estimado_minutos\": 10, \"imagen_portada_repositorio\": null, \"permite_multiples_respuestas\": false}','','2026-06-29 14:43:25.763265',1),(14,'Formulario','2','editar','','','172.20.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36','{\"id\": 2, \"uuid\": \"efe7bf97-dec4-4b02-a774-d49dbd2303db\", \"orden\": 1, \"codigo\": \"SERV-01\", \"estado\": \"publicado\", \"nombre\": \"Encuesta de Acceso y Prestación de Servicios\", \"objetivo\": \"Objetivo: Encuesta de Acceso y Prestación de Servicios\", \"fecha_fin\": null, \"creado_por\": \"1\", \"descripcion\": \"Descripción Encuesta de Acceso y Prestación de Servicios\", \"fecha_inicio\": null, \"introduccion\": \"Introducción Encuesta de Acceso y Prestación de Servicios\", \"eliminado_por\": null, \"esta_eliminado\": false, \"fecha_creacion\": \"2026-06-29T14:41:42.256077+00:00\", \"imagen_portada\": \"formularios/portadas/image_proxma_enc.png\", \"modificado_por\": \"1\", \"version_actual\": 1, \"permite_anonimo\": true, \"permite_offline\": true, \"tipo_formulario\": \"encuesta\", \"fecha_eliminacion\": null, \"fecha_modificacion\": \"2026-06-29T14:42:30.526226+00:00\", \"permite_registro_final\": true, \"tiempo_estimado_minutos\": 5, \"imagen_portada_repositorio\": null, \"permite_multiples_respuestas\": false}','{\"id\": 2, \"uuid\": \"efe7bf97-dec4-4b02-a774-d49dbd2303db\", \"orden\": 2, \"codigo\": \"SERV-01\", \"estado\": \"publicado\", \"nombre\": \"Encuesta de Acceso y Prestación de Servicios\", \"objetivo\": \"Objetivo: Encuesta de Acceso y Prestación de Servicios\", \"fecha_fin\": null, \"creado_por\": \"1\", \"descripcion\": \"Descripción Encuesta de Acceso y Prestación de Servicios\", \"fecha_inicio\": null, \"introduccion\": \"Introducción Encuesta de Acceso y Prestación de Servicios\", \"eliminado_por\": null, \"esta_eliminado\": false, \"fecha_creacion\": \"2026-06-29T14:41:42.256077+00:00\", \"imagen_portada\": \"formularios/portadas/image_proxma_enc.png\", \"modificado_por\": \"1\", \"version_actual\": 1, \"permite_anonimo\": true, \"permite_offline\": true, \"tipo_formulario\": \"encuesta\", \"fecha_eliminacion\": null, \"fecha_modificacion\": \"2026-07-01T00:20:56.897356+00:00\", \"permite_registro_final\": true, \"tiempo_estimado_minutos\": 5, \"imagen_portada_repositorio\": null, \"permite_multiples_respuestas\": false}','','2026-07-01 00:20:56.899080',1),(15,'Formulario','1','editar','','','172.20.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36','{\"id\": 1, \"uuid\": \"1b5f64f9-cd66-48f6-b210-ce6b371bb8fb\", \"orden\": 2, \"codigo\": \"DISC-001\", \"estado\": \"publicado\", \"nombre\": \"Encuesta de Discriminación\", \"objetivo\": \"Objetivo Encuesta de Discriminación\", \"fecha_fin\": null, \"creado_por\": null, \"descripcion\": \"Descripción Encuesta de Discriminación\", \"fecha_inicio\": null, \"introduccion\": \"Introducción Encuesta de Discriminación\", \"eliminado_por\": null, \"esta_eliminado\": false, \"fecha_creacion\": \"2026-06-28T15:28:46.339357+00:00\", \"imagen_portada\": \"formularios/portadas/image_ecu_disponible.png\", \"modificado_por\": \"1\", \"version_actual\": 1, \"permite_anonimo\": true, \"permite_offline\": true, \"tipo_formulario\": \"encuesta\", \"fecha_eliminacion\": null, \"fecha_modificacion\": \"2026-06-29T14:43:25.740388+00:00\", \"permite_registro_final\": true, \"tiempo_estimado_minutos\": 10, \"imagen_portada_repositorio\": null, \"permite_multiples_respuestas\": false}','{\"id\": 1, \"uuid\": \"1b5f64f9-cd66-48f6-b210-ce6b371bb8fb\", \"orden\": 1, \"codigo\": \"DISC-001\", \"estado\": \"publicado\", \"nombre\": \"Encuesta de Discriminación\", \"objetivo\": \"Objetivo Encuesta de Discriminación\", \"fecha_fin\": null, \"creado_por\": null, \"descripcion\": \"Descripción Encuesta de Discriminación\", \"fecha_inicio\": null, \"introduccion\": \"Introducción Encuesta de Discriminación\", \"eliminado_por\": null, \"esta_eliminado\": false, \"fecha_creacion\": \"2026-06-28T15:28:46.339357+00:00\", \"imagen_portada\": \"formularios/portadas/image_ecu_disponible.png\", \"modificado_por\": \"1\", \"version_actual\": 1, \"permite_anonimo\": true, \"permite_offline\": true, \"tipo_formulario\": \"encuesta\", \"fecha_eliminacion\": null, \"fecha_modificacion\": \"2026-07-01T00:21:06.495429+00:00\", \"permite_registro_final\": true, \"tiempo_estimado_minutos\": 10, \"imagen_portada_repositorio\": null, \"permite_multiples_respuestas\": false}','','2026-07-01 00:21:06.496278',1),(16,'SesionAnonima','2','iniciar_sesion','','','172.20.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36',NULL,'{\"id\": 2, \"estado\": \"iniciada\", \"idioma\": \"es\", \"creado_por\": null, \"es_offline\": false, \"formulario\": \"1\", \"user_agent\": \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36\", \"uuid_sesion\": \"435e6b59-1edd-4e31-a075-7a09766a09f9\", \"direccion_ip\": \"172.20.0.1\", \"fecha_inicio\": \"2026-07-01T01:20:35.134307+00:00\", \"zona_horaria\": \"\", \"eliminado_por\": null, \"esta_eliminado\": false, \"fecha_creacion\": \"2026-07-01T01:20:35.134265+00:00\", \"modificado_por\": null, \"fecha_eliminacion\": null, \"fecha_modificacion\": \"2026-07-01T01:20:35.134284+00:00\", \"version_formulario\": \"1\", \"fecha_sincronizacion\": null, \"fecha_ultima_actividad\": \"2026-07-01T01:20:35.133843+00:00\"}','','2026-07-01 01:20:35.147052',NULL),(17,'SesionAnonima','3','iniciar_sesion','','','172.20.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36',NULL,'{\"id\": 3, \"estado\": \"iniciada\", \"idioma\": \"es\", \"creado_por\": null, \"es_offline\": false, \"formulario\": \"1\", \"user_agent\": \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36\", \"uuid_sesion\": \"e92e2999-7f53-4091-a482-853d73e83d08\", \"direccion_ip\": \"172.20.0.1\", \"fecha_inicio\": \"2026-07-01T01:28:00.052969+00:00\", \"zona_horaria\": \"\", \"eliminado_por\": null, \"esta_eliminado\": false, \"fecha_creacion\": \"2026-07-01T01:28:00.052915+00:00\", \"modificado_por\": null, \"fecha_eliminacion\": null, \"fecha_modificacion\": \"2026-07-01T01:28:00.052939+00:00\", \"version_formulario\": \"1\", \"fecha_sincronizacion\": null, \"fecha_ultima_actividad\": \"2026-07-01T01:28:00.052409+00:00\"}','','2026-07-01 01:28:00.063374',NULL);
/*!40000 ALTER TABLE `auditoria_registroauditoria` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=125 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session'),(25,'Can add Pregunta',7,'add_pregunta'),(26,'Can change Pregunta',7,'change_pregunta'),(27,'Can delete Pregunta',7,'delete_pregunta'),(28,'Can view Pregunta',7,'view_pregunta'),(29,'Can add Catalogo geografico',8,'add_catalogogeografico'),(30,'Can change Catalogo geografico',8,'change_catalogogeografico'),(31,'Can delete Catalogo geografico',8,'delete_catalogogeografico'),(32,'Can view Catalogo geografico',8,'view_catalogogeografico'),(33,'Can add Formulario',9,'add_formulario'),(34,'Can change Formulario',9,'change_formulario'),(35,'Can delete Formulario',9,'delete_formulario'),(36,'Can view Formulario',9,'view_formulario'),(37,'Can add Version de formulario',10,'add_formularioversion'),(38,'Can change Version de formulario',10,'change_formularioversion'),(39,'Can delete Version de formulario',10,'delete_formularioversion'),(40,'Can view Version de formulario',10,'view_formularioversion'),(41,'Can add Opcion de respuesta',11,'add_opcionrespuesta'),(42,'Can change Opcion de respuesta',11,'change_opcionrespuesta'),(43,'Can delete Opcion de respuesta',11,'delete_opcionrespuesta'),(44,'Can view Opcion de respuesta',11,'view_opcionrespuesta'),(45,'Can add Columna de matriz',12,'add_preguntamatrizcolumna'),(46,'Can change Columna de matriz',12,'change_preguntamatrizcolumna'),(47,'Can delete Columna de matriz',12,'delete_preguntamatrizcolumna'),(48,'Can view Columna de matriz',12,'view_preguntamatrizcolumna'),(49,'Can add Fila de matriz',13,'add_preguntamatrizfila'),(50,'Can change Fila de matriz',13,'change_preguntamatrizfila'),(51,'Can delete Fila de matriz',13,'delete_preguntamatrizfila'),(52,'Can view Fila de matriz',13,'view_preguntamatrizfila'),(53,'Can add Seccion de formulario',14,'add_seccionformulario'),(54,'Can change Seccion de formulario',14,'change_seccionformulario'),(55,'Can delete Seccion de formulario',14,'delete_seccionformulario'),(56,'Can view Seccion de formulario',14,'view_seccionformulario'),(57,'Can add Regla de pregunta',15,'add_reglapregunta'),(58,'Can change Regla de pregunta',15,'change_reglapregunta'),(59,'Can delete Regla de pregunta',15,'delete_reglapregunta'),(60,'Can view Regla de pregunta',15,'view_reglapregunta'),(61,'Can add Texto de formulario',16,'add_textoformulario'),(62,'Can change Texto de formulario',16,'change_textoformulario'),(63,'Can delete Texto de formulario',16,'delete_textoformulario'),(64,'Can view Texto de formulario',16,'view_textoformulario'),(65,'Can add Configuracion de interfaz',17,'add_configuracioninterfaz'),(66,'Can change Configuracion de interfaz',17,'change_configuracioninterfaz'),(67,'Can delete Configuracion de interfaz',17,'delete_configuracioninterfaz'),(68,'Can view Configuracion de interfaz',17,'view_configuracioninterfaz'),(69,'Can add Respuesta',18,'add_respuesta'),(70,'Can change Respuesta',18,'change_respuesta'),(71,'Can delete Respuesta',18,'delete_respuesta'),(72,'Can view Respuesta',18,'view_respuesta'),(73,'Can add Sesion anonima',19,'add_sesionanonima'),(74,'Can change Sesion anonima',19,'change_sesionanonima'),(75,'Can delete Sesion anonima',19,'delete_sesionanonima'),(76,'Can view Sesion anonima',19,'view_sesionanonima'),(77,'Can add Registro de auditoria',20,'add_registroauditoria'),(78,'Can change Registro de auditoria',20,'change_registroauditoria'),(79,'Can delete Registro de auditoria',20,'delete_registroauditoria'),(80,'Can view Registro de auditoria',20,'view_registroauditoria'),(81,'Can add Catalogo',21,'add_catalogo'),(82,'Can change Catalogo',21,'change_catalogo'),(83,'Can delete Catalogo',21,'delete_catalogo'),(84,'Can view Catalogo',21,'view_catalogo'),(85,'Can add Item de catalogo',22,'add_itemcatalogo'),(86,'Can change Item de catalogo',22,'change_itemcatalogo'),(87,'Can delete Item de catalogo',22,'delete_itemcatalogo'),(88,'Can view Item de catalogo',22,'view_itemcatalogo'),(89,'Can add Idioma',23,'add_idioma'),(90,'Can change Idioma',23,'change_idioma'),(91,'Can delete Idioma',23,'delete_idioma'),(92,'Can view Idioma',23,'view_idioma'),(93,'Can add Traduccion de contenido',24,'add_traduccioncontenido'),(94,'Can change Traduccion de contenido',24,'change_traduccioncontenido'),(95,'Can delete Traduccion de contenido',24,'delete_traduccioncontenido'),(96,'Can view Traduccion de contenido',24,'view_traduccioncontenido'),(97,'Can add Archivo de repositorio',25,'add_archivorepositorio'),(98,'Can change Archivo de repositorio',25,'change_archivorepositorio'),(99,'Can delete Archivo de repositorio',25,'delete_archivorepositorio'),(100,'Can view Archivo de repositorio',25,'view_archivorepositorio'),(101,'Can add Plantilla de notificacion',26,'add_plantillanotificacion'),(102,'Can change Plantilla de notificacion',26,'change_plantillanotificacion'),(103,'Can delete Plantilla de notificacion',26,'delete_plantillanotificacion'),(104,'Can view Plantilla de notificacion',26,'view_plantillanotificacion'),(105,'Can add Notificacion',27,'add_notificacion'),(106,'Can change Notificacion',27,'change_notificacion'),(107,'Can delete Notificacion',27,'delete_notificacion'),(108,'Can view Notificacion',27,'view_notificacion'),(109,'Can add Exportacion',28,'add_exportacion'),(110,'Can change Exportacion',28,'change_exportacion'),(111,'Can delete Exportacion',28,'delete_exportacion'),(112,'Can view Exportacion',28,'view_exportacion'),(113,'Can add Conflicto de sincronizacion',29,'add_conflictosincronizacion'),(114,'Can change Conflicto de sincronizacion',29,'change_conflictosincronizacion'),(115,'Can delete Conflicto de sincronizacion',29,'delete_conflictosincronizacion'),(116,'Can view Conflicto de sincronizacion',29,'view_conflictosincronizacion'),(117,'Can add Operacion de sincronizacion',30,'add_operacionsincronizacion'),(118,'Can change Operacion de sincronizacion',30,'change_operacionsincronizacion'),(119,'Can delete Operacion de sincronizacion',30,'delete_operacionsincronizacion'),(120,'Can view Operacion de sincronizacion',30,'view_operacionsincronizacion'),(121,'Can add Logo de interfaz',31,'add_logointerfaz'),(122,'Can change Logo de interfaz',31,'change_logointerfaz'),(123,'Can delete Logo de interfaz',31,'delete_logointerfaz'),(124,'Can view Logo de interfaz',31,'view_logointerfaz');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$1000000$C9hM5trBpVAR59YZEIsLYz$A3Pkzg4oSknAsk/XQjbbzEXxMtrAc2CGTWhdg74a2P4=','2026-07-01 01:26:52.554830',1,'admin','','','imoliverosh@dane.gov.co',1,1,'2026-06-28 14:58:59.751379');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `catalogos_catalogo`
--

DROP TABLE IF EXISTS `catalogos_catalogo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `catalogos_catalogo` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_modificacion` datetime(6) NOT NULL,
  `fecha_eliminacion` datetime(6) DEFAULT NULL,
  `esta_eliminado` tinyint(1) NOT NULL,
  `codigo` varchar(100) NOT NULL,
  `nombre` varchar(255) NOT NULL,
  `descripcion` longtext NOT NULL,
  `tipo_catalogo` varchar(100) NOT NULL,
  `esta_activo` tinyint(1) NOT NULL,
  `es_sistema` tinyint(1) NOT NULL,
  `orden` int unsigned NOT NULL,
  `creado_por_id` int DEFAULT NULL,
  `eliminado_por_id` int DEFAULT NULL,
  `modificado_por_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`),
  KEY `catalogos_c_esta_ac_b02893_idx` (`esta_activo`),
  KEY `catalogos_c_tipo_ca_479cf7_idx` (`tipo_catalogo`),
  KEY `catalogos_c_orden_20aa36_idx` (`orden`),
  KEY `catalogos_catalogo_creado_por_id_42006686_fk_auth_user_id` (`creado_por_id`),
  KEY `catalogos_catalogo_eliminado_por_id_9c26fd0f_fk_auth_user_id` (`eliminado_por_id`),
  KEY `catalogos_catalogo_modificado_por_id_47781eb0_fk_auth_user_id` (`modificado_por_id`),
  CONSTRAINT `catalogos_catalogo_creado_por_id_42006686_fk_auth_user_id` FOREIGN KEY (`creado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `catalogos_catalogo_eliminado_por_id_9c26fd0f_fk_auth_user_id` FOREIGN KEY (`eliminado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `catalogos_catalogo_modificado_por_id_47781eb0_fk_auth_user_id` FOREIGN KEY (`modificado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `catalogos_catalogo_chk_1` CHECK ((`orden` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `catalogos_catalogo`
--

LOCK TABLES `catalogos_catalogo` WRITE;
/*!40000 ALTER TABLE `catalogos_catalogo` DISABLE KEYS */;
/*!40000 ALTER TABLE `catalogos_catalogo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `catalogos_itemcatalogo`
--

DROP TABLE IF EXISTS `catalogos_itemcatalogo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `catalogos_itemcatalogo` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_modificacion` datetime(6) NOT NULL,
  `fecha_eliminacion` datetime(6) DEFAULT NULL,
  `esta_eliminado` tinyint(1) NOT NULL,
  `codigo` varchar(100) NOT NULL,
  `nombre` varchar(255) NOT NULL,
  `descripcion` longtext NOT NULL,
  `valor` varchar(255) NOT NULL,
  `codigo_externo` varchar(100) NOT NULL,
  `metadatos` json DEFAULT NULL,
  `orden` int unsigned NOT NULL,
  `esta_activo` tinyint(1) NOT NULL,
  `catalogo_id` bigint NOT NULL,
  `creado_por_id` int DEFAULT NULL,
  `eliminado_por_id` int DEFAULT NULL,
  `item_padre_id` bigint DEFAULT NULL,
  `modificado_por_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `catalogos_i_catalog_3a13dd_idx` (`catalogo_id`),
  KEY `catalogos_i_codigo_b916d9_idx` (`codigo`),
  KEY `catalogos_i_esta_ac_0c388b_idx` (`esta_activo`),
  KEY `catalogos_i_item_pa_508a19_idx` (`item_padre_id`),
  KEY `catalogos_i_codigo__fc9b47_idx` (`codigo_externo`),
  KEY `catalogos_i_orden_81fcbc_idx` (`orden`),
  KEY `catalogos_itemcatalogo_creado_por_id_1d529ae5_fk_auth_user_id` (`creado_por_id`),
  KEY `catalogos_itemcatalogo_eliminado_por_id_16049184_fk_auth_user_id` (`eliminado_por_id`),
  KEY `catalogos_itemcatalo_modificado_por_id_9d9d33e6_fk_auth_user` (`modificado_por_id`),
  CONSTRAINT `catalogos_itemcatalo_catalogo_id_da811a82_fk_catalogos` FOREIGN KEY (`catalogo_id`) REFERENCES `catalogos_catalogo` (`id`),
  CONSTRAINT `catalogos_itemcatalo_item_padre_id_af598cda_fk_catalogos` FOREIGN KEY (`item_padre_id`) REFERENCES `catalogos_itemcatalogo` (`id`),
  CONSTRAINT `catalogos_itemcatalo_modificado_por_id_9d9d33e6_fk_auth_user` FOREIGN KEY (`modificado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `catalogos_itemcatalogo_creado_por_id_1d529ae5_fk_auth_user_id` FOREIGN KEY (`creado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `catalogos_itemcatalogo_eliminado_por_id_16049184_fk_auth_user_id` FOREIGN KEY (`eliminado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `catalogos_itemcatalogo_chk_1` CHECK ((`orden` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `catalogos_itemcatalogo`
--

LOCK TABLES `catalogos_itemcatalogo` WRITE;
/*!40000 ALTER TABLE `catalogos_itemcatalogo` DISABLE KEYS */;
/*!40000 ALTER TABLE `catalogos_itemcatalogo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `contenidos_configuracioninterfaz`
--

DROP TABLE IF EXISTS `contenidos_configuracioninterfaz`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `contenidos_configuracioninterfaz` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nombre_aplicativo` varchar(255) NOT NULL,
  `nombre_corto` varchar(100) NOT NULL,
  `descripcion_aplicativo` longtext NOT NULL,
  `texto_pie_pagina` varchar(255) NOT NULL,
  `logo_principal` varchar(100) DEFAULT NULL,
  `logo_secundario` varchar(100) DEFAULT NULL,
  `logo_institucional` varchar(100) DEFAULT NULL,
  `favicon` varchar(100) DEFAULT NULL,
  `color_primario` varchar(20) NOT NULL,
  `color_secundario` varchar(20) NOT NULL,
  `color_acento` varchar(20) NOT NULL,
  `esta_activa` tinyint(1) NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_modificacion` datetime(6) NOT NULL,
  `fecha_eliminacion` datetime(6) DEFAULT NULL,
  `creado_por_id` int DEFAULT NULL,
  `modificado_por_id` int DEFAULT NULL,
  `eliminado_por_id` int DEFAULT NULL,
  `esta_eliminado` tinyint(1) NOT NULL,
  `accion_lengua_senas_habilitada` tinyint(1) NOT NULL,
  `email_soporte` varchar(254) NOT NULL,
  `meta_descripcion_seo` longtext NOT NULL,
  `meta_titulo_seo` varchar(255) NOT NULL,
  `texto_autorizacion_datos` longtext NOT NULL,
  `texto_confirmacion_envio_subtitulo` longtext NOT NULL,
  `texto_confirmacion_envio_titulo` varchar(255) NOT NULL,
  `texto_descripcion_seccion_encuestas` longtext NOT NULL,
  `texto_lengua_senas` varchar(255) NOT NULL,
  `texto_terminos_condiciones` longtext NOT NULL,
  `texto_titulo_seccion_encuestas` varchar(255) NOT NULL,
  `texto_verificacion_exitosa_cuerpo` longtext NOT NULL,
  `texto_verificacion_exitosa_titulo` varchar(255) NOT NULL,
  `url_lengua_senas` varchar(200) NOT NULL,
  `favicon_repositorio_id` bigint DEFAULT NULL,
  `logo_institucional_repositorio_id` bigint DEFAULT NULL,
  `logo_principal_repositorio_id` bigint DEFAULT NULL,
  `logo_secundario_repositorio_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `contenidos__esta_ac_d3b1f1_idx` (`esta_activa`),
  KEY `contenidos_configura_creado_por_id_0e2a06db_fk_auth_user` (`creado_por_id`),
  KEY `contenidos_configura_modificado_por_id_9b3d5afb_fk_auth_user` (`modificado_por_id`),
  KEY `contenidos_configura_eliminado_por_id_7d87a23f_fk_auth_user` (`eliminado_por_id`),
  KEY `contenidos_configura_favicon_repositorio__04e71582_fk_archivos_` (`favicon_repositorio_id`),
  KEY `contenidos_configura_logo_institucional_r_0e9a9e2d_fk_archivos_` (`logo_institucional_repositorio_id`),
  KEY `contenidos_configura_logo_principal_repos_6c4d00e2_fk_archivos_` (`logo_principal_repositorio_id`),
  KEY `contenidos_configura_logo_secundario_repo_54f0d9ae_fk_archivos_` (`logo_secundario_repositorio_id`),
  CONSTRAINT `contenidos_configura_creado_por_id_0e2a06db_fk_auth_user` FOREIGN KEY (`creado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `contenidos_configura_eliminado_por_id_7d87a23f_fk_auth_user` FOREIGN KEY (`eliminado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `contenidos_configura_favicon_repositorio__04e71582_fk_archivos_` FOREIGN KEY (`favicon_repositorio_id`) REFERENCES `archivos_archivorepositorio` (`id`),
  CONSTRAINT `contenidos_configura_logo_institucional_r_0e9a9e2d_fk_archivos_` FOREIGN KEY (`logo_institucional_repositorio_id`) REFERENCES `archivos_archivorepositorio` (`id`),
  CONSTRAINT `contenidos_configura_logo_principal_repos_6c4d00e2_fk_archivos_` FOREIGN KEY (`logo_principal_repositorio_id`) REFERENCES `archivos_archivorepositorio` (`id`),
  CONSTRAINT `contenidos_configura_logo_secundario_repo_54f0d9ae_fk_archivos_` FOREIGN KEY (`logo_secundario_repositorio_id`) REFERENCES `archivos_archivorepositorio` (`id`),
  CONSTRAINT `contenidos_configura_modificado_por_id_9b3d5afb_fk_auth_user` FOREIGN KEY (`modificado_por_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `contenidos_configuracioninterfaz`
--

LOCK TABLES `contenidos_configuracioninterfaz` WRITE;
/*!40000 ALTER TABLE `contenidos_configuracioninterfaz` DISABLE KEYS */;
INSERT INTO `contenidos_configuracioninterfaz` VALUES (1,'App Diversa','AppDiversa','Descripción App Diversa','Pie de Página App Diversa','interfaz/logos/Propuesta_2.jpg','','interfaz/logos/logos_dane_sen_qXXFwQI.png','','','','',1,'2026-06-28 16:32:07.169636','2026-06-28 18:12:45.473979',NULL,NULL,1,NULL,0,0,'','','','','','','','','','','','','',NULL,NULL,NULL,NULL),(2,'App','','','','','','','','','','',1,'2026-06-28 19:26:44.539535','2026-06-28 19:26:44.539571',NULL,NULL,NULL,NULL,0,0,'','','','','','','','','','','','','',NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `contenidos_configuracioninterfaz` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `contenidos_logointerfaz`
--

DROP TABLE IF EXISTS `contenidos_logointerfaz`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `contenidos_logointerfaz` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_modificacion` datetime(6) NOT NULL,
  `fecha_eliminacion` datetime(6) DEFAULT NULL,
  `esta_eliminado` tinyint(1) NOT NULL,
  `codigo` varchar(100) NOT NULL,
  `nombre` varchar(255) NOT NULL,
  `texto_alternativo` varchar(500) NOT NULL,
  `imagen` varchar(100) DEFAULT NULL,
  `orden` int unsigned NOT NULL,
  `esta_activo` tinyint(1) NOT NULL,
  `archivo_repositorio_id` bigint DEFAULT NULL,
  `configuracion_interfaz_id` bigint NOT NULL,
  `creado_por_id` int DEFAULT NULL,
  `eliminado_por_id` int DEFAULT NULL,
  `modificado_por_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `contenidos_logointer_archivo_repositorio__6929ebc4_fk_archivos_` (`archivo_repositorio_id`),
  KEY `contenidos_logointerfaz_creado_por_id_89c6ca65_fk_auth_user_id` (`creado_por_id`),
  KEY `contenidos_logointer_eliminado_por_id_07c8bdee_fk_auth_user` (`eliminado_por_id`),
  KEY `contenidos_logointer_modificado_por_id_ed56b2a4_fk_auth_user` (`modificado_por_id`),
  KEY `contenidos__configu_75d677_idx` (`configuracion_interfaz_id`),
  KEY `contenidos__codigo_01aa92_idx` (`codigo`),
  KEY `contenidos__esta_ac_45d8fe_idx` (`esta_activo`),
  KEY `contenidos__orden_3ec645_idx` (`orden`),
  CONSTRAINT `contenidos_logointer_archivo_repositorio__6929ebc4_fk_archivos_` FOREIGN KEY (`archivo_repositorio_id`) REFERENCES `archivos_archivorepositorio` (`id`),
  CONSTRAINT `contenidos_logointer_configuracion_interf_7ada9aed_fk_contenido` FOREIGN KEY (`configuracion_interfaz_id`) REFERENCES `contenidos_configuracioninterfaz` (`id`),
  CONSTRAINT `contenidos_logointer_eliminado_por_id_07c8bdee_fk_auth_user` FOREIGN KEY (`eliminado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `contenidos_logointer_modificado_por_id_ed56b2a4_fk_auth_user` FOREIGN KEY (`modificado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `contenidos_logointerfaz_creado_por_id_89c6ca65_fk_auth_user_id` FOREIGN KEY (`creado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `contenidos_logointerfaz_chk_1` CHECK ((`orden` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `contenidos_logointerfaz`
--

LOCK TABLES `contenidos_logointerfaz` WRITE;
/*!40000 ALTER TABLE `contenidos_logointerfaz` DISABLE KEYS */;
INSERT INTO `contenidos_logointerfaz` VALUES (1,'2026-06-28 21:28:33.873160','2026-06-28 21:32:05.006660','2026-06-28 21:32:05.006501',1,'logo_institucional','Logo institucional','','interfaz/logos/logo_institucional_umQ3lNf.png',3,1,NULL,2,NULL,1,NULL),(2,'2026-06-28 21:28:33.874313','2026-06-28 21:31:55.721166',NULL,0,'logo_principal','Logo principal','Logo Mi Dato Cuenta','interfaz/logos/Propuesta_2.jpg',1,1,NULL,1,NULL,NULL,1),(3,'2026-06-28 21:28:33.877327','2026-06-28 21:31:20.385088',NULL,0,'logo_institucional','Logo institucional','Logo DANE - SEN','interfaz/logos/logos_dane_sen_qXXFwQI.png',3,1,NULL,1,NULL,NULL,1);
/*!40000 ALTER TABLE `contenidos_logointerfaz` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
INSERT INTO `django_admin_log` VALUES (1,'2026-06-28 15:28:46.341564','1','DISC-001 - Encuesta de Discriminación',1,'[{\"added\": {}}, {\"added\": {\"name\": \"Version de formulario\", \"object\": \"DISC-001 v1\"}}]',9,1),(2,'2026-06-28 15:35:41.331825','1','DISC-001 v1 - CAP-I',1,'[{\"added\": {}}]',14,1),(3,'2026-06-28 15:40:14.277510','1','CAP-I - P1',1,'[{\"added\": {}}]',7,1),(4,'2026-06-28 15:55:48.036945','1','CAP-I - P1',2,'[]',7,1),(5,'2026-06-28 16:01:13.843483','2','CAP-I - P2',1,'[{\"added\": {}}]',7,1),(6,'2026-06-28 16:03:12.996887','1','P2 - OP1-P2',1,'[{\"added\": {}}]',11,1),(7,'2026-06-28 16:03:56.770385','2','P2 - OP2-P2',1,'[{\"added\": {}}]',11,1),(8,'2026-06-28 16:05:32.400746','3','P2 - OP3-P2',1,'[{\"added\": {}}]',11,1),(9,'2026-06-28 16:32:07.171859','1','App Diversa',1,'[{\"added\": {}}]',17,1),(10,'2026-06-28 18:12:45.479601','1','App Diversa',2,'[{\"changed\": {\"fields\": [\"Logo institucional\"]}}]',17,1),(11,'2026-06-28 21:31:20.389098','3','logo_institucional - Logo institucional',2,'[{\"changed\": {\"fields\": [\"Texto alternativo\"]}}]',31,1),(12,'2026-06-28 21:31:35.783378','2','logo_principal - Logo principal',2,'[{\"changed\": {\"fields\": [\"Texto alternativo\"]}}]',31,1),(13,'2026-06-28 21:31:55.722564','2','logo_principal - Logo principal',2,'[]',31,1),(14,'2026-06-28 21:32:05.003486','1','logo_institucional - Logo institucional',3,'',31,1),(15,'2026-06-29 14:41:42.292417','2','SERV-01 - Encuesta de Acceso y Prestación de Servicios',1,'[{\"added\": {}}]',9,1),(16,'2026-06-29 14:42:30.529823','2','SERV-01 - Encuesta de Acceso y Prestación de Servicios',2,'[{\"changed\": {\"fields\": [\"Estado\"]}}, {\"added\": {\"name\": \"Version de formulario\", \"object\": \"SERV-01 v1\"}}]',9,1),(17,'2026-06-29 14:43:25.764824','1','DISC-001 - Encuesta de Discriminación',2,'[{\"changed\": {\"fields\": [\"Imagen portada\"]}}]',9,1),(18,'2026-07-01 00:20:56.905912','2','SERV-01 - Encuesta de Acceso y Prestación de Servicios',2,'[{\"changed\": {\"fields\": [\"Orden\"]}}]',9,1),(19,'2026-07-01 00:21:06.496840','1','DISC-001 - Encuesta de Discriminación',2,'[{\"changed\": {\"fields\": [\"Orden\"]}}]',9,1);
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(25,'archivos','archivorepositorio'),(20,'auditoria','registroauditoria'),(3,'auth','group'),(2,'auth','permission'),(4,'auth','user'),(21,'catalogos','catalogo'),(22,'catalogos','itemcatalogo'),(17,'contenidos','configuracioninterfaz'),(31,'contenidos','logointerfaz'),(5,'contenttypes','contenttype'),(28,'exportaciones','exportacion'),(8,'formularios','catalogogeografico'),(9,'formularios','formulario'),(10,'formularios','formularioversion'),(11,'formularios','opcionrespuesta'),(7,'formularios','pregunta'),(12,'formularios','preguntamatrizcolumna'),(13,'formularios','preguntamatrizfila'),(15,'formularios','reglapregunta'),(14,'formularios','seccionformulario'),(16,'formularios','textoformulario'),(23,'internacionalizacion','idioma'),(24,'internacionalizacion','traduccioncontenido'),(27,'notificaciones','notificacion'),(26,'notificaciones','plantillanotificacion'),(18,'respuestas','respuesta'),(19,'sesiones_anonimas','sesionanonima'),(6,'sessions','session'),(29,'sincronizacion','conflictosincronizacion'),(30,'sincronizacion','operacionsincronizacion');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2026-06-28 14:48:49.763954'),(2,'auth','0001_initial','2026-06-28 14:48:50.401750'),(3,'admin','0001_initial','2026-06-28 14:48:50.576611'),(4,'admin','0002_logentry_remove_auto_add','2026-06-28 14:48:50.595147'),(5,'admin','0003_logentry_add_action_flag_choices','2026-06-28 14:48:50.603130'),(6,'contenttypes','0002_remove_content_type_name','2026-06-28 14:48:50.716902'),(7,'auth','0002_alter_permission_name_max_length','2026-06-28 14:48:50.778793'),(8,'auth','0003_alter_user_email_max_length','2026-06-28 14:48:50.795760'),(9,'auth','0004_alter_user_username_opts','2026-06-28 14:48:50.803087'),(10,'auth','0005_alter_user_last_login_null','2026-06-28 14:48:50.859798'),(11,'auth','0006_require_contenttypes_0002','2026-06-28 14:48:50.867801'),(12,'auth','0007_alter_validators_add_error_messages','2026-06-28 14:48:50.874970'),(13,'auth','0008_alter_user_username_max_length','2026-06-28 14:48:50.939135'),(14,'auth','0009_alter_user_last_name_max_length','2026-06-28 14:48:51.007644'),(15,'auth','0010_alter_group_name_max_length','2026-06-28 14:48:51.023343'),(16,'auth','0011_update_proxy_permissions','2026-06-28 14:48:51.032201'),(17,'auth','0012_alter_user_first_name_max_length','2026-06-28 14:48:51.096276'),(18,'sessions','0001_initial','2026-06-28 14:48:51.137823'),(19,'formularios','0001_initial','2026-06-28 15:04:26.964328'),(20,'contenidos','0001_initial','2026-06-28 16:12:49.469667'),(21,'sesiones_anonimas','0001_initial','2026-06-28 16:44:24.213724'),(22,'respuestas','0001_initial','2026-06-28 16:44:24.353524'),(23,'respuestas','0002_initial','2026-06-28 16:44:24.653196'),(24,'auditoria','0001_initial','2026-06-28 16:53:09.136830'),(25,'contenidos','0002_auditoria_campos','2026-06-28 16:53:09.588899'),(26,'formularios','0002_auditoria_campos','2026-06-28 16:53:15.153559'),(27,'respuestas','0003_auditoria_campos','2026-06-28 16:55:56.571236'),(28,'sesiones_anonimas','0002_auditoria_campos','2026-06-28 16:55:57.141817'),(29,'auditoria','0002_rename_auditoria_entidad_entidad_id_idx_auditoria_r_entidad_0cbcba_idx_and_more','2026-06-28 17:18:05.616701'),(30,'contenidos','0003_remove_configuracioninterfaz_contenidos_cfg_esta_elim_idx_and_more','2026-06-28 17:18:05.685466'),(31,'formularios','0003_remove_catalogogeografico_form_catgeo_esta_elim_idx_and_more','2026-06-28 17:19:15.408013'),(32,'respuestas','0004_remove_respuesta_respuestas_esta_elim_idx_and_more','2026-06-28 17:19:15.478382'),(33,'sesiones_anonimas','0003_remove_sesionanonima_sesiones_an_esta_elim_idx_and_more','2026-06-28 17:19:15.556396'),(34,'catalogos','0001_initial','2026-06-28 17:45:56.738941'),(35,'formularios','0004_pregunta_campo_codigo_padre_catalogo_and_more','2026-06-28 17:53:43.369363'),(36,'internacionalizacion','0001_initial','2026-06-28 18:02:29.484708'),(37,'contenidos','0004_configuracioninterfaz_accion_lengua_senas_habilitada_and_more','2026-06-28 18:19:32.235466'),(38,'formularios','0005_formulario_imagen_portada_alter_textoformulario_tipo','2026-06-28 18:19:32.309090'),(39,'internacionalizacion','0002_traduccioncontenido_archivo_audio_and_more','2026-06-28 18:24:40.501884'),(40,'archivos','0001_initial','2026-06-28 18:46:56.172525'),(41,'contenidos','0005_configuracioninterfaz_favicon_repositorio_and_more','2026-06-28 18:46:56.792336'),(42,'formularios','0006_formulario_imagen_portada_repositorio','2026-06-28 18:46:56.939224'),(43,'internacionalizacion','0003_remove_traduccioncontenido_archivo_audio_and_more','2026-06-28 18:46:57.858113'),(44,'exportaciones','0001_initial','2026-06-28 19:16:23.529974'),(45,'notificaciones','0001_initial','2026-06-28 19:16:24.917504'),(46,'auditoria','0003_alter_registroauditoria_accion','2026-06-28 19:54:44.410620'),(47,'auditoria','0004_alter_registroauditoria_accion','2026-06-28 20:58:41.220353'),(48,'respuestas','0005_respuesta_dispositivo_origen_and_more','2026-06-28 20:58:41.934564'),(49,'sincronizacion','0001_initial','2026-06-28 20:58:42.409132'),(50,'contenidos','0006_logo_interfaz','2026-06-28 21:28:33.865823'),(51,'contenidos','0007_migrar_logos_legacy','2026-06-28 21:28:33.881217'),(52,'formularios','0007_formulario_orden','2026-06-29 15:11:49.454620');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('krukloaty1fo6ae8jh584yp9hoooofsq','.eJxVjEEOwiAQRe_C2hBgWmBcuvcMhBlAqoYmpV0Z765NutDtf-_9lwhxW2vYel7ClMRZaHH63SjyI7cdpHtst1ny3NZlIrkr8qBdXueUn5fD_TuosddvTQWiVh41QnaFoIykEqJhJG-5IGoerQHnhsGA0owMEFmlpCyBN068P9nAN0g:1weD5x:wNgt8vWY0aAaeoz332ePte2eej9-kjnhL7WXgiRsVXE','2026-07-13 14:36:21.347725'),('m07hyinip7a9594g7cvuhsbsrjhgfzcv','.eJxVjEEOwiAQRe_C2hBgWmBcuvcMhBlAqoYmpV0Z765NutDtf-_9lwhxW2vYel7ClMRZaHH63SjyI7cdpHtst1ny3NZlIrkr8qBdXueUn5fD_TuosddvTQWiVh41QnaFoIykEqJhJG-5IGoerQHnhsGA0owMEFmlpCyBN068P9nAN0g:1wejj2:ORudaql_kxLkpqJvRYQ80qo94efcveJzNTsLKqgh4I8','2026-07-15 01:26:52.561834'),('rebeih46ks7za80qj692tscid1auzzc8','.eJxVjEEOwiAQRe_C2hBgWmBcuvcMhBlAqoYmpV0Z765NutDtf-_9lwhxW2vYel7ClMRZaHH63SjyI7cdpHtst1ny3NZlIrkr8qBdXueUn5fD_TuosddvTQWiVh41QnaFoIykEqJhJG-5IGoerQHnhsGA0owMEFmlpCyBN068P9nAN0g:1wdqzx:QCxh_nJx9XNMBdMfbvFrReGaCOVvgynGY97Q0-Tmdbs','2026-07-12 15:00:41.228852');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exportaciones_exportacion`
--

DROP TABLE IF EXISTS `exportaciones_exportacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exportaciones_exportacion` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_modificacion` datetime(6) NOT NULL,
  `fecha_eliminacion` datetime(6) DEFAULT NULL,
  `esta_eliminado` tinyint(1) NOT NULL,
  `uuid` char(32) NOT NULL,
  `tipo` varchar(30) NOT NULL,
  `estado` varchar(20) NOT NULL,
  `usuario` varchar(255) NOT NULL,
  `fecha_inicio` datetime(6) DEFAULT NULL,
  `fecha_fin` datetime(6) DEFAULT NULL,
  `formato` varchar(10) NOT NULL,
  `parametros` json DEFAULT NULL,
  `registros_exportados` int unsigned NOT NULL,
  `error` longtext NOT NULL,
  `archivo_id` bigint DEFAULT NULL,
  `creado_por_id` int DEFAULT NULL,
  `eliminado_por_id` int DEFAULT NULL,
  `modificado_por_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `exportaciones_export_archivo_id_8d34b472_fk_archivos_` (`archivo_id`),
  KEY `exportaciones_exportacion_creado_por_id_82d56191_fk_auth_user_id` (`creado_por_id`),
  KEY `exportaciones_export_eliminado_por_id_59c3185a_fk_auth_user` (`eliminado_por_id`),
  KEY `exportaciones_export_modificado_por_id_1d96d1ca_fk_auth_user` (`modificado_por_id`),
  KEY `exportacion_uuid_69c769_idx` (`uuid`),
  KEY `exportacion_tipo_a2fdf1_idx` (`tipo`),
  KEY `exportacion_estado_c6ddc7_idx` (`estado`),
  KEY `exportacion_formato_1e3779_idx` (`formato`),
  CONSTRAINT `exportaciones_export_archivo_id_8d34b472_fk_archivos_` FOREIGN KEY (`archivo_id`) REFERENCES `archivos_archivorepositorio` (`id`),
  CONSTRAINT `exportaciones_export_eliminado_por_id_59c3185a_fk_auth_user` FOREIGN KEY (`eliminado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `exportaciones_export_modificado_por_id_1d96d1ca_fk_auth_user` FOREIGN KEY (`modificado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `exportaciones_exportacion_creado_por_id_82d56191_fk_auth_user_id` FOREIGN KEY (`creado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `exportaciones_exportacion_chk_1` CHECK ((`registros_exportados` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exportaciones_exportacion`
--

LOCK TABLES `exportaciones_exportacion` WRITE;
/*!40000 ALTER TABLE `exportaciones_exportacion` DISABLE KEYS */;
/*!40000 ALTER TABLE `exportaciones_exportacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `formularios_catalogogeografico`
--

DROP TABLE IF EXISTS `formularios_catalogogeografico`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `formularios_catalogogeografico` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `tipo` varchar(20) NOT NULL,
  `codigo` varchar(50) NOT NULL,
  `nombre` varchar(255) NOT NULL,
  `codigo_padre` varchar(50) NOT NULL,
  `esta_activo` tinyint(1) NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_modificacion` datetime(6) NOT NULL,
  `fecha_eliminacion` datetime(6) DEFAULT NULL,
  `creado_por_id` int DEFAULT NULL,
  `modificado_por_id` int DEFAULT NULL,
  `eliminado_por_id` int DEFAULT NULL,
  `esta_eliminado` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_catalogo_geografico_tipo_codigo` (`tipo`,`codigo`),
  KEY `formularios_esta_ac_c1b79d_idx` (`esta_activo`),
  KEY `formularios_catalogo_creado_por_id_dcd1a55e_fk_auth_user` (`creado_por_id`),
  KEY `formularios_catalogo_modificado_por_id_4f4d27ad_fk_auth_user` (`modificado_por_id`),
  KEY `formularios_catalogo_eliminado_por_id_c8f5b82b_fk_auth_user` (`eliminado_por_id`),
  CONSTRAINT `formularios_catalogo_creado_por_id_dcd1a55e_fk_auth_user` FOREIGN KEY (`creado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `formularios_catalogo_eliminado_por_id_c8f5b82b_fk_auth_user` FOREIGN KEY (`eliminado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `formularios_catalogo_modificado_por_id_4f4d27ad_fk_auth_user` FOREIGN KEY (`modificado_por_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `formularios_catalogogeografico`
--

LOCK TABLES `formularios_catalogogeografico` WRITE;
/*!40000 ALTER TABLE `formularios_catalogogeografico` DISABLE KEYS */;
/*!40000 ALTER TABLE `formularios_catalogogeografico` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `formularios_formulario`
--

DROP TABLE IF EXISTS `formularios_formulario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `formularios_formulario` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `uuid` char(32) NOT NULL,
  `codigo` varchar(50) NOT NULL,
  `nombre` varchar(255) NOT NULL,
  `descripcion` longtext NOT NULL,
  `introduccion` longtext NOT NULL,
  `objetivo` longtext NOT NULL,
  `tipo_formulario` varchar(30) NOT NULL,
  `tiempo_estimado_minutos` int unsigned DEFAULT NULL,
  `estado` varchar(20) NOT NULL,
  `version_actual` int unsigned NOT NULL,
  `permite_anonimo` tinyint(1) NOT NULL,
  `permite_registro_final` tinyint(1) NOT NULL,
  `permite_multiples_respuestas` tinyint(1) NOT NULL,
  `permite_offline` tinyint(1) NOT NULL,
  `fecha_inicio` datetime(6) DEFAULT NULL,
  `fecha_fin` datetime(6) DEFAULT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_modificacion` datetime(6) NOT NULL,
  `creado_por_id` int DEFAULT NULL,
  `fecha_eliminacion` datetime(6) DEFAULT NULL,
  `modificado_por_id` int DEFAULT NULL,
  `eliminado_por_id` int DEFAULT NULL,
  `esta_eliminado` tinyint(1) NOT NULL,
  `imagen_portada` varchar(100) DEFAULT NULL,
  `imagen_portada_repositorio_id` bigint DEFAULT NULL,
  `orden` int unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  UNIQUE KEY `codigo` (`codigo`),
  KEY `formularios_estado_683d50_idx` (`estado`),
  KEY `formularios_codigo_d308fc_idx` (`codigo`),
  KEY `formularios_tipo_fo_61e459_idx` (`tipo_formulario`),
  KEY `formularios_formulario_creado_por_id_93b46271_fk_auth_user_id` (`creado_por_id`),
  KEY `formularios_formular_modificado_por_id_0b43482d_fk_auth_user` (`modificado_por_id`),
  KEY `formularios_formulario_eliminado_por_id_b8a618bf_fk_auth_user_id` (`eliminado_por_id`),
  KEY `formularios_formular_imagen_portada_repos_558fca80_fk_archivos_` (`imagen_portada_repositorio_id`),
  KEY `formularios_orden_4b8f2a_idx` (`orden`),
  CONSTRAINT `formularios_formular_imagen_portada_repos_558fca80_fk_archivos_` FOREIGN KEY (`imagen_portada_repositorio_id`) REFERENCES `archivos_archivorepositorio` (`id`),
  CONSTRAINT `formularios_formular_modificado_por_id_0b43482d_fk_auth_user` FOREIGN KEY (`modificado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `formularios_formulario_creado_por_id_93b46271_fk_auth_user_id` FOREIGN KEY (`creado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `formularios_formulario_eliminado_por_id_b8a618bf_fk_auth_user_id` FOREIGN KEY (`eliminado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `formularios_formulario_chk_1` CHECK ((`tiempo_estimado_minutos` >= 0)),
  CONSTRAINT `formularios_formulario_chk_2` CHECK ((`version_actual` >= 0)),
  CONSTRAINT `formularios_formulario_chk_3` CHECK ((`orden` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `formularios_formulario`
--

LOCK TABLES `formularios_formulario` WRITE;
/*!40000 ALTER TABLE `formularios_formulario` DISABLE KEYS */;
INSERT INTO `formularios_formulario` VALUES (1,'1b5f64f9cd6648f6b210ce6b371bb8fb','DISC-001','Encuesta de Discriminación','Descripción Encuesta de Discriminación','Introducción Encuesta de Discriminación','Objetivo Encuesta de Discriminación','encuesta',10,'publicado',1,1,1,0,1,NULL,NULL,'2026-06-28 15:28:46.339357','2026-07-01 00:21:06.495429',NULL,NULL,1,NULL,0,'formularios/portadas/image_ecu_disponible.png',NULL,1),(2,'efe7bf97dec44b02a774d49dbd2303db','SERV-01','Encuesta de Acceso y Prestación de Servicios','Descripción Encuesta de Acceso y Prestación de Servicios','Introducción Encuesta de Acceso y Prestación de Servicios','Objetivo: Encuesta de Acceso y Prestación de Servicios','encuesta',5,'publicado',1,1,1,0,1,NULL,NULL,'2026-06-29 14:41:42.256077','2026-07-01 00:20:56.897356',1,NULL,1,NULL,0,'formularios/portadas/image_proxma_enc.png',NULL,2);
/*!40000 ALTER TABLE `formularios_formulario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `formularios_formularioversion`
--

DROP TABLE IF EXISTS `formularios_formularioversion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `formularios_formularioversion` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `numero_version` int unsigned NOT NULL,
  `estado` varchar(20) NOT NULL,
  `descripcion_cambio` longtext NOT NULL,
  `es_publicada` tinyint(1) NOT NULL,
  `fecha_publicacion` datetime(6) DEFAULT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `formulario_id` bigint NOT NULL,
  `fecha_modificacion` datetime(6) NOT NULL,
  `fecha_eliminacion` datetime(6) DEFAULT NULL,
  `creado_por_id` int DEFAULT NULL,
  `modificado_por_id` int DEFAULT NULL,
  `eliminado_por_id` int DEFAULT NULL,
  `esta_eliminado` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_formulario_version_numero` (`formulario_id`,`numero_version`),
  KEY `formularios_estado_702b99_idx` (`estado`),
  KEY `formularios_formular_creado_por_id_96a714e5_fk_auth_user` (`creado_por_id`),
  KEY `formularios_formular_modificado_por_id_c3dcbbb1_fk_auth_user` (`modificado_por_id`),
  KEY `formularios_formular_eliminado_por_id_41819c93_fk_auth_user` (`eliminado_por_id`),
  CONSTRAINT `formularios_formular_creado_por_id_96a714e5_fk_auth_user` FOREIGN KEY (`creado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `formularios_formular_eliminado_por_id_41819c93_fk_auth_user` FOREIGN KEY (`eliminado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `formularios_formular_formulario_id_99d1a277_fk_formulari` FOREIGN KEY (`formulario_id`) REFERENCES `formularios_formulario` (`id`),
  CONSTRAINT `formularios_formular_modificado_por_id_c3dcbbb1_fk_auth_user` FOREIGN KEY (`modificado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `formularios_formularioversion_chk_1` CHECK ((`numero_version` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `formularios_formularioversion`
--

LOCK TABLES `formularios_formularioversion` WRITE;
/*!40000 ALTER TABLE `formularios_formularioversion` DISABLE KEYS */;
INSERT INTO `formularios_formularioversion` VALUES (1,1,'publicado','Descripción de versiones del formulario',1,NULL,'2026-06-28 15:28:46.340331',1,'2026-06-28 16:53:09.962409',NULL,NULL,NULL,NULL,0),(2,1,'publicado','',1,NULL,'2026-06-29 14:42:30.528303',2,'2026-06-29 14:42:30.528315',NULL,NULL,NULL,NULL,0);
/*!40000 ALTER TABLE `formularios_formularioversion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `formularios_opcionrespuesta`
--

DROP TABLE IF EXISTS `formularios_opcionrespuesta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `formularios_opcionrespuesta` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `codigo` varchar(50) NOT NULL,
  `etiqueta` varchar(500) NOT NULL,
  `valor` varchar(255) NOT NULL,
  `tooltip` longtext NOT NULL,
  `orden` int unsigned NOT NULL,
  `es_excluyente` tinyint(1) NOT NULL,
  `activa_otro` tinyint(1) NOT NULL,
  `esta_activa` tinyint(1) NOT NULL,
  `pregunta_id` bigint NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_modificacion` datetime(6) NOT NULL,
  `fecha_eliminacion` datetime(6) DEFAULT NULL,
  `creado_por_id` int DEFAULT NULL,
  `modificado_por_id` int DEFAULT NULL,
  `eliminado_por_id` int DEFAULT NULL,
  `esta_eliminado` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_opcion_respuesta_pregunta_codigo` (`pregunta_id`,`codigo`),
  KEY `formularios_orden_70ecfd_idx` (`orden`),
  KEY `formularios_esta_ac_f6d5f0_idx` (`esta_activa`),
  KEY `formularios_opcionre_creado_por_id_b542951b_fk_auth_user` (`creado_por_id`),
  KEY `formularios_opcionre_modificado_por_id_7ae5d641_fk_auth_user` (`modificado_por_id`),
  KEY `formularios_opcionre_eliminado_por_id_fd1a31b9_fk_auth_user` (`eliminado_por_id`),
  CONSTRAINT `formularios_opcionre_creado_por_id_b542951b_fk_auth_user` FOREIGN KEY (`creado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `formularios_opcionre_eliminado_por_id_fd1a31b9_fk_auth_user` FOREIGN KEY (`eliminado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `formularios_opcionre_modificado_por_id_7ae5d641_fk_auth_user` FOREIGN KEY (`modificado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `formularios_opcionre_pregunta_id_bfc17970_fk_formulari` FOREIGN KEY (`pregunta_id`) REFERENCES `formularios_pregunta` (`id`),
  CONSTRAINT `formularios_opcionrespuesta_chk_1` CHECK ((`orden` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `formularios_opcionrespuesta`
--

LOCK TABLES `formularios_opcionrespuesta` WRITE;
/*!40000 ALTER TABLE `formularios_opcionrespuesta` DISABLE KEYS */;
INSERT INTO `formularios_opcionrespuesta` VALUES (1,'OP1-P2','mujer','Mujer','',1,0,0,1,2,'2026-06-28 16:53:11.609890','2026-06-28 16:53:11.655203',NULL,NULL,NULL,NULL,0),(2,'OP2-P2','hombre','Hombre','',2,0,0,1,2,'2026-06-28 16:53:11.609890','2026-06-28 16:53:11.655203',NULL,NULL,NULL,NULL,0),(3,'OP3-P2','intersexual','Intersexual','Intersexual: se trata de una variación orgánica bajo la cual el desarrollo del sexo cromosómico, gonadal o anatómico no coincide con los dos sexos que tradicionalmente se asignan. Se trata de una condición biológica y, en algunos casos, política, debido a que algunas personas construyen su identidad a partir de la no identificación con los dos sexos —masculino y femenino— que cultural y socialmente se establecen. (Decreto 762 de 2018. Artículo 2.4.4.2.1.10)',3,0,0,1,2,'2026-06-28 16:53:11.609890','2026-06-28 16:53:11.655203',NULL,NULL,NULL,NULL,0);
/*!40000 ALTER TABLE `formularios_opcionrespuesta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `formularios_pregunta`
--

DROP TABLE IF EXISTS `formularios_pregunta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `formularios_pregunta` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `codigo` varchar(50) NOT NULL,
  `texto` longtext NOT NULL,
  `descripcion` longtext NOT NULL,
  `tooltip` longtext NOT NULL,
  `tipo_pregunta` varchar(30) NOT NULL,
  `es_obligatoria` tinyint(1) NOT NULL,
  `es_pregunta_filtro` tinyint(1) NOT NULL,
  `permite_otro` tinyint(1) NOT NULL,
  `permite_observacion` tinyint(1) NOT NULL,
  `orden` int unsigned NOT NULL,
  `longitud_minima` int unsigned DEFAULT NULL,
  `longitud_maxima` int unsigned DEFAULT NULL,
  `valor_minimo` decimal(18,2) DEFAULT NULL,
  `valor_maximo` decimal(18,2) DEFAULT NULL,
  `expresion_regular` varchar(500) NOT NULL,
  `mensaje_error` longtext NOT NULL,
  `esta_activa` tinyint(1) NOT NULL,
  `seccion_id` bigint NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_modificacion` datetime(6) NOT NULL,
  `fecha_eliminacion` datetime(6) DEFAULT NULL,
  `creado_por_id` int DEFAULT NULL,
  `modificado_por_id` int DEFAULT NULL,
  `eliminado_por_id` int DEFAULT NULL,
  `esta_eliminado` tinyint(1) NOT NULL,
  `campo_codigo_padre_catalogo` varchar(100) NOT NULL,
  `catalogo_asociado_id` bigint DEFAULT NULL,
  `limite_items_catalogo` int unsigned DEFAULT NULL,
  `permite_busqueda_catalogo` tinyint(1) NOT NULL,
  `pregunta_padre_catalogo_id` bigint DEFAULT NULL,
  `usa_catalogo` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_pregunta_seccion_codigo` (`seccion_id`,`codigo`),
  KEY `formularios_tipo_pr_dc8b82_idx` (`tipo_pregunta`),
  KEY `formularios_esta_ac_c882f2_idx` (`esta_activa`),
  KEY `formularios_orden_19e4fd_idx` (`orden`),
  KEY `formularios_pregunta_creado_por_id_407ddcfa_fk_auth_user_id` (`creado_por_id`),
  KEY `formularios_pregunta_modificado_por_id_4367f049_fk_auth_user_id` (`modificado_por_id`),
  KEY `formularios_pregunta_eliminado_por_id_dd0179cb_fk_auth_user_id` (`eliminado_por_id`),
  KEY `formularios_pregunta_catalogo_asociado_id_6546e4e5_fk_catalogos` (`catalogo_asociado_id`),
  KEY `formularios_pregunta_pregunta_padre_catal_d88cf9cc_fk_formulari` (`pregunta_padre_catalogo_id`),
  CONSTRAINT `formularios_pregunta_catalogo_asociado_id_6546e4e5_fk_catalogos` FOREIGN KEY (`catalogo_asociado_id`) REFERENCES `catalogos_catalogo` (`id`),
  CONSTRAINT `formularios_pregunta_creado_por_id_407ddcfa_fk_auth_user_id` FOREIGN KEY (`creado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `formularios_pregunta_eliminado_por_id_dd0179cb_fk_auth_user_id` FOREIGN KEY (`eliminado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `formularios_pregunta_modificado_por_id_4367f049_fk_auth_user_id` FOREIGN KEY (`modificado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `formularios_pregunta_pregunta_padre_catal_d88cf9cc_fk_formulari` FOREIGN KEY (`pregunta_padre_catalogo_id`) REFERENCES `formularios_pregunta` (`id`),
  CONSTRAINT `formularios_pregunta_seccion_id_7cb5db7c_fk_formulari` FOREIGN KEY (`seccion_id`) REFERENCES `formularios_seccionformulario` (`id`),
  CONSTRAINT `formularios_pregunta_chk_1` CHECK ((`orden` >= 0)),
  CONSTRAINT `formularios_pregunta_chk_2` CHECK ((`longitud_minima` >= 0)),
  CONSTRAINT `formularios_pregunta_chk_3` CHECK ((`longitud_maxima` >= 0)),
  CONSTRAINT `formularios_pregunta_chk_4` CHECK ((`limite_items_catalogo` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `formularios_pregunta`
--

LOCK TABLES `formularios_pregunta` WRITE;
/*!40000 ALTER TABLE `formularios_pregunta` DISABLE KEYS */;
INSERT INTO `formularios_pregunta` VALUES (1,'P1','¿Cuántos años cumplidos tiene?','Descripción de pregunta 1','','numero',1,1,0,0,1,2,3,18.00,109.00,'','La edad debe estar entre 18 y 109 años.',1,1,'2026-06-28 16:53:10.974430','2026-06-28 16:53:11.033951',NULL,NULL,NULL,NULL,0,'codigo',NULL,NULL,0,NULL,0),(2,'P2','Seleccione su sexo biológico al nacer:','','Concepto de Sexo biológico: características biológicas y físicas usadas típicamente para asignar el género al nacer, como son los cromosomas, los niveles hormonales, los genitales externos e internos y los órganos reproductores (PROFAMILIA, 2020).','radio',1,0,0,0,2,NULL,NULL,NULL,NULL,'','Esta pregunta es obligatoria.',1,1,'2026-06-28 16:53:10.974430','2026-06-28 16:53:11.033951',NULL,NULL,NULL,NULL,0,'codigo',NULL,NULL,0,NULL,0);
/*!40000 ALTER TABLE `formularios_pregunta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `formularios_preguntamatrizcolumna`
--

DROP TABLE IF EXISTS `formularios_preguntamatrizcolumna`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `formularios_preguntamatrizcolumna` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `codigo` varchar(50) NOT NULL,
  `etiqueta` varchar(500) NOT NULL,
  `valor` varchar(100) NOT NULL,
  `orden` int unsigned NOT NULL,
  `esta_activa` tinyint(1) NOT NULL,
  `pregunta_id` bigint NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_modificacion` datetime(6) NOT NULL,
  `fecha_eliminacion` datetime(6) DEFAULT NULL,
  `creado_por_id` int DEFAULT NULL,
  `modificado_por_id` int DEFAULT NULL,
  `eliminado_por_id` int DEFAULT NULL,
  `esta_eliminado` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_matriz_columna_pregunta_codigo` (`pregunta_id`,`codigo`),
  KEY `formularios_orden_a53ce9_idx` (`orden`),
  KEY `formularios_esta_ac_e3853c_idx` (`esta_activa`),
  KEY `formularios_pregunta_creado_por_id_32f40bd6_fk_auth_user` (`creado_por_id`),
  KEY `formularios_pregunta_modificado_por_id_5a8e0cd6_fk_auth_user` (`modificado_por_id`),
  KEY `formularios_pregunta_eliminado_por_id_9d12f6a2_fk_auth_user` (`eliminado_por_id`),
  CONSTRAINT `formularios_pregunta_creado_por_id_32f40bd6_fk_auth_user` FOREIGN KEY (`creado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `formularios_pregunta_eliminado_por_id_9d12f6a2_fk_auth_user` FOREIGN KEY (`eliminado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `formularios_pregunta_modificado_por_id_5a8e0cd6_fk_auth_user` FOREIGN KEY (`modificado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `formularios_pregunta_pregunta_id_8fc373e8_fk_formulari` FOREIGN KEY (`pregunta_id`) REFERENCES `formularios_pregunta` (`id`),
  CONSTRAINT `formularios_preguntamatrizcolumna_chk_1` CHECK ((`orden` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `formularios_preguntamatrizcolumna`
--

LOCK TABLES `formularios_preguntamatrizcolumna` WRITE;
/*!40000 ALTER TABLE `formularios_preguntamatrizcolumna` DISABLE KEYS */;
/*!40000 ALTER TABLE `formularios_preguntamatrizcolumna` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `formularios_preguntamatrizfila`
--

DROP TABLE IF EXISTS `formularios_preguntamatrizfila`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `formularios_preguntamatrizfila` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `codigo` varchar(50) NOT NULL,
  `etiqueta` varchar(500) NOT NULL,
  `orden` int unsigned NOT NULL,
  `esta_activa` tinyint(1) NOT NULL,
  `pregunta_id` bigint NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_modificacion` datetime(6) NOT NULL,
  `fecha_eliminacion` datetime(6) DEFAULT NULL,
  `creado_por_id` int DEFAULT NULL,
  `modificado_por_id` int DEFAULT NULL,
  `eliminado_por_id` int DEFAULT NULL,
  `esta_eliminado` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_matriz_fila_pregunta_codigo` (`pregunta_id`,`codigo`),
  KEY `formularios_orden_18e894_idx` (`orden`),
  KEY `formularios_esta_ac_8c9cd3_idx` (`esta_activa`),
  KEY `formularios_pregunta_creado_por_id_63232915_fk_auth_user` (`creado_por_id`),
  KEY `formularios_pregunta_modificado_por_id_a80f54ba_fk_auth_user` (`modificado_por_id`),
  KEY `formularios_pregunta_eliminado_por_id_42b98885_fk_auth_user` (`eliminado_por_id`),
  CONSTRAINT `formularios_pregunta_creado_por_id_63232915_fk_auth_user` FOREIGN KEY (`creado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `formularios_pregunta_eliminado_por_id_42b98885_fk_auth_user` FOREIGN KEY (`eliminado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `formularios_pregunta_modificado_por_id_a80f54ba_fk_auth_user` FOREIGN KEY (`modificado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `formularios_pregunta_pregunta_id_e0e56ab3_fk_formulari` FOREIGN KEY (`pregunta_id`) REFERENCES `formularios_pregunta` (`id`),
  CONSTRAINT `formularios_preguntamatrizfila_chk_1` CHECK ((`orden` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `formularios_preguntamatrizfila`
--

LOCK TABLES `formularios_preguntamatrizfila` WRITE;
/*!40000 ALTER TABLE `formularios_preguntamatrizfila` DISABLE KEYS */;
/*!40000 ALTER TABLE `formularios_preguntamatrizfila` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `formularios_reglapregunta`
--

DROP TABLE IF EXISTS `formularios_reglapregunta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `formularios_reglapregunta` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `operador` varchar(20) NOT NULL,
  `valor_esperado` json NOT NULL,
  `accion` varchar(30) NOT NULL,
  `mensaje` longtext NOT NULL,
  `esta_activa` tinyint(1) NOT NULL,
  `pregunta_destino_id` bigint DEFAULT NULL,
  `pregunta_origen_id` bigint NOT NULL,
  `seccion_destino_id` bigint DEFAULT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_modificacion` datetime(6) NOT NULL,
  `fecha_eliminacion` datetime(6) DEFAULT NULL,
  `creado_por_id` int DEFAULT NULL,
  `modificado_por_id` int DEFAULT NULL,
  `eliminado_por_id` int DEFAULT NULL,
  `esta_eliminado` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `formularios_esta_ac_95316f_idx` (`esta_activa`),
  KEY `formularios_reglapre_pregunta_destino_id_fbfa070a_fk_formulari` (`pregunta_destino_id`),
  KEY `formularios_reglapre_pregunta_origen_id_bc7c4cf4_fk_formulari` (`pregunta_origen_id`),
  KEY `formularios_reglapre_seccion_destino_id_a11b476b_fk_formulari` (`seccion_destino_id`),
  KEY `formularios_reglapregunta_creado_por_id_68ca3eb8_fk_auth_user_id` (`creado_por_id`),
  KEY `formularios_reglapre_modificado_por_id_643c22dc_fk_auth_user` (`modificado_por_id`),
  KEY `formularios_reglapre_eliminado_por_id_7a0c85b4_fk_auth_user` (`eliminado_por_id`),
  CONSTRAINT `formularios_reglapre_eliminado_por_id_7a0c85b4_fk_auth_user` FOREIGN KEY (`eliminado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `formularios_reglapre_modificado_por_id_643c22dc_fk_auth_user` FOREIGN KEY (`modificado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `formularios_reglapre_pregunta_destino_id_fbfa070a_fk_formulari` FOREIGN KEY (`pregunta_destino_id`) REFERENCES `formularios_pregunta` (`id`),
  CONSTRAINT `formularios_reglapre_pregunta_origen_id_bc7c4cf4_fk_formulari` FOREIGN KEY (`pregunta_origen_id`) REFERENCES `formularios_pregunta` (`id`),
  CONSTRAINT `formularios_reglapre_seccion_destino_id_a11b476b_fk_formulari` FOREIGN KEY (`seccion_destino_id`) REFERENCES `formularios_seccionformulario` (`id`),
  CONSTRAINT `formularios_reglapregunta_creado_por_id_68ca3eb8_fk_auth_user_id` FOREIGN KEY (`creado_por_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `formularios_reglapregunta`
--

LOCK TABLES `formularios_reglapregunta` WRITE;
/*!40000 ALTER TABLE `formularios_reglapregunta` DISABLE KEYS */;
/*!40000 ALTER TABLE `formularios_reglapregunta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `formularios_seccionformulario`
--

DROP TABLE IF EXISTS `formularios_seccionformulario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `formularios_seccionformulario` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `codigo` varchar(50) NOT NULL,
  `titulo` varchar(255) NOT NULL,
  `descripcion` longtext NOT NULL,
  `texto_ayuda` longtext NOT NULL,
  `orden` int unsigned NOT NULL,
  `es_visible` tinyint(1) NOT NULL,
  `esta_activo` tinyint(1) NOT NULL,
  `formulario_version_id` bigint NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_modificacion` datetime(6) NOT NULL,
  `fecha_eliminacion` datetime(6) DEFAULT NULL,
  `creado_por_id` int DEFAULT NULL,
  `modificado_por_id` int DEFAULT NULL,
  `eliminado_por_id` int DEFAULT NULL,
  `esta_eliminado` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_seccion_formulario_version_codigo` (`formulario_version_id`,`codigo`),
  KEY `formularios_orden_0fa93d_idx` (`orden`),
  KEY `formularios_esta_ac_a4e2fe_idx` (`esta_activo`),
  KEY `formularios_seccionf_creado_por_id_26f13b27_fk_auth_user` (`creado_por_id`),
  KEY `formularios_seccionf_modificado_por_id_b5f0966c_fk_auth_user` (`modificado_por_id`),
  KEY `formularios_seccionf_eliminado_por_id_6aede0ce_fk_auth_user` (`eliminado_por_id`),
  CONSTRAINT `formularios_seccionf_creado_por_id_26f13b27_fk_auth_user` FOREIGN KEY (`creado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `formularios_seccionf_eliminado_por_id_6aede0ce_fk_auth_user` FOREIGN KEY (`eliminado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `formularios_seccionf_formulario_version_i_8b7167bf_fk_formulari` FOREIGN KEY (`formulario_version_id`) REFERENCES `formularios_formularioversion` (`id`),
  CONSTRAINT `formularios_seccionf_modificado_por_id_b5f0966c_fk_auth_user` FOREIGN KEY (`modificado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `formularios_seccionformulario_chk_1` CHECK ((`orden` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `formularios_seccionformulario`
--

LOCK TABLES `formularios_seccionformulario` WRITE;
/*!40000 ALTER TABLE `formularios_seccionformulario` DISABLE KEYS */;
INSERT INTO `formularios_seccionformulario` VALUES (1,'CAP-I','Capítulo I - Identificación','Descripción Capítulo I - Identificación','Texto de ayuda de Capítulo I - Identificación',1,1,1,1,'2026-06-28 16:53:13.373934','2026-06-28 16:53:13.410601',NULL,NULL,NULL,NULL,0);
/*!40000 ALTER TABLE `formularios_seccionformulario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `formularios_textoformulario`
--

DROP TABLE IF EXISTS `formularios_textoformulario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `formularios_textoformulario` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `tipo` varchar(30) NOT NULL,
  `titulo` varchar(255) NOT NULL,
  `contenido` longtext NOT NULL,
  `orden` int unsigned NOT NULL,
  `esta_activo` tinyint(1) NOT NULL,
  `formulario_version_id` bigint NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_modificacion` datetime(6) NOT NULL,
  `fecha_eliminacion` datetime(6) DEFAULT NULL,
  `creado_por_id` int DEFAULT NULL,
  `modificado_por_id` int DEFAULT NULL,
  `eliminado_por_id` int DEFAULT NULL,
  `esta_eliminado` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `formularios_orden_acb4f0_idx` (`orden`),
  KEY `formularios_esta_ac_574bd0_idx` (`esta_activo`),
  KEY `formularios_textofor_formulario_version_i_ab0a3ae3_fk_formulari` (`formulario_version_id`),
  KEY `formularios_textofor_creado_por_id_c24c33bc_fk_auth_user` (`creado_por_id`),
  KEY `formularios_textofor_modificado_por_id_21a1ec5a_fk_auth_user` (`modificado_por_id`),
  KEY `formularios_textofor_eliminado_por_id_6a0ea5d2_fk_auth_user` (`eliminado_por_id`),
  CONSTRAINT `formularios_textofor_creado_por_id_c24c33bc_fk_auth_user` FOREIGN KEY (`creado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `formularios_textofor_eliminado_por_id_6a0ea5d2_fk_auth_user` FOREIGN KEY (`eliminado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `formularios_textofor_formulario_version_i_ab0a3ae3_fk_formulari` FOREIGN KEY (`formulario_version_id`) REFERENCES `formularios_formularioversion` (`id`),
  CONSTRAINT `formularios_textofor_modificado_por_id_21a1ec5a_fk_auth_user` FOREIGN KEY (`modificado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `formularios_textoformulario_chk_1` CHECK ((`orden` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `formularios_textoformulario`
--

LOCK TABLES `formularios_textoformulario` WRITE;
/*!40000 ALTER TABLE `formularios_textoformulario` DISABLE KEYS */;
/*!40000 ALTER TABLE `formularios_textoformulario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `internacionalizacion_idioma`
--

DROP TABLE IF EXISTS `internacionalizacion_idioma`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `internacionalizacion_idioma` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_modificacion` datetime(6) NOT NULL,
  `fecha_eliminacion` datetime(6) DEFAULT NULL,
  `esta_eliminado` tinyint(1) NOT NULL,
  `codigo_iso` varchar(20) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `nombre_nativo` varchar(100) NOT NULL,
  `direccion_texto` varchar(3) NOT NULL,
  `esta_activo` tinyint(1) NOT NULL,
  `es_predeterminado` tinyint(1) NOT NULL,
  `icono_bandera` varchar(100) NOT NULL,
  `orden` int unsigned NOT NULL,
  `creado_por_id` int DEFAULT NULL,
  `eliminado_por_id` int DEFAULT NULL,
  `modificado_por_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo_iso` (`codigo_iso`),
  KEY `internacion_esta_ac_19661e_idx` (`esta_activo`),
  KEY `internacion_es_pred_3f308f_idx` (`es_predeterminado`),
  KEY `internacion_orden_504431_idx` (`orden`),
  KEY `internacionalizacion_creado_por_id_267bf7d0_fk_auth_user` (`creado_por_id`),
  KEY `internacionalizacion_eliminado_por_id_b6a37128_fk_auth_user` (`eliminado_por_id`),
  KEY `internacionalizacion_modificado_por_id_6bdaec4a_fk_auth_user` (`modificado_por_id`),
  CONSTRAINT `internacionalizacion_creado_por_id_267bf7d0_fk_auth_user` FOREIGN KEY (`creado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `internacionalizacion_eliminado_por_id_b6a37128_fk_auth_user` FOREIGN KEY (`eliminado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `internacionalizacion_modificado_por_id_6bdaec4a_fk_auth_user` FOREIGN KEY (`modificado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `internacionalizacion_idioma_chk_1` CHECK ((`orden` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `internacionalizacion_idioma`
--

LOCK TABLES `internacionalizacion_idioma` WRITE;
/*!40000 ALTER TABLE `internacionalizacion_idioma` DISABLE KEYS */;
/*!40000 ALTER TABLE `internacionalizacion_idioma` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `internacionalizacion_traduccioncontenido`
--

DROP TABLE IF EXISTS `internacionalizacion_traduccioncontenido`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `internacionalizacion_traduccioncontenido` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_modificacion` datetime(6) NOT NULL,
  `fecha_eliminacion` datetime(6) DEFAULT NULL,
  `esta_eliminado` tinyint(1) NOT NULL,
  `entidad` varchar(100) NOT NULL,
  `entidad_uuid` char(32) NOT NULL,
  `campo` varchar(100) NOT NULL,
  `valor_traducido` longtext NOT NULL,
  `creado_por_id` int DEFAULT NULL,
  `eliminado_por_id` int DEFAULT NULL,
  `idioma_id` bigint NOT NULL,
  `modificado_por_id` int DEFAULT NULL,
  `esta_activa` tinyint(1) NOT NULL,
  `lectura_facil` longtext NOT NULL,
  `metadatos` json DEFAULT NULL,
  `texto_alternativo` longtext NOT NULL,
  `transcripcion` longtext NOT NULL,
  `repositorio_audio_id` bigint DEFAULT NULL,
  `repositorio_imagen_id` bigint DEFAULT NULL,
  `repositorio_lengua_senas_id` bigint DEFAULT NULL,
  `repositorio_video_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `internacion_idioma__e34a54_idx` (`idioma_id`),
  KEY `internacion_entidad_5735bf_idx` (`entidad`),
  KEY `internacion_entidad_f8d1a9_idx` (`entidad_uuid`),
  KEY `internacion_campo_1972c3_idx` (`campo`),
  KEY `internacionalizacion_creado_por_id_716fbb4e_fk_auth_user` (`creado_por_id`),
  KEY `internacionalizacion_eliminado_por_id_932ced9c_fk_auth_user` (`eliminado_por_id`),
  KEY `internacionalizacion_modificado_por_id_ae9472a8_fk_auth_user` (`modificado_por_id`),
  KEY `internacionalizacion_repositorio_audio_id_be215c0f_fk_archivos_` (`repositorio_audio_id`),
  KEY `internacionalizacion_repositorio_imagen_i_b2353a30_fk_archivos_` (`repositorio_imagen_id`),
  KEY `internacionalizacion_repositorio_lengua_s_7088651d_fk_archivos_` (`repositorio_lengua_senas_id`),
  KEY `internacionalizacion_repositorio_video_id_84b1a5a8_fk_archivos_` (`repositorio_video_id`),
  CONSTRAINT `internacionalizacion_creado_por_id_716fbb4e_fk_auth_user` FOREIGN KEY (`creado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `internacionalizacion_eliminado_por_id_932ced9c_fk_auth_user` FOREIGN KEY (`eliminado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `internacionalizacion_idioma_id_1f5f8b2b_fk_internaci` FOREIGN KEY (`idioma_id`) REFERENCES `internacionalizacion_idioma` (`id`),
  CONSTRAINT `internacionalizacion_modificado_por_id_ae9472a8_fk_auth_user` FOREIGN KEY (`modificado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `internacionalizacion_repositorio_audio_id_be215c0f_fk_archivos_` FOREIGN KEY (`repositorio_audio_id`) REFERENCES `archivos_archivorepositorio` (`id`),
  CONSTRAINT `internacionalizacion_repositorio_imagen_i_b2353a30_fk_archivos_` FOREIGN KEY (`repositorio_imagen_id`) REFERENCES `archivos_archivorepositorio` (`id`),
  CONSTRAINT `internacionalizacion_repositorio_lengua_s_7088651d_fk_archivos_` FOREIGN KEY (`repositorio_lengua_senas_id`) REFERENCES `archivos_archivorepositorio` (`id`),
  CONSTRAINT `internacionalizacion_repositorio_video_id_84b1a5a8_fk_archivos_` FOREIGN KEY (`repositorio_video_id`) REFERENCES `archivos_archivorepositorio` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `internacionalizacion_traduccioncontenido`
--

LOCK TABLES `internacionalizacion_traduccioncontenido` WRITE;
/*!40000 ALTER TABLE `internacionalizacion_traduccioncontenido` DISABLE KEYS */;
/*!40000 ALTER TABLE `internacionalizacion_traduccioncontenido` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notificaciones_notificacion`
--

DROP TABLE IF EXISTS `notificaciones_notificacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notificaciones_notificacion` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_modificacion` datetime(6) NOT NULL,
  `fecha_eliminacion` datetime(6) DEFAULT NULL,
  `esta_eliminado` tinyint(1) NOT NULL,
  `uuid` char(32) NOT NULL,
  `canal` varchar(20) NOT NULL,
  `destinatario` varchar(500) NOT NULL,
  `estado` varchar(20) NOT NULL,
  `fecha_programada` datetime(6) DEFAULT NULL,
  `fecha_envio` datetime(6) DEFAULT NULL,
  `asunto_generado` varchar(300) NOT NULL,
  `contenido_generado` longtext NOT NULL,
  `variables_utilizadas` json DEFAULT NULL,
  `respuesta_proveedor` json DEFAULT NULL,
  `numero_intentos` int unsigned NOT NULL,
  `error_envio` longtext NOT NULL,
  `creado_por_id` int DEFAULT NULL,
  `eliminado_por_id` int DEFAULT NULL,
  `modificado_por_id` int DEFAULT NULL,
  `plantilla_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `notificacio_uuid_debbb2_idx` (`uuid`),
  KEY `notificacio_canal_028c4a_idx` (`canal`),
  KEY `notificacio_estado_52a925_idx` (`estado`),
  KEY `notificacio_destina_0c5a13_idx` (`destinatario`),
  KEY `notificaciones_notif_creado_por_id_024d11d1_fk_auth_user` (`creado_por_id`),
  KEY `notificaciones_notif_eliminado_por_id_64fef231_fk_auth_user` (`eliminado_por_id`),
  KEY `notificaciones_notif_modificado_por_id_c2832f5c_fk_auth_user` (`modificado_por_id`),
  KEY `notificaciones_notif_plantilla_id_03a229aa_fk_notificac` (`plantilla_id`),
  CONSTRAINT `notificaciones_notif_creado_por_id_024d11d1_fk_auth_user` FOREIGN KEY (`creado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `notificaciones_notif_eliminado_por_id_64fef231_fk_auth_user` FOREIGN KEY (`eliminado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `notificaciones_notif_modificado_por_id_c2832f5c_fk_auth_user` FOREIGN KEY (`modificado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `notificaciones_notif_plantilla_id_03a229aa_fk_notificac` FOREIGN KEY (`plantilla_id`) REFERENCES `notificaciones_plantillanotificacion` (`id`),
  CONSTRAINT `notificaciones_notificacion_chk_1` CHECK ((`numero_intentos` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notificaciones_notificacion`
--

LOCK TABLES `notificaciones_notificacion` WRITE;
/*!40000 ALTER TABLE `notificaciones_notificacion` DISABLE KEYS */;
/*!40000 ALTER TABLE `notificaciones_notificacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notificaciones_plantillanotificacion`
--

DROP TABLE IF EXISTS `notificaciones_plantillanotificacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notificaciones_plantillanotificacion` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_modificacion` datetime(6) NOT NULL,
  `fecha_eliminacion` datetime(6) DEFAULT NULL,
  `esta_eliminado` tinyint(1) NOT NULL,
  `uuid` char(32) NOT NULL,
  `codigo` varchar(100) NOT NULL,
  `nombre` varchar(255) NOT NULL,
  `tipo` varchar(20) NOT NULL,
  `asunto` varchar(300) NOT NULL,
  `contenido_html` longtext NOT NULL,
  `contenido_texto` longtext NOT NULL,
  `usa_variables` tinyint(1) NOT NULL,
  `variables_disponibles` json DEFAULT NULL,
  `esta_activa` tinyint(1) NOT NULL,
  `descripcion` longtext NOT NULL,
  `creado_por_id` int DEFAULT NULL,
  `eliminado_por_id` int DEFAULT NULL,
  `modificado_por_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  UNIQUE KEY `codigo` (`codigo`),
  KEY `notificacio_codigo_666907_idx` (`codigo`),
  KEY `notificacio_tipo_5f57d2_idx` (`tipo`),
  KEY `notificacio_esta_ac_cad121_idx` (`esta_activa`),
  KEY `notificaciones_plant_creado_por_id_be2633e9_fk_auth_user` (`creado_por_id`),
  KEY `notificaciones_plant_eliminado_por_id_3a20b5dd_fk_auth_user` (`eliminado_por_id`),
  KEY `notificaciones_plant_modificado_por_id_25088502_fk_auth_user` (`modificado_por_id`),
  CONSTRAINT `notificaciones_plant_creado_por_id_be2633e9_fk_auth_user` FOREIGN KEY (`creado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `notificaciones_plant_eliminado_por_id_3a20b5dd_fk_auth_user` FOREIGN KEY (`eliminado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `notificaciones_plant_modificado_por_id_25088502_fk_auth_user` FOREIGN KEY (`modificado_por_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notificaciones_plantillanotificacion`
--

LOCK TABLES `notificaciones_plantillanotificacion` WRITE;
/*!40000 ALTER TABLE `notificaciones_plantillanotificacion` DISABLE KEYS */;
/*!40000 ALTER TABLE `notificaciones_plantillanotificacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `respuestas_respuesta`
--

DROP TABLE IF EXISTS `respuestas_respuesta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `respuestas_respuesta` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `valor_texto` longtext NOT NULL,
  `valor_numero` decimal(18,4) DEFAULT NULL,
  `valor_booleano` tinyint(1) DEFAULT NULL,
  `valor_fecha` date DEFAULT NULL,
  `valor_hora` time(6) DEFAULT NULL,
  `valor_fecha_hora` datetime(6) DEFAULT NULL,
  `valor_json` json DEFAULT NULL,
  `archivo_nombre` varchar(300) NOT NULL,
  `archivo_ruta` varchar(500) NOT NULL,
  `latitud` decimal(10,8) DEFAULT NULL,
  `longitud` decimal(11,8) DEFAULT NULL,
  `precision_metros` decimal(10,2) DEFAULT NULL,
  `observacion` longtext NOT NULL,
  `origen_respuesta` varchar(20) NOT NULL,
  `fecha_respuesta_cliente` datetime(6) DEFAULT NULL,
  `fecha_respuesta_servidor` datetime(6) NOT NULL,
  `version_respuesta` int unsigned NOT NULL,
  `requiere_sincronizacion` tinyint(1) NOT NULL,
  `esta_eliminado` tinyint(1) NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_modificacion` datetime(6) NOT NULL,
  `pregunta_id` bigint NOT NULL,
  `sesion_id` bigint NOT NULL,
  `fecha_eliminacion` datetime(6) DEFAULT NULL,
  `creado_por_id` int DEFAULT NULL,
  `modificado_por_id` int DEFAULT NULL,
  `eliminado_por_id` int DEFAULT NULL,
  `dispositivo_origen` varchar(150) NOT NULL,
  `fecha_modificacion_cliente` datetime(6) DEFAULT NULL,
  `uuid_local` char(32) DEFAULT NULL,
  `version_cliente` int unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid_local` (`uuid_local`),
  KEY `respuestas__sesion__cc7f5a_idx` (`sesion_id`),
  KEY `respuestas__pregunt_8dbbcf_idx` (`pregunta_id`),
  KEY `respuestas__origen__ea5d6e_idx` (`origen_respuesta`),
  KEY `respuestas__requier_8716bb_idx` (`requiere_sincronizacion`),
  KEY `respuestas__fecha_r_bc1e10_idx` (`fecha_respuesta_servidor`),
  KEY `respuestas_creado_por_id_fk` (`creado_por_id`),
  KEY `respuestas_modificado_por_id_fk` (`modificado_por_id`),
  KEY `respuestas_eliminado_por_id_fk` (`eliminado_por_id`),
  KEY `respuestas__uuid_lo_5072d5_idx` (`uuid_local`),
  KEY `respuestas__version_5bb7ce_idx` (`version_cliente`),
  CONSTRAINT `respuestas_creado_por_id_fk` FOREIGN KEY (`creado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `respuestas_eliminado_por_id_fk` FOREIGN KEY (`eliminado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `respuestas_modificado_por_id_fk` FOREIGN KEY (`modificado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `respuestas_respuesta_pregunta_id_9d0b4a96_fk_formulari` FOREIGN KEY (`pregunta_id`) REFERENCES `formularios_pregunta` (`id`),
  CONSTRAINT `respuestas_respuesta_sesion_id_d7dac742_fk_sesiones_` FOREIGN KEY (`sesion_id`) REFERENCES `sesiones_anonimas_sesionanonima` (`id`),
  CONSTRAINT `respuestas_respuesta_chk_1` CHECK ((`version_respuesta` >= 0)),
  CONSTRAINT `respuestas_respuesta_chk_2` CHECK ((`version_cliente` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `respuestas_respuesta`
--

LOCK TABLES `respuestas_respuesta` WRITE;
/*!40000 ALTER TABLE `respuestas_respuesta` DISABLE KEYS */;
INSERT INTO `respuestas_respuesta` VALUES (1,'',25.0000,NULL,NULL,NULL,NULL,NULL,'','',NULL,NULL,NULL,'','web',NULL,'2026-06-28 17:31:19.658095',1,0,0,'2026-06-28 17:31:19.657955','2026-06-28 17:31:19.657976',1,1,NULL,NULL,NULL,NULL,'',NULL,NULL,0),(2,'Mujer',NULL,NULL,NULL,NULL,NULL,NULL,'','',NULL,NULL,NULL,'','web',NULL,'2026-06-28 17:31:46.823684',1,0,0,'2026-06-28 17:31:46.823593','2026-06-28 17:31:46.823628',2,1,NULL,NULL,NULL,NULL,'',NULL,NULL,0);
/*!40000 ALTER TABLE `respuestas_respuesta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sesiones_anonimas_sesionanonima`
--

DROP TABLE IF EXISTS `sesiones_anonimas_sesionanonima`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sesiones_anonimas_sesionanonima` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `uuid_sesion` char(32) NOT NULL,
  `fecha_inicio` datetime(6) NOT NULL,
  `fecha_ultima_actividad` datetime(6) NOT NULL,
  `direccion_ip` char(39) DEFAULT NULL,
  `user_agent` longtext NOT NULL,
  `idioma` varchar(20) NOT NULL,
  `zona_horaria` varchar(80) NOT NULL,
  `estado` varchar(20) NOT NULL,
  `token_cliente` varchar(255) NOT NULL,
  `es_offline` tinyint(1) NOT NULL,
  `fecha_sincronizacion` datetime(6) DEFAULT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_modificacion` datetime(6) NOT NULL,
  `formulario_id` bigint NOT NULL,
  `version_formulario_id` bigint NOT NULL,
  `fecha_eliminacion` datetime(6) DEFAULT NULL,
  `creado_por_id` int DEFAULT NULL,
  `modificado_por_id` int DEFAULT NULL,
  `eliminado_por_id` int DEFAULT NULL,
  `esta_eliminado` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid_sesion` (`uuid_sesion`),
  KEY `sesiones_an_uuid_se_8c8060_idx` (`uuid_sesion`),
  KEY `sesiones_an_estado_3dd428_idx` (`estado`),
  KEY `sesiones_an_formula_e8006d_idx` (`formulario_id`),
  KEY `sesiones_an_version_e03f03_idx` (`version_formulario_id`),
  KEY `sesiones_anonimas_se_creado_por_id_412f1d58_fk_auth_user` (`creado_por_id`),
  KEY `sesiones_anonimas_se_modificado_por_id_2402dc1f_fk_auth_user` (`modificado_por_id`),
  KEY `sesiones_anonimas_se_eliminado_por_id_720d00e0_fk_auth_user` (`eliminado_por_id`),
  CONSTRAINT `sesiones_anonimas_se_creado_por_id_412f1d58_fk_auth_user` FOREIGN KEY (`creado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `sesiones_anonimas_se_eliminado_por_id_720d00e0_fk_auth_user` FOREIGN KEY (`eliminado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `sesiones_anonimas_se_formulario_id_d4ae289c_fk_formulari` FOREIGN KEY (`formulario_id`) REFERENCES `formularios_formulario` (`id`),
  CONSTRAINT `sesiones_anonimas_se_modificado_por_id_2402dc1f_fk_auth_user` FOREIGN KEY (`modificado_por_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `sesiones_anonimas_se_version_formulario_i_d8df821d_fk_formulari` FOREIGN KEY (`version_formulario_id`) REFERENCES `formularios_formularioversion` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sesiones_anonimas_sesionanonima`
--

LOCK TABLES `sesiones_anonimas_sesionanonima` WRITE;
/*!40000 ALTER TABLE `sesiones_anonimas_sesionanonima` DISABLE KEYS */;
INSERT INTO `sesiones_anonimas_sesionanonima` VALUES (1,'11111111111111111111111111111111','2026-06-28 17:30:43.229537','2026-06-28 17:33:29.212298','172.20.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36','es-CO','America/Bogota','finalizada','',0,NULL,'2026-06-28 17:30:43.229500','2026-06-28 17:33:29.212364',1,1,NULL,NULL,NULL,NULL,0),(2,'435e6b591edd4e31a0757a09766a09f9','2026-07-01 01:20:35.134307','2026-07-01 01:20:35.133843','172.20.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36','es','','iniciada','p-0WDj8Y88q7Z6hpPbpvFivjSL6S4qpR2lOBWoVudnE',0,NULL,'2026-07-01 01:20:35.134265','2026-07-01 01:20:35.134284',1,1,NULL,NULL,NULL,NULL,0),(3,'e92e29997f534091a482853d73e83d08','2026-07-01 01:28:00.052969','2026-07-01 01:28:00.052409','172.20.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36','es','','iniciada','Tcoj-XaAwT31CYkEXZOD9ikgyxNEPezB6JjrkhieB8E',0,NULL,'2026-07-01 01:28:00.052915','2026-07-01 01:28:00.052939',1,1,NULL,NULL,NULL,NULL,0);
/*!40000 ALTER TABLE `sesiones_anonimas_sesionanonima` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sincronizacion_conflictosincronizacion`
--

DROP TABLE IF EXISTS `sincronizacion_conflictosincronizacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sincronizacion_conflictosincronizacion` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `uuid` char(32) NOT NULL,
  `uuid_local` char(32) NOT NULL,
  `tipo_conflicto` varchar(20) NOT NULL,
  `valor_cliente` json DEFAULT NULL,
  `valor_servidor` json DEFAULT NULL,
  `resolucion` varchar(20) NOT NULL,
  `fecha` datetime(6) NOT NULL,
  `respuesta_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `sincronizacion_confl_respuesta_id_d28cb675_fk_respuesta` (`respuesta_id`),
  KEY `sincronizacion_conflictosincronizacion_uuid_local_0731f12a` (`uuid_local`),
  KEY `sincronizacion_conflictosincronizacion_tipo_conflicto_f7625b8b` (`tipo_conflicto`),
  KEY `sincronizacion_conflictosincronizacion_fecha_10e4659f` (`fecha`),
  CONSTRAINT `sincronizacion_confl_respuesta_id_d28cb675_fk_respuesta` FOREIGN KEY (`respuesta_id`) REFERENCES `respuestas_respuesta` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sincronizacion_conflictosincronizacion`
--

LOCK TABLES `sincronizacion_conflictosincronizacion` WRITE;
/*!40000 ALTER TABLE `sincronizacion_conflictosincronizacion` DISABLE KEYS */;
/*!40000 ALTER TABLE `sincronizacion_conflictosincronizacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sincronizacion_operacionsincronizacion`
--

DROP TABLE IF EXISTS `sincronizacion_operacionsincronizacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sincronizacion_operacionsincronizacion` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `uuid` char(32) NOT NULL,
  `uuid_local` char(32) NOT NULL,
  `uuid_sesion` char(32) NOT NULL,
  `dispositivo` varchar(150) NOT NULL,
  `version_cliente` int unsigned NOT NULL,
  `estado` varchar(20) NOT NULL,
  `fecha_cliente` datetime(6) NOT NULL,
  `fecha_servidor` datetime(6) NOT NULL,
  `numero_reintentos` int unsigned NOT NULL,
  `ultimo_error` longtext NOT NULL,
  `checksum` varchar(128) NOT NULL,
  `origen` varchar(50) NOT NULL,
  `payload` json NOT NULL,
  `resultado` json DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `sincronizacion_operacionsincronizacion_uuid_local_d791a78b` (`uuid_local`),
  KEY `sincronizacion_operacionsincronizacion_uuid_sesion_6923e523` (`uuid_sesion`),
  KEY `sincronizacion_operacionsincronizacion_estado_b6a010ac` (`estado`),
  KEY `sincronizac_disposi_e58f23_idx` (`dispositivo`),
  KEY `sincronizac_fecha_s_645862_idx` (`fecha_servidor`),
  KEY `sincronizac_uuid_se_c042d0_idx` (`uuid_sesion`,`uuid_local`),
  CONSTRAINT `sincronizacion_operacionsincronizacion_chk_1` CHECK ((`version_cliente` >= 0)),
  CONSTRAINT `sincronizacion_operacionsincronizacion_chk_2` CHECK ((`numero_reintentos` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sincronizacion_operacionsincronizacion`
--

LOCK TABLES `sincronizacion_operacionsincronizacion` WRITE;
/*!40000 ALTER TABLE `sincronizacion_operacionsincronizacion` DISABLE KEYS */;
/*!40000 ALTER TABLE `sincronizacion_operacionsincronizacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'appdiversa'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-07-01  1:40:56
