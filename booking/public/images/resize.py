import PIL
from PIL import Image

image=Image.open("Deep Tissue Massage_resized.png")
new_image=image.resize((299,700))
new_image.save("Deep Tissue Massage_resized.png")