from PIL import Image
import glob, os
fs = sorted(glob.glob("frames/f*.png"))
ims = []
for f in fs:
    im = Image.open(f).convert("RGBA")
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    bg.alpha_composite(im)
    ims.append(bg.convert("RGB"))
bbox = None
for im in ims:
    b = Image.eval(im.convert("L"), lambda p: 255 if p < 248 else 0).getbbox()
    if b:
        bbox = b if bbox is None else (min(bbox[0], b[0]), min(bbox[1], b[1]), max(bbox[2], b[2]), max(bbox[3], b[3]))
pad = 6
W, H = ims[0].size
box = (max(0, bbox[0]-pad), max(0, bbox[1]-pad), min(W, bbox[2]+pad), min(H, bbox[3]+pad))
ims = [im.crop(box) for im in ims]
pal = [im.quantize(colors=96, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for im in ims]
pal[0].save("boot.gif", save_all=True, append_images=pal[1:], duration=62, loop=0, optimize=True, disposal=1)
print(len(ims), ims[0].size, os.path.getsize("boot.gif"))
