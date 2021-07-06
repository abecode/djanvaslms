# Canvas REST API to Relational Database

I wanted to try out doing a final project because it seems fun.  Also,
since it is my first time teaching this class, I wanted to gain an
appreciation of how my users/students see the activity.  This is a
strategy in software engineering called "Dogfooding", i.e. you eat the
same food that you sell.  Sometimes the product/dogfood starts out as
an internal product that is later sold to consumers (e.g. Pivotal
Tracker, AWS), and sometimes it is a product that is used by the
company internally (e.g. Facebook).

For my project, I wanted to understand how Canvas stores and
distributes data over it's REST web API.  Canvas has a lot of plugins
(e.g. Zoom), which are made possible through this API.  I like the
idea of a class being a similar plugin, where the professor has
control over the technical aspects of the course page.  This wouldn't
work generally, but for a professor in a software engineering
department, it seems to be a perfect fit.

This project is a small part of the bigger vision of making a class
webpage be a self hosted plugin instead of a Canvas.  It's probably
even less ambitious than many student's projects.  However, like I
mentioned in class, it's always good to have the minimal viable
project (MVP) in mind.  So, I'm just focusing on the aspect where the
student information is scraped out of the Canvas REST API and put into
a database that could be used by a web framework, in this case DJango.
Django provides the Object-Relational mapper (ORM).  Python reads JSON
data from the Canvas API and creates objects that are instances of the
Django Model class.  The Model class is like the resource layer in the
three tier architecture.  It talks to the database and not only saves
the objects, but manages the data definition language (DDL) and
migrations as well.

![Flow Chart](flowchart.png)


![ER Diagram](f2021-630-er-diagram.png)


## Canvas REST API

The Canvas REST API serves JSON data.  There are lots of endpoints,
which can be seen in this [live API
explorer](https://stthomas.instructure.com/doc/api/live#).  These
endpoints can be seen as views of some underlying database that Canvas
manages.  It's kind of a black box and the underlying data may or may
not be relational.  What is served over the API is JSON data and it
shows a good example of denormalization for convenience.  For example,
if the data were normalized, I may have needed to query several tables
to get users/students/teachers and enrollments.  However, because the
data is denormalized (and nested since it's JSON), I got the student,
teachers, and enrollment data all from the enrollment API endpoint.


Students and teachers are all considered users and the user is
returned as a nested object in the enrollment data.  Also grades are
nested in this enrollment output, but I didn't save this because I
think that one benefit of Canvas is having a standard privacy policy
regarding grades.



## Other notes


There's no difference between students and teachers (observers,
designers, etc), they are all users. Enrollments have a type, which
distinquishes teachers, students, designers, etc.  There's a lot of
redundant information, e.g., the type of an enrollment overlaps with
role and role_id. These are probably leftover from a properly
normalized database.

Sometimes there are multiple enrollments for a given user/course.  I'm
not sure why but this doesn't seem right.  I put a unique together
(multicolumn uniques constraint through django, ie in python code) and
then I catch the integrity exception when loading data from the canvas
rest api.

Some courses had 2+k users enrolled (certain university wide courses),
these took a long time to load so I excluded these. Also some
enrollment types (observer) didn't allow me to pull the corresponding
enrollment data so I had to exclude these from the scraping. For the
data I posted, I limited it to just our class.

Also, there are multiple, redundant ids: some are from canvas, some
are from UST (e.g. SISID is the student information system id, the
student's primary key in another database managed by UST or another
third party, not Canvas).  One of the details of this that I had to
deal with is that some of the enrollments were redundant, i.e. the
same teacher was registered twice for the same class (this happened
for teachers but not students).  To deal with this I put a uniqueness
constraint on a combination of columns for the enrollment table:
(user_id, course_id, and type).




## Example Queries

### select all the students in our class
```
select e.id, e.type, c.course_code, u.name 
from canvas_enrollment as e 
join canvas_course as c on e.course_id = c.id 
join canvas_user as u on e.user_id = u.id 
where c.name = "202120SEIS630-02 Database Mgmt Systems & Design";
```

### select my research student from last semester
```
/* this query shouldn't return results because I limited the data 
that shared with the class */
select e.id, e.type, c.course_code, u.name 
from canvas_enrollment as e 
join canvas_course c on e.course_id = c.id 
join canvas_user u on e.user_id = u.id 
where c.name = "202040SEIS795-01 Research,Independent Study";
```

# Topics

## REST API

The data comes from Canvas's REST api.  With REST api's you need to be
conscientious about rate limits.  To play nice with the api, I put
exponential backoff when hitting the api.  The script that does
synchronization of the data from canvas's rest api to the relational
db is a command that is registered in django.

## Subtype Entities

The default way that data is stored on canvas's api leads to a
database design where all users are the same (students, teachers,
observers, and designers were the examples I saw).  Also, the
enrollments have a type which distinguishes between these types of
users.  In the book we read about subtype entities.  In this case, it
might be possible to apply a subtype entity because users could have
subtypes (student, teacher, observer, etc), and/or relationships could
have subtypes.  However, the current design is simpler.  I think it
might be possible to expose a more nuanced model with subtypes as
views but I didn't have enough time to try this.

## Forward Engineering

I observed the json that came out of canvas's rest api and I designed
objects in python that store the fields in the json.  These objects
subclass from the django Model class and this allows them to be used
for forward engineering.  In ER diagrams, when we start with the
diagram and generate DDL, that is forward engineering.  In this case,
we have the Model subclasses instead of the diagram but the big
picture is the same.

## Reverse Engineering

I used the reverse engineering technique to generate the ER diagram
from the DDL created by Django in the forward engineering step.  This
is a simple diagram with only 3 connected entities: canvas_user
(contains both students and teachers), canvas_enrollment (also
contains both students and teachers), and canvas_course.  I also have
an unconnected table, canvas_rawjsoncourse, which I used as a staging
table.

## ETL/Staging File

When I first started loading the data from the Canvas API into the
relational database, I used a staging table.  This was a table with
just the course id and json text blob as the two columns.  It may not
have been very necessary but in practice it could be good to keep the
original raw json.

## Foreign keys/Cardinality/Relationships

This design is not very strict with minimum cardinality.  In principle
there could be many teachers of a class for example.  The main
illustration of cardinality is that there is a many-to-many
relationship between users and courses, which is mediated by the
enrollment table.  The term for this table is an association table,
i.e. an intersection table with more columns than just the foreign
keys.

## Normalization

As mentioned earlier, the results scraped from the Canvas API are
denormalized.  This makes it convenient to make a single request and
get back all the information in the response.  The example is the enrollment api endpoint.  It returned not only the 

## Naming

## DBA

to create the blank database schema, I logged into the system schema/user.  The following commands create a user/schema called djanvas

```
CREATE USER djanvas IDENTIFIED BY dbfun;
grant create session to djanvas;
grant DBA to djanvas;
```

I added a dedicated connection to this schema in SQL Developer like we
did in class.  I also added the db config to proj/proj/settings.py:

```
    'oracle': {
        'ENGINE':   'django.db.backends.oracle',
        'NAME':     '140.209.68.150:1521/XEPDB1',
        #'HOST': '140.209.68.150',
        #'PORT': 1521,
        'USER':     'djanvas',
        'PASSWORD': 'dbfun',
    }
```

https://www.shubhamdipt.com/blog/django-transfer-data-from-sqlite-to-another-database/

```
python manage.py dumpdata > db.json
```

Change the database settings to new database such as of MySQL / PostgreSQL.

```
python manage.py migrate
```

```
python manage.py shell 
```

Enter the following in the shell
```
from django.contrib.contenttypes.models import ContentType
ContentType.objects.all().delete()
```

```
python manage.py loaddata db.json
```

# Conclusion

I learned a few things from this project.  I better appreciate how
Canvas works.  I can't say I understand it completely, but I
understand it enough to get some useful information out. If I wanted
to figure out how many students I've had it would be pretty hard and
time consuming to calculate if I had to poke around and get it out of
Canvas, put it in a spreadsheet, etc.  However, with the data in a
database, it could be very quick and also enable other types of
queries.  It would also help professors practice SQL (professors need
practice too).

