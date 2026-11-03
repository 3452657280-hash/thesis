import glob, os, shutil, sys
src = max(glob.glob(r".vio/state/browser_captures/*.png"), key=os.path.getmtime) if len(sys.argv) < 3 else sys.argv[2]
dst = os.path.join("交付", "论文图片", sys.argv[1])
shutil.copy(src, dst)
print("saved", dst)
