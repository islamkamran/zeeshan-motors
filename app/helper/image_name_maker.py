import os
import shutil

def format_image_name_int(vehicle_id: int, filename: str) -> str:
    """Ensure the image name is formatted correctly."""
    base_name, ext = os.path.splitext(filename)
    if not base_name.startswith(str(vehicle_id)):
        return f"{vehicle_id}_int_{base_name}{ext}"
    return filename

def format_image_name_ext(vehicle_id: int, filename: str) -> str:
    """Ensure the image name is formatted correctly."""
    base_name, ext = os.path.splitext(filename)
    if not base_name.startswith(str(vehicle_id)):
        return f"{vehicle_id}_ext_{base_name}{ext}"
    return filename