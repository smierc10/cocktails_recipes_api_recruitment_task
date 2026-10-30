import uuid

from PIL import Image, ImageOps
from django.core.exceptions import ValidationError
import io

from django.core.files.uploadedfile import InMemoryUploadedFile

MAX_IMAGE_SIZE = 1024 * 1024 * 20  # 20MiB

valid_file_types = ["JPEG", "webp", "PNG"]


def verify_and_convert_image(image):

    if image.size > MAX_IMAGE_SIZE:
        raise ValueError(
            f"File to large maximum file size is {MAX_IMAGE_SIZE / (1024 * 1024):.2} MiB, provided file's size is {image.size / (1024 * 1024):.2} MiB"
        )

    try:
        img = Image.open(image)
        img.verify()
    except Exception as e:
        raise ValidationError(f"Image failed PIL verification step: {e}")

    if img.format not in valid_file_types:
        raise ValueError(
            f"Image (of type {img.format}) is not on supported formats list: {', '.join(valid_file_types)}"
        )

    image.seek(0)
    img = Image.open(image)
    output = io.BytesIO()

    img = ImageOps.exif_transpose(img) or img

    img.save(output, format="WEBP", quality=80, speed=8)
    output.seek(0)
    output_size = output.getbuffer().nbytes

    new_filename = f"{uuid.uuid4()}.webp"

    return InMemoryUploadedFile(
        file=output,
        name=new_filename,
        content_type="image/webp",
        field_name="ImageField",
        size=output_size,
        charset=None,
    )
