

delete from annotationKeyword;
delete from annotationLocation;
delete from annotationPerson;
delete from annotations;

delete from docs;
delete from persons;
delete from keywords;

delete from works;

DELETE FROM sqlite_sequence WHERE name = 'persons';
DELETE FROM sqlite_sequence WHERE name = 'keywords';
DELETE FROM sqlite_sequence WHERE name = 'docs';
DELETE FROM sqlite_sequence WHERE name = 'works';
DELETE FROM sqlite_sequence WHERE name = 'annotations';



# all locations!
#delete from locations
#DELETE FROM sqlite_sequence WHERE name = 'locations'
