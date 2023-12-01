import PySimpleGUI as sg #type:ignore
from PIL import Image
import io

def convert_to_bytes(img):
   with io.BytesIO() as bio:
      img.save(bio, format="PNG")
      del img
      return bio.getvalue()

def colours_used(team):
    if team == 1:
        return 1, 0, 0
    elif team == 2:
        return 0, 1, 0
    elif team == 3:
        return 0, 0, 1
    elif team == 4:
        return 0, 1, 1
    elif team == 5:
        return 1, 0, 1
    else:
        return 1, 1, 1

ROWS, COLUMNS = 20, 30
GRAPH_SIZE = (900, 600)

graph_colour_menu = []
for i in range (1, 7):
    round = ['Round ' + (str)(j) + '::,' + (str)(i) + ',' + (str)(j) for j in range(1, 10)]
    graph_colour_menu.append('Team ' + (str)(i))
    graph_colour_menu.append(round)

graph_board = [[sg.Graph(
    canvas_size=GRAPH_SIZE,
    graph_bottom_left=(0, 0),
    graph_top_right=GRAPH_SIZE,
    key="-GRAPH-",
    change_submits=True,  # mouse click events
    drag_submits=True,
    background_color='white',
    right_click_menu = ['&Right', ['Rotate', ['90 degrees', '180 degrees', '270 degrees'],
                                    'Colour', graph_colour_menu,
                                    'Delete']]
)]]

team_id = []
current_list = [0, 1, 2, 3, 4]
unused_blocks = [i for i in range (1, 61)]

sidebar = [[sg.Button(image_filename='images/block' + str(unused_blocks[current_list[0]]) + '.png', key='block0', image_subsample=2), 
            sg.Text('1', key='text0')],
          [sg.Button(image_filename='images/block' + str(unused_blocks[current_list[1]]) + '.png', key='block1', image_subsample=2), 
           sg.Text('2', key='text1')],
          [sg.Button(image_filename='images/block' + str(unused_blocks[current_list[2]]) + '.png', key='block2', image_subsample=2),
            sg.Text('3', key='text2')],
          [sg.Button(image_filename='images/block' + str(unused_blocks[current_list[3]]) + '.png', key='block3', image_subsample=2), 
           sg.Text('4', key='text3')],
          [sg.Button(image_filename='images/block' + str(unused_blocks[current_list[4]]) + '.png', key='block4', image_subsample=2), 
           sg.Text('5', key='text4')],
          [sg.Text('Block used: ')],
          [sg.Input(key='-IN-')],
          [sg.Button('Enter', bind_return_key=True, key='-CYCLE-')],
          [sg.Text('Team tile (press the button, don\'t enter)')],
          [sg.Input(key='-TEAM-')],
          [sg.Button('Enter team')]]

layout = [
    [sg.Column(graph_board), 
    sg.VerticalSeparator(),
    sg.Column(sidebar)]]
# Create the window
window = sg.Window("testing testing", layout, size=(1200, 650), icon=convert_to_bytes(Image.open('images/logo.png')))
window.Finalize()

graph = window["-GRAPH-"]  # type: sg.Graph
dragging = False
start_point = end_point = prior_rect = None
keys = {}

for i in range(ROWS):
    y_ = (int)(GRAPH_SIZE[1] / ROWS * i)
    graph.draw_line((0, y_), (GRAPH_SIZE[0], y_))

for i in range(COLUMNS):
    x_ = (int)(GRAPH_SIZE[0] / COLUMNS * i)
    graph.draw_line((x_, 0), (x_, GRAPH_SIZE[1]))

graph.draw_image('images/robbery.png', location=(360, 390))
graph.draw_image('images/robbery.png', location=(540, 210))
graph.draw_image('images/stone.png', location=(540, 390))
graph.draw_image('images/stone.png', location=(360, 210))
graph.draw_image('images/exchange.png', location=(450, 300))
graph.draw_image('images/exchange.png', location=(180, 510))
graph.draw_image('images/exchange.png', location=(180, 120))
graph.draw_image('images/exchange.png', location=(690, 510))
graph.draw_image('images/exchange.png', location=(690, 120))
graph.draw_image('images/robbery.png', location=(450, 510))
graph.draw_image('images/robbery.png', location=(450, 120))
graph.draw_image('images/pieces.png', location=(690, 300))
graph.draw_image('images/pieces.png', location=(180, 300))

# Create an event loop
while True:
    event, values = window.read()
    print(event)
    print(values)
    if event == sg.WIN_CLOSED:
        break
    elif 'block' in event:
        window.save_window_screenshot_to_disk('backup.png')
        index = current_list[int(event[-1])]
        id = graph.draw_image('images/block' + (str)(unused_blocks[index]) + '.png', location=(GRAPH_SIZE[0]/2, GRAPH_SIZE[1]/2))
        keys[id] = (str)(unused_blocks[index])
        graph.update()
    if event == '-GRAPH-':
        x, y = values["-GRAPH-"]
        if not dragging:
            start_point = (x, y)
            dragging = True
            drag_figures = graph.get_figures_at_location((x,y))
            lastxy = x, y
        else:
            end_point = (x, y)
        delta_x, delta_y = x - lastxy[0], y - lastxy[1]
        lastxy = x,y
        if None not in (start_point, end_point):
            for fig in drag_figures:
                if fig > 63:
                    graph.move_figure(fig, delta_x, delta_y)
                    graph.update()

    elif event.endswith('+UP'):  # The drawing has ended because mouse up
        start_point, end_point = None, None  # enable grabbing a new rect
        dragging = False
        prior_rect = None

    elif 'degrees' in event:
        window.save_window_screenshot_to_disk('backup.png')
        degree = (int)(event.split()[0])
        x, y = values["-GRAPH-"]
        figures = graph.get_figures_at_location((x,y))
        for i in figures:
            if i > 63 and i not in team_id:
                name = keys[i]
                image = Image.open('images/block' + name + '.png')
                rotated_image = image.rotate(degree, expand=True)
                rotated_image.save('images/block' + name + '.png')
                image_bytes = convert_to_bytes(rotated_image)
                id = graph.draw_image(data=image_bytes, location=(x, y))
                keys[id] = name

                graph.delete_figure(i)

    elif event == 'Delete':
        window.save_window_screenshot_to_disk('backup.png')
        x, y = values["-GRAPH-"]
        figures = graph.get_figures_at_location((x,y))
        for i in figures:
            if i > 63:
                graph.delete_figure(i)

    elif 'Round' in event:
        window.save_window_screenshot_to_disk('backup.png')
        team, round = (int)(event.split(',')[1]), (int)(event.split(',')[2])
        red_used, green_used, blue_used = colours_used(team)
        increment = 20
        x, y = values["-GRAPH-"]
        figures = graph.get_figures_at_location((x,y))
        for i in figures:
            if i > 63 and i not in team_id:
                name = keys[i]
                image = Image.open('images/block' + name + '.png')
                image = image.convert('RGBA')
                d = image.getdata()
 
                new_image = []
                for item in d:
                    if item != (0, 0, 0, 0):
                        new_image.append(((40 + increment * round) * red_used, (40 + increment * round) * green_used, (40 + increment * round) * blue_used))
                    else:
                        new_image.append(item)
                
                image.putdata(new_image)
                image.save('images/block' + name + '.png')
                image_bytes = convert_to_bytes(image)
                id = graph.draw_image(data=image_bytes, location=(x, y))
                keys[id] = name

                graph.delete_figure(i)
    elif event == '-CYCLE-':
        window.save_window_screenshot_to_disk('backup.png')
        input = values['-IN-']
        if not input.isdigit():
            sg.popup('Please enter a natural number!')
        else:
            input = (int)(input)
            if input not in unused_blocks:
                sg.popup('Entry does not exist in list!')
            else:
                current_list[0] = unused_blocks.index(input) % (len(unused_blocks) - 1)
                index = unused_blocks.remove(input)

                for i in range (1, 5):
                    current_list[i] = (current_list[i - 1] + 1) % len(unused_blocks)
                for i in range(5):
                    print(current_list)
                    window['block' + str(i)].update(image_filename='images/block' + str(unused_blocks[current_list[i]]) + '.png', image_subsample=2)
                    window['text' + str(i)].update(value=str(unused_blocks[current_list[i] % len(unused_blocks)]))
                    window['-IN-'].update(value='')
    elif event == 'Enter team':
        window.save_window_screenshot_to_disk('backup.png')
        input = values['-TEAM-']
        if not input.isdigit():
            sg.popup('Please enter a natural number!')
        else:
            input = (int)(input)
            if input not in range (1, 7):
                sg.popup('Please enter a team from 1-6!')
            else:
                id = graph.draw_image('images/team' + (str)(input) + '.png', location=(GRAPH_SIZE[0]/2, GRAPH_SIZE[1]/2))
                team_id.append(id)
                window['-TEAM-'].update(value='')
                graph.update()
    
window.close()