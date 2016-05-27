/*!
    Copyright (C) 2016 Google Inc., authors, and contributors <see AUTHORS file>
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
    Created By: tomaz@reciprocitylabs.com
    Maintained By: tomaz@reciprocitylabs.com
*/

// Component with dropdown mapping
GGRC.Components('dropdown-mapping', {
  tag: 'dropdown-mapping',
  template: can.view(GGRC.mustache_path +
    '/workflows/dropdown_mapping.mustache'),
  scope: {
    instances: [],
    selectedId: undefined
  }
});
