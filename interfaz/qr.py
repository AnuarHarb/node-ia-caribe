"""Código QR en SVG para enlaces en la LAN (sin depender de internet)."""

from __future__ import annotations

import io

import qrcode
from qrcode.image.svg import SvgPathImage


def svg_de_enlace(url: str) -> bytes:
    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=8, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    imagen = qr.make_image(image_factory=SvgPathImage)
    buf = io.BytesIO()
    imagen.save(buf)
    return buf.getvalue()
