/*!
    Copyright (C) 2014 Google Inc., authors, and contributors <see AUTHORS file>
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
    Created By: brad@reciprocitylabs.com
    Maintained By: brad@reciprocitylabs.com
*/

;(function(can, $, CMS) {

can.Observe("CMS.ModelHelpers.CycleTask", {
  findInCacheById : function() { return null; },
}, {
  init : function() {
    this.attr("owners", new CMS.Models.Person.List(this.owners));
  },
  save : function() {
    var that = this;
    // FIXME: temporary fix for 'Could not get any raw data while
    // converting using .models'
    this._data.owners = $.map(this._data.owners, function(owner){
      return {
        id: owner.id,
        type: owner.type,
      };
    });
    return new CMS.Models.TaskGroupTask({
      task_group: that.task_group,
      title: that.title,
      description: that.description,
      sort_index: Number.MAX_SAFE_INTEGER / 2,
      contact: that.contact,
      context: that.context
    }).save().then(function(task_group_task) {
      return new CMS.Models.CycleTaskGroupObjectTask({
        cycle: that.cycle,
        start_date: that.cycle.reify().start_date,
        end_date: that.cycle.reify().end_date,
        task_group_task: task_group_task,
        sort_index: that.sort_index,
        title: that.title,
        description: that.description,
        status: "Assigned",
        contact: that.contact,
        context: that.context
      }).save();
    });
  },
  computed_errors: can.compute(function() {
    var errors = null;
    if(!this.attr("title")) {
      errors = { title: "Must be defined" };
    }
    return errors;
  })
});

var approval_workflow_errors_compute;
can.Observe("CMS.ModelHelpers.ApprovalWorkflow", {
  defaults : {
    original_object: null
  }
}, {
  save: function() {
    var that = this,
        aws_dfd = this.original_object.get_binding("approval_workflows").refresh_list();

    return aws_dfd.then(function(aws){
      var ret;
      if (aws.length < 1) {
        ret = $.when(
          new CMS.Models.Workflow({
            frequency: "one_time",
            status: "Active",
            title: "Object review for "
                    + that.original_object.constructor.title_singular
                    + ' "' + that.original_object.title + '"',
            object_approval: true,
            notify_on_change: true,
            notify_custom_message: "<br/><br/>"
              + GGRC.current_user.name + " (" + GGRC.current_user.email
              + ") asked you to review newly created "
              + that.original_object.constructor.model_singular + ' "' + that.original_object.title
              + '" before ' + moment(that.end_date).format("MM/DD/YYYY") + ". "
              + "Click <a href='" + window.location.href.replace(/#.*$/, "")
              + "#workflows_widget'>here</a> to perform a review.",
            context: that.original_object.context
          }).save()
        ).then(function(wf) {
            return $.when(
              wf,
              new CMS.Models.TaskGroup({
                workflow : wf,
                title: "Object review for "
                        + that.original_object.constructor.title_singular
                        + ' "' + that.original_object.title + '"',
                contact: that.contact,
                context: wf.context
              }).save()
            );
        }).then(function(wf, tg) {
            return $.when(
              wf,
              new CMS.Models.TaskGroupTask({
                task_group: tg,
                start_date: moment().format('MM/DD/YYYY'),
                end_date: that.end_date,
                object_approval: true,
                sort_index: (Number.MAX_SAFE_INTEGER / 2).toString(10),
                contact: that.contact,
                context: wf.context,
                task_type: "text",
                title: "Object review for "
                        + that.original_object.constructor.title_singular
                        + ' "' + that.original_object.title + '"'
              }).save()
            );
        }).then(function (wf, tgt) {
          return $.when(
            wf,
            new CMS.Models.Relationship({
              source: tgt,
              destination: that.original_object,
              context: wf.context
            }).save()
          );
        });
      } else {
        ret = $.when(
          aws[0].instance.refresh(),
          $.when.apply(
            $,
            can.map(aws[0].instance.task_groups.reify(), function(tg) {
              return tg.refresh();
            })
          ).then(function() {
            return $.when.apply($, can.map(can.makeArray(arguments), function(tg) {
              return tg.attr("contact", that.contact).save().then(function(tg) {
                return $.when.apply($, can.map(tg.task_group_tasks.reify(), function(tgt) {
                  return tgt.refresh().then(function(tgt) {
                    return tgt.attr({
                      'contact': that.contact,
                      'end_date': that.end_date,
                      'start_date': moment().format('MM/DD/YYYY'),
                      'task_type': tgt.task_type || 'text'
                      }).save();
                  });
                }));
              });
            }));
          })
        );
      }

      return ret.then(function(wf) {
        return new CMS.Models.Cycle({
          workflow: wf,
          autogenerate: true,
          context: wf.context
        }).save();
      });
    });
  },
  computed_errors: (approval_workflow_errors_compute = can.compute(function() {
    var errors = null;
    if(!this.attr("contact")) {
      errors = { contact: "Must be defined" };
    }
    if(!this.attr("end_date")) {
      errors = $.extend(errors, { end_date : "Must be defined" });
    }
    return errors;
  })),
  computed_unsuppressed_errors: approval_workflow_errors_compute
});

})(this.can, this.can.$, this.CMS);
