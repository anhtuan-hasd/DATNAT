# Thư viện vẽ nút khung (toạ độ px kiểu sách; y tính từ trên xuống, đổi sang y-up bằng Y())
from dr import *
FS=10
SER='Liberation Serif'
def Y(p): return -p
def T(ax,x,py,s,fs=FS,ha='left',va='center',serif=False,**k):
    return ax.text(x,Y(py),s,fontsize=fs,ha=ha,va=va,family=SER if serif else 'Liberation Sans',**k)
def L(ax,pts,lw=0.9,z=2,ls='-'):
    p=[(x,Y(y)) for x,y in pts]; line(ax,p,lw=lw,z=z,ls=ls)
def B(ax,pts,r=0,lw=2.1,z=4):
    bar(ax,[(x,Y(y)) for x,y in pts],r=r,lw=lw,z=z)
def tie(ax,x0,x1,py,thick=True):
    L(ax,[(x0,py),(x1,py)],lw=2.1 if thick else 0.8,z=3)
def hk(ax,x,py,dx,dy,lw=1.0): L(ax,[(x,py),(x+dx,py+dy)],lw=lw,z=3)
def col(ax,ox,hc,p0,p1,sp=25,thick_every=3,start=None,faces=True,legs=True):
    """thân cột trong phạm vi px p0..p1 (p0 trên, p1 dưới): 2 cạnh bê tông, chân đai, cốt dọc, đai"""
    L(ax,[(ox,p0),(ox,p1)],lw=LW_CON); L(ax,[(ox+hc,p0),(ox+hc,p1)],lw=LW_CON)
    if legs:
        for x in (ox+7,ox+hc-7): L(ax,[(x,p0),(x,p1)],lw=0.9)
    if faces:
        for x in (ox+15,ox+hc-15): L(ax,[(x,p0),(x,p1)],lw=2.1,z=4)
    y=start if start is not None else p0+sp; i=0
    while y<p1-8:
        tie(ax,ox+7,ox+hc-7,y,thick=(i%thick_every==0)); y+=sp; i+=1
def colbreak(ax,ox,hc,py,amp=14):
    """ký hiệu gãy ở chân cột (tia chớp)"""
    L(ax,[(ox-12,py),(ox+hc*0.28,py),(ox+hc*0.46,py+amp*2.4),(ox+hc*0.62,py-amp*0.0),(ox+hc+12,py)],lw=LW_CON)
def beambreak(ax,xr,p0,p1):
    m=(p0+p1)/2
    L(ax,[(xr,p0),(xr,m-12),(xr-14,m+4),(xr+10,m+14),(xr,p1)],lw=LW_CON)
def lv_dn(ax,x,py,s,L_=150,side='r',fs=FS):
    """▽ trên mặt cấu kiện, gạch ngang phía trên, nhãn (chữ Times) trên gạch"""
    h=9
    ax.add_patch(Polygon([(x-h,Y(py-1.6*h)),(x+h,Y(py-1.6*h)),(x,Y(py))],closed=True,fc='white',ec='k',lw=0.8,zorder=6))
    x2=x+L_ if side=='r' else x-L_
    L(ax,[(min(x,x2)-0,py-1.6*h),(max(x,x2),py-1.6*h)],lw=0.8)
    T(ax,(x+x2)/2,py-1.6*h-6,s,ha='center',va='bottom',serif=True,fs=fs)
def lv_up(ax,x,py,s,L_=130,side='r',fs=FS,dxt=0,dyt=10):
    """△ dưới mặt dầm, nhãn nằm bên phải/ dưới"""
    h=9
    ax.add_patch(Polygon([(x-h,Y(py+1.6*h)),(x+h,Y(py+1.6*h)),(x,Y(py))],closed=True,fc='white',ec='k',lw=0.8,zorder=6))
    x2=x+L_ if side=='r' else x-L_
    L(ax,[(min(x,x2),py+1.6*h),(max(x,x2),py+1.6*h)],lw=0.8)
    T(ax,(x+x2)/2+dxt,py+1.6*h+dyt,s,ha='center',va='top',serif=True,fs=fs)
def bigM(ax,p0,p1,bulge=70,txt='M',tpos=None):
    """mũi tên cong mô men (đầu rỗng) từ p0 đến p1 (px từ trên xuống)"""
    x0,y0=p0; x1,y1=p1
    c1=(x0+bulge*1.5,y0+10); c2=(x1+bulge*1.0,y1-60)
    t=np.linspace(0,1,50)
    px=(1-t)**3*x0+3*(1-t)**2*t*c1[0]+3*(1-t)*t**2*c2[0]+t**3*x1
    py=(1-t)**3*y0+3*(1-t)**2*t*c1[1]+3*(1-t)*t**2*c2[1]+t**3*y1
    ax.plot(px,-py,color='k',lw=0.8)
    d=np.array([px[-1]-px[-4],-(py[-1]-py[-4])]); d/=np.linalg.norm(d); n=np.array([-d[1],d[0]])
    tip=np.array([px[-1],-py[-1]]); a=18; w=7
    ax.add_patch(Polygon([tip,tip-a*d+w*n,tip-a*d-w*n],closed=True,fc='white',ec='k',lw=0.8,zorder=6))
    T(ax,x1+22,y1+18,txt,fs=FS+1,ha='left')
def spac(ax,x,py,w,dy,label='Khoảng cách cốt đai',l1='≤ 500',l2='≤ 15Ømin',xl=None):
    """nhãn 'Khoảng cách cốt đai { ≤500 / ≤15Ømin' (ngoặc trái) và ngoặc nhọn phụ phía phải"""
    # ngoặc nhỏ trước 2 dòng
    xb=x
    brace_left_px(ax,xb,py-dy*0.55,py+dy*0.55,12)
    T(ax,xb+6,py-dy*0.28,l1,fs=FS)
    T(ax,xb+6,py+dy*0.28,l2.replace('min','')+'',fs=FS) if False else None
    T(ax,xb+6,py+dy*0.28,l2.split('min')[0],fs=FS)
    ax.text(xb+6+0.0,Y(py+dy*0.28),'',fontsize=FS)
    # chỉ số dưới min
    return
def brace_left_px(ax,x,p0,p1,w,lw=0.8):
    ym=(p0+p1)/2; h=p1-p0; t=np.linspace(0,1,30)
    def bez(a,b,c,d): return [(1-s)**3*np.array(a)+3*(1-s)**2*s*np.array(b)+3*(1-s)*s**2*np.array(c)+s**3*np.array(d) for s in t]
    up=bez((x,p0),(x,p0+h*0.14),(x,ym-h*0.14),(x-w,ym)); dn=bez((x-w,ym),(x,ym+h*0.14),(x,p1-h*0.14),(x,p1))
    p=np.array(up+dn); ax.plot(p[:,0],-p[:,1],color='k',lw=lw)
def brace_right_px(ax,x,p0,p1,w,lw=0.8):
    ym=(p0+p1)/2; h=p1-p0; t=np.linspace(0,1,30)
    def bez(a,b,c,d): return [(1-s)**3*np.array(a)+3*(1-s)**2*s*np.array(b)+3*(1-s)*s**2*np.array(c)+s**3*np.array(d) for s in t]
    up=bez((x,p0),(x,p0+h*0.14),(x,ym-h*0.14),(x+w,ym)); dn=bez((x+w,ym),(x,ym+h*0.14),(x,p1-h*0.14),(x,p1))
    p=np.array(up+dn); ax.plot(p[:,0],-p[:,1],color='k',lw=lw)
def Tmin(ax,x,py,pre,sub='min',fs=FS):
    ax.text(x,Y(py),pre+r'$_{\mathrm{'+sub+'}}$',fontsize=fs,ha='left',va='center',family='Liberation Sans')
def stir_label(ax,xtxt,pyc,l1='≤ 500',l2='Ø',lab='Khoảng cách cốt đai',big=False,l2txt=None,w=None,dy=24,brace_x=None):
    """Khoảng cách cốt đai { ≤500 ; ≤15Ømin  — kèm ngoặc nhọn lớn bên phải (tuỳ chọn)"""
    T(ax,xtxt,pyc,lab,serif=True)
    renderer=ax.figure.canvas.get_renderer()
def spacing(ax,xlab,pyc,l1='≤ 500',l2='≤ 15Ø',bigbrace=None,dy=22):
    """xlab: toạ độ x bắt đầu của chữ 'Khoảng cách cốt đai'; pyc: tâm theo px; bigbrace=(x,p0,p1)"""
    t=ax.text(xlab,Y(pyc),'Khoảng cách cốt đai',fontsize=FS,ha='left',va='center',family=SER)
    ax.figure.canvas.draw()
    bb=t.get_window_extent().transformed(ax.transData.inverted())
    xb=bb.x1+14
    brace_left_px(ax,xb+12,pyc-dy-8,pyc+dy+8,12)
    T(ax,xb+20,pyc-dy*0.55,l1)
    ax.text(xb+20,Y(pyc+dy*0.55),l2+r'$_{\mathrm{min}}$',fontsize=FS,ha='left',va='center')
    if bigbrace:
        bx,p0,p1=bigbrace
        if bx is None: bx=xb+138
        brace_left_px(ax,bx,p0,p1,14)
    return xb
def ldr(ax,xt,pyt,s,tgt,ha='left',va='bottom',fs=FS):
    """chú thích Times có gạch chân và đường dẫn (px từ trên xuống)"""
    t=ax.text(xt,Y(pyt),s,fontsize=fs,ha=ha,va=va,family=SER)
    ax.figure.canvas.draw()
    bb=t.get_window_extent().transformed(ax.transData.inverted())
    yb=bb.y0-1.5
    line(ax,[(bb.x0,yb),(bb.x1,yb)],lw=0.8)
    sx=bb.x1 if tgt[0]>(bb.x0+bb.x1)/2 else bb.x0
    if abs(tgt[0]-bb.x1)<abs(tgt[0]-bb.x0) and tgt[0]>bb.x1: sx=bb.x1
    line(ax,[(sx,yb),(tgt[0],Y(tgt[1]))],lw=0.8)
def dh(ax,x0,x1,py,txt='',off=-4,ext=None,fs=FS,serif=False,tpos='above'):
    ax.annotate('',xy=(x0,Y(py)),xytext=(x1,Y(py)),arrowprops=dict(arrowstyle='<|-|>',lw=0.7,color='k',mutation_scale=7,shrinkA=0,shrinkB=0),zorder=6)
    if ext is not None:
        for x in (x0,x1): L(ax,[(x,py),(x,ext)],lw=0.7)
    if txt: ax.text((x0+x1)/2,Y(py+off),txt,fontsize=fs,ha='center',va='bottom' if tpos=='above' else 'top',family=SER if serif else 'Liberation Sans')
def dv(ax,py0,py1,x,txt='',ext=None,xt=None,fs=FS,rot=90):
    ax.annotate('',xy=(x,Y(py0)),xytext=(x,Y(py1)),arrowprops=dict(arrowstyle='<|-|>',lw=0.7,color='k',mutation_scale=7,shrinkA=0,shrinkB=0),zorder=6)
    if ext is not None:
        for p in (py0,py1): L(ax,[(x,p),(ext,p)],lw=0.7)
    if txt: ax.text(xt if xt is not None else x-6,Y((py0+py1)/2),txt,fontsize=fs,ha='right',va='center',rotation=rot)
def lan_v(ax,x,p0,p1,ext_to=None,xt=None,txt=r'$L_{an}$'):
    dv(ax,p0,p1,x,txt,ext=ext_to,xt=xt if xt else x-5)
def beambreak_l(ax,xl,p0,p1):
    m=(p0+p1)/2
    L(ax,[(xl,p0),(xl,m-12),(xl+14,m+4),(xl-10,m+14),(xl,p1)],lw=LW_CON)
def arrow_path(ax,pts,r=0,head0=False,head1=True,lw=0.9,ms=9):
    p=rrpath([(x,Y(y)) for x,y in pts],r) if r else np.array([(x,Y(y)) for x,y in pts],float)
    ax.plot(p[:,0],p[:,1],color='k',lw=lw,zorder=6)
    def head(a,b):
        d=b-a; d=d/np.linalg.norm(d); n=np.array([-d[1],d[0]]); w=3.2; l=11
        ax.add_patch(Polygon([b,b-l*d+w*n,b-l*d-w*n],closed=True,fc='k',ec='k',lw=0.5,zorder=7))
    k=min(6,len(p)-1)
    if head1: head(p[-k-1] if len(p)>k else p[0],p[-1])
    if head0: head(p[k],p[0])
def rtxt(ax,x,py,s,fs=FS-1): ax.text(x,Y(py),s,fontsize=fs,ha='left',va='center',family='Liberation Serif')
