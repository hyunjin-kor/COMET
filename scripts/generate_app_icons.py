from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = ROOT / "frontend" / "public"
ELECTRON_DIR = ROOT / "electron"


def lerp_color(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(x + (y - x) * t) for x, y in zip(a, b))


def make_linear_gradient(size: int, top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    image = Image.new("RGBA", (size, size))
    pixels = image.load()
    for y in range(size):
        t = y / max(size - 1, 1)
        color = lerp_color(top, bottom, t)
        for x in range(size):
            pixels[x, y] = (*color, 255)
    return image


def rounded_mask(size: int, inset: int, radius: int) -> Image.Image:
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((inset, inset, size - inset, size - inset), radius=radius, fill=255)
    return mask


def glow_layer(size: int, center: tuple[float, float], radius: float, color: tuple[int, int, int, int]) -> Image.Image:
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.ellipse(
        (center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius),
        fill=color,
    )
    return layer.filter(ImageFilter.GaussianBlur(radius=max(6, int(radius * 0.16))))


def polygon_shadow(size: int, points: list[tuple[float, float]], offset: tuple[int, int], blur: int, fill: tuple[int, int, int, int]) -> Image.Image:
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    ox, oy = offset
    draw.polygon([(x + ox, y + oy) for x, y in points], fill=fill)
    return layer.filter(ImageFilter.GaussianBlur(radius=blur))


def draw_icon(size: int) -> Image.Image:
    inset = max(2, int(size * 0.075))
    radius = max(8, int(size * 0.22))
    border_width = max(1, int(size * 0.012))
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))

    background = make_linear_gradient(size, (92, 193, 255), (38, 118, 219))
    canvas.paste(background, (0, 0), rounded_mask(size, inset, radius))

    canvas.alpha_composite(glow_layer(size, (size * 0.33, size * 0.27), size * 0.22, (255, 255, 255, 58)))

    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(
        (inset, inset, size - inset, size - inset),
        radius=radius,
        outline=(255, 255, 255, 92),
        width=border_width,
    )

    outer = [
        (size * 0.50, size * 0.21),
        (size * 0.66, size * 0.31),
        (size * 0.66, size * 0.55),
        (size * 0.50, size * 0.66),
        (size * 0.34, size * 0.55),
        (size * 0.34, size * 0.31),
    ]

    canvas.alpha_composite(
        polygon_shadow(size, outer, (0, max(2, int(size * 0.014))), max(3, int(size * 0.018)), (0, 0, 0, 60))
    )
    draw.polygon(outer, fill=(13, 36, 69, 255), outline=(232, 245, 255, 232))

    pellet_r = size * 0.04
    for cx, cy in ((0.43, 0.46), (0.57, 0.46), (0.50, 0.57)):
        draw.ellipse(
            (
                size * cx - pellet_r,
                size * cy - pellet_r,
                size * cx + pellet_r,
                size * cy + pellet_r,
            ),
            fill=(165, 242, 224, 255),
        )

    arrow_points = [
        (size * 0.26, size * 0.66),
        (size * 0.39, size * 0.58),
        (size * 0.50, size * 0.62),
        (size * 0.67, size * 0.43),
    ]
    arrow_width = max(3, int(size * 0.078))
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.line(arrow_points, fill=(255, 255, 255, 76), width=arrow_width + max(2, int(size * 0.02)), joint="curve")
    glow_draw.polygon(
        [
            (size * 0.75, size * 0.37),
            (size * 0.62, size * 0.41),
            (size * 0.68, size * 0.52),
        ],
        fill=(255, 214, 107, 76),
    )
    canvas.alpha_composite(glow.filter(ImageFilter.GaussianBlur(radius=max(3, int(size * 0.02)))))

    draw.line(arrow_points, fill=(255, 255, 255, 255), width=arrow_width, joint="curve")
    draw.polygon(
        [
            (size * 0.76, size * 0.37),
            (size * 0.63, size * 0.41),
            (size * 0.69, size * 0.52),
        ],
        fill=(255, 214, 107, 255),
    )

    return canvas


def save_pngs() -> None:
    for size in (32, 128, 256, 512):
        icon = draw_icon(size)
        icon.save(PUBLIC_DIR / f"icon-{size}x{size}.png")
        if size == 512:
            icon.save(PUBLIC_DIR / "icon.png")
            icon.save(PUBLIC_DIR / "icon-512x512.png")
            icon.save(ELECTRON_DIR / "icon.png")


def save_ico() -> None:
    icon = draw_icon(512)
    icon.save(
        PUBLIC_DIR / "icon.ico",
        format="ICO",
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )


def main() -> None:
    save_pngs()
    save_ico()


if __name__ == "__main__":
    main()
