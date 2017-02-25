import bottle
import os
import random

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
        distance_x, distance_y =  get_distance(my_head, food_location)
        total = abs(distance_x) + abs(distance_y)
        return total

    all_food = map(get_food_value, data["food"])

    smallest = min(all_food)
    food_index = all_food.index(smallest)
    return data["food"][food_index]


def get_next_move(data, target_location):

    my_snake = _get_me(data)
    my_location = my_snake["coords"]
    my_head = my_location[0]

    distance_x, distance_y =  get_distance(my_head, target_location)
    
    if abs(distance_x) > abs(distance_y):
        if distance_x > 0:
            return "left"
        else:
            return "right"

    if distance_y > 0:
        return "up"
    else:
        return "down"


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
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))
