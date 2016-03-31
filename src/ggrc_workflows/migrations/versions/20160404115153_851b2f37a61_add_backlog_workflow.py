# Copyright (C) 2016 Google Inc., authors, and contributors <see AUTHORS file>
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
# Created By: tomaz@reciprocitylabs.com
# Maintained By: tomaz@reciprocitylabs.com

"""Add backlog workflow

Revision ID: 851b2f37a61
Revises: 1263c1ab4642
Create Date: 2016-04-04 11:51:53.349729

"""

# revision identifiers, used by Alembic.
revision = '851b2f37a61'
down_revision = '1263c1ab4642'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
import datetime
from ggrc import app


def upgrade():

  conn = op.get_bind()

  # Add a column 'kind' to workflows table
  #op.add_column(u'workflows', sa.Column(u'kind',
  #                                      sa.String(255), nullable=True))


  try:
    transaction = conn.begin()

    # Add a column 'kind' to workflows table
    conn.execute("alter table workflows add column kind VARCHAR(255)")

    #import ipdb; ipdb.set_trace()
    # Create a backlog workflow
    # 1.) Create a workflow context (leave related_object_id empty)
    sql = """
      INSERT INTO contexts (name, related_object_id, related_object_type, created_at, updated_at)
      VALUES ("Workflow Context {date_now}", -111, "Workflow", NOW(), NOW())
    """.format(date_now=str(datetime.datetime.now()))
    rv1 = conn.execute(sql)
    #import ipdb; ipdb.set_trace()
    sql2 = """
      SELECT id FROM contexts WHERE related_object_id = -111
    """
    #import ipdb; ipdb.set_trace()
    res = conn.execute(sql2)
    # same as rv1.context.get_lastrowid() ?
    wf_ctx_id = res.fetchone()[0]

    #import ipdb; ipdb.set_trace()
    # 2.) Create workflow Person?
    # 3.) Create workflow (with kind='Backlog')
    sql = """
      INSERT INTO workflows(
          description, title, slug, created_at, updated_at, context_id,
          frequency, status, recurrences, is_old_workflow, kind
      )
      VALUES (
          "Backlog workflow", "Backlog (one time)", "BACKLOG-ONETIME-1",
          NOW(), NOW(), {context_id}, "one_time", "Active", 0, 0, "Backlog"
      )
    """.format(context_id=wf_ctx_id)
    conn.execute(sql)
    #import ipdb; ipdb.set_trace()
    res2 = conn.execute("select id from workflows where kind = 'Backlog'")
    wf_id = res2.fetchone()[0]
    # 4.) Update workflow context - set related_object_id to workflow id
    
    #import ipdb; ipdb.set_trace()
    sql = """
      UPDATE contexts set related_object_id = {wf_id} where related_object_id = -111
    """.format(wf_id=wf_id)
    conn.execute(sql)

    #import ipdb; ipdb.set_trace()
    # 5.) Create a workflow Cycle
    # TODO: what role do start_date and end_date play in cycles table?
    sql = """
      INSERT INTO cycles(
          workflow_id, description, title, slug, context_id, is_current, start_date, end_date
      )
      VALUES (
          {wf_id}, "Backlog workflow", "Backlog (one time)", "BACKLOG-CYCLE-1",
          {wf_ctx_id}, 1, null, null
      )
    """.format(wf_id=wf_id, wf_ctx_id=wf_ctx_id)
    #import ipdb; ipdb.set_trace()
    rv2 = conn.execute(sql)
    cycle_id = conn.execute("""select id from cycles where slug = 'BACKLOG-CYCLE-1'""").fetchone()[0]
    # 6.) Create Cycle task group
    # TODO: what role do start_date and end_date play in cycle_task_groups table?

    #import ipdb; ipdb.set_trace()
    # TODO: add context_id
    # TODO: custom attributes on workflow, migration should include this?!
    sql = """
      INSERT INTO cycle_task_groups (
          cycle_id, slug, title, status, start_date, end_date, sort_index 
      )
      VALUES (
          {cycle_id}, "BACKLOG-CYCLEGROUP-1", "Backlog TaskGroup", "InProgress", null, null, ""
      )
    """.format(cycle_id=cycle_id)
    conn.execute(sql)

    import ipdb; ipdb.set_trace()
    #raise IntegrityError
    
    transaction.commit()
    import ipdb; ipdb.set_trace()
  except IntegrityError as error:
    app.logger.error(error)
    transaction.rollback()
    conn.execute("alter table workflows drop column kind")
    raise StandardError
  except:
    transaction.rollback()
    conn.execute("alter table workflows drop column kind")
    raise StandardError
 

  pass


def downgrade():
  pass
