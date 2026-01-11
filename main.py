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
    with col_eyes_select:
        with st.container():
            eyes_select_slot = st.empty()
            eyes_select_button_slot = st.empty()

    with st.container():
            color_select_slot = st.empty()
            color_select_button_slot = st.empty()

randomize_all_slot = st.empty()

with st.container(border=True, horizontal=True):
    opt_include_non_breedable = st.checkbox('Include non-breedable eyes')
    opt_include_jade_charas = st.checkbox('Include Jade Forest-exclusive characters', True)
    opt_include_external_charas = st.checkbox('Include Lab Tama characters', True)

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
    
    if not opt_include_external_charas:
        if chara['IsExternal']:
            return False
        
    return True

def eyes_filter(chara):
    if not opt_include_non_breedable:
        if chara['Stage'] < 5:
            return False
    
    return True

charas_list = list(filter(chara_filter, data['Characters']))
eyes_list = list(filter(eyes_filter, charas_list))

# Render buttons and selectboxes

if body_select_button_slot.button('🎲', 'random_body', use_container_width=True):
    st.session_state['body'] = random.choice(charas_list)

if eyes_select_button_slot.button('🎲', 'random_eyes', use_container_width=True):
    st.session_state['eyes'] = random.choice(eyes_list)

if color_select_button_slot.button('🎲', 'random_color', use_container_width=True):
    st.session_state['color'] = random.choice(data['Palettes'])

if randomize_all_slot.button('🎲 All', 'random_all', use_container_width=True):
    st.session_state['body'] = random.choice(charas_list)
    st.session_state['eyes'] = random.choice(eyes_list)
    st.session_state['color'] = random.choice(data['Palettes'])

def selectbox_formatter(data):
    if data:
        return data['Name']
    else:
        return ''

selected_body = body_select_slot.selectbox('Body', charas_list, key='body', format_func=selectbox_formatter)
selected_eyes = eyes_select_slot.selectbox('Eyes', eyes_list, key='eyes', format_func=selectbox_formatter)
selected_color = color_select_slot.selectbox('Color', data['Palettes'], key='color', format_func=selectbox_formatter)

# Generate image
with Image.open(os.path.join('images', f'{selected_body['Id']}_body.png')) as body_image, \
    Image.open(os.path.join('images', f'{selected_eyes['Id']}_eyes.png')) as eyes_image, \
    Image.open(os.path.join('images', f'{selected_body['Id']}_mouth.png')) as mouth_image:

    # Try to figure out drawing offsets and dimension of image, since some parts may
    # have negative offsets
    draw_offset = [0, 0]
    for prop in ('EyePos', 'MouthPos'):
        for i in range(2):
            if selected_body[prop][i] < draw_offset[i]:
                draw_offset[i] = selected_body[prop][i]

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

    if selected_color['Colors']:
        replace_palette(body_image, selected_color['Colors'])
        replace_palette(mouth_image, selected_color['Colors'])

    composite_image = Image.new('RGBA', image_dimension, '#fff0')
    composite_image.paste(body_image, (draw_offset[0], draw_offset[1]), body_image.convert('RGBA'))
    composite_image.paste(eyes_image, (draw_offset[0] + selected_body['EyePos'][0], draw_offset[1] + selected_body['EyePos'][1]), eyes_image.convert('RGBA'))
    composite_image.paste(mouth_image, (draw_offset[0] + selected_body['MouthPos'][0], draw_offset[1] + selected_body['MouthPos'][1]), mouth_image.convert('RGBA'))

# Add to history
key = f'{selected_body['Id']}_{selected_eyes['Id']}_{selected_color['Name']}'
if key not in st.session_state['history']:
    # I originally wanted images to click to restore selections, but apparently
    # clickable images is not a thing
    st.session_state['history'][key] = {
        'selected_body': selected_body,
        'selected_eyes': selected_eyes,
        'selected_color': selected_color,
        'image': composite_image
    }

# Render image
out_image_slot_big.image(composite_image, width=160)
out_image_slot_small.image(composite_image)

# Render history
with history_container:
    history_list = list(st.session_state['history'].items())
    history_list.reverse()
    for k, v in history_list:
        st.image(v['image'], f'{v['selected_body']['Name']} x {v['selected_eyes']['Name']}, {v['selected_color']['Name']}', 96)
