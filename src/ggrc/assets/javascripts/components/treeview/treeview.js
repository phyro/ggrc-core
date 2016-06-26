/*!
    Copyright (C) 2016 Google Inc., authors, and contributors <see AUTHORS file>
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
    Created By: tomaz@reciprocitylabs.com
    Maintained By: tomaz@reciprocitylabs.com
*/

(function (can, $) {
  'use strict';
  /**
   *  Treeview component which renders a treeview with given options
   *
   *  @param {JSON} treeViewOptions - options for the treeview eg.
   *   {
   *     draw_children: true,
   *     parent_instance: object,
   *     model: CMS.Models.CycleTaskGroupObjectTask,
   *     mapping: 'cycle_task_group_object_tasks',
   *     header_view: GGRC.mustache_path +
            '/cycle_task_group_object_tasks/tree_header.mustache',
   *     add_item_view: GGRC.mustache_path +
   *       '/cycle_task_group_object_tasks/tree_add_item.mustache'
   *   }
   *  @param {can.Model} instance - instance that will act as
   *    parent_instance for the treeview (mapping will be applied on it)
   */

  GGRC.Components('treeview', {
    tag: 'tree-view',
    template: can.view(GGRC.mustache_path +
      '/treeview/treeview.mustache'),
    scope: {
      treeViewOptions: undefined,
      instance: undefined
    },
    events: {
      '{scope} instance': function () {
        // Sets treeview options and recreates treeview
        var options = this.scope.attr('treeViewOptions');
        if (this.scope.instance) {
          options.attr('parent_instance', this.scope.attr('instance'));
        }
        if (this.scope._treeView) {
          // Empty and destroy treeview
          this.scope._treeView.element.empty();
          this.scope._treeView.custom_destroy();
        }
        // NOTE: even though you kill stickies in custom_destroy this component
        // could get rerendered with a new scope, meaning that the previous one
        // didn't get destroyed with custom_destroy
        Stickyfill.kill();
        // Create a new treeview and display it
        this.scope._treeView = new CMS.Controllers.TreeView(
          this.element.find('.tree-structure'), options);
        // Display treeview
        this.scope._treeView.display();
      }
    }
  });
})(window.can, window.can.$);
