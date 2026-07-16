"""
Utilidades para comprimir imágenes antes de guardarlas en el servidor.

Objetivo: que cada foto (principalmente facturas/tickets) pese ~300 KB o menos,
manteniendo suficiente resolución para que el texto sea legible.
"""
import io
from PIL import Image, ImageOps

# Lado máximo de la imagen en píxeles. 1600px es más que suficiente
# para leer una factura con claridad.
MAX_DIMENSION = 1600

# Calidad JPEG inicial (0-100)
INITIAL_QUALITY = 78

# Tamaño objetivo máximo en bytes (~300 KB)
TARGET_SIZE_BYTES = 300 * 1024

# Calidad mínima aceptable antes de rendirnos (evita imágenes ilegibles)
MIN_QUALITY = 40


def compress_image(contents: bytes) -> bytes:
    """
    Comprime una imagen:
      1. Corrige la orientación EXIF (fotos de tablet/celular).
      2. Redimensiona para que el lado más largo no supere MAX_DIMENSION.
      3. Re-codifica como JPEG, bajando la calidad progresivamente
         hasta quedar por debajo de TARGET_SIZE_BYTES (o llegar a MIN_QUALITY).

    Devuelve los bytes del JPEG comprimido.
    Lanza excepción si el contenido no es una imagen válida.
    """
    img = Image.open(io.BytesIO(contents))

    # Respetar la rotación que la cámara guardó en los metadatos EXIF
    img = ImageOps.exif_transpose(img)

    # JPEG no soporta transparencia ni paletas -> convertir a RGB
    if img.mode != "RGB":
        img = img.convert("RGB")

    # Redimensionar manteniendo proporción (solo reduce, nunca agranda)
    img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.LANCZOS)

    quality = INITIAL_QUALITY
    while True:
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality, optimize=True)
        if buffer.tell() <= TARGET_SIZE_BYTES or quality <= MIN_QUALITY:
            return buffer.getvalue()
        quality -= 8