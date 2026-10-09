from jt import *
from matplotlib.patches import Ellipse
def circ(ax,x,y,d,fill=False,lw=0.9):
    ax.add_patch(Circle((x,Y(y)),d/2,fc='k' if fill else 'white',ec='k',lw=lw,zorder=6))
def capsule(ax,x,y,w=16,h=9,vertical=False):
    from matplotlib.patches import FancyBboxPatch
    if vertical: w,h=h,w
    ax.add_patch(FancyBboxPatch((x-w/2+h/2,Y(y)-h/2),w-h,h,boxstyle=f'round,pad=0,rounding_size={h/2}',fc='white',ec='k',lw=0.9,zorder=6,mutation_aspect=1)) if False else None
    ax.add_patch(Ellipse((x,Y(y)),w,h,fc='white',ec='k',lw=0.9,zorder=6))
    ax.add_patch(Ellipse((x-(w-h)/2*(0 if vertical else 1),Y(y)+( (w-h)/2*0 if not vertical else -(h-w)/2*0)),h*0.55,h*0.55,fc='k',ec='k',zorder=7)) if False else None
    if vertical: ax.add_patch(Circle((x,Y(y)+ (h-w)/2),w*0.28,fc='k',ec='k',zorder=7))
    else: ax.add_patch(Circle((x-(w-h)/2,Y(y)),h*0.28,fc='k',ec='k',zorder=7))
def sec_small(ax,x0,y0,W,H,bars,mark=False,lbl=None,ly=None,c=9,stir_r=6,dd=9):
    ax.add_patch(Rectangle((x0,Y(y0+H)),W,H,fc='none',ec='k',lw=LW_CON,zorder=2))
    stirrup(ax,x0+c,Y(y0+H)+c,x0+W-c,Y(y0)-c,r=stir_r,lw=1.6,hk=7)
    for (fx,fy,k) in bars:
        bx=x0+c+dd/2+1+fx*(W-2*c-dd-2); by=Y(y0+H)+c+dd/2+1+fy*(H-2*c-dd-2)
        if k=='c': circ(ax,bx,-by,dd,fill=False)
        else: circ(ax,bx,-by,dd,fill=False)
    if lbl:
        T(ax,x0+W/2,ly,lbl,ha='center',va='top')
def col_a():
    fig,ax=new(8.2,7.6,(60,1330),(-1000,-30))
    x0,x1=612,738; ytop,ybot=55,630; st,sb=482,540
    L(ax,[(x0,ytop),(x0,st)],lw=LW_CON); L(ax,[(x1,ytop),(x1,st)],lw=LW_CON)
    L(ax,[(x0,sb),(x0,ybot)],lw=LW_CON); L(ax,[(x1,sb),(x1,ybot)],lw=LW_CON)
    L(ax,[(x0-30,ytop),(x0+45,ytop),(x0+68,ytop-35),(x0+90,ytop),(x1+30,ytop)],lw=LW_CON)
    L(ax,[(x0-30,ybot),(x0+45,ybot),(x0+68,ybot+35),(x0+90,ybot),(x1+30,ybot)],lw=LW_CON)
    # sàn
    L(ax,[(470,st),(x0,st)],lw=LW_CON); L(ax,[(x1,st),(915,st)],lw=LW_CON)
    L(ax,[(470,sb),(x0,sb)],lw=LW_CON); L(ax,[(x1,sb),(915,sb)],lw=LW_CON)
    L(ax,[(470,st),(470,st+12),(440,st+30),(470,st+40),(440,sb)],lw=LW_CON) if False else None
    for xe,sg in ((440,-1),(915,1)):
        L(ax,[(xe,st),(xe,st+14),(xe+sg*22,st+30),(xe-sg*8,st+42),(xe,sb)] if False else [(xe+ (sg*0),st),(xe,st+10),(xe+sg*26*-1+0,st+28),(xe+sg*0,st+42),(xe,sb)],lw=LW_CON)
    # chân đai + cốt dọc
    for x in (x0+13,x1-13): L(ax,[(x,ytop+10),(x,ybot-5)],lw=0.9)
    # cốt dọc trên (thu vào 50 ở đoạn 290-330)
    L(ax,[(x0+22,ytop+10),(x0+22,285),(x0+31,330),(x0+31,st-8)],lw=1.6,z=4)
    L(ax,[(x1-22,ytop+10),(x1-22,285),(x1-31,330),(x1-31,st-8)],lw=1.6,z=4)
    L(ax,[(675,ytop+10),(675,st-8)],lw=2.0,z=4)
    # cốt chờ phía dưới (nét đứt)
    for x in (x0+22,x1-22,675): L(ax,[(x,st-8),(x,ybot-8)],lw=1.2,ls=(0,(5,3)),z=4)
    # đai
    y=130
    while y<285:
        tie(ax,x0+13,x1-13,y,thick=True); y+=26
    # đai tại chỗ bẻ khuỷu (thu hẹp)
    tie(ax,x0+16,x1-16,298,thick=True); tie(ax,x0+22,x1-22,318,thick=True)
    y=362
    while y<st-4:
        tie(ax,x0+22,x1-22,y,thick=True); y+=9
    # kích thước 50
    for (ya,yb) in ((330,380),(440,482)):
        pass
    dv(ax,330,382,790,'',ext=None); dv(ax,436,482,790,'',ext=None)
    L(ax,[(728,330),(805,330)],lw=0.6); L(ax,[(728,382),(805,382)],lw=0.6); L(ax,[(728,436),(805,436)],lw=0.6); L(ax,[(728,482),(805,482)],lw=0.6)
    T(ax,775,356,'50',fs=FS-2,rot=90) if False else ax.text(776,Y(356),'50',fontsize=FS-2,rotation=90,ha='center',va='center')
    ax.text(776,Y(459),'50',fontsize=FS-2,rotation=90,ha='center',va='center')
    # chú thích
    ldr(ax,805,205,'Đặt cốt đai tại chỗ bẻ khuỷu',(722,285))
    T(ax,845,300,'Chiều dài đoạn bẻ khuỷu',serif=True,va='center'); T(ax,845,343,'bằng 10 lần đoạn thu vào',serif=True); T(ax,845,386,'(i=1:10)',serif=True)
    L(ax,[(738,322),(1160,322)],lw=0.7)
    # cao độ sàn
    h=9
    ax.add_patch(Polygon([(960-h,Y(st-1.6*h)),(960+h,Y(st-1.6*h)),(960,Y(st))],closed=True,fc='white',ec='k',lw=0.8,zorder=6))
    L(ax,[(950,st),(1035,st)],lw=0.8); T(ax,960,st-23,'Cao độ sàn',serif=True,va='bottom') if False else T(ax,1000,st-24,'Cao độ sàn',serif=True,ha='center',va='bottom')
    # Lan và nhãn
    lan_v(ax,550,362,475,ext_to=x0-4,xt=545)
    T(ax,578,415,'1',fs=FS+1); L(ax,[(572,430),(590,430)],lw=0.8)
    T(ax,774,415,'1',fs=FS+1); L(ax,[(768,430),(786,430)],lw=0.8)
    spacing(ax,170,205,l1='≤ 500',l2='≤ 15Ø',bigbrace=(570,85,360),dy=22)
    spacing(ax,60,405,l1='≤ 300',l2='≤ 10Ø',dy=22)
    # mặt cắt 1-1
    X0,Y0,W,H=612,688,128,84
    ax.add_patch(Rectangle((X0,Y(Y0+H)),W,H,fc='none',ec='k',lw=LW_CON))
    stirrup(ax,X0+10,Y(Y0+H)+10,X0+W-10,Y(Y0)-10,r=6,lw=1.8,hk=8)
    for fx in (0,1):
        for fy in (0,1): circ(ax,X0+17+fx*(W-34),-(Y(Y0+H)+17+fy*(H-34)),11,fill=True)
    for fx,fy,vert in ((0.5,1,True),(0.5,0,True),(0,0.5,False),(1,0.5,False)):
        capsule(ax,X0+17+fx*(W-34),-(Y(Y0+H)+17+fy*(H-34)),w=17,h=10,vertical=vert)
    capsule(ax,792,Y0+8+H/2-8,w=17,h=10)
    T(ax,815,Y0+H/2-8,'Ký hiệu hướng bẻ khuỷu cốt thép dọc',serif=True)
    T(ax,X0+W/2,Y0+H+25,'1-1',ha='center',serif=False); L(ax,[(X0+W/2-18,Y0+H+34),(X0+W/2+18,Y0+H+34)],lw=0.8)
    T(ax,X0-50,60,'a)',fs=13) if False else T(ax,420,62,'a)',fs=13)
    save(fig,'out/h511a.png')
def col_b():
    fig,ax=new(8.2,9.4,(60,1330),(-1130,-30))
    u0,u1=630,740; l0,l1=598,780; ytop=60; st,sb=420,465; ybot=620
    L(ax,[(u0,ytop),(u0,st)],lw=LW_CON); L(ax,[(u1,ytop),(u1,st)],lw=LW_CON)
    L(ax,[(l0,sb),(l0,ybot)],lw=LW_CON); L(ax,[(l1,sb),(l1,ybot)],lw=LW_CON)
    L(ax,[(u0-30,ytop),(u0+40,ytop),(u0+62,ytop-32),(u0+82,ytop),(u1+30,ytop)],lw=LW_CON)
    L(ax,[(l0-30,ybot),(l0+55,ybot),(l0+78,ybot+35),(l0+100,ybot),(l1+30,ybot)],lw=LW_CON)
    L(ax,[(470,st),(u0,st)],lw=LW_CON); L(ax,[(u1,st),(915,st)],lw=LW_CON)
    L(ax,[(470,sb),(l0,sb)],lw=LW_CON); L(ax,[(l1,sb),(915,sb)],lw=LW_CON)
    for xe,sg in ((470,-1),(915,1)):
        L(ax,[(xe,st),(xe,st+10),(xe+sg*22*-1,st+22),(xe,st+32),(xe,sb)],lw=LW_CON)
    for x in (u0+10,u1-10): L(ax,[(x,ytop+8),(x,st)],lw=0.9)
    for x in (l0+10,l1-10): L(ax,[(x,sb),(x,ybot-5)],lw=0.9)
    # cốt cột trên đi xuống qua sàn, neo Lan
    for x in (u0+22,u1-22): L(ax,[(x,ytop+8),(x,535)],lw=1.6,z=4)
    L(ax,[(u0+36,300),(u0+36,535)],lw=1.4,z=4) if False else None
    # cốt cột dưới bẻ vào sàn (nét đứt trên đỉnh sàn)
    B(ax,[(l0+14,ybot-5),(l0+14,st+5),(l0+54,st+5)],r=14,lw=1.8)
    B(ax,[(l1-14,ybot-5),(l1-14,st+5),(l1-54,st+5)],r=14,lw=1.8)
    L(ax,[(l0+54,st+5),(l1-54,st+5)],lw=1.3,ls=(0,(5,3)),z=4)
    # đai
    y=100
    while y<270: tie(ax,u0+10,u1-10,y,thick=True); y+=24
    y=295
    while y<st-6: tie(ax,u0+10,u1-10,y,thick=True); y+=10
    for y in (470,495,520,545,570): tie(ax,l0+10,l1-10,y,thick=True)
    # nhãn
    ldr(ax,865,305,'Nên neo vào sàn nếu mô men lớn',(775,st+4),ha='left') if False else None
    t=ax.text(870,Y(310),'Nên neo vào sàn nếu mô men lớn',fontsize=FS,family=SER,ha='left',va='bottom')
    L(ax,[(870,315),(1250,315)],lw=0.8); L(ax,[(870,315),(775,st+2)],lw=0.8)
    h=9
    ax.add_patch(Polygon([(1000-h,Y(st-1.6*h)),(1000+h,Y(st-1.6*h)),(1000,Y(st))],closed=True,fc='white',ec='k',lw=0.8,zorder=6))
    L(ax,[(950,st-1.6*h),(1035,st-1.6*h)],lw=0.8) if False else L(ax,[(945,st),(1060,st)],lw=0.8)
    T(ax,1000,st-26,'Mặt trên sàn',serif=True,ha='center',va='bottom')
    ax.add_patch(Polygon([(895-h,Y(sb+1.6*h)),(895+h,Y(sb+1.6*h)),(895,Y(sb))],closed=True,fc='white',ec='k',lw=0.8,zorder=6))
    L(ax,[(850,sb+1.6*h),(960,sb+1.6*h)],lw=0.8); T(ax,905,sb+1.6*h+10,'Mặt dưới sàn',serif=True,va='top')
    lan_v(ax,572,297,410,ext_to=u0-4,xt=568)
    dv(ax,410,535,1152,'',ext=None); L(ax,[(1090,410),(1160,410)],lw=0.7) if False else None
    L(ax,[(1090,410),(1160,410)],lw=0.7); L(ax,[(780,535),(1160,535)],lw=0.7)
    ax.text(1130,Y(473),'L$_{an}$',fontsize=FS,rotation=90,ha='center',va='center')
    T(ax,596,347,'1',fs=FS+1); L(ax,[(590,362),(608,362)],lw=0.8); T(ax,782,347,'1',fs=FS+1); L(ax,[(776,362),(794,362)],lw=0.8)
    T(ax,548,497,'2',fs=FS+1); L(ax,[(542,512),(560,512)],lw=0.8); T(ax,818,497,'2',fs=FS+1); L(ax,[(812,512),(830,512)],lw=0.8)
    spacing(ax,150,165,l1='≤ 500',l2='≤ 15Ø',bigbrace=(590,80,298),dy=22)
    spacing(ax,110,330,l1='≤ 300',l2='≤ 10Ø',dy=22)
    # 1-1
    X0,Y0,W,H=632,680,118,100
    ax.add_patch(Rectangle((X0-12,Y(Y0+H+12)),W+24,H+24,fc='none',ec='k',lw=LW_CON)) if False else None
    ax.add_patch(Rectangle((X0-15,Y(Y0+H+15)),W+30,H+30,fc='none',ec='k',lw=LW_CON))
    stirrup(ax,X0+3,Y(Y0+H)+3,X0+W-3,Y(Y0)-3,r=6,lw=1.8,hk=8)
    for fx in (0,1):
        for fy in (0,1): circ(ax,X0+14+fx*(W-28),-(Y(Y0+H)+14+fy*(H-28)),10,fill=False,lw=1.1)
    T(ax,X0+W/2,Y0+H+42,'1-1',ha='center'); L(ax,[(X0+W/2-18,Y0+H+51),(X0+W/2+18,Y0+H+51)],lw=0.8)
    # 2-2
    X0,Y0,W,H=602,900,175,125
    ax.add_patch(Rectangle((X0-12,Y(Y0+H+12)),W+24,H+24,fc='none',ec='k',lw=LW_CON))
    stirrup(ax,X0+2,Y(Y0+H)+2,X0+W-2,Y(Y0)-2,r=7,lw=2.0,hk=9)
    for fx in (0,1):
        for fy in (0,1): circ(ax,X0+13+fx*(W-26),-(Y(Y0+H)+13+fy*(H-26)),10,fill=False,lw=1.1)
    # đai cột trên (nét đứt, chiếu lên)
    ax.add_patch(Rectangle((X0+36,Y(Y0+H-8)),W-72,H-18,fc='none',ec='k',lw=1.2,ls=(0,(4,3)),zorder=4))
    for fx in (0,1):
        for fy in (0,1): circ(ax,X0+45+fx*(W-90),-(Y(Y0+H)+19+fy*(H-38)),9,fill=False,lw=1.0)
    ldr(ax,830,Y0+55,'Đai định vị',(X0+W-10,Y0+75),ha='left') if False else None
    T(ax,820,Y0+50,'Đai định vị',serif=True); T(ax,820,Y0+88,'Ít nhất 3 cái',serif=True)
    L(ax,[(812,Y0+66),(950,Y0+66)],lw=0.8); L(ax,[(812,Y0+66),(X0+W-4,Y0+82)],lw=0.8)
    T(ax,X0+W/2,Y0+H+45,'2-2',ha='center'); L(ax,[(X0+W/2-18,Y0+H+54),(X0+W/2+18,Y0+H+54)],lw=0.8)
    T(ax,440,62,'b)',fs=13)
    save(fig,'out/h511b.png')
if __name__=='__main__': col_a(); col_b()
