DO $$
    DECLARE identity_id1 integer;
    DECLARE identity_id2 integer;
    DECLARE identity_id3  integer;
    DECLARE thread_id1  integer;
    DECLARE comment_id1  integer;
    DECLARE comment_id3  integer;
BEGIN

WITH t1 as(
DELETE FROM comment WHERE thread_id = (SELECT id FROM thread WHERE client_id = 'demo')
), t2 as (
DELETE FROM identity WHERE id IN (SELECT identity_id FROM comment WHERE thread_id = (SELECT id FROM thread WHERE client_id = 'demo'))
)
DELETE FROM thread WHERE client_id = 'demo'
;
INSERT INTO identity VALUES (nextval('identity_id_seq'), now(), '{"remote_addrs": ["172.17.42.1"]}') RETURNING id INTO identity_id1;
INSERT INTO identity VALUES (nextval('identity_id_seq'), now(), '{"names": ["joe"], "remote_addrs": ["172.17.42.1"]}') RETURNING id INTO identity_id2;
INSERT INTO identity VALUES (nextval('identity_id_seq'), now(), '{"names": ["claire"], "remote_addrs": ["172.17.42.1"]}') RETURNING id INTO identity_id3;

INSERT INTO thread VALUES (nextval('thread_id_seq'), 'demo', now(), '{}') RETURNING id INTO thread_id1;

INSERT INTO comment VALUES (nextval('comment_id_seq'), identity_id2, thread_id1, NULL, NULL, now(), now(), 'Does it do markdown?', '{"hash": "80d635ccd165", "author": "joe", "remote_addr": "172.17.42.1"}') RETURNING id INTO comment_id1;
INSERT INTO comment VALUES (nextval('comment_id_seq'), identity_id1, thread_id1, comment_id1, NULL, now(), now(), '> Does it *do markdown?*

It **sure** **[does](https://pg-discuss.readthedocs.org/en/latest/features.html#pluggable-comment-renderer)!**', '{"hash": "80d635ccd111", "author": "claire", "remote_addr": "172.17.42.1"}');
INSERT INTO comment VALUES (nextval('comment_id_seq'), identity_id2, thread_id1, NULL, NULL, now(), now(), 'But how does it handle unicode?', '{"hash": "80d635ccd165", "author": "joe", "remote_addr": "172.17.42.1"}') RETURNING id INTO comment_id3;
INSERT INTO comment VALUES (nextval('comment_id_seq'), identity_id1, thread_id1, comment_id3, NULL, now(), now(), '# very n̴̩͙̮i̴̧̟̮c̷̤ę̶̨̩l̶͕͕͍y̶̫̤̤ ❀✌❃', '{"hash": "80d635ccd111", "author": "claire", "remote_addr": "172.17.42.1"}');
INSERT INTO comment VALUES (nextval('comment_id_seq'), identity_id3, thread_id1, NULL, NULL, now(), now(), 'Code?

```
from random import randint

def roll():
   print(randint(1,6))

if __name__ == ''''__main__'''':
    roll()
```', '{"hash": "80d635ccd000", "remote_addr": "172.17.42.1"}');
END$$
