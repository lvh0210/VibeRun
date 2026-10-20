import os
import math
from PIL import Image, ImageDraw, ImageFilter

def create_viberun_logo(output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    size = 512
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Base Squircle / Rounded Rectangle
    pad = 32
    radius = 110
    squircle_box = [pad, pad, size - pad, size - pad]

    # Gradient background: Deep Obsidian to Midnight Navy
    bg_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    bg_draw = ImageDraw.Draw(bg_img)
    for y in range(pad, size - pad):
        factor = (y - pad) / (size - 2 * pad)
        r = int(18 * (1 - factor) + 10 * factor)
        g = int(22 * (1 - factor) + 14 * factor)
        b = int(32 * (1 - factor) + 24 * factor)
        bg_draw.line([(pad, y), (size - pad, y)], fill=(r, g, b, 255))

    # Mask for rounded corners
    mask = Image.new("L", (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle(squircle_box, radius=radius, fill=255)
    img.paste(bg_img, (0, 0), mask)

    # 2. Glowing Neon Border (Electric Cyan to Neon Purple)
    border_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    b_draw = ImageDraw.Draw(border_img)
    b_draw.rounded_rectangle(squircle_box, radius=radius, outline=(0, 210, 255, 200), width=8)
    
    # Soft outer glow
    glow = border_img.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(glow, img)
    img = Image.alpha_composite(img, border_img)

    # 3. Dynamic "V" Monogram with Search Beam
    # Draw futuristic angular "V"
    v_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    v_draw = ImageDraw.Draw(v_layer)

    # Left wing of V
    left_polygon = [
        (130, 140),
        (200, 140),
        (256, 320),
        (200, 320)
    ]
    # Right wing of V (longer & dynamic)
    right_polygon = [
        (256, 320),
        (380, 140),
        (440, 140),
        (290, 380),
        (222, 380)
    ]

    # Gradient fill for V: Electric Cyan (0, 242, 254) to Vivid Purple (155, 50, 255)
    for y in range(130, 390):
        t = (y - 130) / (390 - 130)
        cr = int(0 * (1 - t) + 180 * t)
        cg = int(242 * (1 - t) + 60 * t)
        cb = int(254 * (1 - t) + 255 * t)
        v_draw.line([(0, y), (size, y)], fill=(cr, cg, cb, 255))

    # Mask the V polygons
    v_mask = Image.new("L", (size, size), 0)
    vm_draw = ImageDraw.Draw(v_mask)
    vm_draw.polygon(left_polygon, fill=255)
    vm_draw.polygon(right_polygon, fill=255)

    # Circular magnifying glass ring integrated at the top-right wing of V
    ring_center = (370, 190)
    ring_radius = 65
    ring_box = [ring_center[0] - ring_radius, ring_center[1] - ring_radius,
                ring_center[0] + ring_radius, ring_center[1] + ring_radius]
    vm_draw.ellipse(ring_box, outline=255, width=22)

    # Search handle shooting outwards
    vm_draw.line([(370 + 46, 190 + 46), (370 + 85, 190 + 85)], fill=255, width=22)

    v_final = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    v_final.paste(v_layer, (0, 0), v_mask)

    # Inner Glow for V
    v_glow = v_final.filter(ImageFilter.GaussianBlur(12))
    img = Image.alpha_composite(img, v_glow)
    img = Image.alpha_composite(img, v_final)

    # 4. Save formats
    # Large PNG
    png_path = os.path.join(output_dir, "logo.png")
    img.save(png_path, "PNG")
    print(f"Generated: {png_path}")

    # UI Search Bar icon (28x28 and 32x32)
    icon_28 = img.resize((28, 28), Image.Resampling.LANCZOS)
    icon_28_path = os.path.join(output_dir, "logo_28.png")
    icon_28.save(icon_28_path, "PNG")

    icon_32 = img.resize((32, 32), Image.Resampling.LANCZOS)
    icon_32_path = os.path.join(output_dir, "logo_32.png")
    icon_32.save(icon_32_path, "PNG")

    # Multi-resolution Windows ICO
    ico_path = os.path.join(output_dir, "logo.ico")
    img.save(
        ico_path,
        format="ICO",
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    )
    print(f"Generated: {ico_path}")

if __name__ == "__main__":
    assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
    create_viberun_logo(assets_dir)
