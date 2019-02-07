from __future__ import print_function

import collections, re, sys, time, traceback

try:
  import colorama
  colorama.init()
except ImportError:
  print('colorama not installed')

try:
  import peewee as pw
  import playhouse.migrate
except ImportError:
  print('peewee or herman not installed')
  # don't error, because setup needs to be able to run this to get the version

if sys.version_info >= (3,0):
  raw_input = input
  from collections.abc import Iterable
else:
  from collections import Iterable



DEBUG = False
PW3 = not hasattr(pw, 'Clause')

# peewee doesn't do defaults in the database - doh!
DIFF_DEFAULTS = False

__version__ = '3.7.0'


try:
  UNICODE_EXISTS = bool(type(unicode))
except NameError:
  unicode = lambda s: str(s)


###################
# Peewee 2 Shims
###################

if PW3:
  def extract_query_from_migration(migration):
    if isinstance(migration, Iterable):
      # Postgrsql has context first, MySql has context last :(
      ctx = next(obj for obj in migration if isinstance(obj, pw.Context))
    else:
      ctx = migration
    return [ctx.query()]

  def _table_name(model):
    return model._meta.table_name

  def _column_name(field):
    return field.column_name

  def _field_type(field):
    return field.field_type

  def _is_foreign_key(field):
    return hasattr(field, 'rel_model')

  def create_table(model):
    manager = pw.SchemaManager(model)
    ctx = manager._create_table()
    return [(''.join(ctx._sql), ctx._values)]

  def rename_table(migrator, before, after):
    migration = migrator.rename_table(before, after, with_context=True)
    return extract_query_from_migration(migration)

  def drop_table(migrator, name):
    migration = migrator.make_context().literal('DROP TABLE ').sql(pw.Entity(name))
    return extract_query_from_migration(migration)

  def create_index(model, fields, unique):
    manager = pw.SchemaManager(model)
    ctx = manager._create_index(pw.ModelIndex(model, fields, unique=unique))
    return [(''.join(ctx._sql), ctx._values)]

  def drop_index(migrator, model, index):
    migration = migrator.make_context().literal('DROP INDEX ').sql(pw.Entity(index.name))
    if is_mysql(model._meta.database):
      migration = migration.literal(' ON ').sql(pw.Entity(_table_name(model)))
    return extract_query_from_migration(migration)

  def create_foreign_key(field):
    manager = pw.SchemaManager(field.model)
    ctx = manager._create_foreign_key(field)
    return [(''.join(ctx._sql), ctx._values)]

  def drop_foreign_key(db, migrator, table_name, fk_name):
    drop_stmt = ' DROP FOREIGN KEY ' if is_mysql(db) else ' DROP CONSTRAINT '
    migration = migrator._alter_table(migrator.make_context(), table_name).literal(drop_stmt).sql(pw.Entity(fk_name))
    return extract_query_from_migration(migration)

  def drop_default(db, migrator, table_name, column_name, field):
    migration = migrator._alter_column(ctx, table_name, column_name).literal('DROP DEFAULT')
    return extract_query_from_migration(migration)

  def set_default(db, migrator, table_name, column_name, field):
    migration = migrator.apply_default(table_name, column_name, field, with_context=True)
    return extract_query_from_migration(migration)

  def alter_add_column(db, migrator, ntn, column_name, field):
    migration = migrator.alter_add_column(ntn, column_name, field, with_context=True)
    to_run = extract_query_from_migration(migration)
    if is_mysql(db) and _is_foreign_key(field):
      to_run += create_foreign_key(field)
    return to_run

  def drop_not_null(migrator, ntn, defined_col):
    migration = migrator.drop_not_null(ntn, defined_col.name, with_context=True)
    return extract_query_from_migration(migration)

  def rename_column(db, migrator, table, ocn, ncn, field):
    if is_mysql(db):
      ctx = migrator.make_context()
      migration = migrator._alter_table(ctx, table).literal(' CHANGE ').sql(pw.Entity(ocn)).literal(' ').sql(field.ddl(ctx))
    else:
      migration = migrator.rename_column(table, ocn, ncn, with_context=True)
    return extract_query_from_migration(migration)

  def drop_column(db, migrator, table, column_name):
    migrator.explicit_delete_foreign_key = False
    migration = migrator.drop_column(table, column_name, cascade=False, with_context=True)
    return extract_query_from_migration(migration)

  def change_column_type(db, migrator, table_name, column_name, field):
    column_type = _field_type(field)
    ctx = migrator.make_context()
    if is_postgres(db):
      migration = migrator._alter_column(ctx, table_name, column_name).literal(' TYPE ').sql(field.ddl_datatype(ctx))
    elif is_mysql(db):
      migration = migrator._alter_table(ctx, table_name).literal(' MODIFY COLUMN ').sql(field.ddl(ctx))
    else:
      raise Exception('how do i change a column type for %s?' % db)

    return extract_query_from_migration(migration)

  def add_not_null(db, migrator, table, column_name, field):
    cmds = []
    if field.default is not None:
      cmds += set_default(db, migrator, table, column_name, field)
    if is_mysql(db):
      ctx = migrator.make_context()
      cmds.append(migrator._alter_table(ctx, table).literal(' MODIFY COLUMN ').sql(field.ddl(ctx)).query())
    else:
      migration = migrator.add_not_null(table, column_name, with_context=True)
      cmds += extract_query_from_migration(migration)
    return cmds

  def indexes_on_model(model):
    return [
      pw.IndexMetadata('', '', [_column_name(f) for f in idx._expressions], idx._unique, _table_name(model))
      for idx in model._meta.fields_to_index()
    ]

else:
  def normalize_op_to_clause(migrator, op):
    if isinstance(op, pw.Clause): return op
    playhouse.migrate
    kwargs = op.kwargs.copy()
    kwargs['generate'] = True
    ret = getattr(migrator, op.method)(*op.args, **kwargs)
    return ret

  def _table_name(cls):
    return cls._meta.db_table

  def _column_name(cls):
    return cls.db_column

  def _field_type(field):
    compiler = field.model_class._meta.database.compiler()
    return compiler.get_column_type(field.get_db_field())

  def _is_foreign_key(field):
    return isinstance(field, pw.ForeignKeyField)

  def create_table(cls):
    compiler = cls._meta.database.compiler()
    return [compiler.create_table(cls)]

  def rename_table(migrator, before, after):
    compiler = migrator.database.compiler()
    op = migrator.rename_table(before, after, generate=True)
    return normalize_whatever_junk_peewee_migrations_gives_you(migrator, op)

  def drop_table(migrator, table_name):
    compiler = migrator.database.compiler()
    return [compiler.parse_node(pw.Clause(pw.SQL('DROP TABLE'), pw.Entity(table_name)))]

  def create_index(model, fields, name):
    compiler = model._meta.database.compiler()
    return [compiler.create_index(model, fields, name)]

  def drop_index(migrator, model, index):
    compiler = migrator.database.compiler()
    op = migrator.drop_index(_table_name(model), index.name, generate=True)
    return normalize_whatever_junk_peewee_migrations_gives_you(migrator, op)

  def create_foreign_key(field):
    compiler = field.model_class._meta.database.compiler()
    return [compiler.create_foreign_key(field.model_class, field)]

  def drop_foreign_key(db, migrator, table_name, fk_name):
    drop_stmt = 'drop foreign key' if is_mysql(db) else 'DROP CONSTRAINT'
    op = pw.Clause(pw.SQL('ALTER TABLE'), pw.Entity(table_name), pw.SQL(drop_stmt), pw.Entity(fk_name))
    return normalize_whatever_junk_peewee_migrations_gives_you(migrator, op)

  def drop_default(db, migrator, table_name, column_name, field):
    op = pw.Clause(pw.SQL('ALTER TABLE'), pw.Entity(table_name), pw.SQL('ALTER COLUMN'), pw.Entity(column_name), pw.SQL('DROP DEFAULT'))
    return normalize_whatever_junk_peewee_migrations_gives_you(migrator, op)

  def set_default(db, migrator, table_name, column_name, field):
    default = field.default
    if callable(default): default = default()
    param = pw.Param(field.db_value(default))
    op = pw.Clause(pw.SQL('ALTER TABLE'), pw.Entity(table_name), pw.SQL('ALTER COLUMN'), pw.Entity(column_name), pw.SQL('SET DEFAULT'), param)
    return normalize_whatever_junk_peewee_migrations_gives_you(migrator, op)

  def alter_add_column(db, migrator, ntn, column_name, field):
    compiler = migrator.database.compiler()
    operation = migrator.alter_add_column(ntn, column_name, field, generate=True)
    to_run = normalize_whatever_junk_peewee_migrations_gives_you(migrator, operation)
    if is_mysql(db) and _is_foreign_key(field):
      to_run += create_foreign_key(field)
    return to_run

  def drop_not_null(migrator, ntn, defined_col):
    compiler = migrator.database.compiler()
    op = migrator.drop_not_null(ntn, defined_col.name, generate=True)
    return normalize_whatever_junk_peewee_migrations_gives_you(migrator, op)

  def rename_column(db, migrator, ntn, ocn, ncn, field):
    compiler = db.compiler()
    if is_mysql(db):
      junk = pw.Clause(
        pw.SQL('ALTER TABLE'), pw.Entity(ntn), pw.SQL('CHANGE'), pw.Entity(ocn), compiler.field_definition(field)
      )
    else:
      junk = migrator.rename_column(ntn, ocn, ncn, generate=True)
    return normalize_whatever_junk_peewee_migrations_gives_you(migrator, junk)

  def drop_column(db, migrator, ntn, column_name):
    migrator.explicit_delete_foreign_key = False
    op = migrator.drop_column(ntn, column_name, generate=True, cascade=False)
    return normalize_whatever_junk_peewee_migrations_gives_you(migrator, op)

  def change_column_type(db, migrator, table_name, column_name, field):
    column_type = _field_type(field)
    if is_postgres(db):
      op = pw.Clause(pw.SQL('ALTER TABLE'), pw.Entity(table_name), pw.SQL('ALTER'), field.as_entity(), pw.SQL('TYPE'), field.__ddl_column__(column_type))
    elif is_mysql(db):
      op = pw.Clause(*[pw.SQL('ALTER TABLE'), pw.Entity(table_name), pw.SQL('MODIFY')] + field.__ddl__(column_type))
    else:
      raise Exception('how do i change a column type for %s?' % db)
    return normalize_whatever_junk_peewee_migrations_gives_you(migrator, op)

  def normalize_whatever_junk_peewee_migrations_gives_you(migrator, junk):
    # sometimes a clause, sometimes an operation, sometimes a list mixed with clauses and operations
    # turn it into a list of (sql,params) tuples
    compiler = migrator.database.compiler()
    if not hasattr(junk, '__iter__'):
      junk = [junk]
    junk = [normalize_op_to_clause(migrator, o) for o in junk]
    junk = [compiler.parse_node(clause) for clause in junk]
    return junk

  def add_not_null(db, migrator, table, column_name, field):
    cmds = []
    compiler = db.compiler()
    if field.default is not None:
      # if default is a function, turn it into a value
      # this won't work on columns requiring uniquiness, like UUIDs
      # as all columns will share the same called value
      default = field.default() if hasattr(field.default, '__call__') else field.default
      op = pw.Clause(pw.SQL('UPDATE'), pw.Entity(table), pw.SQL('SET'), field.as_entity(), pw.SQL('='), default, pw.SQL('WHERE'), field.as_entity(), pw.SQL('IS NULL'))
      cmds.append(compiler.parse_node(op))
    if is_postgres(db) or is_sqlite(db):
      junk = migrator.add_not_null(table, column_name, generate=True)
      cmds += normalize_whatever_junk_peewee_migrations_gives_you(migrator, junk)
      return cmds
    elif is_mysql(db):
      op = pw.Clause(pw.SQL('ALTER TABLE'), pw.Entity(table), pw.SQL('MODIFY'), compiler.field_definition(field))
      cmds.append(compiler.parse_node(op))
      return cmds
    raise Exception('how do i add a not null for %s?' % db)

  def indexes_on_model(model):
    return [pw.IndexMetadata('', '', [_column_name(f)], f.unique, _table_name(model)) for f in model._fields_to_index()]

####

def mark_fks_as_deferred(table_names):
  add_fks = []
  table_names_to_models = {_table_name(cls): cls for cls in all_models.keys() if _table_name(cls) in table_names}

  for model in table_names_to_models.values():
    for field in model._meta.sorted_fields:
      if _is_foreign_key(field):
        add_fks.append(field)
        if not field.deferred:
          field.__pwdbev__not_deferred = True
          field.deferred = True
  return add_fks

def calc_table_changes(existing_tables, ignore_tables=None):
  if ignore_tables:
    ignore_tables = set(ignore_tables) | globals()['ignore_tables']
  else:
    ignore_tables = globals()['ignore_tables']
  existing_tables = set(existing_tables)
  table_names_to_models = {unicode(_table_name(cls)):cls for cls in all_models.keys()}
  defined_tables = set(table_names_to_models.keys())
  adds = defined_tables - existing_tables - ignore_tables
  deletes = existing_tables - defined_tables - ignore_tables
  renames = {}
  for to_add in list(adds):
    cls = table_names_to_models[to_add]
    if hasattr(cls._meta, 'aka'):
      akas = cls._meta.aka
      if hasattr(akas, 'lower'):
        akas = [akas]
      for a in akas:
        a = unicode(a)
        if a in deletes:
          renames[a] = to_add
          adds.remove(to_add)
          deletes.remove(a)
          break
  add_fks = mark_fks_as_deferred(adds)
  return adds, add_fks, deletes, renames

def is_postgres(db):
  return isinstance(db, pw.PostgresqlDatabase)

def is_mysql(db):
  return isinstance(db, pw.MySQLDatabase)

def is_sqlite(db):
  return isinstance(db, pw.SqliteDatabase)

def auto_detect_migrator(db):
  if is_postgres(db):
    return playhouse.migrate.PostgresqlMigrator(db)
  if is_sqlite(db):
    return playhouse.migrate.SqliteMigrator(db)
  if is_mysql(db):
    return playhouse.migrate.MySQLMigrator(db)
  raise Exception("could not auto-detect migrator for %s - please provide one via the migrator kwarg" % repr(db.__class__.__name__))

_re_varchar = re.compile('^varchar[(]\\d+[)]$')
def normalize_column_type(t):
  t = t.lower()
  if t in ['serial', 'int', 'integer auto_increment', 'auto']: t = 'integer'
  if t in ['timestamp without time zone', 'datetime']: t = 'timestamp'
  if t in ['timestamp with time zone', 'datetime_tz']: t = 'timestamptz'
  if t in ['time without time zone']: t = 'time'
  if t in ['character varying']: t = 'varchar'
  if _re_varchar.match(t): t = 'varchar'
  if t in ['decimal', 'real', 'float']: t = 'numeric'
  if t in ['boolean']: t = 'bool'
  return unicode(t)


def normalize_default(default):
  if default is None: return None
  if hasattr(default, 'lower'):
    default = unicode(default)
    if default.startswith('nextval('): return None
    default = default.split('::')[0]
    default = default.strip("'")
  return default

def can_convert(type1, type2):
  if type1=='array': return False
  return True

def are_data_types_equal(db, type_a, type_b):
  if type_a == type_b: return True
  type_a, type_b = sorted([type_a, type_b])
  if is_mysql(db) and type_a=='bool' and type_b=='tinyint': return True
  if is_postgres(db) and type_a=='char' and type_b=='character': return True
  return False

def column_def_changed(db, a, b):
  # b is the defined column
  return (
    a.null!=b.null or
    not are_data_types_equal(db, a.data_type, b.data_type) or
    (b.max_length is not None and a.max_length!=b.max_length) or
    (b.precision is not None and a.precision!=b.precision) or
    (b.scale is not None and a.scale!=b.scale) or
    a.primary_key!=b.primary_key or
    (DIFF_DEFAULTS and normalize_default(a.default)!=normalize_default(b.default))
  )

ColumnMetadata = collections.namedtuple('ColumnMetadata', (
  'name', 'data_type', 'null', 'primary_key', 'table', 'default', 'max_length', 'precision', 'scale'
))

def get_columns_by_table(db, schema='public'):
  columns_by_table = collections.defaultdict(list)
  if is_postgres(db) or is_mysql(db):
    if schema=='public' and is_mysql(db):
      schema_check = 'c.table_schema=DATABASE()'
      params = []
    else:
      schema_check = 'c.table_schema=%s'
      params = [schema]
    sql = '''
        select
          c.column_name,
          c.data_type,
          c.is_nullable='YES' as is_nullable,
          coalesce(tc.constraint_type='PRIMARY KEY',false) as primary_key,
          c.table_name,
          c.column_default,
          c.character_maximum_length as max_length,
          c.numeric_precision,
          c.numeric_scale
        from information_schema.columns as c
        left join information_schema.key_column_usage as kcu
        on (c.table_name=kcu.table_name and c.table_schema=kcu.table_schema and c.column_name=kcu.column_name)
        left join information_schema.table_constraints as tc
        on (tc.table_name=kcu.table_name and tc.table_schema=kcu.table_schema and tc.constraint_name=kcu.constraint_name)
        where %s
        order by c.ordinal_position
    ''' % schema_check
    cursor = db.execute_sql(sql, params)
  else:
    raise Exception("don't know how to get columns for %s" % db)
  for row in cursor.fetchall():
    data_type = normalize_column_type(row[1])
    max_length = None if row[6]==4294967295 else row[6] # MySQL returns 4294967295L for LONGTEXT fields
    default = None if row[5] is not None and row[5].startswith('nextval') else row[5]
    precision = row[7] if data_type=='numeric' else None
    scale = row[8] if data_type=='numeric' else None
    column = ColumnMetadata(row[0], data_type, row[2], row[3], row[4], default, max_length, precision, scale)
    columns_by_table[column.table].append(column)
  return columns_by_table

ForeignKeyMetadata = collections.namedtuple('ForeignKeyMetadata', ('column', 'dest_table', 'dest_column', 'table', 'name'))

def get_foreign_keys_by_table(db, schema='public'):
  fks_by_table = collections.defaultdict(list)
  if is_postgres(db):
    sql = """
      select kcu.column_name, ccu.table_name, ccu.column_name, tc.table_name, tc.constraint_name
      from information_schema.table_constraints as tc
      join information_schema.key_column_usage as kcu
        on (tc.constraint_name = kcu.constraint_name and tc.constraint_schema = kcu.constraint_schema)
      join information_schema.constraint_column_usage as ccu
        on (ccu.constraint_name = tc.constraint_name and ccu.constraint_schema = tc.constraint_schema)
      where tc.constraint_type = 'FOREIGN KEY' and tc.table_schema = %s
    """
    cursor = db.execute_sql(sql, (schema,))
  elif is_mysql(db):
    sql = """
      select column_name, referenced_table_name, referenced_column_name, table_name, constraint_name
      from information_schema.key_column_usage
      where table_schema=database() and referenced_table_name is not null and referenced_column_name is not null
    """
    cursor = db.execute_sql(sql, [])
  elif is_sqlite(db):
    # does not work
    sql = """
      SELECT sql
        FROM (
              SELECT sql sql, type type, tbl_name tbl_name, name name
                FROM sqlite_master
               UNION ALL
              SELECT sql, type, tbl_name, name
                FROM sqlite_temp_master
             )
       WHERE type != 'meta'
         AND sql NOTNULL
         AND name NOT LIKE 'sqlite_%'
         AND sql LIKE '%REFERENCES%'
       ORDER BY substr(type, 2, 1), name
    """
    cursor = db.execute_sql(sql, [])
  else:
    raise Exception("don't know how to get FKs for %s" % db)
  for row in cursor.fetchall():
    fk = ForeignKeyMetadata(row[0], row[1], row[2], row[3], row[4])
    fks_by_table[fk.table].append(fk)
  return fks_by_table

def get_indexes_by_table(db, table, schema='public'):
  # peewee's get_indexes returns the columns in an index in arbitrary order
  if is_postgres(db):
    query = '''
      select index_class.relname,
        idxs.indexdef,
        array_agg(table_attribute.attname order by array_position(index.indkey, table_attribute.attnum)),
        index.indisunique,
        table_class.relname
      from pg_catalog.pg_class index_class
      join pg_catalog.pg_index index on index_class.oid = index.indexrelid
      join pg_catalog.pg_class table_class on table_class.oid = index.indrelid
      join pg_catalog.pg_attribute table_attribute on table_class.oid = table_attribute.attrelid and table_attribute.attnum = any(index.indkey)
      join pg_catalog.pg_indexes idxs on idxs.tablename = table_class.relname and idxs.indexname = index_class.relname
      where table_class.relname = %s and table_class.relkind = %s and idxs.schemaname = %s
      group by index_class.relname, idxs.indexdef, index.indisunique, table_class.relname;
    '''
    cursor = db.execute_sql(query, (table, 'r', schema))
    return [pw.IndexMetadata(*row) for row in cursor.fetchall()]
  else:
    return db.get_indexes(table, schema=schema)

def calc_column_changes(db, migrator, etn, ntn, existing_columns, defined_fields, existing_fks_by_column):
  defined_fields_by_column_name = {unicode(_column_name(f)):f for f in defined_fields}
  defined_columns = [ColumnMetadata(
    unicode(_column_name(f)),
    normalize_column_type(_field_type(f)),
    f.null,
    f.primary_key,
    unicode(ntn),
    f.default,
    f.max_length if hasattr(f, 'max_length') else None,
    f.max_digits if hasattr(f, 'max_digits') else None,
    f.decimal_places if hasattr(f, 'decimal_places') else None,
  ) for f in defined_fields if isinstance(f, pw.Field)]

  existing_cols_by_name = {c.name:c for c in existing_columns}
  defined_cols_by_name = {c.name:c for c in defined_columns}
  existing_col_names = set(existing_cols_by_name.keys())
  defined_col_names = set(defined_cols_by_name.keys())
  new_cols = defined_col_names - existing_col_names
  delete_cols = existing_col_names - defined_col_names
  rename_cols = {}
  for cn in list(new_cols):
    sc = defined_cols_by_name[cn]
    field = defined_fields_by_column_name[cn]
    if hasattr(field, 'akas'):
      for aka in field.akas:
        if aka in delete_cols:
          ec = existing_cols_by_name[aka]
          if can_convert(sc.data_type, ec.data_type):
            rename_cols[ec.name] = sc.name
            new_cols.discard(cn)
            delete_cols.discard(aka)

  alter_statements = []
  renames_new_to_old = {v:k for k,v in rename_cols.items()}
  not_new_columns = defined_col_names - new_cols

  # look for column metadata changes
  for col_name in not_new_columns:
    existing_col = existing_cols_by_name[renames_new_to_old.get(col_name, col_name)]
    defined_col = defined_cols_by_name[col_name]
    field = defined_fields_by_column_name[defined_col.name]
    if column_def_changed(db, existing_col, defined_col):
      len_alter_statements = len(alter_statements)

      different_type = existing_col.data_type != defined_col.data_type
      different_length = defined_col.max_length is not None and existing_col.max_length != defined_col.max_length
      different_precision = defined_col.precision is not None and existing_col.precision != defined_col.precision
      different_scale = defined_col.scale is not None and existing_col.scale != defined_col.scale

      should_cast = different_type and can_convert(existing_col.data_type, defined_col.data_type)
      should_recast = not different_type and (different_length or different_precision or different_scale)

      if existing_col.null and not defined_col.null:
        alter_statements += add_not_null(db, migrator, ntn, defined_col.name, field)
      if not existing_col.null and defined_col.null:
        alter_statements += drop_not_null(migrator, ntn, defined_col)
      if should_cast or should_recast:
        stmts = change_column_type(db, migrator, ntn, defined_col.name, field)
        alter_statements += stmts
      if DIFF_DEFAULTS:
        if normalize_default(existing_col.default) is not None and normalize_default(defined_col.default) is None:
          alter_statements += drop_default(db, migrator, ntn, defined_col.name, field)
        elif normalize_default(existing_col.default) != normalize_default(defined_col.default):
          alter_statements += set_default(db, migrator, ntn, defined_col.name, field)
      if not (len_alter_statements < len(alter_statements)):
        if existing_col.data_type == u'array':
          # type reporting for arrays is broken in peewee
          # it returns the underlying type of the array, not array
          # ignore array columns for now (HACK)
          pass
        else:
          raise Exception("In table %s I don't know how to change %s into %s" % (repr(ntn), existing_col, defined_col))

  # look for fk changes
  for col_name in not_new_columns:
    existing_column_name = renames_new_to_old.get(col_name, col_name)
    defined_field = defined_fields_by_column_name[col_name]
    existing_fk = existing_fks_by_column.get(existing_column_name)
    foreign_key = _is_foreign_key(defined_field)
    if foreign_key and not existing_fk and not (hasattr(defined_field, 'fake') and defined_field.fake):
      alter_statements += create_foreign_key(defined_field)
    if not foreign_key and existing_fk:
      alter_statements += drop_foreign_key(db, migrator, ntn, existing_fk.name)
  return new_cols, delete_cols, rename_cols, alter_statements


def calc_changes(db, ignore_tables=None):
  migrator = None # expose eventually?
  if migrator is None:
    migrator = auto_detect_migrator(db)

  existing_tables = [unicode(t) for t in db.get_tables()]
  existing_indexes = {table:get_indexes_by_table(db, table) for table in existing_tables}
  existing_columns_by_table = get_columns_by_table(db)
  foreign_keys_by_table = get_foreign_keys_by_table(db)

  table_names_to_models = {_table_name(cls): cls for cls in all_models.keys()}

  to_run = []

  table_adds, add_fks, table_deletes, table_renames = calc_table_changes(existing_tables, ignore_tables=ignore_tables)
  table_renamed_from = {v: k for k, v in table_renames.items()}
  for tbl in table_adds:
    to_run += create_table(table_names_to_models[tbl])
  for field in add_fks:
    if hasattr(field, '__pwdbev__not_deferred') and field.__pwdbev__not_deferred:
      field.deferred = False
    to_run += create_foreign_key(field)
  for k, v in table_renames.items():
    to_run += rename_table(migrator, k, v)


  rename_cols_by_table = {}
  deleted_cols_by_table = {}
  for etn, ecols in existing_columns_by_table.items():
    if etn in table_deletes: continue
    ntn = table_renames.get(etn, etn)
    model = table_names_to_models.get(ntn)
    if not model: continue
    defined_fields = model._meta.sorted_fields
    defined_column_name_to_field = {unicode(_column_name(f)):f for f in defined_fields}
    existing_fks_by_column = {fk.column:fk for fk in foreign_keys_by_table[etn]}
    adds, deletes, renames, alter_statements = calc_column_changes(db, migrator, etn, ntn, ecols, defined_fields, existing_fks_by_column)
    for column_name in adds:
      field = defined_column_name_to_field[column_name]
      to_run += alter_add_column(db, migrator, ntn, column_name, field)
      if not field.null:
        # alter_add_column strips null constraints
        # add them back after setting any defaults
        if field.default is not None:
          to_run += set_default(db, migrator, ntn, column_name, field)
        else:
          to_run.append(('-- adding a not null column without a default will fail if the table is not empty',[]))
        to_run += add_not_null(db, migrator, ntn, column_name, field)

    for column_name in deletes:
      fk = existing_fks_by_column.get(column_name)
      if fk:
        to_run += drop_foreign_key(db, migrator, ntn, fk.name)
      to_run += drop_column(db, migrator, ntn, column_name)
    for ocn, ncn in renames.items():
      field = defined_column_name_to_field[ncn]
      to_run += rename_column(db, migrator, ntn, ocn, ncn, field)
    to_run += alter_statements
    rename_cols_by_table[ntn] = renames
    deleted_cols_by_table[ntn] = deletes

  for ntn, model in table_names_to_models.items():
    etn = table_renamed_from.get(ntn, ntn)
    deletes = deleted_cols_by_table.get(ntn,set())
    existing_indexes_for_table = [i for i in existing_indexes.get(etn, []) if not any([(c in deletes) for c in i.columns])]
    to_run += calc_index_changes(db, migrator, existing_indexes_for_table, model, rename_cols_by_table.get(ntn, {}))

  '''
  to_run += calc_perms_changes($schema_tables, noop) unless $check_perms_for.empty?
  '''
  for tbl in table_deletes:
    to_run += drop_table(migrator, tbl)
  return to_run

def indexes_are_same(i1, i2):
  return unicode(i1.table)==unicode(i2.table) and i1.columns==i2.columns and i1.unique==i2.unique

def normalize_indexes(indexes):
  return [(unicode(idx.table), tuple(unicode(c) for c in idx.columns), idx.unique) for idx in indexes]


def calc_index_changes(db, migrator, existing_indexes, model, renamed_cols):
  to_run = []
  fields = list(model._meta.sorted_fields)
  fields_by_column_name = {_column_name(f):f for f in fields}
  pk_cols = set([unicode(_column_name(f)) for f in fields if f.primary_key])
  existing_indexes = [i for i in existing_indexes if not all([(unicode(c) in pk_cols) for c in i.columns])]
  normalized_existing_indexes = normalize_indexes(existing_indexes)
  existing_indexes_by_normalized_existing_indexes = dict(zip(normalized_existing_indexes, existing_indexes))
  normalized_existing_indexes = set(normalized_existing_indexes)
  defined_indexes = indexes_on_model(model)
  for fields, unique in model._meta.indexes:
    try:
      columns = [_column_name(model._meta.fields[fname]) for fname in fields]
    except KeyError as e:
      raise Exception("Index %s on %s references field %s in a multi-column index, but that field doesn't exist. (Be sure to use the field name, not the db_column name, when specifying a multi-column index.)" % ((fields, unique), model.__name__, repr(e.message)))
    defined_indexes.append(pw.IndexMetadata('', '', columns, unique, _table_name(model)))
  normalized_defined_indexes = set(normalize_indexes(defined_indexes))
  to_add = normalized_defined_indexes - normalized_existing_indexes
  to_del = normalized_existing_indexes - normalized_defined_indexes
  for index in to_del:
    index = existing_indexes_by_normalized_existing_indexes[index]
    to_run += drop_index(migrator, model, index)
  for index in to_add:
    to_run += create_index(model, [fields_by_column_name[col] for col in index[1]], index[2])
  return to_run

def evolve(db, interactive=True, ignore_tables=None):
  if interactive:
    print((colorama.Style.BRIGHT + colorama.Fore.RED + 'Making updates to database: {}'.format(db.database) + colorama.Style.RESET_ALL))
  to_run = calc_changes(db, ignore_tables=ignore_tables)
  if not to_run:
    if interactive:
      print('Nothing to do... Your database is up to date!')
    return

  commit = True
  if interactive:
    commit = _confirm(db, to_run)
  _execute(db, to_run, interactive=interactive, commit=commit)


def _execute(db, to_run, interactive=True, commit=True):
  if interactive: print()
  try:
    with db.atomic() as txn:
      for sql, params in to_run:
        if interactive or DEBUG: print_sql(' %s; %s' % (sql, params or ''))
        if sql.strip().startswith('--'): continue
        db.execute_sql(sql, params)
      if interactive:
        print()
        print(
          (colorama.Style.BRIGHT + 'SUCCESS!' + colorama.Style.RESET_ALL) if commit else 'TEST PASSED - ROLLING BACK',
          colorama.Style.DIM + '-',
          'https://github.com/keredson/peewee-db-evolve' + colorama.Style.RESET_ALL
        )
        print()
      if not commit:
        txn.rollback()
  except Exception as e:
    print()
    print('------------------------------------------')
    print(colorama.Style.BRIGHT + colorama.Fore.RED + ' SQL EXCEPTION - ROLLING BACK ALL CHANGES' + colorama.Style.RESET_ALL)
    print('------------------------------------------')
    print()
    raise e

COLORED_WORDS = None

def init_COLORED_WORDS():
  global COLORED_WORDS
  COLORED_WORDS = [
    (colorama.Fore.GREEN, ['CREATE', 'ADD']),
    (colorama.Fore.YELLOW, ['ALTER', 'SET', 'RENAME']),
    (colorama.Fore.RED, ['DROP']),
    (colorama.Style.BRIGHT + colorama.Fore.BLUE, ['INTEGER','VARCHAR','TIMESTAMP','TEXT','SERIAL']),
    (colorama.Style.BRIGHT, ['BEGIN','COMMIT']),
    (colorama.Fore.CYAN, ['FOREIGN KEY', 'REFERENCES', 'UNIQUE']),
    (colorama.Style.BRIGHT + colorama.Fore.CYAN, ['PRIMARY KEY']),
    (colorama.Style.BRIGHT + colorama.Fore.MAGENTA, ['NOT NULL','NULL']),
    (colorama.Style.DIM, [' ON ', '(', ')', 'INDEX', 'TABLE', 'COLUMN', 'CONSTRAINT' ,' TO ',';']),
  ]

def print_sql(sql):
  if COLORED_WORDS is None: init_COLORED_WORDS()
  for color, patterns in COLORED_WORDS:
    for pattern in patterns:
      sql = sql.replace(pattern, color + pattern + colorama.Style.RESET_ALL)
  print(sql)


def _confirm(db, to_run):
  print()
  print("Your database needs the following %s:" % ('changes' if len(to_run)>1 else 'change'))
  print()
  if is_postgres(db): print_sql('  BEGIN TRANSACTION;\n')
  for sql, params in to_run:
    print_sql('  %s; %s' % (sql, params or ''))
  if is_postgres(db): print_sql('\n  COMMIT;')
  print()
  while True:
    print('Do you want to run %s? (%s)' % (('these commands' if len(to_run)>1 else 'this command'), ('type yes, no or test' if is_postgres(db) else 'yes or no')), end=' ')
    response = raw_input().strip().lower()
    if response=='yes' or (is_postgres(db) and response=='test'):
      break
    if response=='no':
      sys.exit(1)
  print('Running in', end=' ')
  for i in range(3):
    print('%i...' % (3-i), end=' ')
    sys.stdout.flush()
    time.sleep(1)
  print()
  return response=='yes'




all_models = {}
ignore_tables = set()

def register(model):
  if hasattr(model._meta, 'evolve') and not model._meta.evolve:
    ignore_tables.add(_table_name(model))
  else:
    all_models[model] = []

def unregister(model):
  del all_models[model]

def clear():
  all_models.clear()
  ignore_tables.clear()

def _add_model_hook():
  ModelBase = pw.BaseModel if hasattr(pw, 'BaseModel') else pw.ModelBase
  init = ModelBase.__init__
  def _init(*args, **kwargs):
    cls = args[0]
    fields = args[3]
    if '__module__' in fields:
      del fields['__module__']
    register(cls)
    init(*args, **kwargs)
  ModelBase.__init__ = _init

def _add_field_hook():
  init = pw.Field.__init__
  def _init(*args, **kwargs):
    self = args[0]
    if 'aka' in kwargs:
      akas = kwargs['aka']
      if hasattr(akas, 'lower'):
        akas = [akas]
      self.akas = akas
      del kwargs['aka']
    init(*args, **kwargs)
  pw.Field.__init__ = _init

def _add_fake_fk_field_hook():
  init = pw.ForeignKeyField.__init__
  def _init(*args, **kwargs):
    self = args[0]
    if 'fake' in kwargs:
      self.fake = kwargs['fake']
      del kwargs['fake']
    init(*args, **kwargs)
  pw.ForeignKeyField.__init__ = _init

def add_evolve():
  pw.Database.evolve = evolve

if 'pw' in globals():
  _add_model_hook()
  _add_field_hook()
  _add_fake_fk_field_hook()
  add_evolve()


__all__ = ['evolve']
