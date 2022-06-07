

CREATE TABLE URLS (
id SERIAL PRIMARY KEY,
initial_url TEXT,
found_url TEXT
);

INSERT INTO URLS ( initial_url , found_url ) 
        VALUES ('test1', 'test1');
