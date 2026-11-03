import glob, os, sys
from PIL import Image
name, box = sys.argv[1], tuple(int(v) for v in sys.argv[2].split(","))
src = max(glob.glob(r".vio/state/browser_captures/*.png"), key=os.path.getmtime)
im = Image.open(src).crop(box)
im.save(os.path.join("交付", "论文图片", name))
print("saved", name, im.size)
