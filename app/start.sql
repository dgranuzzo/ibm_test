
CREATE DATABASE urls_db;

CREATE USER ‘user1’@’localhost’ IDENTIFIED BY ‘passd13’;
GRANT ALL PRIVILEGES ON urls_db.* TO ‘user1’@’localhost’;


USE urls_db;

CREATE TABLE urls (
id int NOT NULL AUTO_INCREMENT,
initial_url varchar(500),
found_url varchar(500),
PRIMARY KEY (id)
);
