
CREATE DATABASE urls_db;

USE urls_db;

CREATE TABLE urls (
id int NOT NULL AUTO_INCREMENT,
initial_url varchar(500),
found_url varchar(500),
PRIMARY KEY (id)
);
