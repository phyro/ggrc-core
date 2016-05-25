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
    var view = can.view(this.options.view, {
      tree_view_options: options,
      workflow: GGRC.page_instance()
    });
    this.element.html(view);
  }
});
