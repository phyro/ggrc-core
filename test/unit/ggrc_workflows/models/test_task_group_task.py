# Copyright (C) 2016 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

import unittest
from datetime import date
from datetime import datetime
from sqlalchemy.orm import attributes


from ggrc import db
from ggrc.models import computed_property
from ggrc.models import mixins
from ggrc.models import relationship
from ggrc_workflows.models import task_group_task
from ggrc_workflows.models import mixins as wf_mixins

from unit.ggrc.models import test_mixins_base


class TestTaskGroupTask(unittest.TestCase):

  def test_validate_task_type(self):
    t = task_group_task.TaskGroupTask()
    self.assertRaises(ValueError, t.validate_task_type, "task_type", "helloh")
    self.assertEqual("menu", t.validate_task_type("task_type", "menu"))

  def test_validate_date(self):
    t = task_group_task.TaskGroupTask()
    self.assertEqual(date(2002, 4, 16), t.validate_date(date(2, 4, 16)))
    self.assertEqual(date(2014, 7, 23),
                     t.validate_date(datetime(2014, 7, 23, 22, 5, 7)))
    self.assertEqual(date(2014, 7, 23),
                     t.validate_date(datetime(2014, 7, 23, 0, 0, 0)))

  def test_validate_end_date_decorator(self):
    t = task_group_task.TaskGroupTask()
    t.end_date = date(15, 4, 17)
    self.assertEqual(date(2015, 4, 17), t.end_date)

    t.start_date = date(2015, 4, 17)
    self.assertRaises(ValueError,
                      t.validate_end_date, "end_date", date(2014, 2, 5))

    t.end_date = date(2015, 2, 17)
    self.assertEqual(date(2015, 2, 17), t.end_date)

  def test_validate_start_date_decorator(self):
    t = task_group_task.TaskGroupTask()
    t.start_date = date(16, 4, 21)
    self.assertEqual(date(2016, 4, 21), t.start_date)

    t.end_date = date(2016, 4, 21)

    t.start_date = date(2015, 2, 25)
    self.assertEqual(date(2015, 2, 25), t.start_date)

    t.start_date = date(2015, 6, 17)
    self.assertEqual(date(2015, 6, 17), t.start_date)


class TestTaskGroupTaskMixins(test_mixins_base.TestMixinsBase):
  """ Test that TaskGroupTask has the expected mixins and corresponding
  attributes """

  def setUp(self):
    self.model = task_group_task.TaskGroupTask
    self.included_mixins = [
        db.Model,
        mixins.Base,
        mixins.Described,
        mixins.Slugged,
        mixins.Titled,
        mixins.WithContact,
        relationship.Relatable,
        wf_mixins.RelativeTimeboxed,
    ]

    self.attributes_introduced = [
        ('task_group_id', attributes.InstrumentedAttribute),
        ('sort_index', attributes.InstrumentedAttribute),
        ('object_approval', attributes.InstrumentedAttribute),
        ('task_type', attributes.InstrumentedAttribute),
        ('response_options', attributes.InstrumentedAttribute),
        ('display_name', computed_property.computed_property),          # Base          # noqa
        ('description', attributes.InstrumentedAttribute),              # Described     # noqa
        ('slug', attributes.InstrumentedAttribute),                     # Slugged       # noqa
        ('title', attributes.InstrumentedAttribute),                    # Titled        # noqa
        ('contact_id', attributes.InstrumentedAttribute),               # WithContact   # noqa
        ('secondary_contact_id', attributes.InstrumentedAttribute),     # WithContact   # noqa
        ('contact', attributes.InstrumentedAttribute),                  # WithContact   # noqa
        ('secondary_contact', attributes.InstrumentedAttribute),        # WithContact   # noqa
        ('related_sources', attributes.InstrumentedAttribute),          # Relatable     # noqa
        ('related_destinations', attributes.InstrumentedAttribute),     # Relatable     # noqa
        ('relative_start_month', attributes.InstrumentedAttribute),     # RelativeTimeboxed   # noqa
        ('relative_start_day', attributes.InstrumentedAttribute),       # RelativeTimeboxed   # noqa
        ('relative_end_month', attributes.InstrumentedAttribute),       # RelativeTimeboxed   # noqa
        ('relative_end_day', attributes.InstrumentedAttribute),         # RelativeTimeboxed   # noqa
    ]
