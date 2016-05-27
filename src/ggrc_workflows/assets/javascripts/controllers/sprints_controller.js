/*!
    Copyright (C) 2016 Google Inc., authors, and contributors <see AUTHORS file>
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
    Created By: tomaz@reciprocitylabs.com
    Maintained By: tomaz@reciprocitylabs.com
*/

can.Control("CMS.Controllers.Sprints", {
  defaults: {
    view: GGRC.mustache_path + '/workflows/sprints.mustache',
    workflow: GGRC.page_instance()
  }
}, {
  init: function (el, options) {
    this.render_page(el, options);
  },
  render_page: function (el, options) {
    // Get workflow cycles and sort them by created_at
    options.workflow.get_binding('cycles').refresh_instances()
    .then(function (cycles) {
      var cycleInstances = _.map(cycles, 'instance');

      var sortedCycles = _.sortBy(cycleInstances, function (cycle) {
        return -cycle.created_at;
      });

      var view = can.view(this.options.view, {
        tree_view_options: options,
        workflow: GGRC.page_instance(),
        cycles: sortedCycles
      });
      this.element.html(view);
    }.bind(this));
  },
  '{workflow.status} change': function () {
    // If the cycle is activated you need to rerender Sprints tab
    this.render_page(this.element, this.options);
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

// Component with dropdown mapping
can.Component.extend({
  tag: "dropdown-mapping",
  template: can.view(GGRC.mustache_path +
    '/workflows/dropdown_mapping.mustache'),
  scope: {
    instances: [],
    selectedId: undefined
  }
});
