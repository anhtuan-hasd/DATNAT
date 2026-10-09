from jt import *
def beamF(ax,ox,xb0,xb1,F_x,a=True,hs_ext=True):
    xl,xr=ox+187-187,ox+678-187
    pass
def f51():
    fig,ax=new(10.6,3.6,(60,1640),(-600,-30))
    def beam(x0,x1,ytop,yslab,ybot,notch=None):
        # biên ngoài
        L(ax,[(x0,ytop),(x1,ytop)],lw=0.7) 
        L(ax,[(x0,yslab),(x1,yslab)],lw=LW_CON) if notch is None else None
        L(ax,[(x0,ybot)]+[(x1,ybot)],lw=0.7)
        L(ax,[(x0,ytop),(x0,288),(x0-22,295),(x0+3,300),(x0,ybot)] if False else [(x0,yslab),(x0,285),(x0-22,295),(x0,300),(x0,ybot+22)],lw=LW_CON)
        L(ax,[(x1,yslab),(x1,285),(x1+22,295),(x1,300),(x1,ybot+22)],lw=LW_CON)
        L(ax,[(x0,ybot),(x0,ybot+22)],lw=LW_CON); L(ax,[(x1,ybot),(x1,ybot+22)],lw=LW_CON)
    # ---- a)
    x0,x1=187,678; yt,ys,yb=130,160,438
    L(ax,[(160,yt),(680,yt)],lw=0.6)
    L(ax,[(x0,ys),(385,ys),(385,277),(468,277),(468,ys),(x1,ys)],lw=LW_CON)
    L(ax,[(x0,ys),(x0,285),(x0-22,295),(x0,300),(x0,yb+22)],lw=LW_CON)
    L(ax,[(x1,ys),(x1,285),(x1+22,295),(x1,300),(x1,yb+22)],lw=LW_CON)
    L(ax,[(x0,yb),(x1,yb)],lw=0.7); L(ax,[(x0,yb-12),(x1,yb-12)],lw=1.2)
    L(ax,[(x0,yb-18),(x1,yb-18)],lw=0.7)
    L(ax,[(385,277),(385,296),(468,296),(468,277)],lw=0.8)
    L(ax,[(385,277),(468,277)],lw=0.8,ls=(0,(6,3)))
    L(ax,[(385,277),(240,yb-20)],lw=0.8,ls=(0,(10,6))); L(ax,[(468,277),(608,yb-20)],lw=0.8,ls=(0,(10,6)))
    ax.annotate('',xy=(427,Y(277)),xytext=(427,Y(100)),arrowprops=dict(arrowstyle='-|>',lw=2.2,color='k',mutation_scale=14,shrinkA=0,shrinkB=0),zorder=6)
    T(ax,442,160,'F',fs=14,ha='left')
    ax.add_patch(Circle((427,Y(277)),2.6,fc='k',zorder=7))
    L(ax,[(428,278),(497,262)],lw=0.7); T(ax,500,248,'Trọng tâm đặt F',fs=FS-1.5)
    # 45°
    t=np.linspace(np.pi,np.pi*0.75,12)
    ax.plot(305+0*t+ 36*np.cos(np.linspace(0,np.pi/4,12)),Y(yb-20)+36*np.sin(np.linspace(0,np.pi/4,12)),color='k',lw=0.7) if False else None
    cxa=300; arc=np.linspace(0,np.deg2rad(45),12); ax.plot(cxa+55*np.cos(arc),Y(yb-20)+55*np.sin(arc),color='k',lw=0.7)
    ax.text(290,Y(yb-48),'45$^o$',fontsize=FS+2,rotation=-60,ha='center',va='center')
    # kích thước chiều cao
    dv(ax,yt,yb,95,'',ext=None); L(ax,[(75,yt),(160,yt)],lw=0.6); L(ax,[(75,yb),(160,yb)],lw=0.6)
    ax.text(70,Y(285),'h',fontsize=FS+2,rotation=90,ha='center',va='center')
    dv(ax,277,yb-12,748,'',ext=None); L(ax,[(695,277),(755,277)],lw=0.6); L(ax,[(695,yb-12),(755,yb-12)],lw=0.6) if False else L(ax,[(695,yb-12),(755,yb-12)],lw=0.6)
    ax.text(722,Y(348),r'$h_s$',fontsize=FS+2,rotation=90,ha='center',va='center')
    dv(ax,yt,yb-12,818,'',ext=None); L(ax,[(695,yt),(825,yt)],lw=0.6); L(ax,[(695,yb-12),(825,yb-12)],lw=0.6)
    ax.text(795,Y(268),r'$h_o$',fontsize=FS+2,rotation=90,ha='center',va='center')
    for xa,xb,txt in ((240,385,r'$h_s$'),(385,468,'b'),(468,608,r'$h_s$')):
        dh(ax,xa,xb,520,txt,ext=None,off=-3,fs=FS+2)
    for xx in (240,385,468,608): L(ax,[(xx,500),(xx,528)],lw=0.6)
    T(ax,427,556,'Phạm vi bố trí cốt treo',fs=FS-1.5,ha='center')
    T(ax,100,45,'a)',fs=13)
    # ---- b)
    x0,x1=1005,1495; 
    L(ax,[(910,yt),(1500,yt)],lw=0.6)
    L(ax,[(x0,ys),(1200,ys),(1200,yb),(1288,yb),(1288,ys),(x1,ys)],lw=LW_CON)
    L(ax,[(x0,ys),(x0,285),(x0-22,295),(x0,300),(x0,yb+22)],lw=LW_CON)
    L(ax,[(x1,ys),(x1,285),(x1+22,295),(x1,300),(x1,yb+22)],lw=LW_CON)
    L(ax,[(x0,yb),(x1,yb)],lw=0.7); L(ax,[(x0,yb-12),(x1,yb-12)],lw=1.2) if False else None
    L(ax,[(x0,yb-14),(x1,yb-14)],lw=0.7)
    ax.annotate('',xy=(1243,Y(yb-14)),xytext=(1243,Y(262)),arrowprops=dict(arrowstyle='-|>',lw=2.2,color='k',mutation_scale=14,shrinkA=0,shrinkB=0),zorder=6)
    T(ax,1243,240,'F',fs=14,ha='center')
    L(ax,[(1245,yb-14),(1320,yb-36)],lw=0.7); T(ax,1325,yb-40,'Trọng tâm đặt F',fs=FS-1.5)
    dv(ax,yt,yb,918,'',ext=None); L(ax,[(895,yt),(1005,yt)],lw=0.6) if False else None
    L(ax,[(905,yb),(1005,yb)],lw=0.6)
    ax.text(893,Y(285),'h',fontsize=FS+2,rotation=90,ha='center',va='center')
    dv(ax,yt,yb-14,1590,'',ext=None); L(ax,[(1500,yt),(1600,yt)],lw=0.6); L(ax,[(1500,yb-14),(1600,yb-14)],lw=0.6) if False else L(ax,[(1500,yb-14),(1600,yb-14)],lw=0.6)
    ax.text(1565,Y(285),'h',fontsize=FS+2,rotation=90,ha='center',va='center')
    for xa,xb in ((1117,1200),(1200,1288),(1288,1372)):
        dh(ax,xa,xb,520,'b',ext=None,off=-3,fs=FS+2)
    for xx in (1117,1200,1288,1372): L(ax,[(xx,500),(xx,528)],lw=0.6)
    T(ax,1245,556,'Phạm vi bố trí cốt treo',fs=FS-1.5,ha='center')
    T(ax,920,45,'b)',fs=13)
    save(fig,'out/h51.png')
def f52():
    fig,ax=new(10.4,3.9,(60,1500),(-600,-80))
    # trái: dầm chính nhìn từ bên
    x0,x1,yt,yb=105,635,215,488
    L(ax,[(x0,yt),(x1,yt)],lw=LW_CON); L(ax,[(x0,yb),(x1,yb)],lw=LW_CON)
    L(ax,[(x0,yt),(x0,330),(x0+12,345),(x0-12,355),(x0,yb)],lw=LW_CON) if False else None
    L(ax,[(x0,yt),(x0,340),(x0+14,352),(x0,360),(x0,yb)],lw=LW_CON)
    L(ax,[(x1,yt),(x1,340),(x1-14,352),(x1,360),(x1,yb)],lw=LW_CON)
    ax.add_patch(Rectangle((320,Y(398)),90,398-220,fc='none',ec='k',lw=LW_CON,zorder=3))
    # gạch chéo
    for k in range(-6,9):
        xa=320+k*20; 
        pts=[(xa,398),(xa+ (398-220),220)]
        # cắt theo hình chữ nhật
        import numpy as np
        (xa0,ya0),(xa1,ya1)=pts
        t0=max(0,(320-xa0)/(xa1-xa0)); t1=min(1,(410-xa0)/(xa1-xa0))
        if t1>t0: L(ax,[(xa0+(xa1-xa0)*t0,ya0+(ya1-ya0)*t0),(xa0+(xa1-xa0)*t1,ya0+(ya1-ya0)*t1)],lw=0.7)
    # mặt cắt 1-1 ký hiệu
    for xs in (128,598):
        ax.annotate('',xy=(xs,Y(205)),xytext=(xs,Y(140)),arrowprops=dict(arrowstyle='-|>',lw=0.9,color='k',mutation_scale=9,shrinkA=0,shrinkB=0))
        L(ax,[(xs-18,205),(xs+18,205)],lw=2.0); T(ax,xs-26,135,'1',fs=FS+1,ha='right')
    T(ax,612,135,'1',fs=FS+1,ha='left') if False else None
    dv(ax,yt,398,722,'',ext=None); L(ax,[(640,yt),(730,yt)],lw=0.6); L(ax,[(412,398),(730,398)],lw=0.6)
    ax.text(702,Y(305),'h',fontsize=FS+2,rotation=90,ha='center',va='center')
    dh(ax,320,410,535,'b',ext=None,off=-3,fs=FS+2)
    for xx in (320,410): L(ax,[(xx,500),(xx,543)],lw=0.6)
    # chú thích 1, 2
    L(ax,[(412,372),(470,520),(540,520)],lw=0.7); T(ax,482,512,'2',fs=FS+1,ha='left',va='bottom')
    ax.annotate('',xy=(235,Y(yb+2)),xytext=(185,Y(560)),arrowprops=dict(arrowstyle='-|>',lw=0.8,color='k',mutation_scale=8,shrinkA=0,shrinkB=0)) if False else None
    ax.annotate('',xy=(190,Y(yb+2)),xytext=(232,Y(562)),arrowprops=dict(arrowstyle='-|>',lw=0.8,color='k',mutation_scale=8,shrinkA=0,shrinkB=0))
    L(ax,[(232,562),(290,562)],lw=0.7); T(ax,200,548,'1',fs=FS+1,ha='right')
    # phải: mặt cắt 1-1 (nhìn bằng)
    X0,X1=800,1355; 
    T(ax,1080,115,'1-1',fs=FS+2,ha='center'); L(ax,[(1055,125),(1105,125)],lw=0.9)
    for y in (245,375): L(ax,[(X0+10,y),(X1-10,y)],lw=2.0,z=4)
    L(ax,[(X0+10,238),(X1-10,238)],lw=0.7); L(ax,[(X0+10,382),(X1-10,382)],lw=0.7)
    L(ax,[(X0+10,238),(X0+10,238)],lw=0.5)
    L(ax,[(X0,238),(X0,295),(X0+14,305),(X0-8,315),(X0,380)],lw=LW_CON) if False else None
    for xs in (810,1345): pass
    L(ax,[(X0,240),(X0,300),(X0+14,310),(X0-8,320),(X0,385)],lw=LW_CON) if False else None
    xs=[930,968,1000,1038,1068,1105,1138,1190,1232]
    for x in xs: L(ax,[(x,236),(x,388)],lw=2.4,z=4)
    L(ax,[(1035,388),(1035,545)],lw=LW_CON); L(ax,[(1128,388),(1128,545)],lw=LW_CON)
    L(ax,[(1050,388),(1050,520)],lw=1.6); L(ax,[(1100,388),(1100,520)],lw=1.6)
    L(ax,[(1040,525),(1052,540),(1076,520),(1088,540),(1128,525)],lw=LW_CON) if False else None
    for y in (447,490): L(ax,[(1050,y),(1100,y)],lw=2.4,z=4)
    # biên dầm chính
    L(ax,[(X0,238),(X1,238)],lw=0.5)
    L(ax,[(X0+4,232),(X1-4,232)],lw=0.5) if False else None
    L(ax,[(X0,236),(X0,262)],lw=0.5) if False else None
    # kích thước
    L(ax,[(1128,447),(1166,447)],lw=0.6); L(ax,[(1128,388),(1166,388)],lw=0.6) if False else None
    dv(ax,388,447,1160,'',ext=None); ax.text(1190,Y(417),'h/3',fontsize=FS-0.5,rotation=90,ha='center',va='center')
    dh(ax,893,1268,585,'b+2h',ext=None,off=-4,fs=FS+1)
    for xx in (893,1268): L(ax,[(xx,235),(xx,592)],lw=0.5)
    ax.annotate('',xy=(1075,Y(470)),xytext=(1060,Y(172)),arrowprops=dict(arrowstyle='-|>',lw=0.7,color='k',mutation_scale=8,shrinkA=0,shrinkB=0)) if False else None
    ax.annotate('',xy=(968,Y(330)),xytext=(1022,Y(188)),arrowprops=dict(arrowstyle='-|>',lw=0.7,color='k',mutation_scale=8,shrinkA=0,shrinkB=0))
    ax.annotate('',xy=(1078,Y(470)),xytext=(1022,Y(188)),arrowprops=dict(arrowstyle='-|>',lw=0.7,color='k',mutation_scale=8,shrinkA=0,shrinkB=0))
    L(ax,[(1010,188),(1070,188)],lw=0.7); T(ax,1030,170,'3',fs=FS+1,ha='center')
    save(fig,'out/h52.png')
if __name__=='__main__': f51(); f52()
