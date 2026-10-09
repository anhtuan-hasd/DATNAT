from dr import *
import numpy as np, math
from matplotlib.patches import Rectangle, Circle
SER='Liberation Serif'
def ldr(ax,xt,yt,s,tgt,ha='left',va='bottom',fs=TXT+0.5,serif=True):
    t=ax.text(xt,yt,s,fontsize=fs,ha=ha,va=va,family=SER if serif else 'Liberation Sans')
    ax.figure.canvas.draw(); bb=t.get_window_extent().transformed(ax.transData.inverted())
    yb=bb.y0-0.12*(bb.y1-bb.y0); line(ax,[(bb.x0,yb),(bb.x1,yb)],lw=LW_DIM)
    sx=bb.x1 if tgt[0]>(bb.x0+bb.x1)/2 else bb.x0
    line(ax,[(sx,yb),tgt],lw=LW_DIM)
def mark(ax,x,y,n,r=95):
    """số hiệu thanh trong vòng tròn (quy ước bản vẽ VN)"""
    ax.text(x,y,str(n),fontsize=8.5,ha='center',va='center',zorder=9,
            bbox=dict(boxstyle='circle,pad=0.28',fc='white',ec='k',lw=0.8))

# ---------------------------------------------------------------- DẦM CB
def beam():
    L=6900; H=700; fc=300
    q=70.82; QC=248.33; MC=462.37
    fig=plt.figure(figsize=(9.0,6.8))
    X0,X1=-1000,8350
    # ---------- (a) hình bao mô men âm và khả năng chịu mô men
    a=fig.add_axes([0,0.66,1,0.34]); a.axis('off'); a.set_xlim(X0,X1); a.set_ylim(-80,720)
    xs=np.linspace(0,L,300); Mx=MC-QC*(xs/1000)+(q/2)*(xs/1000)**2
    # trục dầm
    line(a,[(0,0),(L,0)],lw=0.7)
    # đường cong |M-| (ước lượng)
    line(a,list(zip(xs,Mx)),lw=1.5,c='k',z=3)
    for xc in (0,L): line(a,[(xc,-30),(xc,12)],lw=0.7)
    # đường khả năng chịu lực M_u (bậc thang)
    xa,xb=2150,L-2000
    line(a,[(-280,492.5),(xa,492.5),(xa,260.2),(xb,260.2),(xb,492.5),(L+650+300,492.5)],lw=1.3,c='k',ls=(0,(6,2.5)),z=4)
    ax=a
    ax.text(-950,492.5,'M$_u$ = 492,5\n(2Ø25+3Ø22)',fontsize=8.5,ha='left',va='center',family=SER)
    ax.text(-950,260.2,'M$_u$ = 260,2\n(chỉ 2Ø25)',fontsize=8.5,ha='left',va='center',family=SER)
    ax.text(-950,462.37,'|M$_C$| = 462,37',fontsize=8.5,ha='left',va='center',family=SER) if False else None
    # tiết diện cắt lý thuyết
    for xt,lab in ((940,'x$_{lt}$ = 940'),(L-827,'x$_{lt}$ = 827')):
        line(a,[(xt,0),(xt,260.2)],lw=0.7,ls=(0,(2,2)))
        a.plot([xt],[260.2],'o',ms=4.5,color='k',zorder=6)
    a.text(940,-28,'940',fontsize=8.5,ha='center',va='top'); a.text(L-827,-28,'827',fontsize=8.5,ha='center',va='top')
    # đoạn kéo dài W
    dimh(a,940,2150,330,'W = 1165',ext=None,arr=True,toff=14,fs=8.5)
    line(a,[(940,260.2),(940,330)],lw=0.6); line(a,[(2150,260.2),(2150,330)],lw=0.6)
    dimh(a,L-2000,L-827,330,'W = 1165',ext=None,arr=True,toff=14,fs=8.5)
    line(a,[(L-827,260.2),(L-827,330)],lw=0.6); line(a,[(L-2000,260.2),(L-2000,330)],lw=0.6)
    ldr(a,2300,590,'Hình bao |M| (mô men âm) ước lượng, tải phân bố đều tương đương — xem 12.5',(2500,Mx[np.searchsorted(xs,2500)]+4),fs=9)
    ldr(a,3300,350,'Khả năng chịu mô men M$_u$ của các nhóm thanh trên',(3300,262),fs=9,va='bottom') if False else None
    a.text(X0+60,716,'a)  Hình bao vật liệu của thép trên (mô men âm)',fontsize=10.5,ha='left',va='top',family=SER,weight='bold')
    for xc,lab in ((0,'C'),(L,'B')): a.text(xc,-70,'',fontsize=1)
    # ---------- (b) mặt đứng bố trí
    b=fig.add_axes([0,0.33,1,0.33]); b.axis('off'); b.set_xlim(X0,X1); b.set_ylim(-1250,1800)
    for xc in (0,L):
        for sg in (-1,1): line(b,[(xc+sg*fc,-450),(xc+sg*fc,H+450)],lw=LW_CON)
        for yy in (-450,H+450): zig_v(b,xc-fc-60,xc+fc+60,yy,45)
    # dầm BA bên phải B (chỉ đoạn đầu)
    line(b,[(L+fc,H),(L+fc+900,H)],lw=LW_CON+0.2); line(b,[(L+fc,H-400),(L+fc+900,H-400)],lw=LW_CON+0.2)
    zig_h(b,H-400,H,L+fc+900,40)
    line(b,[(fc,0),(L-fc,0)],lw=LW_CON+0.2); line(b,[(fc,H),(L-fc,H)],lw=LW_CON+0.2)
    # đai
    def st(x,lw=0.8): line(b,[(x,24),(x,H-24)],lw=lw,z=3)
    dense=[fc+50+150*k for k in range(12)]; dense2=[L-fc-50-150*k for k in range(12)]
    mid=list(range(2250,4800,250))
    for x in dense+dense2+mid: st(x)
    xD=L/2
    hang=[xD+sg*(110+50+75*k) for k in range(5) for sg in (-1,1)]
    for x in hang: st(x,1.3)
    b.add_patch(Rectangle((xD-110,H-300),220,300,fc='none',ec='k',lw=LW_CON,zorder=3))
    b.add_patch(Rectangle((xD-110,H-300),220,300,fc='none',ec='k',lw=0,hatch='////',zorder=2))
    # ---- thép
    y1=H-40.5; y2=H-89
    # ① 2Ø25 góc trên: chạy suốt, uốn xuống cột C (chân 900), đi tiếp sang BA
    bar(b,[(L+fc+700,y1),(-280,y1),(-280,y1-900)],r=120,lw=3.2)
    # ② 3Ø22 gia cường: nhóm C (uốn xuống 800, cắt 2150) và nhóm B (từ 4900 sang BA 7850)
    bar(b,[(2150,y2),(-280,y2),(-280,y2-800)],r=110,lw=2.6)
    bar(b,[(L-2000,y2),(L+fc+650,y2)],lw=2.6)
    # ③ 3Ø22 dưới, neo 450 vào cột
    bar(b,[(fc-450,40.5),(L-fc+450,40.5)],lw=3.0)
    # ④ cốt cạnh bên
    for yy in (H*0.62,H*0.38): line(b,[(fc-0,yy),(L-fc,yy)],lw=1.3,z=3)
    # ---- số hiệu + chú thích
    mark(b,1000,y1+170,1); line(b,[(1000,y1+75),(1000,y1+3)],lw=0.7)
    mark(b,1550,y2-175,2); line(b,[(1550,y2-80),(1550,y2-4)],lw=0.7)
    mark(b,5700,y2+145,2); line(b,[(5700,y2+50),(5700,y2+4)],lw=0.7)
    mark(b,3000,40.5-170,3); line(b,[(3000,40.5-75),(3000,40.5-3)],lw=0.7)
    mark(b,4300,H*0.5+10,4); line(b,[(4300,H*0.5+10-75),(4300,H*0.5-35)],lw=0.7) if False else None
    mark(b,700,-155,5); line(b,[(700,-60),(700,12)],lw=0.7)
    mark(b,3200,-155,6); line(b,[(3200,-60),(3200,12)],lw=0.7)
    mark(b,xD+110+50+75*2,H+170,7); line(b,[(xD+110+50+75*2,H+75),(xD+110+50+75*2,H-24)],lw=0.7)
    # ký hiệu cắt thép
    for xc in (2150,L-2000):
        ax_=b; line(ax_,[(xc,y2-70),(xc,y2+70)],lw=0.6,ls=(0,(2,2)))
    # ghi độ dài tới điểm cắt
    dimh(b,0,2150,H+620,'2150 (từ tim C)',ext=y2,arr=True,toff=14,fs=8.5)
    dimh(b,L-2000,L,H+620,'2000 (từ tim B)',ext=y2,arr=True,toff=14,fs=8.5)
    dimh(b,L,L+fc+650,H+620,'650 sang BA',ext=y2,arr=True,toff=14,fs=8.5)
    ldr(b,-960,H+700,'Chân uốn xuống cột 900 (②: 800), r ≥ 8d',(-280,y1-500),fs=9) if False else None
    ldr(b,-420,-720,'Chân uốn xuống cột:\nthanh 1 dài 900, thanh 2 dài 800',(-285,-150),fs=9,va='top',ha='right')
    ldr(b,L+400,-700,'Thanh 3 neo 450 qua mép cột',(L-fc+300,34),fs=9,va='top')
    ldr(b,3550,H+900,'Dầm phụ D 220×300 — cốt treo (7): 5Ø8 mỗi bên, a75',(xD+110,H-60),fs=9)
    b.text(X0+60,1440,'b)  Mặt đứng bố trí cốt thép (mặt đứng không đúng tỉ lệ chiều dài; mặt cắt vẽ ở hình dưới)',fontsize=10.5,ha='left',va='top',family=SER,weight='bold') if False else None
    b.text(X0+60,1780,'b)  Mặt đứng bố trí cốt thép dầm CB',fontsize=10.5,ha='left',va='top',family=SER,weight='bold')
    # ---- chuỗi kích thước đai
    s=0.0045*(X1-X0)
    def dim(x1,x2,y,txt):
        dimh(b,x1,x2,y,txt,ext=-30,arr=False,toff=45,s=s,fs=9)
    y0=-620
    dim(fc,fc+1725,y0-0,'Ø8a150, 12 đai (L/4 = 1725)')
    dim(fc+1725,L-fc-1725,y0,'Ø8a250 (11 đai)')
    dim(L-fc-1725,L-fc,y0,'Ø8a150, 12 đai')
    dimh(b,0,L,-930,'L = 6900 (tim cột C – tim cột B)',ext=-640,arr=True,toff=14,fs=9.5)
    # ---- (c) bảng ghi chú nhỏ phía dưới
    c=fig.add_axes([0.02,0.0,0.96,0.33]); c.axis('off'); c.set_xlim(0,1); c.set_ylim(0,1)
    rows=[('①','2Ø25','thép trên, hàng ngoài, chạy suốt, uốn xuống cột C 900, đi tiếp sang dầm BA'),
          ('②','3Ø22','thép gia cường gối (nhóm C: cắt tại 2150; nhóm B: cắt tại 2000 tính từ tim B, vào BA 650 sau mép cột)'),
          ('③','3Ø22','thép dưới, chạy suốt, neo 450 mm qua mép cột mỗi đầu'),
          ('④','2×2Ø12','cốt cấu tạo cạnh bên (h = 700), suốt dài dầm'),
          ('⑤','Ø8a150','đai vùng gối, 12 đai mỗi đầu, đai đầu cách mép cột 50'),
          ('⑥','Ø8a250','đai giữa nhịp, 11 đai'),
          ('⑦','Ø8a75','cốt treo, 5 đai mỗi bên dầm phụ D (đặt thêm)')]
    c.text(0.0,0.97,'Chú giải số hiệu thanh',fontsize=10.5,weight='bold',va='top',family=SER)
    for i,(n,a_,t) in enumerate(rows):
        yy=0.86-i*0.115
        c.text(0.012,yy,str(i+1),fontsize=8.5,ha='center',va='center',bbox=dict(boxstyle='circle,pad=0.28',fc='white',ec='k',lw=0.8))
        c.text(0.035,yy,a_,fontsize=9.5,va='center',weight='bold')
        c.text(0.14,yy,t,fontsize=9.5,va='center',family=SER)
    fig.savefig('out/hlay_beam.png',dpi=190,bbox_inches='tight',pad_inches=0.04,facecolor='white'); plt.close(fig)
if __name__=='__main__': beam()

# ---------------------------------------------------------------- CỘT 22 hai tầng
def column():
    fig,ax=new(6.6,8.6,(-3300,2700),(-950,9800)); ax.set_aspect('auto')
    cx0,cx1=0,600
    # móng
    line(ax,[(-900,-700),(1500,-700),(1500,0),(-900,0)],lw=LW_CON+0.2)
    line(ax,[(-900,-700),(-900,0)],lw=LW_CON+0.2)
    ax.add_patch(Rectangle((-900,-700),2400,700,fc='none',ec='k',lw=0,hatch='///',zorder=1,alpha=0.35))
    # cột
    for x in (cx0,cx1): line(ax,[(x,0),(x,9500)],lw=LW_CON)
    zig_v(ax,cx0-70,cx1+70,9600,45)
    # dầm tầng 2 và 3 (hai bên)
    for yb in (4500,8400):
        for sgn,xe in ((-1,-1100),(1,1000)):
            xa=cx0 if sgn<0 else cx1
            line(ax,[(xa,yb),(xe,yb)],lw=LW_CON+0.2); line(ax,[(xa,yb+700),(xe,yb+700)],lw=LW_CON+0.2)
            zig_h(ax,yb,yb+700,xe,40)
    # cốt dọc
    # tầng 1: chờ từ móng, chân L dài 200 ra ngoài, thẳng lên 6350
    bar(ax,[(-140,-600),(60,-600),(60,6350)],r=0,lw=3.0) if False else None
    bar(ax,[(-140,-640),(60,-640),(60,6350)],r=100,lw=3.0)
    bar(ax,[(740,-640),(540,-640),(540,6350)],r=100,lw=3.0)
    # tầng 2: từ mặt sàn tầng 2 (y=5200) lên, nối chồng 1150 với tầng 1; thanh tầng 2 lệch vào 50
    bar(ax,[(110,5200),(110,9400)],lw=3.0); bar(ax,[(490,5200),(490,9400)],lw=3.0)
    # đai
    def st(y,lw=1.0): line(ax,[(20,y),(580,y)],lw=lw,z=3)
    zones=[]
    p_found=[-500,-350,-200]
    d1=[50+150*k for k in range(5)]; m1=list(range(850,3651,200)); t1=[4450-150*k for k in range(5)][::-1]
    j2=[4600,4750,4900,5050]; lap=[5250+150*k for k in range(8)]
    m2=list(range(6500,7701,200)); t2=[7900+150*k for k in range(4)]; j3=[8500,8650,8800,8950]
    allst=p_found+d1+m1+t1+j2+lap+m2+t2+j3
    for y in allst: st(y,lw=1.8 if (y in d1 or y in t1 or y in lap or y in t2 or y in j2 or y in j3 or y in p_found) else 1.0)
    # ký hiệu mức
    level(ax,-900,0,'−1,300 (mặt móng)',L=900,side='left') if False else None
    level(ax,-1100,4500+700,'+3,900 (sàn tầng 2)',L=900,side='left')
    level(ax,-1100,9100,'+7,800 (sàn tầng 3)',L=900,side='left')
    level(ax,-5,1300,'±0,000',L=900,side='left')
    # kích thước bên trái
    xl=-2600
    dimv(ax,0,5200,xl,'',ext=None,arr=True) if False else None
    ax.annotate('',xy=(xl-250,0),xytext=(xl-250,5200),arrowprops=dict(arrowstyle='<|-|>',lw=LW_DIM,color='k',mutation_scale=7,shrinkA=0,shrinkB=0))
    ax.text(xl-300,2600,'tầng 1: H = 5200',fontsize=9,rotation=90,ha='right',va='center')
    ax.annotate('',xy=(xl-250,5200),xytext=(xl-250,9100),arrowprops=dict(arrowstyle='<|-|>',lw=LW_DIM,color='k',mutation_scale=7,shrinkA=0,shrinkB=0))
    ax.text(xl-300,7150,'tầng 2: H = 3900',fontsize=9,rotation=90,ha='right',va='center')
    # kích thước phải: các vùng đai (ngoặc nhọn phải)
    def zone(y0,y1,lab,xr=1150,w=70):
        brace_left(ax,xr+w,y0,y1,w) if False else None
        ym=(y0+y1)/2
        # ngoặc phải: vẽ bằng ngoặc trái lật
        t=np.linspace(0,1,30); h=y1-y0
        def bez(p0,p1,p2,p3): return [(1-s)**3*np.array(p0)+3*(1-s)**2*s*np.array(p1)+3*(1-s)*s**2*np.array(p2)+s**3*np.array(p3) for s in t]
        up=bez((xr,y1),(xr,y1-h*0.12),(xr,ym+h*0.12),(xr+w,ym)); dn=bez((xr+w,ym),(xr,ym-h*0.12),(xr,y0+h*0.12),(xr,y0))
        p=np.array(up+dn); ax.plot(p[:,0],p[:,1],color='k',lw=0.8)
        ax.text(xr+w+40,ym,lab,fontsize=9,ha='left',va='center',family=SER)
    zone(0,750,'Ø8a150 (5 đai) — đầu cột 750')
    zone(750,3750,'Ø8a200 (15 đai)')
    zone(3750,4500,'Ø8a150 (5 đai) — đầu cột 750')
    zone(4500,5200,'Ø8a150 trong nút (4 đai, không cắt)')
    zone(5200,6350,'Ø8a150 trên đoạn nối 1150 (8 đai)')
    zone(6350,7800,'Ø8a200 (7 đai)')
    zone(7800,8400,'Ø8a150 (4 đai) — đầu cột 600')
    zone(-700,0,'Trong móng: 3 đai Ø8',xr=1560,w=60)
    # chú thích thép
    ldr(ax,-2050,-300,'Thép chờ L: chân 200,\nr ≥ 8d',(-120,-640),fs=9,va='top')
    ldr(ax,-2150,6050,'Thép tầng 1: 2Ø25+1Ø22\n(mỗi phía) + 1Ø16 cạnh dài',(60,5600),fs=9)
    ldr(ax,-2150,6950,'Thép tầng 2 bắt đầu ở mặt sàn,\nnối chồng 1150 với thép tầng 1',(110,6000),fs=9)
    dimv(ax,5200,6350,-170,'1150',ext=None,arr=True,toff=60) if False else None
    ax.annotate('',xy=(660,5200),xytext=(660,6350),arrowprops=dict(arrowstyle='<|-|>',lw=LW_DIM,color='k',mutation_scale=7,shrinkA=0,shrinkB=0)) if False else None
    ax.text(300,-880,'Hình vẽ không đúng tỉ lệ (chiều cao thu nhỏ)',fontsize=8.5,ha='center',va='top',family=SER,style='italic')
    save(fig,'out/hlay_col.png',dpi=190)
if __name__=='__main__': column()

# ---------------------------------------------------------------- Vùng tới hạn (kháng chấn, DCM) – minh hoạ nút biên
def critical():
    fig,ax=new(7.4,5.4,(-1500,5200),(-300,5100)); ax.set_aspect('auto')
    cw=600; yb0,yb1=2000,2700
    # cột
    for x in (0,cw): line(ax,[(x,-100),(x,4800)],lw=LW_CON)
    zig_v(ax,-70,cw+70,-100,45); zig_v(ax,-70,cw+70,4800,45)
    # dầm
    line(ax,[(cw,yb0),(4600,yb0)],lw=LW_CON+0.2); line(ax,[(cw,yb1),(4600,yb1)],lw=LW_CON+0.2)
    zig_h(ax,yb0,yb1,4600,40)
    # vùng tới hạn: tô nhạt
    from matplotlib.patches import Rectangle
    for (x,y,w,h) in ((0,yb0-750,cw,750),(0,yb1,cw,750),(cw,yb0,700,yb1-yb0)):
        ax.add_patch(Rectangle((x,y),w,h,fc='#d9d9d9',ec='none',zorder=0.5))
    ax.add_patch(Rectangle((0,yb0),cw,yb1-yb0,fc='#bdbdbd',ec='none',zorder=0.6))
    # đai cột dày a100
    def sc(y,lw=1.1): line(ax,[(15,y),(cw-15,y)],lw=lw,z=3)
    for y in range(yb0-50,yb0-750-1,-100): sc(y)
    for y in range(yb0+50,yb1,100): sc(y)
    for y in range(yb1+50,yb1+750,100): sc(y)
    for y in range(yb0-850,yb0-1650,-200): sc(y,0.8)
    for y in range(yb1+850,yb1+1650,200): sc(y,0.8)
    # đai dầm a150 trong 700 từ mép cột
    def sb(x,lw=1.1): line(ax,[(x,yb0+20),(x,yb1-20)],lw=lw,z=3)
    for x in [cw+50+150*k for k in range(5)]: sb(x)
    for x in range(1450,4400,250): sb(x,0.8)
    # thép dọc
    for x in (60,cw-60): line(ax,[(x,-60),(x,4760)],lw=2.6,z=4)
    line(ax,[(cw,yb1-60),(4600,yb1-60)],lw=2.8,z=4); line(ax,[(cw,yb0+60),(4600,yb0+60)],lw=2.8,z=4)
    # kích thước
    dimh(ax,cw,cw+700,yb1+260,'l$_{cr}$ = h$_w$ = 700',ext=yb1,arr=True,toff=14,fs=9)
    ax.text(cw+850,yb1+190,'đai Ø8a150 ≤ min(h$_w$/4; 24d$_{bw}$; 225; 8d$_{bL}$) = 175',fontsize=9,family=SER,va='bottom')
    dimv(ax,yb1,yb1+750,-250,'',ext=0,arr=True)
    ax.text(-300,yb1+375,'l$_{cr}$ = max(h$_c$; l$_{cl}$/6; 450) = 750',fontsize=9,ha='right',va='center',family=SER)
    dimv(ax,yb0-750,yb0,-250,'',ext=0,arr=True)
    ax.text(-300,yb0-375,'l$_{cr}$ = 750',fontsize=9,ha='right',va='center',family=SER)
    ax.text(-300,yb0-375-250,'Ø8a100',fontsize=9,ha='right',va='center',family=SER)
    ax.text(-300,yb1+375-260,'Ø8a100 ≤ min(b$_0$/2; 175; 8d$_{bL}$) = 101',fontsize=9,ha='right',va='center',family=SER)
    ax.text(-300,(yb0+yb1)/2,'Nút biên: Ø8a100 (như vùng tới hạn cột)\nđai không cắt; nút 4 dầm: ≤ 150',fontsize=9,ha='right',va='center',family=SER)
    ax.text(cw+150,yb0-150,'1) Vùng tô xám = vùng tới hạn (vùng dẻo); vùng tô đậm = nút khung',fontsize=9,ha='left',va='top',family=SER)
    ax.text(cw+150,yb0-330,'2) Ngoài vùng tới hạn: cột Ø8a200 (≤ min(12d$_{bL}$; b/2; 300) = 192 theo thực hành); dầm Ø8a250',fontsize=8.5,ha='left',va='top',family=SER) if False else None
    ldr(ax,1900,1200,'Ngoài vùng tới hạn: cột Ø8a200, dầm Ø8a250\n(≤ 0,75d = 484 và theo tính toán cắt)',(300,yb0-1050),fs=9,va='top')
    save(fig,'out/hlay_crit.png',dpi=190)
if __name__=='__main__': critical()
