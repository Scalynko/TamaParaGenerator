#!/usr/bin/python
from PIL import Image
import os.path
import streamlit as st
import random
from colors import color
from tama import tamagotchi, jadeExclusive, nonBreedableEyes
st.set_page_config(page_title="TamaPara Generator")

tamagotchiList = eyeList = list(tamagotchi)
colorList = list(color)
eyeList = list(filter(lambda x: x not in nonBreedableEyes, eyeList))


#Checkboxes
colcheck1, colcheck2 = st.columns(2)
with colcheck1:
    nonBreedableCheck = st.checkbox("Add Non-Breedable Eyes") 
if nonBreedableCheck:
    eyeList = sorted(eyeList + nonBreedableEyes)
    
with colcheck2:
    jadeCheck = st.checkbox("Remove Jade Forest Exclusives")
if jadeCheck:
    tamagotchiList = list(filter(lambda x: x not in jadeExclusive, tamagotchiList))
    eyeList = list(filter(lambda x: x not in jadeExclusive, eyeList))
    
#Randomizers
with st.container(horizontal=True):
    if st.button("🎲 All"):
        st.session_state["Tamagotchi"] = random.choice(tamagotchiList)
        st.session_state["Color"] = random.choice(colorList)
        st.session_state["Eyes"] = random.choice(eyeList)
    if st.button("🎲 Tama"):
        st.session_state["Tamagotchi"] = random.choice(tamagotchiList)
    if st.button("🎲 Color"):
        st.session_state["Color"] = random.choice(colorList)
    if st.button("🎲 Eyes"):
        st.session_state["Eyes"] = random.choice(eyeList)


chosenTama = st.selectbox("Tamagotchi", tamagotchiList,key="Tamagotchi")
image = Image.open("character/" + chosenTama + ".png")
pixels = image.load()

colorPrompt = st.selectbox("Color", colorList,key="Color")

eyeType = st.selectbox("Eyes", eyeList,key="Eyes")
eyeImage = Image.open("eyes/" + eyeType + ".png")

baseColor = tamagotchi[chosenTama]["baseColor"]
eyePosition = tamagotchi[chosenTama]["eyePosition"]
adjustments = tamagotchi[eyeType]["adjustments"]

whiteCount = [0,0,0,0,0,0]
maxwhite = maxwhiteindex = 0

                    
if (baseColor != colorPrompt):
    for i in range(image.size[0]):
        for j in range(image.size[1]):
            for x in range(6):
            # if pixel contains rgb value in the tamagotchi's base color palette, change it to the same indexed one in the desired palette
                if pixels[i,j] == color[baseColor][x]:
                    pixels[i,j] = color[colorPrompt][x]
                    whiteCount[x] += 1
                    maxwhite = max(whiteCount)
                    maxwhiteindex = whiteCount.index(maxwhite)

# This is the ugliest way to fix it, I need to learn more about palettes lol

    if (colorPrompt == "white"):
        for i in range(image.size[0]):
                for j in range(image.size[1]):
                    if pixels[i,j] == color[colorPrompt][maxwhiteindex]:
                         pixels[i,j] = color[colorPrompt][1]
                    elif pixels[i,j] == color[colorPrompt][maxwhiteindex+1]:
                         pixels[i,j] = color[colorPrompt][2]


# The eyes that have blush effects or eyebrows look weird
eyePosition = (eyePosition[0],eyePosition[1]+adjustments)


# This is probably easier for now
if os.path.exists("mask/" + chosenTama + ".png"):
    # Making a mask using a new background and a crop of the mask
    mask = Image.open("mask/" + chosenTama + ".png")
    eyePositionBox = [eyePosition[0], eyePosition[1], eyePosition[0]+40, eyePosition[1]+20]
    eyeImage = Image.composite(Image.new("RGBA", (40,20)), eyeImage, mask.crop(eyePositionBox))
    
image.paste(eyeImage, eyePosition, eyeImage)

st.image(image,"",160)
st.image(image)
#Initializing so I don't get an error (this image is not shown anyway)
if "previmages" not in st.session_state:
    st.session_state["previmages"] = [image]
st.session_state["previmages"].append(image)
st.header("Previous Inputs",divider=True)
if st.button("Clear"):
    st.session_state["previmages"] = st.session_state["previmages"][:1]
# Reverse it so it's new first
for picture in reversed(st.session_state["previmages"][1:]):

    st.image(picture)
