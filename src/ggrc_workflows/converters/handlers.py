# Copyright (C) 2015 Google Inc., authors, and contributors <see AUTHORS file>
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
# Created By: miha@reciprocitylabs.com
# Maintained By: miha@reciprocitylabs.com

""" Module for all special column handlers for workflow objects """

from datetime import date

from ggrc import db
from ggrc.converters import errors
from ggrc.converters import get_importables
from ggrc.converters.handlers import CheckboxColumnHandler
from ggrc.converters.handlers import ColumnHandler
from ggrc.converters.handlers import UserColumnHandler
from ggrc.models import Person
from ggrc_workflows.models import CycleTaskGroup
from ggrc_workflows.models import TaskGroup
from ggrc_workflows.models import TaskGroupObject
from ggrc_workflows.models import Workflow
from ggrc_workflows.models import WorkflowPerson


class FrequencyColumnHandler(ColumnHandler):

  """ Handler for workflow frequency column """

  frequency_map = {
      "one time": "one_time"
  }

  def parse_item(self):
    """ parse frequency value

    Returning None will set the default frequency to one_time.
    """
    if not self.raw_value:
      return None
    value = self.raw_value.lower()
    frequency = self.frequency_map.get(value, value)
    if frequency not in self.row_converter.object_class.VALID_FREQUENCIES:
      self.add_error(errors.WRONG_VALUE_ERROR, column_name=self.display_name)
    return frequency

  def get_value(self):
    reverse_map = {v: k for k, v in self.frequency_map.items()}
    value = getattr(self.row_converter.obj, self.key, self.value)
    return reverse_map.get(value, value)


class ParentColumnHandler(ColumnHandler):

  """ handler for directly mapped columns """

  parent = None

  def __init__(self, row_converter, key, **options):
    super(ParentColumnHandler, self).__init__(row_converter, key, **options)

  def parse_item(self):
    """ get parent workflow id """
    # pylint: disable=protected-access
    if self.raw_value == "":
      self.add_error(errors.MISSING_VALUE_ERROR, column_name=self.display_name)
      return None
    slug = self.raw_value
    obj = self.new_objects.get(self.parent, {}).get(slug)
    if obj is None:
      obj = self.parent.query.filter(self.parent.slug == slug).first()
    if obj is None:
      self.add_error(errors.UNKNOWN_OBJECT,
                     object_type=self.parent._inflector.human_singular.title(),
                     slug=slug)
    return obj

  def get_value(self):
    value = getattr(self.row_converter.obj, self.key, self.value)
    return value.slug


class WorkflowColumnHandler(ParentColumnHandler):

  """ handler for workflow column in task groups """

  def __init__(self, row_converter, key, **options):
    """ init workflow handler """
    self.parent = Workflow
    super(WorkflowColumnHandler, self).__init__(row_converter, key, **options)


class TaskGroupColumnHandler(ParentColumnHandler):

  """ handler for task group column in task group tasks """

  def __init__(self, row_converter, key, **options):
    """ init task group handler """
    self.parent = TaskGroup
    super(TaskGroupColumnHandler, self).__init__(row_converter, key, **options)


class CycleTaskGroupColumnHandler(ParentColumnHandler):

  """ handler for task group column in task group tasks """

  def __init__(self, row_converter, key, **options):
    """ init task group handler """
    self.parent = CycleTaskGroup
    super(CycleTaskGroupColumnHandler, self).__init__(row_converter, key, **options)


class TaskDateColumnHandler(ColumnHandler):

  """ handler for start and end columns in task group tasks """

  def parse_item(self):
    """ parse start and end columns fow workflow tasks

    Parsed item will be in d, m, y order, with possible missisg y.
    """
    try:
      value = [int(v) for v in self.raw_value.split("/")]
      if len(value) > 1:
        tmp = value[0]
        value[0] = value[1]
        value[1] = tmp
      else:
        value.append(0)
      return value
    except ValueError:
      self.add_error(errors.WRONG_VALUE_ERROR, column_name=self.display_name)
    return None


class TaskStartColumnHandler(TaskDateColumnHandler):

  """ handler for start column in task group tasks """

  def set_obj_attr(self):
    """ set all possible start date attributes """
    frequency = self.row_converter.obj.task_group.workflow.frequency
    if frequency == "one_time":
      if len(self.value) != 3:
        self.add_error(errors.WRONG_VALUE_ERROR, column_name=self.display_name)
        return
      self.row_converter.obj.start_date = date(*self.value[::-1])
    self.row_converter.obj.relative_start_day = self.value[0]
    self.row_converter.obj.relative_start_month = self.value[1]


class TaskEndColumnHandler(TaskDateColumnHandler):

  """ handler for end column in task group tasks """

  def set_obj_attr(self):
    """ set all possible end date attributes """
    frequency = self.row_converter.obj.task_group.workflow.frequency
    if self.value is None:
      return
    frequency = self.row_converter.obj.task_group.workflow.frequency
    if frequency == "one_time":
      if len(self.value) != 3:
        self.add_error(errors.WRONG_VALUE_ERROR, column_name=self.display_name)
        return
      self.row_converter.obj.end_date = date(*self.value[::-1])
    self.row_converter.obj.relative_end_day = self.value[0]
    self.row_converter.obj.relative_end_month = self.value[1]


class TaskTypeColumnHandler(ColumnHandler):

  """ handler for task type column in task group tasks """

  type_map = {
      "rich text": "text",
      "drop down": "menu",
      "checkboxes": "checkbox",
  }

  def parse_item(self):
    """ parse task type column value """
    if self.raw_value == "":
      return None
    value = self.type_map.get(self.raw_value.lower())
    if value is None:
      self.add_warning(errors.WRONG_REQUIRED_VALUE,
                       value=self.raw_value,
                       column_name=self.display_name)
      value = self.row_converter.obj.default_task_type()
    return value


class WorkflowPersonColumnHandler(UserColumnHandler):

  def parse_item(self):
    return self.get_users_list()

  def set_obj_attr(self):
    pass

  def get_value(self):
    workflow_person = db.session.query(WorkflowPerson.person_id).filter_by(
        workflow_id=self.row_converter.obj.id,)
    users = Person.query.filter(Person.id.in_(workflow_person))
    emails = [user.email for user in users]
    return "\n".join(emails)

  def remove_current_people(self):
    WorkflowPerson.query.filter_by(
        workflow_id=self.row_converter.obj.id).delete()

  def insert_object(self):
    if self.dry_run or not self.value:
      return
    self.remove_current_people()
    for owner in self.value:
      workflow_person = WorkflowPerson(
          workflow=self.row_converter.obj,
          person=owner
      )
      db.session.add(workflow_person)
    self.dry_run = True


class ObjectsColumnHandler(ColumnHandler):

  def __init__(self, row_converter, key, **options):
    self.mappable = get_importables()
    self.new_slugs = row_converter.block_converter.converter.new_objects
    super(ObjectsColumnHandler, self).__init__(row_converter, key, **options)

  def parse_item(self):
    lines = [line.split(":", 1) for line in self.raw_value.splitlines()]
    objects = []
    for object_class, slug in lines:
      slug = slug.strip()
      class_ = self.mappable.get(object_class.strip().lower())
      new_object_slugs = self.new_slugs[class_]
      obj = class_.query.filter(class_.slug == slug).first()
      if obj:
        objects.append(obj)
      elif not (slug in new_object_slugs and self.dry_run):
        self.add_warning(errors.UNKNOWN_OBJECT,
                         object_type=class_._inflector.human_singular.title(),
                         slug=slug)
    return objects

  def set_obj_attr(self):
    self.value = self.parse_item()

  def get_value(self):
    task_group_objects = TaskGroupObject.query.filter_by(
        task_group_id=self.row_converter.obj.id).all()
    lines = ["{}: {}".format(t.object._inflector.title_singular.title(),
                             t.object.slug)
             for t in task_group_objects]
    return "\n".join(lines)

  def insert_object(self):
    for object_ in self.value:
      tgo = TaskGroupObject(
          task_group=self.row_converter.obj,
          object=object_,
      )
      db.session.add(tgo)
    db.session.flush()

  def set_value(self):
    pass

class ExportOnlyColumnHandler(ColumnHandler):

  def parse_item(self):
    pass

  def set_obj_attr(self):
    pass

  def get_value(self):
    return ""

  def insert_object(self):
    pass

  def set_value(self):
    pass


class CycleObjectColumnHandler(ExportOnlyColumnHandler):

  def get_value(self):
    obj = self.row_converter.obj.cycle_task_group_object
    if not obj or not obj.object:
      return ""
    return "{}: {}".format(obj.object._inflector.human_singular.title(),
                           obj.object.slug)


class CycleWorkflowColumnHandler(ExportOnlyColumnHandler):

  def get_value(self):
    return self.row_converter.obj.workflow.slug


COLUMN_HANDLERS = {
    "frequency": FrequencyColumnHandler,
    "cycle_task_group": CycleTaskGroupColumnHandler,
    "cycle_object": CycleObjectColumnHandler,
    "notify_on_change": CheckboxColumnHandler,
    "relative_end_date": TaskEndColumnHandler,
    "relative_start_date": TaskStartColumnHandler,
    "task_group": TaskGroupColumnHandler,
    "task_type": TaskTypeColumnHandler,
    "workflow": WorkflowColumnHandler,
    "cycle_workflow": CycleWorkflowColumnHandler,
    "workflow_mapped": WorkflowPersonColumnHandler,
    "task_group_objects": ObjectsColumnHandler,
}
