from collections import OrderedDict
import json
import os.path
from PIL import Image
import random
import streamlit as st

with open('data.json') as f:
    data = json.load(f)

st.set_page_config(page_title="Tamagotchi Paradise Genes Generator")

# Layout

st.title('Tamagotchi Paradise Genes Generator')

st.header('Generate')

with st.container(border=True):
    col_body_select, col_eyes_select = st.columns(2)
    with col_body_select:
        with st.container():
            body_select_slot = st.empty()
            body_select_button_slot = st.empty()
            body_select_preview_slot = st.empty()
    with col_eyes_select:
        with st.container():
            eyes_select_slot = st.empty()
            eyes_select_button_slot = st.empty()
            eyes_select_preview_slot = st.empty()

    with st.container():
            color_select_slot = st.empty()
            color_select_button_slot = st.empty()
            color_select_preview_slot = st.empty()

randomize_all_slot = st.empty()

with st.container(border=True, horizontal=True):
    opt_include_non_breedable = st.checkbox('Include non-breedable eyes')
    opt_include_jade_charas = st.checkbox('Include Jade Forest-exclusive characters', True)
    opt_include_wave3_charas = st.checkbox('Include Orange Tropics and White Glacier characters', True)
    opt_include_external_eyes = st.checkbox('Include Lab Tama eyes', True)
    opt_include_external_bodies = st.checkbox('Include Lab Tama bodies')

with st.container(border=True):
    col_image_big, col_image_small = st.columns(2, vertical_alignment='center')
    with col_image_big:
        with st.container(horizontal_alignment='center'):
            out_image_slot_big = st.empty()
    with col_image_small:
        with st.container(horizontal_alignment='center'):
            out_image_slot_small = st.empty()

st.header('History')

history_container = st.container(horizontal=True)


# Logic

if 'history' not in st.session_state:
    st.session_state['history'] = OrderedDict()

# Filter characters

def chara_filter(chara):
    if not opt_include_jade_charas:
        if chara['IsJade']:
            return False

    if not opt_include_wave3_charas:
        if chara['IsWave3']:
            return False

    return True

def body_filter(chara):
    if not opt_include_external_bodies:
        if chara['IsExternal']:
            return False

    return True

def eyes_filter(chara):
    if not opt_include_non_breedable:
        if chara['Stage'] < 5 or chara['Name'] == 'BBMARUTCHI':
            return False

    if not opt_include_external_eyes:
        if chara['IsExternal']:
            return False
    return True

charas_list = list(filter(chara_filter, data['Characters']))
bodies_list = list(filter(body_filter, charas_list))
eyes_list = list(filter(eyes_filter, charas_list))

# Render buttons and selectboxes

if body_select_button_slot.button('🎲', 'random_body', use_container_width=True):
    st.session_state['body'] = random.choice(bodies_list)

if eyes_select_button_slot.button('🎲', 'random_eyes', use_container_width=True):
    st.session_state['eyes'] = random.choice(eyes_list)

if color_select_button_slot.button('🎲', 'random_color', use_container_width=True):
    st.session_state['color'] = random.choice(data['Palettes'])

if randomize_all_slot.button('🎲 All', 'random_all', use_container_width=True):
    st.session_state['body'] = random.choice(bodies_list)
    st.session_state['eyes'] = random.choice(eyes_list)
    st.session_state['color'] = random.choice(data['Palettes'])

def selectbox_formatter(data):
    if data:
        return data['Name']
    else:
        return ''

selected_body = body_select_slot.selectbox('Body', bodies_list, key='body', format_func=selectbox_formatter)
selected_eyes = eyes_select_slot.selectbox('Eyes', eyes_list, key='eyes', format_func=selectbox_formatter)
selected_color = color_select_slot.selectbox('Color', data['Palettes'], key='color', format_func=selectbox_formatter)
key = f'{selected_body['Id']}_{selected_eyes['Id']}_{selected_color['Name']}'

# Generate image
def generate_image(body, eyes, color):
    with Image.open(os.path.join('images', f'{body['Id']}_body.png')) as body_image, \
        Image.open(os.path.join('images', f'{eyes['Id']}_eyes.png')) as eyes_image, \
        Image.open(os.path.join('images', f'{body['Id']}_mouth.png')) as mouth_image:

        # Try to figure out drawing offsets and dimension of image, since some parts may
        # have negative offsets
        draw_offset = [0, 0]
        for prop in ('EyePos', 'MouthPos'):
            for i in range(2):
                if body[prop][i] < draw_offset[i]:
                    draw_offset[i] = body[prop][i]

        # Now this is how much to offset sprites so the leftmost starts at the left
        # and topmost starts at the top
        draw_offset = [-draw_offset[0], -draw_offset[1]]

        image_dimension = [0, 0]
        for image in (body_image, eyes_image, mouth_image):
            part_max_x = image.width + draw_offset[0]
            part_max_y = image.height + draw_offset[1]

            if part_max_x > image_dimension[0]:
                image_dimension[0] = part_max_x
            if part_max_y > image_dimension[1]:
                image_dimension[1] = part_max_y

        def replace_palette(image, new_palette):
            curr_palette = image.getpalette('RGBA')
            curr_palette[:len(new_palette)] = new_palette
            image.putpalette(curr_palette, 'RGBA')

        if color['Colors']:
            replace_palette(body_image, color['Colors'])
            replace_palette(mouth_image, color['Colors'])

        composite_image = Image.new('RGBA', image_dimension, '#fff0')
        composite_image.paste(body_image, (draw_offset[0], draw_offset[1]), body_image.convert('RGBA'))
        composite_image.paste(eyes_image, (draw_offset[0] + body['EyePos'][0], draw_offset[1] + body['EyePos'][1]), eyes_image.convert('RGBA'))
        composite_image.paste(mouth_image, (draw_offset[0] + body['MouthPos'][0], draw_offset[1] + body['MouthPos'][1]), mouth_image.convert('RGBA'))
    return(composite_image)

# Preview Tamagotchis with different features
@st.dialog("Preview", width="large")
def preview(list):
    with st.container(horizontal=True, horizontal_alignment="center"):
        if list == "body":
            for i in bodies_list:
                st.image(generate_image(i, selected_eyes, selected_color), f'{i['Name']} x {selected_eyes['Name']}, {selected_color['Name']}', 80)
        elif list == "eyes":
            for i in eyes_list:
                st.image(generate_image(selected_body, i, selected_color), f'{selected_body['Name']} x {i['Name']}, {selected_color['Name']}', 80)
        elif list == "color":
            for i in data['Palettes']:
                st.image(generate_image(selected_body, selected_eyes, i), f'{selected_body['Name']} x {selected_eyes['Name']}, {i['Name']}', 80)


if key in st.session_state['history']:
    composite_image = st.session_state['history'][key]['image']
else:
    composite_image = generate_image(selected_body, selected_eyes, selected_color)
    # Add to history
    # I originally wanted images to click to restore selections, but apparently
    # clickable images is not a thing
    st.session_state['history'][key] = {
        'selected_body': selected_body['Name'],
        'selected_eyes': selected_eyes['Name'],
        'selected_color': selected_color['Name'],
        'image': composite_image
    }
# Render Preview buttons
if body_select_preview_slot.button('🔎', 'preview_bodytype', use_container_width=True):
    preview("body")
if eyes_select_preview_slot.button('🔎', 'preview_eyetype', use_container_width=True):
    preview("eyes")
if color_select_preview_slot.button('🔎', 'preview_colortype', use_container_width=True):
    preview("color")

# Render image
out_image_slot_big.image(composite_image, width=160)
out_image_slot_small.image(composite_image)

# Render history
with history_container:
    history_list = list(st.session_state['history'].items())
    history_list.reverse()
    for k, v in history_list:
        st.image(v['image'], f'{v['selected_body']} x {v['selected_eyes']}, {v['selected_color']}', 96)
