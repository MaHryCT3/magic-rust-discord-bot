from image_generator.application import start_generation

# import base64
# from io import BytesIO
# from image_generator.image_generator import get_server_status_image
# from PIL import Image

start_generation()
# image = get_server_status_image()
# with BytesIO() as image_binary:
#         image.save(image_binary, 'PNG')
#         image_binary.seek(0)
#         received_image_binary = image_binary.read()
# print(received_image_binary)
# fp = BytesIO(received_image_binary)
# with Image.open(fp, formats=['PNG']) as opened_image:
#       opened_image.show()

# #image.show()
