/*!
    Copyright (C) 2016 Google Inc., authors, and contributors <see AUTHORS file>
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
    Created By: tomaz@reciprocitylabs.com
    Maintained By: tomaz@reciprocitylabs.com
*/

can.Control("CMS.Controllers.Sprints", {
  defaults: {
    view: GGRC.mustache_path + '/workflows/sprints.mustache'
  }
}, {
  init: function (el, options) {
    var workflow = GGRC.page_instance();
    // Get workflow cycles and sort them by created_at
    workflow.get_binding('cycles').refresh_instances().then(function (cycles) {
      var cycles = _.map(cycles, 'instance');

      var sortedCycles = _.sortBy(cycles, function (cycle) {
        return -cycle.created_at;
      });

      var view = can.view(this.options.view, {
        tree_view_options: options,
        workflow: GGRC.page_instance(),
        cycles: sortedCycles
      });
      this.element.html(view);
    }.bind(this));
  }
});
