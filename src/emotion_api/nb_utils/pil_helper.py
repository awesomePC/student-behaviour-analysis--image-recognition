import os
from .error_handling import trace_error
from .basic_file_folder_creation import generate_filename


def save_image(img, filename=None, base_folder=None, type="jpeg", mode="RGB"):
    """
    save pillow image object to disk

    Args:
        img (numpy): pillow image object
        filename (str, optional): Filename with path. Defaults to None. If not provided it will auto generate.
        base_folder (str, optional): Root folder path. Defaults to "None".
        type (str, optional): Output Image type. Defaults to "jpeg".
        mode (str, optional): Image writing mode. Defaults to "RGB".
    Returns:
        str: Filename
    """
    if not filename:
        if type.lower() in ["png"]:
            filename = generate_filename(extension=".png")
        else:
            filename = generate_filename(extension=".jpeg")
    
    if not base_folder:
        from tempfile import gettempdir
        base_folder = gettempdir()

    try:
        filename = os.path.join(base_folder, filename)
        img.save(filename)
        return filename
    except:
        error = trace_error()
        print(error)
        return False

def save_array(image_array, filename=None, base_folder=None, type="jpeg", mode="RGB"):
    """
    save numpy image array as image file

    Args:
        image_array (numpy): Numpy array
        filename (str, optional): Filename with path. Defaults to None. If not provided it will auto generate.
        base_folder (str, optional): Root folder path. Defaults to "None".
        type (str, optional): Output Image type. Defaults to "jpeg".
        mode (str, optional): Image writing mode. Defaults to "RGB".
    Returns:
        str: Filename
    """
    from PIL import Image
    img = Image.fromarray(image_array)
    
    return save_image(
	img, 
	filename=filename, 
	base_folder=base_folder, 
	type=type, 
	mode=mode
    )
