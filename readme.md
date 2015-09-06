
Submission for /r/pygame challenge


###Features

Infinite grid - new cells are added to the edges of the grid when necessary. As you might expect this results in progressively slower performance as the grid grows.

Draw Modes - Cells can be drawn as squares or circles or the connections between live cells (from center to center) can be drawn as lines.

Color schemes - Cells are colored depending on the number of live neighbors.

Staggered Grids - I experimented with a non-orthogonal (but not actually hexagonal) grid. This means only 6 neighbors instead of 8 as well as different neighborhood indices depending on the whether the cell's column
is even or odd.

Rule Variants - Nine additional rules with interesting enough behavior that they have names. 
 
###Controls

ESC - exit
SPACE - toggle between editing and running sim
UP/DOWN - speed up / slow down sim
R - shortcut for Randomize button - randomly sets all cells in grid to alive or dead
P - shortcut for Patterns button
Click Cell - in editing mode this will toggle the cell between alive and dead


###Patterns

Pretty much only implemented for Game of Life, but clicking on the Patterns button opens a menu of pre-defined patterns. Click on a pattern and you'll return to editing mode with that pattern ready to be placed on the grid.