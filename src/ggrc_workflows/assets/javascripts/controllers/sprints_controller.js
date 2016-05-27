/*!
    Copyright (C) 2016 Google Inc., authors, and contributors <see AUTHORS file>
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
    Created By: tomaz@reciprocitylabs.com
    Maintained By: tomaz@reciprocitylabs.com
*/

can.Control('CMS.Controllers.Sprints', {
  defaults: {
    view: GGRC.mustache_path + '/workflows/sprints.mustache',
    workflow: GGRC.page_instance()
  }
}, {
  init: function (el, options) {
    this.renderPage(el, options);
  },
  renderPage: function (el, options) {
    // Get workflow cycles and sort them by created_at
    options.workflow.get_binding('cycles').refresh_instances()
    .then(function (cycles) {
      var cycleInstances = _.map(cycles, 'instance');

      var sortedCycles = _.sortBy(cycleInstances, function (cycle) {
        return -cycle.created_at;
      });

      var view = can.view(this.options.view, {
        treeViewOptions: options,
        workflow: GGRC.page_instance(),
        cycles: sortedCycles
      });
      this.element.html(view);
    }.bind(this));
  },
  '{workflow.status} change': function () {
    // If the cycle is activated you need to rerender Sprints tab
    this.renderPage(this.element, this.options);
  }
});
