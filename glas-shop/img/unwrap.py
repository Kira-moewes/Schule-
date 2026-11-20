# Each cut-out jar photo -> (1) 360° wrap texture for a lathe body, (2) the jar's real silhouette profile, so texture and 3D shape line up row by row
import sys,json,numpy as np
from PIL import Image,ImageFilter
D=sys.argv[1];meta={}
for k in ['weiss','braun','erdnuss','pumpkin','schoko']:
    im=Image.open(f'{D}/{k}.png').convert('RGBA');A=np.asarray(im).astype(float);a=A[...,3]
    h,w=a.shape;rows=(a>128).sum(1);widest=rows.max()
    top=int(np.argmax(rows>0));L=int(.3*h);band=rows[top:top+L];s=int(L*.25)
    neck=top+s+int(np.argmin(band[s:]))
    bot=h-1-int(np.argmax(rows[::-1]>widest*.3))
    bh=bot-neck;scale=widest
    TW=2048;TH=int(TW/np.pi*bh/widest)
    patch=A[neck+int(bh*.05):neck+int(bh*.15),w//2-widest//5:w//2+widest//5,:3].reshape(-1,3);fill=np.median(patch,0)
    rgb=A[...,:3]*(a[...,None]/255)+fill*(1-a[...,None]/255)
    lr=[]
    for y in range(h):
        xs=np.where(a[y]>128)[0];lr.append((xs[0]+1.5,xs[-1]-1.5) if len(xs)>3 else (w/2,w/2))
    th=(np.arange(TW)/TW-.5)*2*np.pi;lim=np.radians(84)
    wgt=np.clip((lim-np.abs(th))/np.radians(14),0,1);sn=.5+.5*np.sin(np.clip(th,-lim,lim))
    out=np.zeros((TH,TW,3))
    for r in range(TH):
        y=neck+(r+.5)/TH*bh;y0=int(y);l,rr=lr[min(y0,h-1)]
        xs=np.clip(l+sn*(rr-l),0,w-1);x0=xs.astype(int);fx=xs-x0;x1=np.minimum(x0+1,w-1)
        row=rgb[y0,x0]*(1-fx[:,None])+rgb[y0,x1]*fx[:,None]
        out[r]=row*wgt[:,None]+fill*(1-wgt[:,None])
    Image.fromarray(out.clip(0,255).astype('uint8')).filter(ImageFilter.UnsharpMask(2,50,2)).save(f'{D}/{k}-wrap.jpg',quality=88)
    prof=[]  # [radius, height] in jar-width units, bottom -> neck
    for i in range(41):
        y=bot-i/40*bh;l,rr=lr[int(y)];prof.append([round(max(rr-l,0)/scale/2,4),round(i/40*bh/scale,4)])
    meta[k]={'profile':prof,'lid':round((neck-top)/scale,3),'lidW':round(rows[top+2:neck].max()/scale,3),'fill':'#%02x%02x%02x'%tuple(int(v) for v in fill)}
    print(k,TH,meta[k]['lid'],meta[k]['lidW'],prof[0],prof[20],prof[-1])
json.dump(meta,open(f'{D}/meta.json','w'))
