# Copyright (C) 2015 Google Inc., authors, and contributors <see AUTHORS file>
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
# Created By: miha@reciprocitylabs.com
# Maintained By: urban@reciprocitylabs.com


"""Tests for workflow specific imports."""

from datetime import date
from os.path import abspath
from os.path import dirname
from os.path import join

from integration.ggrc.converters import TestCase

from ggrc import db
from ggrc.converters import errors
from ggrc_workflows.models.task_group import TaskGroup
from ggrc_workflows.models.task_group_object import TaskGroupObject
from ggrc_workflows.models.task_group_task import TaskGroupTask
from ggrc_workflows.models.workflow import Workflow

THIS_ABS_PATH = abspath(dirname(__file__))


class TestWorkflowObjectsImport(TestCase):
  """Test imports for basic workflow objects."""

  CSV_DIR = join(THIS_ABS_PATH, "test_csvs/")

  def setUp(self):
    TestCase.setUp(self)
    self.client.get("/login")

  def test_full_good_import(self):
    """Test full good import without any warnings."""
    filename = "workflow_small_sheet.csv"
    response = self.import_file(filename)

    messages = ("block_errors", "block_warnings", "row_errors", "row_warnings")

    for block in response:
      for message in messages:
        self.assertEqual(set(), set(block[message]))

    self.assertEqual(1, Workflow.query.count())
    self.assertEqual(1, TaskGroup.query.count())
    self.assertEqual(4, TaskGroupTask.query.count())
    self.assertEqual(0, TaskGroupObject.query.count())

    task2 = TaskGroupTask.query.filter_by(slug="t-2").first()
    task3 = TaskGroupTask.query.filter_by(slug="t-3").first()
    task4 = TaskGroupTask.query.filter_by(slug="t-4").first()
    self.assertEqual(task2.start_date, date(2015, 7, 10))
    self.assertEqual(task2.end_date, date(2016, 12, 30))
    self.assertIn("ch2", task3.response_options)
    self.assertIn("option 1", task4.response_options)
    # check that tasks have relationships to objectives
    self.assertEqual(len(task2.related_sources + task2.related_destinations),
                     3)
    self.assertEqual(len(task3.related_sources + task3.related_destinations),
                     2)

  def test_import_task_date_format(self):
    """Test import of tasks for workflows

    This is a test for various imports of task dates for all types of
    workflows. This test ignores all warnings returned by the file import,
    since those are verified in a different test.

    Raises:
      AssertionError: if the start and end values on tasks don't match the
        values in the imported csv files.
    """
    filename = "workflow_big_sheet.csv"
    self.import_file(filename)

    # Assert that CSV import got imported correctly
    getters = {
        "one_time": lambda task: (task.start_date, task.end_date),
        "weekly": lambda task: (task.relative_start_day,
                                task.relative_end_day),
        "monthly": lambda task: (task.relative_start_day,
                                 task.relative_end_day),
        "quarterly": lambda task: ((task.relative_start_month,
                                    task.relative_start_day),
                                   (task.relative_end_month,
                                    task.relative_end_day)),
        "annually": lambda task: ((task.relative_start_month,
                                   task.relative_start_day),
                                  (task.relative_end_month,
                                   task.relative_end_day))
    }

    tasks = [
        ["task-1", "one_time", (date(2015, 7, 1), date(2015, 7, 15))],
        ["task-2", "weekly", (2, 5)],
        ["task-3", "monthly", (1, 22)],
        ["task-4", "quarterly", ((1, 5), (2, 15))],
        ["task-10", "quarterly", ((3, 5), (1, 1))],
        ["task-11", "quarterly", ((3, 5), (1, 1))],
        ["task-5", "annually", ((5, 7), (7, 15))],
    ]

    for slug, freq, result in tasks:
      task = db.session.query(TaskGroupTask).filter(
          TaskGroupTask.slug == slug).one()
      getter = getters[freq]
      self.assertEqual(task.task_group.workflow.frequency, freq)
      self.assertEqual(
          getter(task), result,
          "Failed importing data for task with slug = '{}'".format(slug))

  def test_import_task_types(self):
    """Test task import with warnings

    Check that the warnings for bay task type field work and that the task type
    gets set to default when an invalid values is found in the csv.

    Raises:
      AssertionError: When file import does not return correct errors for the
        example csv, or if any of the tasks does not have the expected task
        type.

    """
    filename = "workflow_big_sheet.csv"
    response = self.import_file(filename)
    expected_messages = {
        "Workflow": {},
        "Task Group": {},
        "Task Group Task": {
            "row_warnings": set([
                errors.WRONG_REQUIRED_VALUE.format(
                    line=38, value="aaaa", column_name="Task Type"
                ),
                errors.MISSING_VALUE_WARNING.format(
                    line=39, default_value="Rich Text", column_name="Task Type"
                ),
                errors.MISSING_VALUE_WARNING.format(
                    line=40, default_value="Rich Text", column_name="Task Type"
                ),
            ])
        },
    }
    messages = (
        "block_errors",
        "block_warnings",
        "row_errors",
        "row_warnings",
    )
    # Assert that there were no import errors
    for obj in response:
      if obj['name'] in expected_messages:
        for message in messages:
          self.assertEqual(
              set(obj[message]),
              expected_messages[obj["name"]].get(message, set())
          )
          self.assertEqual(obj["ignored"], 0)

    task_types = {
        "text": [
            "task-1",
            "task-2",
            "task-4",
            "task-7",
            "task-9",
            "task-10",
            "task-11",
        ],
        "menu": [
            "task-5",
            "task-8",
        ],
        "checkbox": [
            "task-3",
            "task-6",
        ],
    }

    for task_type, slugs in task_types.items():
      self._test_task_types(task_type, slugs)

    # test task relationships
    task_relationship_types = {
      "task-1": ["Policy", "Regulation"],
      "task-2": ["Objective"],
      "task-3": [],
      "task-4": [],
      "task-5": [],
      "task-6": ["Policy"] * 2 + ["Contract"] * 5,
      "task-7": ["Policy", "Regulation"],
      "task-8": ["Objective"],
      "task-9": [],
      "task-10": [],
      "task-11": []
    }
    tasks = db.session.query(TaskGroupTask).all()
    for task in tasks:
      task_rel_source_types = [r.source_type for r in task.related_sources]
      task_rel_destination_types = [r.destination_type
                                    for r in task.related_destinations]
      task_rel_types = task_rel_source_types + task_rel_destination_types
      self.assertEqual(sorted(task_rel_types),
                       sorted(task_relationship_types[task.slug]))


  def _test_task_types(self, expected_type, task_slugs):
    """Test that all listed tasks have rich text type.

    This is a part of the test_import_task_date_format

    Args:
      expected_type: Expected task type for all tasks specified by task_slugs.
      task_slugs: list of slugs for the tasks that will be tested.

    Raises:
      AssertionError: if any of the tasks does not exists or if their type is
        not text.
    """
    tasks = db.session.query(TaskGroupTask).filter(
        TaskGroupTask.slug.in_(task_slugs)).all()
    for task in tasks:
      self.assertEqual(
          task.task_type,
          expected_type,
          "task '{}' has type '{}', expected '{}'".format(
              task.slug,
              task.task_type,
              expected_type,
          )
      )
    self.assertEqual(len(tasks), len(task_slugs))
