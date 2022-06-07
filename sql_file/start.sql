


GRANT ALL PRIVILEGES ON URLS_DB.* TO 'user1'@'localhost';
GRANT ALL PRIVILEGES ON URLS_DB.* TO 'user1'@'%';

CREATE TABLE URLS_DB.URLS (
id int NOT NULL AUTO_INCREMENT,
initial_url varchar(500),
found_url varchar(500),
PRIMARY KEY (id)
);

INSERT IGNORE INTO URLS ( initial_url , found_url ) 
        VALUES ('test1', 'test1');
