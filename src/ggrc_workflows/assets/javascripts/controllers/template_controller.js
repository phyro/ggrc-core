/*!
    Copyright (C) 2016 Google Inc., authors, and contributors <see AUTHORS file>
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
    Created By: tomaz@reciprocitylabs.com
    Maintained By: tomaz@reciprocitylabs.com
*/

can.Control("CMS.Controllers.Template", {
  defaults: {
    view: GGRC.mustache_path + '/workflows/template.mustache'
  }
}, {
  init: function (el, options) {
    this.render_page(el, options);
  },
  render_page: function (el, options) {
    var treeview;
    var view = can.view(this.options.view, {
      workflow: GGRC.page_instance()
    });
    this.element.html(view);

    // render TreeView
    treeview = new CMS.Controllers.TreeView(
      this.element.find('.tree-structure'), options);
    treeview.display();
  }
});
