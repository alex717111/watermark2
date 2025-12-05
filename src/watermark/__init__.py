"""Watermark module for video watermarking functionality."""

from .image_watermark import add_image_watermark
from .text_watermark_v2 import add_text_watermark

__all__ = ['add_image_watermark', 'add_text_watermark']
