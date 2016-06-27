/*!
    Copyright (C) 2016 Google Inc.
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
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
    // set filter hidden on this page by default
    CMS.Models.DisplayPrefs.getSingleton().then(function (display_prefs) {
      display_prefs.setFilterHidden(true);
    }).then(function () {
      // Get workflow cycles and sort them by created_at
      options.workflow.refresh_all('cycles').then(function (cycles) {
        var sortedCycles = _.sortBy(cycles, function (cycle) {
          return -cycle.created_at;
        });

        var view = can.view(
          this.options.view,
          {
            treeViewOptions: options,
            workflow: GGRC.page_instance(),
            cycles: sortedCycles
          });
        this.element.html(view);
      }.bind(this));
    }.bind(this));
  },
  '{workflow} next_cycle_start_date': function () {
    // If cycle gets added you need to rerender Sprints tab
    this.renderPage(this.element, this.options);
  },
  '{workflow} status': function () {
    // If the cycle is activated on one-time workflow you need
    // to rerender Sprints tab
    this.renderPage(this.element, this.options);
  }
});
