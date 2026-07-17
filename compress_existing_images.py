#!/usr/bin/env python3
"""
Comprime imágenes YA EXISTENTES (facturas de 3-6 MB) para reducir su peso a
~300 KB, CONSERVANDO EL NOMBRE DE ARCHIVO EXACTO (incluida la extensión),
porque esos nombres ya están guardados en la base de datos.

Características de seguridad:
  - NO modifica los originales: escribe los resultados en un directorio de salida
    separado. Así puedes verificar antes de reemplazar nada.
  - Si un archivo ya pesa menos que el objetivo, se copia tal cual (sin recomprimir,
    para no perder calidad innecesariamente).
  - Si al comprimir el resultado no es más pequeño, se conserva el original.
  - Modo --dry-run para ver el ahorro estimado sin escribir nada.

Uso:
    # Ver qué haría, sin escribir:
    python3 compress_existing_images.py ./uploads ./uploads_compressed --dry-run

    # Ejecutar de verdad:
    python3 compress_existing_images.py ./uploads ./uploads_compressed

Después de verificar visualmente que las imágenes en ./uploads_compressed se ven
bien, reemplazas la carpeta original (o la mueves al volumen). Nunca borres los
originales hasta haber confirmado.

NOTA sobre la extensión: para lograr la mayor compresión, TODAS las imágenes se
re-codifican como JPEG, pero se guardan con el nombre y extensión originales. Es
decir, un archivo 'abc_factura.png' quedará como bytes JPEG dentro de un archivo
llamado '.png'. Los navegadores y las etiquetas <img> lo muestran sin problema,
así que la app sigue funcionando y la base de datos no requiere ningún cambio.
"""
import io
import os
import shutil
import sys
import argparse
from PIL import Image, ImageOps

MAX_DIMENSION = 1600
INITIAL_QUALITY = 78
TARGET_SIZE_BYTES = 300 * 1024
MIN_QUALITY = 40

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff", ".tif"}


def compress_bytes(contents: bytes) -> bytes:
    """Devuelve una versión JPEG comprimida (~300 KB máx) de la imagen."""
    img = Image.open(io.BytesIO(contents))
    img = ImageOps.exif_transpose(img)  # corregir rotación de la cámara
    if img.mode != "RGB":
        img = img.convert("RGB")
    img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.LANCZOS)

    quality = INITIAL_QUALITY
    while True:
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality, optimize=True)
        if buffer.tell() <= TARGET_SIZE_BYTES or quality <= MIN_QUALITY:
            return buffer.getvalue()
        quality -= 8


def human(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def main():
    parser = argparse.ArgumentParser(description="Comprime imágenes existentes conservando el nombre.")
    parser.add_argument("input_dir", help="Carpeta con las imágenes originales (ej: ./uploads)")
    parser.add_argument("output_dir", help="Carpeta donde escribir las comprimidas (ej: ./uploads_compressed)")
    parser.add_argument("--dry-run", action="store_true", help="Solo calcular, no escribir archivos")
    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        print(f"ERROR: no existe la carpeta de entrada: {args.input_dir}")
        sys.exit(1)

    if not args.dry_run:
        os.makedirs(args.output_dir, exist_ok=True)

    total_before = 0
    total_after = 0
    n_compressed = 0
    n_copied = 0
    n_skipped = 0
    errors = []

    for name in sorted(os.listdir(args.input_dir)):
        src = os.path.join(args.input_dir, name)
        if not os.path.isfile(src):
            continue

        ext = os.path.splitext(name)[1].lower()
        if ext not in IMAGE_EXTENSIONS:
            n_skipped += 1
            continue

        original_size = os.path.getsize(src)
        total_before += original_size
        dst = os.path.join(args.output_dir, name)  # MISMO nombre exacto

        # Si ya es pequeña, copiar sin recomprimir (no perder calidad)
        if original_size <= TARGET_SIZE_BYTES:
            total_after += original_size
            n_copied += 1
            if not args.dry_run:
                shutil.copy2(src, dst)
            continue

        try:
            with open(src, "rb") as f:
                data = f.read()
            compressed = compress_bytes(data)
        except Exception as e:
            errors.append(f"{name}: {e}")
            total_after += original_size
            if not args.dry_run:
                shutil.copy2(src, dst)  # fallback: conservar original
            continue

        # Si comprimir no ayudó, conservar el original
        if len(compressed) >= original_size:
            total_after += original_size
            n_copied += 1
            if not args.dry_run:
                shutil.copy2(src, dst)
        else:
            total_after += len(compressed)
            n_compressed += 1
            if not args.dry_run:
                with open(dst, "wb") as f:
                    f.write(compressed)

    print("=" * 60)
    print("DRY RUN (no se escribió nada)" if args.dry_run else "COMPLETADO")
    print("=" * 60)
    print(f"Imágenes comprimidas : {n_compressed}")
    print(f"Copiadas sin cambio  : {n_copied} (ya eran pequeñas o no se pudieron reducir)")
    print(f"Archivos no-imagen   : {n_skipped} (ignorados)")
    print(f"Peso ANTES           : {human(total_before)}")
    print(f"Peso DESPUÉS         : {human(total_after)}")
    if total_before:
        ahorro = 100 * (1 - total_after / total_before)
        print(f"Ahorro               : {ahorro:.1f} %")
    if errors:
        print(f"\n⚠️  {len(errors)} archivo(s) con error (se conservó el original):")
        for e in errors[:10]:
            print(f"   - {e}")


if __name__ == "__main__":
    main()