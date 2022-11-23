CREATE TABLE bme280 (
  ID          int           NOT NULL AUTO_INCREMENT,
  Temperatura decimal(10,1) NOT NULL,
  Humidade    decimal(10,1) NOT NULL,
  Pressão     decimal(10,1) NOT NULL,
  Timestamp   char(20)      NOT NULL,
  PRIMARY KEY (ID)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci