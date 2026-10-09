# Drafting helpers: bản vẽ cấu tạo cốt thép (phong cách như hình sách A)
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Polygon, Rectangle
from matplotlib.path import Path
from matplotlib.patches import PathPatch
plt.rcParams['font.family']='Liberation Sans'
plt.rcParams['mathtext.fontset']='custom'
plt.rcParams['mathtext.rm']='Liberation Sans'
plt.rcParams['mathtext.it']='Liberation Sans:italic'
plt.rcParams['mathtext.default']='regular'
TXT=8.5
TICK=0.0045
LW_CON=0.9; LW_STIR=1.0; LW_BAR=2.4; LW_DIM=0.6
def new(w,h,xlim,ylim):
    fig=plt.figure(figsize=(w,h)); ax=fig.add_axes([0,0,1,1]); ax.set_aspect('equal'); ax.axis('off')
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); return fig,ax
def line(ax,pts,lw=LW_CON,c='k',ls='-',z=2,cap='butt'):
    p=np.array(pts); ax.plot(p[:,0],p[:,1],color=c,lw=lw,ls=ls,zorder=z,solid_capstyle=cap,solid_joinstyle='round')
def poly(ax,pts,closed=True,**k):
    pts=list(pts); 
    if closed: pts=pts+[pts[0]]
    line(ax,pts,**k)
def rrpath(pts,r):
    """đường gấp khúc có bo tròn bán kính r tại các góc trong (không bo hai đầu)"""
    P=[np.array(p,float) for p in pts]; out=[P[0]]
    for i in range(1,len(P)-1):
        a,b,c=P[i-1],P[i],P[i+1]
        u=(a-b); u/=np.linalg.norm(u); v=(c-b); v/=np.linalg.norm(v)
        ang=np.arccos(np.clip(np.dot(u,v),-1,1)); 
        if abs(ang-np.pi)<1e-3: out.append(b); continue
        d=r/np.tan(ang/2); d=min(d,np.linalg.norm(a-b)*0.9,np.linalg.norm(c-b)*0.9)
        rr=d*np.tan(ang/2)
        p1=b+u*d; p2=b+v*d
        bis=(u+v); bis/=np.linalg.norm(bis); cen=b+bis*(rr/np.sin(ang/2))
        a1=np.arctan2(*(p1-cen)[::-1]); a2=np.arctan2(*(p2-cen)[::-1])
        da=(a2-a1+np.pi)%(2*np.pi)-np.pi
        t=np.linspace(a1,a1+da,14)
        out+= [cen+rr*np.array([np.cos(x),np.sin(x)]) for x in t]
    out.append(P[-1]); return np.array(out)
def bar(ax,pts,r=0,lw=LW_BAR,c='k',z=4,ls='-'):
    p=rrpath(pts,r) if r>0 else np.array(pts,float)
    ax.plot(p[:,0],p[:,1],color=c,lw=lw,zorder=z,solid_capstyle='butt',solid_joinstyle='round',ls=ls)
def dot(ax,x,y,d,c='k',z=5):
    ax.add_patch(Circle((x,y),d/2,fc=c,ec=c,zorder=z))
def stirrup(ax,x0,y0,x1,y1,r=0,lw=LW_STIR,hook=True,z=3,hk=None):
    p=rrpath([(x0,y0),(x1,y0),(x1,y1),(x0,y1),(x0,y0)],r) if r else np.array([(x0,y0),(x1,y0),(x1,y1),(x0,y1),(x0,y0)])
    ax.plot(p[:,0],p[:,1],color='k',lw=lw,zorder=z)
    if hook:
        s=hk if hk else min(x1-x0,y1-y0)*0.12
        line(ax,[(x0,y1),(x0+s,y1-s)],lw=lw,z=z)
def brk(ax,x,y,w,vertical=True,gap=None,lw=LW_CON):
    """ký hiệu gãy (zigzag) cắt một thanh dọc/ngang tại (x,y) có độ rộng w"""
    pass
def zig_v(ax,x0,x1,y,amp,lw=LW_CON):
    """gãy ngang: đường tia chớp nằm ngang từ x0 đến x1 ở cao độ y"""
    xm=(x0+x1)/2
    line(ax,[(x0,y),(xm-amp*0.3,y),(xm+amp*0.4,y+amp),(xm-amp*0.4,y-amp),(xm+amp*0.3,y),(x1,y)],lw=lw)
def zig_h(ax,y0,y1,x,amp,lw=LW_CON):
    ym=(y0+y1)/2
    line(ax,[(x,y0),(x,ym-amp*0.3),(x+amp,ym+amp*0.4),(x-amp,ym-amp*0.4),(x,ym+amp*0.3),(x,y1)],lw=lw)
def tick(ax,x,y,ang,s):
    a=np.deg2rad(ang)
    ax.plot([x-s*np.cos(a),x+s*np.cos(a)],[y-s*np.sin(a),y+s*np.sin(a)],color='k',lw=LW_DIM+0.3,zorder=6)
def dimh(ax,x1,x2,y,txt,ext=None,tpos='above',fs=TXT,s=None,toff=None,arr=False,ms=7):
    """kích thước nằm ngang: gạch xiên 45° (chuẩn bản vẽ xây dựng) + số"""
    s=s or TICK*abs(ax.get_xlim()[1]-ax.get_xlim()[0])
    if arr: ax.annotate('',xy=(x1,y),xytext=(x2,y),arrowprops=dict(arrowstyle='<|-|>',lw=LW_DIM,color='k',mutation_scale=ms,shrinkA=0,shrinkB=0),zorder=6)
    else:
        line(ax,[(x1,y),(x2,y)],lw=LW_DIM)
        for x in (x1,x2): tick(ax,x,y,45,s)
    if ext is not None:
        for x in (x1,x2): line(ax,[(x,y),(x,ext)],lw=LW_DIM*0.8)
    if txt:
        off=toff if toff is not None else s*1.1
        ax.text((x1+x2)/2,y+(off if tpos=='above' else -off),txt,ha='center',va='bottom' if tpos=='above' else 'top',fontsize=fs)
def dimv(ax,y1,y2,x,txt,ext=None,side='left',fs=TXT,s=None,toff=None,rot=90,arr=False,ms=7):
    s=s or TICK*abs(ax.get_xlim()[1]-ax.get_xlim()[0])
    if arr: ax.annotate('',xy=(x,y1),xytext=(x,y2),arrowprops=dict(arrowstyle='<|-|>',lw=LW_DIM,color='k',mutation_scale=ms,shrinkA=0,shrinkB=0),zorder=6)
    else:
        line(ax,[(x,y1),(x,y2)],lw=LW_DIM)
        for y in (y1,y2): tick(ax,x,y,45,s)
    if ext is not None:
        for y in (y1,y2): line(ax,[(x,y),(ext,y)],lw=LW_DIM*0.8)
    if txt:
        off=toff if toff is not None else s*1.2
        ax.text(x-(off if side=='left' else -off),(y1+y2)/2,txt,ha='right' if side=='left' else 'left',va='center',fontsize=fs,rotation=rot if rot!=90 else 0)
def dimv_rot(ax,y1,y2,x,txt,ext=None,fs=TXT,s=None,toff=None,side='left',arr=False,ms=7):
    s=s or TICK*abs(ax.get_xlim()[1]-ax.get_xlim()[0])
    if arr: ax.annotate('',xy=(x,y1),xytext=(x,y2),arrowprops=dict(arrowstyle='<|-|>',lw=LW_DIM,color='k',mutation_scale=ms,shrinkA=0,shrinkB=0),zorder=6)
    else:
        line(ax,[(x,y1),(x,y2)],lw=LW_DIM)
        for y in (y1,y2): tick(ax,x,y,45,s)
    if ext is not None:
        for y in (y1,y2): line(ax,[(x,y),(ext,y)],lw=LW_DIM*0.8)
    off=toff if toff is not None else s*1.4
    ax.text(x-(off if side=='left' else -off),(y1+y2)/2,txt,ha='center',va='center',fontsize=fs,rotation=90)
def text(ax,x,y,s,fs=TXT,ha='left',va='center',**k):
    return ax.text(x,y,s,fontsize=fs,ha=ha,va=va,**k)
def leader(ax,xy_text,xy_tgt,s,fs=TXT,ha='left',va='bottom',underline=True,elbow=None,serif=True):
    """chú thích có đường dẫn: gạch chân dưới chữ rồi xiên tới đối tượng"""
    x,y=xy_text; tx,ty=xy_tgt
    t=ax.text(x,y,s,fontsize=fs,ha=ha,va=va,family='Liberation Serif' if serif else 'Liberation Sans')
    fig=ax.figure; fig.canvas.draw()
    bb=t.get_window_extent().transformed(ax.transData.inverted())
    if ha=='left': xa,xb=bb.x0,bb.x1
    elif ha=='right': xa,xb=bb.x0,bb.x1
    else: xa,xb=bb.x0,bb.x1
    ybase=bb.y0-0.15*(bb.y1-bb.y0)
    if underline: line(ax,[(xa,ybase),(xb,ybase)],lw=LW_DIM)
    # đường dẫn từ đầu gần đối tượng của gạch chân
    sx= xb if tx>(xa+xb)/2 else xa
    line(ax,[(sx,ybase),(tx,ty)],lw=LW_DIM)
def level(ax,x,y,s,dx=0,side='right',fs=TXT,L=None,serif=True):
    """ký hiệu cao độ ▽ trên gạch ngang, nhãn trên gạch"""
    L=L or 0.12*abs(ax.get_xlim()[1]-ax.get_xlim()[0])
    h=0.008*abs(ax.get_xlim()[1]-ax.get_xlim()[0])
    ax.add_patch(Polygon([(x-h,y+h*1.6),(x+h,y+h*1.6),(x,y)],closed=True,fc='white',ec='k',lw=0.7,zorder=6))
    x2=x+L if side=='right' else x-L
    line(ax,[(x,y+h*1.6),(x2,y+h*1.6)],lw=LW_DIM)
    ax.text((x+x2)/2+ (h*2 if side=='right' else -h*2)*0,y+h*2.0,s,fontsize=fs,ha='center',va='bottom',family='Liberation Serif' if serif else 'Liberation Sans')
def brace_left(ax,x,y0,y1,w,lw=0.8):
    """ngoặc nhọn { bên trái, đỉnh nhọn hướng trái"""
    ym=(y0+y1)/2; h=y1-y0
    t=np.linspace(0,1,30)
    def bez(p0,p1,p2,p3):
        return [(1-s)**3*np.array(p0)+3*(1-s)**2*s*np.array(p1)+3*(1-s)*s**2*np.array(p2)+s**3*np.array(p3) for s in t]
    pts=bez((x,y0),(x-w*0.0,y0+h*0.1),(x-w*0.0,ym-h*0.15),(x-w,ym-h*0.0)) if False else None
    up=bez((x,y1),(x,y1-h*0.12),(x,ym+h*0.12),(x-w,ym))
    dn=bez((x-w,ym),(x,ym-h*0.12),(x,y0+h*0.12),(x,y0))
    p=np.array(up+dn); ax.plot(p[:,0],p[:,1],color='k',lw=lw)
def brace_text(ax,x,ymid,dy,w,lines,fs=TXT,gap=0.0,serif=False):
    """như '{ ≤500 / ≤15Ømin' dùng cho khoảng cách đai"""
    brace_left(ax,x,ymid-dy,ymid+dy,w)
    ax.text(x+w*0.4,ymid+dy*0.55,lines[0],fontsize=fs,ha='left',va='center')
    ax.text(x+w*0.4,ymid-dy*0.55,lines[1],fontsize=fs,ha='left',va='center')
def moment_arrow(ax,xy,rad,ang0,ang1,ls='-'):
    """mũi tên cong biểu thị mô men M (nét mảnh, đầu hở)"""
    cx,cy=xy; t=np.linspace(np.deg2rad(ang0),np.deg2rad(ang1),40)
    p=np.c_[cx+rad*np.cos(t),cy+rad*np.sin(t)]
    ax.plot(p[:,0],p[:,1],color='k',lw=0.7)
    d=p[-1]-p[-4]; d/=np.linalg.norm(d); n=np.array([-d[1],d[0]]); a=0.25*rad
    tip=p[-1]
    ax.plot([tip[0],tip[0]-a*d[0]+0.4*a*n[0]],[tip[1],tip[1]-a*d[1]+0.4*a*n[1]],color='k',lw=0.9)
    ax.plot([tip[0],tip[0]-a*d[0]-0.4*a*n[0]],[tip[1],tip[1]-a*d[1]-0.4*a*n[1]],color='k',lw=0.9)
def arrow(ax,p0,p1,lw=0.8,hw=None):
    ax.annotate('',xy=p1,xytext=p0,arrowprops=dict(arrowstyle='-|>',lw=lw,color='k',mutation_scale=8,shrinkA=0,shrinkB=0))
def label(ax,x,y,s,fs=11,**k):
    ax.text(x,y,s,fontsize=fs,ha='left',va='center',family='Liberation Sans',**k)
def save(fig,path,dpi=220):
    fig.savefig(path,dpi=dpi,bbox_inches='tight',pad_inches=0.04,facecolor='white'); plt.close(fig)
