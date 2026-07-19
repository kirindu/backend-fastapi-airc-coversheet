#!/usr/bin/env python3
"""
Comprime imágenes YA EXISTENTES (facturas de 3-6 MB) a ~300 KB, CONSERVANDO EL
NOMBRE DE ARCHIVO EXACTO (incluida la extensión), porque esos nombres ya están
guardados en la base de datos.

Pensado para correr sobre miles de imágenes en el shell de Render:

  - --dry-run es INSTANTÁNEO: solo cuenta archivos y estima el ahorro,
    sin comprimir nada. Úsalo primero para saber cuántas imágenes hay.

  - El modo real muestra PROGRESO EN VIVO (cada 25 archivos) para que veas
    que está avanzando.

  - Es REANUDABLE: si el shell se desconecta y el proceso muere, vuelve a
    ejecutarlo con el mismo comando y continúa donde quedó (salta los
    archivos que ya existen en la carpeta de salida).

  - NO modifica los originales: escribe en una carpeta de salida separada.

Uso:
    # 1) Inventario rápido (no comprime):
    python3 compress_existing_images.py ./uploads ./uploads/_compressed --dry-run

    # 2) Comprimir de verdad (reanudable, con progreso):
    python3 compress_existing_images.py ./uploads ./uploads/_compressed

IMPORTANTE - correr sin que se muera al desconectarse el shell:
    Ejecútalo en segundo plano y guarda el log, así puedes cerrar la pestaña:

        nohup python3 compress_existing_images.py ./uploads ./uploads/_compressed \\
            > compress.log 2>&1 &

    Y para ver el progreso cuando quieras:

        tail -f compress.log

NOTA sobre la extensión: para máxima compresión todas las imágenes se
re-codifican como JPEG pero se guardan con su nombre y extensión originales
(un 'foto.png' quedará con bytes JPEG dentro de un archivo '.png'). Los
navegadores y las etiquetas <img> lo muestran sin problema, y la base de datos
no requiere ningún cambio.
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
PROGRESS_EVERY = 25  # imprimir progreso cada N archivos

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff", ".tif"}


def compress_bytes(contents: bytes) -> bytes:
    img = Image.open(io.BytesIO(contents))
    img = ImageOps.exif_transpose(img)
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


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def log(msg: str):
    print(msg, flush=True)  # flush para que el shell de Render lo muestre en vivo


def list_images(input_dir: str):
    """Lista solo archivos de imagen en input_dir, ignorando subcarpetas."""
    result = []
    for name in sorted(os.listdir(input_dir)):
        full = os.path.join(input_dir, name)
        if not os.path.isfile(full):
            continue  # ignora subcarpetas (incluida la de salida)
        if os.path.splitext(name)[1].lower() in IMAGE_EXTENSIONS:
            result.append(name)
    return result


def main():
    parser = argparse.ArgumentParser(description="Comprime imágenes existentes conservando el nombre.")
    parser.add_argument("input_dir")
    parser.add_argument("output_dir")
    parser.add_argument("--dry-run", action="store_true",
                        help="Inventario rápido: cuenta y estima sin comprimir")
    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        log(f"ERROR: no existe la carpeta: {args.input_dir}")
        sys.exit(1)

    images = list_images(args.input_dir)
    total = len(images)

    # ---------- DRY RUN: instantáneo, sin comprimir ----------
    if args.dry_run:
        total_size = 0
        big_size = 0
        n_big = 0
        for name in images:
            size = os.path.getsize(os.path.join(args.input_dir, name))
            total_size += size
            if size > TARGET_SIZE_BYTES:
                n_big += 1
                big_size += size
        n_small = total - n_big
        small_size = total_size - big_size
        # Estimación: las grandes rondarán ~200 KB; las pequeñas se copian igual
        est_after = small_size + n_big * 200 * 1024
        log("=" * 60)
        log("INVENTARIO (dry-run, no se comprimió nada)")
        log("=" * 60)
        log(f"Imágenes encontradas       : {total}")
        log(f"  - grandes (a comprimir)  : {n_big}")
        log(f"  - ya pequeñas (se copian): {n_small}")
        log(f"Peso total actual          : {human(total_size)}")
        log(f"Peso estimado despues      : ~{human(est_after)}")
        if total_size:
            log(f"Ahorro estimado            : ~{100*(1-est_after/total_size):.0f} %")
        log("")
        log("Para ejecutar de verdad (reanudable), corre el mismo comando SIN --dry-run.")
        return

    # ---------- EJECUCIÓN REAL: con progreso y reanudable ----------
    os.makedirs(args.output_dir, exist_ok=True)
    log(f"Procesando {total} imagenes...  (reanudable: salta las ya hechas)")

    total_before = total_after = 0
    n_compressed = n_copied = n_resumed = 0
    errors = []

    for i, name in enumerate(images, start=1):
        src = os.path.join(args.input_dir, name)
        dst = os.path.join(args.output_dir, name)  # MISMO nombre exacto
        original_size = os.path.getsize(src)
        total_before += original_size

        if os.path.exists(dst):
            total_after += os.path.getsize(dst)
            n_resumed += 1
        elif original_size <= TARGET_SIZE_BYTES:
            shutil.copy2(src, dst)
            total_after += original_size
            n_copied += 1
        else:
            try:
                with open(src, "rb") as f:
                    data = f.read()
                compressed = compress_bytes(data)
                if len(compressed) >= original_size:
                    shutil.copy2(src, dst)
                    total_after += original_size
                    n_copied += 1
                else:
                    with open(dst, "wb") as f:
                        f.write(compressed)
                    total_after += len(compressed)
                    n_compressed += 1
            except Exception as e:
                errors.append(f"{name}: {e}")
                shutil.copy2(src, dst)
                total_after += original_size

        if i % PROGRESS_EVERY == 0 or i == total:
            pct = 100 * i / total if total else 100
            log(f"  [{i}/{total}] {pct:.0f}%  |  acumulado: "
                f"{human(total_before)} -> {human(total_after)}")

    log("=" * 60)
    log("COMPLETADO")
    log("=" * 60)
    log(f"Comprimidas          : {n_compressed}")
    log(f"Copiadas sin cambio  : {n_copied}")
    log(f"Ya estaban hechas    : {n_resumed} (reanudadas de una corrida anterior)")
    log(f"Peso ANTES           : {human(total_before)}")
    log(f"Peso DESPUES         : {human(total_after)}")
    if total_before:
        log(f"Ahorro               : {100*(1-total_after/total_before):.1f} %")
    if errors:
        log(f"\n{len(errors)} archivo(s) con error (se conservo el original):")
        for e in errors[:10]:
            log(f"   - {e}")


if __name__ == "__main__":
    main()