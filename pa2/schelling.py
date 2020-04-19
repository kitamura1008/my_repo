'''
Schelling Model of Housing Segregation

OUR NAME Takayuki Kitamura
		 Tetsuo Fujino

Program for simulating a variant of Schelling's model of
housing segregation.  This program takes five parameters:

    filename -- name of a file containing a sample city grid

    R - The radius of the neighborhood: home at Location (i, j) is in
        the neighborhood of the home at Location (k,l)
        if k-R <= i <= k+R and l-R <= j <= l+R

    Similarity threshold - minimum acceptable threshold for ratio of the number
                           of similar neighbors to the number of occupied homes
                           in a neighborhood.

    Occupancy threshold - minimum acceptable threshold for ratio of the number
                          of occupied homes to the total number of homes
                          in a neighborhood.

    max_steps - the maximum number of passes to make over the city
                during a simulation.

Sample:
  python3 schelling.py --grid_file=tests/a19-sample-grid.txt --r=1 \
                       --simil_threshold=0.44 --occup_threshold=0.5 \
                       --max_steps=1
'''

import os
import sys
import click
import utility


def is_satisfied(grid, R, location, simil_threshold, occup_threshold):
    '''
    Determine whether or not the homeowner at a specific location is
    satisfied using a neighborhood of radius R and specified
    similarity and occupancy thresholds.

    Inputs:
        grid: the grid
        R: radius for the neighborhood
        location: a grid location
        simil_threshold: lower bound for similarity score
        occup_threshold: lower bound for occupancy score

    Returns: Boolean
    '''

    assert utility.is_grid(grid), ("The grid argument has the wrong type.  "
                                   "It should be a list of lists of strings "
                                   "with the same number of rows and columns")

    # We recommend adding an assertion to check that the location does
    # not contain an open (unoccupied) home.

    (x, y) = location

    assert grid[x][y] != "O"

    left = x - R
    if R > x:
        left = 0
    right = x + R
    if x + R >= len(grid):
        right = len(grid) - 1
    upr = y - R
    if R > y:
        upr = 0
    btm = y + R
    if y + R >= len(grid):
        btm = len(grid) - 1

    num_m_r = 0
    num_o = 0
    for x1 in range(left, right + 1):
        for y1 in range(upr, btm + 1):
            if grid[x1][y1] == grid[x][y]:
                num_m_r += 1
            if grid[x1][y1] == "O":
                num_o += 1

    simil_score = num_m_r / ((right - left + 1)*(btm - upr + 1) - num_o)
    occup_score = 1 - (num_o/ ((right - left + 1)*(btm - upr + 1)))

    return simil_score >= simil_threshold and occup_score >= occup_threshold


def best_loc(grid, R, location, simil_threshold, occup_threshold, opens):
    '''
    Find the nearest location which satisfies a homeowner.

    Inputs:
        grid: the grid
        R: radius for the neighborhood
        location: a grid location
        simil_threshold: lower bound for similarity score
        occup_threshold: lower bound for occupancy score
        opens: (list of tuples) a list of open locations

    Returns: (tuple) the best location for the homeowner
    '''
    (x, y) = location
    min_distance = 0
    num_satisfied_opens = 0
    best_location = (x, y)
    for (ox, oy) in opens:
        grid[ox][oy], grid[x][y] = grid[x][y], grid[ox][oy]
        if is_satisfied(grid, R, (ox, oy), simil_threshold, occup_threshold):
            distance = abs(x - ox) + abs(y - oy)
            num_satisfied_opens += 1
            if min_distance == 0 or min_distance >= distance:
                min_distance = distance
                best_location = (ox, oy)
        grid[ox][oy], grid[x][y] = grid[x][y], grid[ox][oy]
    if num_satisfied_opens == 1:
        best_location = (x, y)
    return best_location


def new_grid(grid, R, location, simil_threshold, occup_threshold, opens):
    '''
    Make the grid and the list of open locations, and count the number of
    relocation after a homeowner moves to the best location.

    Inputs:
        grid: the grid
        R: radius for the neighborhood
        location: a grid location
        simil_threshold: lower bound for similarity score
        occup_threshold: lower bound for occupancy score
        opens: (list of tuples) a list of open locations

    Returns: (int) the number of relocation
    '''
    reloc = 0
    (x, y) = location
    if not is_satisfied(grid, R, location, simil_threshold, occup_threshold):
        (i, j) = best_loc(grid, R, location, simil_threshold,
        	          occup_threshold, opens)
        if (i, j) != (x, y):
            grid[x][y], grid[i][j] = grid[i][j], grid[x][y]
            opens.remove((i, j))
            opens.append((x, y))
            reloc += 1
    return reloc


def sim_1step(grid, R, simil_threshold, occup_threshold, opens):
    '''
    simulate one step abou the whole grid.

    Inputs:
        grid: the grid
        R: radius for the neighborhood
        location: a grid location
        simil_threshold: lower bound for similarity score
        occup_threshold: lower bound for occupancy score
        opens: (list of tuples) a list of open locations

    Returns: (int) the total number of relocation during one step
    '''
    num_rel = 0
    for x in range(0, len(grid)):
        for y in range(0, len(grid)):
            if grid[x][y] != "O":
                reloc = new_grid(grid, R, (x, y), simil_threshold,
                	         occup_threshold, opens)
                num_rel += reloc
    return num_rel


#pylint: disable-msg=too-many-arguments
def do_simulation(grid, R, simil_threshold, occup_threshold, max_steps, opens):
    '''
    Do a full simulation.

    Inputs:
        grid: (list of lists of strings) the grid
        R: (int) radius for the neighborhood
        simil_threshold: (float) Similarity threshold
        occup_threshold: (float) Occupancy threshold
        max_steps: (int) maximum number of steps to do
        opens: (list of tuples) a list of open locations

    Returns:
        The total number of relocations completed.
    '''

    assert utility.is_grid(grid), ("The grid argument has the wrong type.  "
                                   "It should be a list of lists of strings "
                                   "with the same number of rows and columns")

    n_steps = 0
    acc_num_rel = 0
    while n_steps < max_steps:
        num_rel = sim_1step(grid, R, simil_threshold, occup_threshold, opens)
        acc_num_rel += num_rel
        n_steps += 1
        if num_rel == 0:
            break
    return acc_num_rel

@click.command(name="schelling")
@click.option('--grid_file', type=click.Path(exists=True))
@click.option('--r', type=int, default=1, help="neighborhood radius")
@click.option('--simil_threshold', type=float, default=0.44,
              help="Similarity threshold")
@click.option('--occup_threshold', type=float, default=0.70,
              help="Occupancy threshold")
@click.option('--max_steps', type=int, default=1)
def go(grid_file, r, simil_threshold, occup_threshold, max_steps):
    '''
    Put it all together: do the simulation and process the results.
    '''
    if grid_file is None:
        print("No parameters specified...just loading the code")
        return

    grid = utility.read_grid(grid_file)
    opens = utility.find_opens(grid)

    if len(grid) < 20:
        print("Initial state of city:")
        for row in grid:
            print(row)
        print()

    num_relocations = do_simulation(grid, r, simil_threshold,
                                    occup_threshold, max_steps,
                                    opens)
    print("Number of relocations done: " + str(num_relocations))

    if len(grid) < 20:
        print()
        print("Final state of the city:")
        for row in grid:
            print(row)

if __name__ == "__main__":
    go() # pylint: disable=no-value-for-parameter
