Tamagotchi Paradise Genes Generator
===================================

This app allows you to pick the body, eyes, and color of Tamagotchi Paradise
characters to preview how they would look like.

Usage
-----
Select the character for body and eyes, then a color. The preview will update
when you update any selection. Under each selection is a randomize button that
will randomize the selection above it. You can also click on the randomize all
button to randomize all three selections. There is also a preview button that
display all the items in the selection with the selected features without
needing to randomize or go through all of them.

A running history of your generated characters is available in the history
section.

You can customize the set of characters that appear in the lists. **Include
non-breedable eyes** will include eyes of non-adult characters in the eyes list.
**Include Jade Forest-exclusive characters** will include characters only
available on Jade Forest in the lists. **Include Lab Tama eyes** will
include the eyes of the characters that you can breed with on Lab Tamas.
**Include Lab Tama bodies** will include the bodies of the Lab Tama
characters. You may have to remake your selections after changing the settings.

Running locally
---------------
Set up venv/requirements as you'd usually do, then run

```sh
streamlit run main.py
```

Data source
-----------
This app is driven by a `data.json` file, which contains definitions for
characters and palettes.

### Characters
The `Characters` property is a list of character definitions, with the following
properties:

- `Name`: name of character
- `Id`: ID of character as found in game data. Lab Tama characters do not have a
  real ID, so they start at `60100` and is sequential based on order specified
  to the data generator.
- `Stage`: character's stage; `5` is adult, any under that is not breedable
- `IsJade`: is character Jade Forest-exclusive
- `IsExternal`: is character from Lab Tama
- `EyePos`: an array of two elements, X and Y position of eye sprite relative to
  top left of body sprite. All eye sprites should have the same dimensions.
- `MouthPos`: an array of two elements, X and Y position of mouth sprite
  relative to top left of body sprite. All mouth sprites should have the same
  dimensions.

Sprites are stored in the `images` folder, with a pattern of `{Id}_{type}.png`.
Types are `body`, `eyes`, and `mouth`. The sprites must be in palette-indexed
format.

### Palettes
The `Palettes` property is a list of palette definitions, with the following
properties:

- `Name`: name of color
- `Colors`: array of R/G/B/A values, flattened in the way you would find from
  returned by Pillow's `Image.getpalette()`. There should be 8 * 4 elements.
  These values replace the body and mouth sprite palettes from the start if this
  array is not empty. The number of elements is not enforced, but you may
  experience weirdness if you do not have the recommended number of elements.

Note the `Original` color: because there are no `Colors` specified, the sprites'
palettes will not be replaced.
