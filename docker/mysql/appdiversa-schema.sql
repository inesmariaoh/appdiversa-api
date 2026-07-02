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

-- Dump completed on 2026-07-01  1:34:05
