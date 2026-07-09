"""Generate tiny original image fixtures. No third-party media.

Writes a 4x4 TIFF and, if pillow-heif is available, a 4x4 HEIC. Both are trivially
small and generated here, so nothing copyrighted is committed. The files are
gitignored; they are recreated on each run.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def save_tiff():
    try:
        from PIL import Image
        Image.new("RGB", (4, 4), (120, 120, 120)).save(
            os.path.join(HERE, "sample.tiff"), format="TIFF")
        print("wrote sample.tiff")
    except Exception as exc:
        print("could not write TIFF (needs Pillow):", exc)


def save_heic():
    try:
        from PIL import Image
        import pillow_heif
        pillow_heif.register_heif_opener()
        Image.new("RGB", (4, 4), (120, 120, 120)).save(
            os.path.join(HERE, "sample.heic"), format="HEIF")
        print("wrote sample.heic")
    except Exception as exc:
        print("could not write HEIC (needs Pillow and pillow-heif):", exc)


if __name__ == "__main__":
    save_tiff()
    save_heic()
