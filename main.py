#!/usr/bin/python
from PIL import Image
import os.path
import streamlit as st
from colors import color
from tama import tamagotchi
st.set_page_config(page_title="TamaPara Generator")


chosenTama = st.selectbox("Tamagotchi", tamagotchi)
image = Image.open("character/" + chosenTama + ".png")
pixels = image.load()

colorPrompt = st.selectbox("Color", color)

eyeType = st.selectbox("Eyes", tamagotchi)
eyeImage = Image.open("eyes/" + eyeType + ".png")


baseColor = tamagotchi[chosenTama]["baseColor"]
eyePosition = tamagotchi[chosenTama]["eyePosition"]
adjustments = tamagotchi[eyeType]["adjustments"]


if (baseColor != colorPrompt):
    for i in range(image.size[0]):
        for j in range(image.size[1]):
            for x in range(6):
                # if pixel contains rgb value in the tamagotchi's base color palette, change it to the same indexed one in the desired palette
                if pixels[i,j] == color[baseColor][x]:
                    pixels[i,j] = color[colorPrompt][x]


# The eyes that have blush effects or eyebrows look weird
eyePosition = (eyePosition[0],eyePosition[1]+adjustments)


# This is probably easier for now
if os.path.exists("mask/" + chosenTama + ".png"):
    # Making a mask using a new background and a crop of the mask
    mask = Image.open("mask/" + chosenTama + ".png")
    eyePositionBox = [eyePosition[0], eyePosition[1], eyePosition[0]+40, eyePosition[1]+19]
    eyeImage = Image.composite(Image.new("RGBA", (40,19)), eyeImage, mask.crop(eyePositionBox))
    
image.paste(eyeImage, eyePosition, eyeImage)
st.image(image,"",160)