-- Permisos para que Django pueda crear bases de datos de prueba (test_*).
GRANT ALL PRIVILEGES ON `test_%`.* TO 'appdiversa_user'@'%';
FLUSH PRIVILEGES;
