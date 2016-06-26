/*!
    Copyright (C) 2016 Google Inc., authors, and contributors <see AUTHORS file>
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
    Created By: tomaz@reciprocitylabs.com
    Maintained By: tomaz@reciprocitylabs.com
*/

/**
 * This component listens for changes on selectedId so it can changes
 * the selectedInstance which is needed by some of it's child elements
 */
GGRC.Components('sprints-observer', {
  tag: 'sprints-observer',
  template: '<content/>',
  scope: {
    instances: null,
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
      var selected = _.find(this.scope.instances, function (inst) {
        return inst.id === Number(this.scope.selectedId);
      }.bind(this))
      this.scope.attr('selectedInstance', selected);
    }
  }
});
