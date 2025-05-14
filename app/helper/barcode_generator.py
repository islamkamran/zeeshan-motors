import os
import shutil
from fastapi import APIRouter, Form, File, UploadFile, Depends, Header, HTTPException
from sqlalchemy.orm import Session
import logging
from barcode import Code128
from barcode.writer import ImageWriter
from PIL import Image
import qrcode
from qrcode.constants import ERROR_CORRECT_H

UPLOAD_DIR = "uploads/barcodes/"

def generate_barcode_vehicle(data: str, vehicle_id: int) -> str:
    """THE FUNCTION NAME IS BARCODE BUT IT HAVE QRCODE AS THE PROJECT REQUIREMENT WAS CHANGED AT THE END AND I DONOT WANT TO MISS UP ALL THE CODE :) PARDONS IN ADVANCE ONLY 3 FUNCTIONS TOTAL FOR BARCODES WHICH ARE QRCODES NOW"""
    qrcode_filename = f"{vehicle_id}_vehicle_qrcode.png"
    qrcode_path = os.path.join(UPLOAD_DIR, qrcode_filename)

    # Create a QR code with high error correction and small size
    qr = qrcode.QRCode(
        version=2,  # Controls the size of the QR code (1 to 40, where 2 is small)
        error_correction=ERROR_CORRECT_H,  # High error correction
        box_size=10,  # Size of each box in the QR code grid
        border=4,  # Border size in boxes
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Generate the QR code image
    qr_image = qr.make_image(fill_color="black", back_color="white")
    qr_image = qr_image.convert("RGB")  # Ensure compatibility with saving formats

    # Save the QR code image to the specified path
    qr_image.save(qrcode_path)

    return qrcode_path
