var fs = require('fs');
var tree = require('markdown-tree');

var flatten = function (tree, prefix) {
    if ()
}

fs.readFile('./spec.md', function (error, data) {
    console.log(flatten(tree(data.toString()), ''));
});
