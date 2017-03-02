import bottle
import os
import random
from pypaths import astar

# data
# example_data = {
#     u'snakes': [
#     {
#         u'health_points': 100,
#         u'taunt': u'df0bfa20-ff6f-4054-9007-9cce441bb534 (20x20)',
#         u'coords': [[1, 19], [1, 19], [1, 19]],
#         u'name': u'battlesnake-python',
#         u'id': u'50b127ee-d802-4aad-8310-53cc3c54dbf0'
#         }],
#     u'turn': 0,
#     u'food': [[19, 12]],
#     u'height': 20,
#     u'width': 20,
#     u'dead_snakes': [],
#     u'game_id': u'df0bfa20-ff6f-4054-9007-9cce441bb534',
#     u'you': u'50b127ee-d802-4aad-8310-53cc3c54dbf0'
# }


def _get_me(data):
    for snake in data["snakes"]:
        if snake["id"] == data["you"]:
            return snake
    raise Exception("I can't find myself!")


def get_distance(point_a, point_b):
    distance_x = point_a[0] - point_b[0]
    distance_y = point_a[1] - point_b[1]
    return distance_x, distance_y


def rate_my_food(data):
    my_snake = _get_me(data)
    my_location = my_snake["coords"]
    my_head = my_location[0]

    def get_food_value(food_location):
        distance_x, distance_y = get_distance(my_head, food_location)
        total = abs(distance_x) + abs(distance_y)
        return total

    all_food = map(get_food_value, data["food"])

    smallest = min(all_food)
    food_index = all_food.index(smallest)
    return data["food"][food_index]


def _is_occupied(data, target_location):

    all_snake_points = []
    for snake in data["snakes"]:
        all_snake_points.append(snake["coords"])

    return target_location in all_snake_points


def get_neighbors_function(data):

    def func(coord):
        neighbor_list = [(coord[0], coord[1] + 1),
                         (coord[0], coord[1] - 1),
                         (coord[0] + 1, coord[1]),
                         (coord[0] - 1, coord[1])]

        height = data["height"]
        width = data["width"]

        all_snake_points = []
        for snake in data["snakes"]:
            for point in snake["coords"]:
                all_snake_points.append(tuple(point))

        print "Looking in %s" % all_snake_points

        values = [c for c in neighbor_list
                if c != coord
                and c not in all_snake_points
                and c[0] >= 0 and c[0] < width
                and c[1] >= 0 and c[1] < height]

        print "Location %s has valid locations %s" %(coord, values)

        return values


    return func


def get_next_move(data, target_location):
    my_snake = _get_me(data)
    my_location = my_snake["coords"]
    my_head = my_location[0]

    # neighbors = astar.grid_neighbors(data["height"], data["width"])

    finder = astar.pathfinder(neighbors=get_neighbors_function(data))

    # ToDo: There is a better way of doing this
    search_start = tuple(my_head)
    search_end = tuple(target_location)
    total_moves, path = finder(search_start, search_end)

    next_x, next_y = path[1]
    head_x, head_y = my_head

    if head_x < next_x:
        return "right"

    if head_x > next_x:
        return "left"

    # y logic is reversed, not sure why
    if head_y < next_y:
        return "down"

    if head_y > next_y:
        return "up"

    raise Exception("I don't know where to go")

@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.post('/start')
def start():
    data = bottle.request.json
    game_id = data['game_id']
    board_width = data['width']
    board_height = data['height']

    head_url = '%s://%s/static/head.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    # TODO: Do things with data

    return {
        'color': '#00FF00',
        'taunt': '{} ({}x{})'.format(game_id, board_width, board_height),
        'head_url': head_url,
        'name': 'battlesnake-python'
    }


@bottle.post('/move')
def move():
    data = bottle.request.json

    print "Start Move for turn %s" % data["turn"]
    food_location = rate_my_food(data)

    print "The nearest best food is at %s" % food_location

    next_move = get_next_move(data, food_location)

    print "Moving snake %s" % next_move

    # TODO: Do things with data
    # directions = ['up', 'down', 'left', 'right']

    return {
        'move': next_move,
        'taunt': 'battlesnake-python!'
    }


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv(
        'IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))
