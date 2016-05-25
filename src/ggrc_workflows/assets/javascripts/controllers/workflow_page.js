/*!
    Copyright (C) 2014 Google Inc., authors, and contributors <see AUTHORS file>
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
    Created By: dan@reciprocitylabs.com
    Maintained By: dan@reciprocitylabs.com
*/

;(function(CMS, GGRC, can, $) {

  function _generate_cycle() {
    var workflow = GGRC.page_instance(),
        dfd = new $.Deferred(),
        cycle;

    GGRC.Controllers.Modals.confirm({
      modal_title : "Confirm",
      modal_confirm : "Proceed",
      skip_refresh : true,
      button_view : GGRC.mustache_path + "/workflows/confirm_start_buttons.mustache",
      content_view : GGRC.mustache_path + "/workflows/confirm_start.mustache",
      instance : workflow
    }, function(params, option) {
      var data = {};

      can.each(params, function(item) {
        data[item.name] = item.value;
      });

      cycle = new CMS.Models.Cycle({
        context: workflow.context.stub(),
        workflow: { id: workflow.id, type: "Workflow" },
        autogenerate: true
      });

      cycle.save().then(function(cycle) {
        // Cycle created. Workflow started.
        setTimeout(function() {
          dfd.resolve();
          window.location.hash = 'current_widget/cycle/' + cycle.id;
        }, 250);
      });
    }, function() {
      dfd.reject();
    });
    return dfd;
  }

  can.Control("GGRC.Controllers.WorkflowPage", {
    defaults: {
    }
  }, {
    //  FIXME: This should trigger expansion of the TreeNode, without using
    //    global event listeners or routes or timeouts, but currently object
    //    creation and tree insertion is disconnected.
    "{CMS.Models.TaskGroup} created": function(model, ev, instance) {
      if (instance instanceof CMS.Models.TaskGroup) {
        setTimeout(function() {
          // If the TaskGroup was created as part of a Workflow, we don't want to
          //  do a redirect here
          if (instance._no_redirect) {
            return;
          }
          window.location.hash =
            'task_group_widget/task_group/' + instance.id;
        }, 250);
      }
    }
  });

  can.Component.extend({
    tag: "workflow-start-cycle",
    content: "<content/>",
    events: {
      click: _generate_cycle
    }
  });

  can.Component.extend({
    tag: "workflow-activate",
    template: "<content/>",
    init: function() {
      this.scope._can_activate_def();
    },
    scope: {
      waiting: true,
      can_activate: false,
      _can_activate_def: function() {
        var self = this,
            workflow = GGRC.page_instance();
        self.attr('waiting', true);
        $.when(
          workflow.refresh_all('task_groups', 'task_group_objects'),
          workflow.refresh_all('task_groups', 'task_group_tasks')
        ).then(function() {
          var task_groups = workflow.task_groups.reify(),
              can_activate = task_groups.length;

          task_groups.each(function(task_group) {
            if (!task_group.task_group_tasks.length) {
              can_activate = false;
            }
          });
          self.attr('can_activate', can_activate);
          self.attr('waiting', false);
        });
      },
      _handle_refresh: function (model) {
        var models = ['TaskGroup', 'TaskGroupTask', 'TaskGroupObject'];
        if (models.indexOf(model.shortName) > -1) {
          this._can_activate_def();
        }
      },
      _restore_button: function () {
          this.attr('waiting', false);
      },
      _activate: function() {
        var workflow = GGRC.page_instance(),
            scope = this,
            restore_button = scope._restore_button.bind(scope),
            cycle;
        scope.attr('waiting', true);
        if (workflow.frequency !== 'one_time') {
          workflow.refresh().then(function() {
            workflow.attr('recurrences', true);
            workflow.attr('status', "Active");
            return workflow.save();
          }, restore_button).then(function(workflow) {
            if (moment(workflow.next_cycle_start_date).isSame(moment(), "day")) {
              return new CMS.Models.Cycle({
                context: workflow.context.stub(),
                workflow: { id: workflow.id, type: "Workflow" },
                autogenerate: true
              }).save();
            }
          }, restore_button).then(restore_button);
        } else {
          _generate_cycle().then(function() {
            return workflow.refresh();
          }, restore_button).then(function(workflow) {
            return workflow.attr('status', "Active").save();
          }, restore_button).then(restore_button);
        }
      }
    },
    events: {
      "{can.Model.Cacheable} created": function(model) {
        this.scope._handle_refresh(model);
      },
      "{can.Model.Cacheable} destroyed": function(model) {
        this.scope._handle_refresh(model);
      },
      "button click": function() {
        this.scope._activate();
      }
    }
  });

  can.Component.extend({
    tag: "workflow-deactivate",
    template: "<content/>",
    events: {
      click: function() {
        var workflow = GGRC.page_instance();
        workflow.refresh().then(function(workflow) {
          workflow.attr('recurrences', false).save();
        });
      }
    }
  });


  can.Model.Cacheable("CMS.ModelHelpers.CloneWorkflow", {
    defaults : {
      clone_people: true,
      clone_tasks: true,
      clone_objects: true
    }
  }, {
    refresh: function() {
      return $.when(this);
    },
    save: function() {
      var workflow = new CMS.Models.Workflow({
        clone: this.source_workflow.id,
        context: null,
        clone_people: this.clone_people,
        clone_tasks: this.clone_tasks,
        clone_objects: this.clone_objects
      });

      return workflow.save().then(function(workflow) {
        GGRC.navigate(workflow.viewLink);
        return this;
      });

    }
  });

  can.Component.extend({
    tag: "workflow-clone",
    template: "<content/>",
    events: {
      click: function(el) {
        var workflow, $target;

        $target = $('<div class="modal hide"></div>').uniqueId();
        $target.modal_form({}, el);
        $target.ggrc_controllers_modals({
          modal_title: "Clone Workflow",
          model: CMS.ModelHelpers.CloneWorkflow,
          instance: new CMS.ModelHelpers.CloneWorkflow({ source_workflow: this.scope.workflow }),
          content_view: GGRC.mustache_path + "/workflows/clone_modal_content.mustache",
          custom_save_button_text: "Proceed",
          button_view: GGRC.Controllers.Modals.BUTTON_VIEW_SAVE_CANCEL
        });
      }
    }
  });

  can.Model.Cacheable("CMS.ModelHelpers.CloneTaskGroup", {
    defaults : {
      clone_objects: true,
      clone_tasks: true,
      clone_people: true
    }
  }, {
    refresh: function() {
      return $.when(this);
    },
    save: function() {
      var task_group = new CMS.Models.TaskGroup({
        clone: this.source_task_group.id,
        context: null,
        clone_objects: this.clone_objects,
        clone_tasks: this.clone_tasks,
        clone_people: this.clone_people
      });

      return task_group.save();
    }
  });

  can.Component.extend({
    tag: "task-group-clone",
    template: "<content/>",
    events: {
      click: function(el) {
        var $target;

        $target = $('<div class="modal hide"></div>').uniqueId();
        $target.modal_form({}, el);
        $target.ggrc_controllers_modals({
          modal_title: "Clone Task Group",
          model: CMS.ModelHelpers.CloneTaskGroup,
          instance: new CMS.ModelHelpers.CloneTaskGroup({ source_task_group: this.scope.taskGroup }),
          content_view: GGRC.mustache_path + "/task_groups/clone_modal_content.mustache",
          custom_save_button_text: "Proceed",
          button_view: GGRC.Controllers.Modals.BUTTON_VIEW_SAVE_CANCEL
        });
      }
    }
  });

  can.Component.extend({
    tag: "cycle-end-cycle",
    template: "<content/>",
    events: {
      click: function () {
        this.scope.cycle.refresh().then(function (cycle) {
          cycle.attr('is_current', false).save().then(function () {
            return GGRC.page_instance().refresh();
          }).then(function () {
            // We need to update person's assigned_tasks mapping manually
            var person_id = GGRC.current_user.id,
                person = CMS.Models.Person.cache[person_id];
                binding = person.get_binding('assigned_tasks');

            // FIXME: Find a better way of removing stagnant items from the list.
            binding.list.splice(0, binding.list.length);
            return binding.loader.refresh_list(binding);
          });
        });
      }
    }
  });

  /**
   * This component listens for changes on selectedId so it can changes
   * the selectedInstance which is needed by some of it's child elements
   */
  can.Component.extend({
    tag: "sprints-observer",
    template: "<content/>",
    scope: {
      instances: undefined,
      selectedId: null,
      selectedInstance: null
    },
    init: function () {
      var active = _.first(this.scope.instances);
      if (active && active.id) {
        this.scope.attr('selectedId', active.id);
      }
    },
    events: {
      '{scope} selectedId': function () {
        this.scope.attr('selectedInstance',
                        _.find(this.scope.instances, function (inst) {
                          return inst.id === Number(this.scope.selectedId);
                        }.bind(this)));
      }
    }
  });

  /**
   *  Treeview component which renders a treeview with given options
   *
   *  @param {JSON} treeViewOptions - options for the treeview eg.
   *   {
   *     draw_children: true,
   *     parent_instance: object,
   *     model: CMS.Models.CycleTaskGroupObjectTask,
   *     mapping: 'cycle_task_group_object_tasks',
   *     header_view: GGRC.mustache_path + '/cycle_task_group_object_tasks/tree_header.mustache',
   *     add_item_view: GGRC.mustache_path +
   *       '/cycle_task_group_object_tasks/tree_add_item.mustache'
   *   }
   *    reified
   *  @param {can.Model} instance - instance that will act as
   *    parent_instance for the treeview (mapping will be applied on it)
   */

  can.Component.extend({
    tag: "tree-view",
    template: "<div><ul class='tree-structure new-tree'></ul></div>",
    scope: {
      treeViewOptions: undefined,
      instance: undefined
    },
    events: {
      '{scope} instance': function () {
        // Sets treeview options and recreates treeview
        var rerender = false;
        var options = this.scope.attr('treeViewOptions');
        if (this.scope.instance) {
          options.attr('parent_instance', this.scope.attr('instance'));
        }
        if (this.scope._treeView) {
          // If you already have a treeview you have it's header so don't
          // add another one when creating a new treeview
          options.show_header = false;
          rerender = true;
          // Empty and destroy treeview
          this.scope._treeView.element.empty();
          this.scope._treeView.destroy();
        }
        // Create a new treeview and display it
        this.scope._treeView = new CMS.Controllers.TreeView(this.element.find('.tree-structure'), options);

        // rebind header_view events
        var treeview_dfd = this.scope._treeView.display();
        if (rerender) {
          // Because you're rerendering only the treeview you must bind events
          // for treeview header
          treeview_dfd.then(function (data) {
            if (this.scope._treeView.element) {
              var treeview = this.scope._treeView.element.control();
              if (treeview) {
                treeview.bind_header_events();
              }
            }
          }.bind(this));
        }
      }
    }
  });

  can.Component.extend({
    tag: "dropdown-mapping",
    template: can.view(GGRC.mustache_path +
      '/workflows/dropdown_mapping.mustache'),
    scope: {
      instances: [],
      selectedId: undefined
    }
  });
})(this.CMS, this.GGRC, this.can, this.can.$);
