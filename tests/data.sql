INSERT INTO user (username, password, api_key)
VALUES ('test', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f',
        '647b370dc5a980fb07a87aa6370d371de2c0b40226236fd708c9b03c2b5f14fd'),
       ('other', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79',
        '53117e6dee7463659a73c29ba125b8be86481ec586269f7cca3045375c6bfc5b');

INSERT INTO urls (url_name, shortener_string, original_url, creator_id, created)
VALUES ('test url', 'testing', 'https://example.com', 1, '2023-08-27 00:00:00'),
       ('Example 1', 'exampleOne', 'https://example.com', 1, '2023-09-07 00:00:00'),
       ('Example 2', 'exampleTwo', 'https://example.com', 1, '2023-09-07 00:00:00');