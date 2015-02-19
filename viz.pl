use Makefile::GraphViz;

$parser = Makefile::GraphViz->new;
$parser->parse('makefile');

# plot the tree rooted at the 'default' goal in Makefile:
$gv = $parser->plot;
$gv->as_png('default.png');
