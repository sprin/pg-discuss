=================
Database Overview
=================

PostgreSQL
==========

PostgreSQL was chosen as the only supported backend because it's stability,
performance, and features make it an excellent fit for large and small
deployments. As well as offering traditional RDBMS features, PostgreSQL offers
a JSON column type which can be used as a schemaless document object which can
contain scalars, arrays, and other nested objects. This hybrid
relational/non-relational model is leveraged extensively in pg-discuss. Python
support is excellent with the `psycopg2` driver, the `SQLAlchemy` database
abstraction toolkit, and the `alembic` schema migration tool.

Low latency of common operations is a goal of pg-discuss, and by using some
PostgreSQL features, we can keep the number of round trips to the database at a
minimum. Autocommit mode allows immediate execution of non-transactional
statements, and Conditional Table Expressions (CTEs) allow inserts and updates
to be chained in a single statement. As a result, the most common operations
can be performed with only one or two trips to the database.

SQLAlchemy and alembic
======================

The SQLAlchemy Declarative format is used to define the models. However,
the SQLAlchemy Core is used for querying; the ORM is not used. One reason is
that Core supports advanced JSONB functions and CTEs, which are leveraged in
pg-discuss. In general, Core allows the query author to stick closer to the
SQL, use advanced built-in SQL functions, and more easily predict the number
and sequence of statements that are emitted to the database. However,
extensions are free to use the ORM if desired.

`alembic` is the chosen schema migration tool. It is used to provide the
initial schema, and also to sync with any schema updates that may be made in
newer versions of pg-discuss. However, because schemaless JSONB columns are
present on every core table, migrations are not needed to added new attributes.
Extensions should only need to use migrations to add entirely new tables.

The `Flask-SQLAlchemy` and `Flask-Migrate` extensions are used to simplify
configuration of `SQLAlchemy` and `alembic`.

Core Schema
===========

Three models comprise the core of the schema: `Thread`, `Comment`, and
`Identity`. All of these models use a hybrid relational/nonrelational schema.
The core relational attributes are implemented as columns of standard types.
All of these tables also have a non-relational column of type JSONB called
`custom_json`, which allows persistence of custom attributes without a
pre-defined schema. This JSON object is how extensions can persist and use new
attributes.  Because attributes in the JSON object can be queried individually,
as well as set individually using PostgreSQL's `jsonb_set` function, this
column can be treated as a document object ala NoSQL datastores. Since JSONB
also supports indexes on attributes, filtering on these attributes can be very
performant.

Thread
------

`Thread` represents a collection of comments associated with a particular
external item, such as a blog post or other web page. Each external item
must have a `client_id` associated with it that ties it to its thread. While
the URL of the page may seem like an obvious choice, it should be avoided
since URLs may change (domain changes, slug changes, etc). Also, the
possibility of multiple items with threads on the same page should be
considered. Defining `client_id` for each item to be an immutable, unique
string is highly recommended. The JavaScript client may also send the URL
in addition to the `client_id` upon thread creation, and a simple extension can
capture and persist the URL in the `custom_json` column.

Comment
-------

`Comment` represents a particular version of a comment associated with a
particular thread via `thread_id`. Optionally, it can be associated with an
Identity via `identity_id`, and a parent comment via `parent_id`. If comment
editing and archiving are enabled, an archived comment may point to the
current comment via `version_of_id`. The `text` column contains the comment
text itself, and the `custom_json` column allows persistence of custom
attributes by extensions.

Identity
--------

`Identity` models an identity used to submit a comment. What the identity
actually represents is up to the chosen `IdentityPolicy`: by default it
simply represents a browser session, thus enabling users to edit and delete
their own comments in the same browser session. Other implementations of
`IdentityPolicy` may associate an `Identity` with a user who has been
authenticated by another service, or perhaps an extension may create a login
mechanism within the pg-discuss app. Custom `Identity` attributes can be
persisted in `custom_json`.

Technically, it is not required to use this model. If it is not desired to have
any association between comments and logical identities, nor any authorization
controls on creating, editing, or deleting, then a null `IdentityPolicy` can be
used.

Other Models
============

IdentityToCommentAssociation
----------------------------

`IdentityToCommentAssociation` models many-to-many relationships between
`Identity` and `Comment` models. The type of relationship is defined by
`rel_type` string, and other attributes can be stored in `custom_json`. This
model is made available solely for extensions and is not used in the core.

Possible uses by extensions include:

 - upvotes/downvotes
 - likes/dislikes
 - abuse reports

AdminUser
---------

`AdminUser` provides the schema for authenticating Admin users via Flask-Login,
if the included `AdminExt` is enabled. The hashed password is stored in
`password`. The user can be disabled via the `active` flag.
