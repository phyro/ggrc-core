/*!
    Copyright (C) 2016 Google Inc.
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
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
