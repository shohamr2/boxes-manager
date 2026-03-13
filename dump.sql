PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE boxes (
	id INTEGER NOT NULL, 
	name VARCHAR, 
	photo VARCHAR, 
	created_at DATETIME, 
	PRIMARY KEY (id)
);
INSERT INTO boxes VALUES(1,'1 - משחקי קופסא מהסלון','none','2026-03-13 14:43:36.165044');
INSERT INTO boxes VALUES(2,'2 - משחקי קופסא מהסלון','none','2026-03-13 14:43:44.887293');
INSERT INTO boxes VALUES(3,'3 - משחקי קופסא מהסלון','none','2026-03-13 14:43:50.821352');
INSERT INTO boxes VALUES(4,'קופסאת תחפושת 1 - מגירות מקלט','none','2026-03-13 16:54:32.104494');
CREATE TABLE items (
	id INTEGER NOT NULL, 
	name VARCHAR, 
	photo VARCHAR, 
	quantity INTEGER, 
	box_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(box_id) REFERENCES boxes (id)
);
INSERT INTO items VALUES(1,'cshev','none',1,NULL);
INSERT INTO items VALUES(2,'דקעדע','fda0b96e-1734-4903-a1a6-030b11ae5dc7_lick better.png',1,NULL);
INSERT INTO items VALUES(3,'מטען','37a543c7-cdaf-4d2b-98ef-31595d361b14_image.jpg',3,NULL);
INSERT INTO items VALUES(4,'כנפיי מלאך קטנות','4eecacaa-8d89-4c83-a53b-99fcde1c9d67_image.jpg',1,4);
INSERT INTO items VALUES(5,'כנפיי מלאך גדולות','3361e729-14a1-4f9e-a055-5eb5fc4235c8_image.jpg',1,4);
INSERT INTO items VALUES(6,'קשת הילה מלאך','252a46d4-d296-445b-b8b8-242e43bdadc0_image.jpg',1,4);
INSERT INTO items VALUES(7,'שרשרת הוואי','64c622f9-6ddb-467c-b79b-71d6e63442ce_image.jpg',20,4);
INSERT INTO items VALUES(8,'כובע וויקינג','66ba4285-04d2-4ce0-860e-e2f9a6f1cfae_image.jpg',1,4);
INSERT INTO items VALUES(9,'תחפושת הגיבן מנוטרדם','a91ff68d-f948-4a49-8603-ea8a86975142_image.jpg',1,4);
INSERT INTO items VALUES(10,'מקל סבא קטן','5e9b6bf6-8fb2-42f0-84d6-761d85651247_image.jpg',1,4);
INSERT INTO items VALUES(11,'תחפושת טינקרבל','771f72fa-ea0e-4e6b-beb5-5532b7f1caea_image.jpg',1,4);
INSERT INTO items VALUES(12,'תחפושת פיטר פן','a24bc581-bb8a-4471-8862-92a69f3719b9_image.jpg',1,4);
INSERT INTO items VALUES(13,'אל בד פיטר פן, טינקרבל ובת הים','74e0c144-2005-47c5-b6ea-fa3eac29f06c_image.jpg',1,4);
COMMIT;
