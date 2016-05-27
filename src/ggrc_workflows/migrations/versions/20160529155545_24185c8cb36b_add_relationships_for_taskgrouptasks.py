"""Add relationships for TaskGroupTasks

Revision ID: 24185c8cb36b
Revises: 851b2f37a61
Create Date: 2016-05-29 15:55:45.003063

"""

# revision identifiers, used by Alembic.
revision = '24185c8cb36b'
down_revision = '851b2f37a61'

from alembic import op
import datetime
import numbers
import sqlalchemy as sa


def transform_for_sql(value):
  # import ipdb;ipdb.set_trace()
  if value is None:
    return "NULL"
  if isinstance(value, numbers.Number):
    return str(value)
  if isinstance(value, datetime.datetime) or\
     isinstance(value, datetime.date):
    return "'{}'".format(str(value))
  if isinstance(value, basestring):
    return "'{}'".format(str(value))
  import ipdb; ipdb.set_trace()

def create_clone(tgt, idx, conn):
  """Returns a dictionary with taskgrouptask values same as tgt"""

  tgt_copy = tgt.copy()
  # delete the 'id', 'created_at' and 'updated_at' columns
  del tgt_copy['id']
  del tgt_copy['created_at']
  del tgt_copy['updated_at']
  # set a new slug (old_slug + '-1', '-2' etc.)
  tgt_copy['slug'] += "-" + str(idx + 1)
  tgt_cols = tgt_copy.keys()
  cols_str = ", ".join(tgt_cols)
  values_str = ", ".join([transform_for_sql(tgt_copy[col]) for col in tgt_cols])
  sql = "INSERT INTO task_group_tasks ({columns}) VALUES ({values})".format(
    columns=cols_str,
    values=values_str
  )
  result_proxy = conn.execute(sql)
  # Return 'id', you will need it when creating relationships for this task
  return {
    "id": result_proxy.lastrowid
  }


def create_relationship(tgt, tgo, conn):
  """Inserts the record into database"""
  sql = """INSERT INTO relationships
        (source_type, source_id, destination_type, destination_id)
      VALUES
        ('{source_type}', {source_id}, '{destination_type}', {destination_id})""".format(
    source_type="TaskGroupTask", source_id=tgt['id'],
    destination_type=tgo["object_type"], destination_id=tgo["object_id"]
  )
  conn.execute(sql)


def get_tgts(tg_id, conn):
  sql = "SELECT * from task_group_tasks where task_group_id = {}".format(tg_id)
  result_proxy = conn.execute(sql)
  # for each row get it's dictionary representation
  return map(dict, result_proxy)

def get_tgos(tg_id, conn):
  sql = "SELECT * from task_group_objects where task_group_id = {}".format(tg_id)
  result_proxy = conn.execute(sql)
  # for each row get it's dictionary representation
  return map(dict, result_proxy)


def upgrade():
  """Make TaskGroupObject's related to Tasks"""
  # Wrap in a transaction
  conn = op.get_bind()
  try:
    transaction = conn.begin()

    # For each taskgroup find its 'id' and parent workflow's 'is_old_workflow'
    task_groups_sql = """
      SELECT tg.id as 'tg_id', wf.is_old_workflow from task_groups as tg
      JOIN workflows as wf ON tg.workflow_id = wf.id
    """
    tgs = conn.execute(task_groups_sql)
    for tg_id, is_old_workflow in tgs.fetchall():
      # Find this taskgroup's TaskGroupTasks and TaskGroupObjects
      tgts = get_tgts(tg_id, conn)
      tgos = get_tgos(tg_id, conn)
      if is_old_workflow:
        for tgt in tgts:
          # You have only 1 Task. You need to create (len(tgos)-1) additional
          # tasks that will be clones of the one you have.
          # NOTE: you need to insert cloned tasks in database to get their ids
          new_tgts = [create_clone(tgt, idx, conn)
                      for idx in range(len(tgos)-1)]
          # same_tgts has type: [{"id":tgt_id, ...}, ...] but we only need 'id'
          same_tgts = [tgt] + new_tgts
          # Scenarios:
          #  len(tgos) == 0:
          #     - If you have no objects you should not create any relationship
          #  len(tgos) > 0:
          #     - You know that len(new_tgts) == len(tgos) because you had 1 task
          #       and you created (len(tgos)-1) clones. You can zip them and
          #       create relationships on pairs
          for cur_tgt, cur_tgo in zip(same_tgts, tgos):
            create_relationship(cur_tgt, cur_tgo, conn)
      else:
        # continue
        # If the workflow is 'new' then map all objects to every task
        # If task group has no objects then you don't need to create any relationship
        for tgt in tgts:
          for tgo in tgos:
            create_relationship(tgt, tgo, conn)

    # TODO check if old and new workflows work

    # TODO add new ones to fulltext?
    # import ipdb; ipdb.set_trace()
    # raise Exception
    #result = conn.execute(find_duplicates_query)
    #duplicate_records = result.fetchall()
    #attributes = [dict(zip(result.keys(), r)) for r in duplicate_records]

    transaction.commit()
  except Exception as error:
    import ipdb; ipdb.set_trace()
    print '---------------------------------------------'
    print(error)
    transaction.rollback()
    raise StandardError


def downgrade():
    pass
