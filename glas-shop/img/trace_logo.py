# Trace the hand-lettered logo into a smooth vector path (crisp at any size)
import sys,numpy as np,potrace
from PIL import Image,ImageFilter
im=Image.open(sys.argv[1]).convert('L')
w,h=im.size;im=im.resize((w*4,h*4),Image.LANCZOS).filter(ImageFilter.GaussianBlur(2))  # upsample + soften so the trace follows the stroke, not the pixels
bm=potrace.Bitmap(np.asarray(im)>=128)  # potracer treats True as background
path=bm.trace(turdsize=10,alphamax=1.15,opticurve=True,opttolerance=0.4)
ys,xs=np.where(np.asarray(im)<128);X0,X1,Y0,Y1=xs.min(),xs.max(),ys.min(),ys.max()
def bbox(c):
    pts=[c.start_point]+[q for seg in c.segments for q in ([seg.c,seg.end_point] if seg.is_corner else [seg.end_point])]
    return min(q.x for q in pts),min(q.y for q in pts),max(q.x for q in pts),max(q.y for q in pts)
d=[];dot=[]
for c in path:
    x0,y0,x1,y1=bbox(c)
    if x0>X0+.78*(X1-X0) and y1<Y0+.4*(Y1-Y0):dot.append((x0,y0,x1,y1));continue  # the sketchy almond over the i: replace with a clean solid one

    s=c.start_point;d.append(f"M{s.x:.1f},{s.y:.1f}")
    for seg in c.segments:
        if seg.is_corner:d.append(f"L{seg.c.x:.1f},{seg.c.y:.1f}L{seg.end_point.x:.1f},{seg.end_point.y:.1f}")
        else:d.append(f"C{seg.c1.x:.1f},{seg.c1.y:.1f} {seg.c2.x:.1f},{seg.c2.y:.1f} {seg.end_point.x:.1f},{seg.end_point.y:.1f}")
    d.append("Z")
if dot:  # solid almond, tilted like the original
    x0=min(b[0] for b in dot);y0=min(b[1] for b in dot);x1=max(b[2] for b in dot);y1=max(b[3] for b in dot)
    cx,cy,rw,rh=(x0+x1)/2,(y0+y1)/2,(x1-x0)/2*.9,(y1-y0)/2*.95
    d.append(f'M{cx:.1f},{cy-rh:.1f}C{cx+rw*1.25:.1f},{cy-rh*.35:.1f} {cx+rw*.9:.1f},{cy+rh:.1f} {cx:.1f},{cy+rh:.1f}C{cx-rw*.9:.1f},{cy+rh:.1f} {cx-rw*1.25:.1f},{cy-rh*.35:.1f} {cx:.1f},{cy-rh:.1f}Z')
pad=8
vb=f"{X0-pad} {Y0-pad} {X1-X0+2*pad} {Y1-Y0+2*pad}"
open(sys.argv[2],'w').write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}"><path fill-rule="evenodd" d="{"".join(d)}"/></svg>')
print(vb,len("".join(d)))
