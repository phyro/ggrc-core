# Copyright (C) 2016 Google Inc., authors, and contributors <see AUTHORS file>
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
# Created By: tomaz@reciprocitylabs.com
# Maintained By: tomaz@reciprocitylabs.com

"""Add label column to task and cycletask

Revision ID: 24da4fdcf53a
Revises: 851b2f37a61
Create Date: 2016-05-03 14:30:45.738793

"""

# revision identifiers, used by Alembic.
revision = '24da4fdcf53a' # pylint: disable=invalid-name
down_revision = '851b2f37a61' # pylint: disable=invalid-name

from alembic import op
import sqlalchemy as sa


def upgrade():
  # TODO: 2 space indent.
  op.add_column('task_group_tasks',
                sa.Column('label', sa.String(length=250), nullable=True))
  op.add_column('cycle_task_group_object_tasks',
                sa.Column('label', sa.String(length=250), nullable=True))
  # Set label column to the value of parent group title
  # task_group_task
  sql = """
      UPDATE task_group_tasks
      LEFT JOIN task_groups
          ON task_group_tasks.task_group_id = task_groups.id
      SET task_group_tasks.label = task_groups.title
  """
  op.execute(sql)
  # cycle_task_group_object_task
  sql = """
      UPDATE cycle_task_group_object_tasks as ctgot
      LEFT JOIN cycle_task_groups as ctg
          ON ctgot.cycle_task_group_id = ctg.id
      SET ctgot.label = ctg.title
  """
  op.execute(sql)


def downgrade():
  op.drop_column('task_group_tasks', 'label')
  op.drop_column('cycle_task_group_object_tasks', 'label')
