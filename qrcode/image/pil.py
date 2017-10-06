# Needed on case-insensitive filesystems
from __future__ import absolute_import

# Try to import PIL in either of the two ways it can be installed.
try:
    from PIL import Image, ImageDraw
except ImportError:  # pragma: no cover
    import Image
    import ImageDraw

import qrcode.image.base
from qrcode.image import Style

import base64
import cStringIO
import webcolors


class PilImage(qrcode.image.base.BaseImage):
    """
    PIL image builder, default format is PNG.
    """
    kind = "PNG"
    mask = None

    def new_image(self, **kwargs):
        back_color = kwargs.get("back_color", "white")
        fill_color = kwargs.get("fill_color", "black")

        if fill_color.lower() != "black" or back_color.lower() != "white":
            if back_color.lower() == "transparent":
                mode = "RGBA"
                back_color = None
            else:
                mode = "RGB"
        else:
            mode = "1"

        img = Image.new(mode, (self.pixel_size, self.pixel_size), back_color)
        self.fill_color = fill_color
        self.back_color = webcolors.name_to_rgb(back_color)
        self._idr = ImageDraw.Draw(img)
        return img

    def draw(self, row, col, style=Style.SQUARE):
        if self.escavate and not self.is_empty(row, col):
            return

        if style == Style.SQUARE:
            self._drawrect(row, col)
        elif style == Style.DOT:
            self._drawround(row, col)

    def _drawrect(self, row, col):
        box = self.pixel_box(row, col)
        self._idr.rectangle(box, fill=self.fill_color)

    def _drawround(self, row, col):
        circle_offset = self.box_size / 10
        box = self.pixel_box(row, col)
        box = (box[0][0]+circle_offset, box[0][1]+circle_offset, box[1][0]-circle_offset, box[1][1]-circle_offset)
        self._idr.ellipse(box, fill=self.fill_color)

    def add_logo(self, logo, override_img=None):
        image_string = cStringIO.StringIO(base64.b64decode(logo))
        img = Image.open(image_string)
        new_size = int(self.pixel_size / 6.2) * 2
        img = img.resize((new_size, new_size))
        center = self.pixel_size / 2
        (override_img or self._img).paste(img, (center - new_size/2, center - new_size/2, center + new_size/2, center + new_size/2), img)

    def set_mask(self, logo):
        img = Image.new("RGB", (self.pixel_size, self.pixel_size), "white")
        self.add_logo(logo, img)
        self.mask = img

    def save(self, stream, format=None, **kwargs):
        if format is None:
            format = kwargs.get("kind", self.kind)
        if "kind" in kwargs:
            del kwargs["kind"]
        self._img = self._img.resize((600, 600), Image.ANTIALIAS)
        self._img.save(stream, format=format, **kwargs)

    def __getattr__(self, name):
        return getattr(self._img, name)
