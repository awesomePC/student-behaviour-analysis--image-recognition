# Edit In Place jQuery plugin for Bootstrap
Super basic edit-in-place jquery plugin for Bootstrap.
Needed this for another project and thought it'd be cool to share it.

[Demo](https://dylangauthier.github.io/jquery-bootstrap-edit-in-place/)

## Getting Started

### Prerequisites

 1. Bootstrap 3.3
 2. jQuery

### Usage

Grab and import ` dist/eip.min.js` to your project.

Then change
```
<p>I want to become editable!</p>
```
to :
```
<p>
  <span class="whateveryouwant">I am now editable :D</span>
</p>
```

Then add 
```
$('.whateveryouwant').editable();
```

### Options

 - `onChange` : Callback `function()` when the input's value has been changed.

### TODO  - Do not allow editable elements like `body`, `table` and such.
 - Refactor code, pretty sure we can improve a lot.
 - Add support for others css frameworks or native.
 - Find limitations and fix them.
