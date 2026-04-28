from pathlib import Path
from PIL import Image, ImageDraw


SIZE = 256
OUT_DIR = Path("sprites") / "units"
ATTACK_DIR = OUT_DIR / "attacks"


UNITS = {
    "commander": {
        "file": "commander.png",
        "body": (80, 92, 120, 255),
        "trim": (238, 198, 86, 255),
        "weapon": "sword",
        "crest": (190, 54, 62, 255),
    },
    "warrior": {
        "file": "warrior.png",
        "body": (115, 92, 78, 255),
        "trim": (204, 210, 214, 255),
        "weapon": "axe",
        "crest": (154, 82, 48, 255),
    },
    "archer": {
        "file": "archer.png",
        "body": (68, 112, 76, 255),
        "trim": (222, 190, 112, 255),
        "weapon": "bow",
        "crest": (78, 54, 36, 255),
    },
    "healer": {
        "file": "healer.png",
        "body": (226, 218, 190, 255),
        "trim": (80, 170, 150, 255),
        "weapon": "staff",
        "crest": (248, 236, 155, 255),
    },
    "trebuchet": {
        "file": "trebuchet.png",
        "body": (120, 92, 58, 255),
        "trim": (82, 68, 52, 255),
        "weapon": "trebuchet",
        "crest": (176, 130, 70, 255),
    },
    "viking": {
        "file": "viking.png",
        "body": (96, 108, 130, 255),
        "trim": (218, 218, 205, 255),
        "weapon": "hammer",
        "crest": (224, 172, 72, 255),
    },
}


def draw_shadow(draw):
    draw.ellipse((62, 206, 194, 232), fill=(0, 0, 0, 54))


def draw_humanoid(draw, cfg, pose=0):
    body = cfg["body"]
    trim = cfg["trim"]
    crest = cfg["crest"]
    skin = (205, 154, 112, 255)
    dark = (38, 34, 33, 255)
    metal = (188, 196, 202, 255)
    lean = [0, 8, 16, 4][pose]
    arm_raise = [0, -16, -28, -8][pose]

    draw_shadow(draw)
    draw.polygon(
        [(94 + lean, 86), (160 + lean, 86), (178 + lean, 184), (78 + lean, 184)],
        fill=body,
        outline=dark,
    )
    draw.rectangle((88 + lean, 132, 168 + lean, 146), fill=trim)
    draw.rectangle((106 + lean, 184, 124 + lean, 216), fill=dark)
    draw.rectangle((144 + lean, 184, 162 + lean, 216), fill=dark)
    draw.ellipse((96 + lean, 44, 158 + lean, 104), fill=skin, outline=dark, width=3)
    draw.polygon(
        [(90 + lean, 58), (128 + lean, 28), (166 + lean, 58), (158 + lean, 42), (98 + lean, 42)],
        fill=trim,
        outline=dark,
    )
    draw.polygon(
        [(122 + lean, 22), (134 + lean, 22), (140 + lean, 40), (116 + lean, 40)],
        fill=crest,
        outline=dark,
    )
    draw.rectangle((112 + lean, 72, 120 + lean, 78), fill=dark)
    draw.rectangle((138 + lean, 72, 146 + lean, 78), fill=dark)
    draw.line((120 + lean, 92, 142 + lean, 92), fill=dark, width=3)
    draw.line((92 + lean, 104, 56 + lean, 150 + arm_raise), fill=body, width=14)
    draw.line((166 + lean, 104, 204 + lean, 132 + arm_raise), fill=body, width=14)
    draw.ellipse((48 + lean, 142 + arm_raise, 64 + lean, 158 + arm_raise), fill=skin, outline=dark)
    draw.ellipse((196 + lean, 124 + arm_raise, 212 + lean, 140 + arm_raise), fill=skin, outline=dark)
    return lean, arm_raise, metal, dark, trim


def draw_weapon(draw, cfg, pose=0):
    weapon = cfg["weapon"]
    lean, arm_raise, metal, dark, trim = draw_humanoid(draw, cfg, pose)
    if weapon == "sword":
        points = [
            (204 + lean, 126 + arm_raise),
            (230 + lean + pose * 6, 72 + arm_raise - pose * 12),
        ]
        draw.line(points, fill=metal, width=8)
        draw.line((194 + lean, 140 + arm_raise, 214 + lean, 112 + arm_raise), fill=trim, width=6)
    elif weapon == "axe":
        draw.line((202 + lean, 128 + arm_raise, 224 + lean + pose * 8, 72 + arm_raise), fill=(95, 62, 38, 255), width=8)
        draw.pieslice((204 + lean + pose * 8, 54 + arm_raise, 244 + lean + pose * 8, 94 + arm_raise), 80, 280, fill=metal, outline=dark)
    elif weapon == "bow":
        draw.arc((188 + lean + pose * 4, 72 + arm_raise, 236 + lean + pose * 4, 172 + arm_raise), -80, 80, fill=(84, 54, 32, 255), width=6)
        draw.line((214 + lean + pose * 4, 82 + arm_raise, 214 + lean + pose * 4, 162 + arm_raise), fill=metal, width=2)
        draw.line((200 + lean, 124 + arm_raise, 242 + lean + pose * 8, 116 + arm_raise), fill=metal, width=4)
    elif weapon == "staff":
        draw.line((202 + lean, 136 + arm_raise, 224 + lean + pose * 4, 56 + arm_raise), fill=(98, 67, 45, 255), width=8)
        glow = (95, 224, 194, 170)
        draw.ellipse((210 + lean + pose * 4, 42 + arm_raise, 238 + lean + pose * 4, 70 + arm_raise), fill=glow, outline=trim, width=4)
    elif weapon == "hammer":
        draw.line((198 + lean, 128 + arm_raise, 230 + lean + pose * 5, 78 + arm_raise), fill=(94, 62, 40, 255), width=9)
        draw.rectangle((210 + lean + pose * 5, 54 + arm_raise, 252 + lean + pose * 5, 82 + arm_raise), fill=metal, outline=dark, width=3)


def draw_trebuchet(draw, cfg, pose=0):
    body = cfg["body"]
    trim = cfg["trim"]
    dark = (42, 34, 26, 255)
    draw_shadow(draw)
    draw.rectangle((64, 164, 194, 190), fill=body, outline=dark, width=4)
    draw.line((80, 190, 52, 222), fill=dark, width=8)
    draw.line((176, 190, 206, 222), fill=dark, width=8)
    draw.ellipse((56, 188, 98, 230), fill=trim, outline=dark, width=4)
    draw.ellipse((154, 188, 196, 230), fill=trim, outline=dark, width=4)
    draw.polygon((96, 164, 128, 82, 160, 164), outline=dark, fill=None)
    arm_angles = [(118, 82, 224, 62), (118, 82, 214, 40), (118, 82, 180, 24), (118, 82, 204, 92)]
    draw.line(arm_angles[pose], fill=body, width=10)
    x1, y1, x2, y2 = arm_angles[pose]
    draw.ellipse((x2 - 12, y2 - 12, x2 + 12, y2 + 12), fill=(76, 76, 74, 255), outline=dark)
    draw.rectangle((112, 70, 132, 176), fill=trim, outline=dark, width=3)


def make_unit_image(name, cfg, pose=0):
    image = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    if cfg["weapon"] == "trebuchet":
        draw_trebuchet(draw, cfg, pose)
    else:
        draw_weapon(draw, cfg, pose)
    return image


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ATTACK_DIR.mkdir(parents=True, exist_ok=True)
    for name, cfg in UNITS.items():
        idle = make_unit_image(name, cfg, 0)
        idle.save(OUT_DIR / cfg["file"])
        if name == "commander":
            blue_commander = idle.copy()
            overlay = Image.new("RGBA", blue_commander.size, (58, 116, 210, 72))
            blue_commander.alpha_composite(overlay)
            blue_commander.save(OUT_DIR / "Blue commander.png")
        for pose in range(4):
            make_unit_image(name, cfg, pose).save(ATTACK_DIR / f"{name}_attack_{pose}.png")


if __name__ == "__main__":
    main()
