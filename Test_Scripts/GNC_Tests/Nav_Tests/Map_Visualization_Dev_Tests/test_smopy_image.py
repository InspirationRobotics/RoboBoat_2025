import smopy

# smopy map class definition can be found here: https://github.com/rossant/smopy/blob/master/smopy.py

# SW, SE
map = smopy.Map((27.362951, -82.453479, 27.365954, -82.453677), z=19)

# map.show_ipython() - will only work when run on a Jupyter notebook.
image = map.to_pil()
image.save('test_smopy_map.png')