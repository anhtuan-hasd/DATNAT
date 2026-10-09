from dr import *
# ---------- Hình 5.4: bố trí thép dọc trên tiết diện dầm ----------
def beam_section():
    fig,ax=new(8.2,4.6,(-60,860),(-120,720))
    b,h=250,700; X0=120
    # bê tông
    poly(ax,[(X0,0),(X0+b,0),(X0+b,h),(X0,h)],lw=1.0)
    c=20; d=22; r=10
    # đai
    stirrup(ax,X0+c,c,X0+b-c,h-c,r=12,lw=1.2)
    xs=np.linspace(X0+c+d/2+6,X0+b-c-d/2-6,5)
    ytop=h-c-8-d/2; 
    for x in xs: dot(ax,x,ytop,d)
    ybot1=c+8+d/2; ybot2=ybot1+d+25*0+30
    ybot2=ybot1+d+12
    for x in xs: dot(ax,x,ybot1,d); dot(ax,x,ybot2,d)
    # cốt giá cạnh bên (S<=400)
    yS1=h-c-8-d/2-380; yS2=yS1-380 if False else None
    ys=[ytop-0.55*(ytop-ybot2), ytop-0.55*(ytop-ybot2)-250]
    ys=[ytop-290, ytop-290-290]
    ys=[ytop-300, ytop-600+0]
    ys=[h-c-8-d/2-290, h-c-8-d/2-290-310]
    for y in ys:
        dot(ax,xs[0],y,d*0.7); dot(ax,xs[-1],y,d*0.7)
    # đường dẫn "cốt dọc cấu tạo khi h>=700"
    ym=ys[0]
    line(ax,[(xs[0],ys[0]),((X0+b/2),ys[0]+130),(xs[-1],ys[0])],lw=0.6)
    line(ax,[(X0+b/2,ys[0]+130),(X0+b+260,ys[0]+130)],lw=0.6)
    text(ax,X0+b+200,ys[0]+185,'Cốt dọc cấu tạo khi h ≥700',fs=9)
    text(ax,X0+b+270,ys[0]+75,r'$A_{S\ ct}\geq0.1\%\,(0.5bS)$',fs=9)
    # kích thước h
    dimv_rot(ax,0,h,X0-80,'h',ext=X0,fs=11)
    # S<=400
    xd=X0-45
    dimv(ax,ytop,ys[0],xd,'S≤400',ext=X0,side='left',fs=9,toff=18)
    dimv(ax,ys[0],ys[1],xd,'S≤400',ext=X0,side='left',fs=9,toff=18)
    # t0 >=(30,dmax) phía trên: giữa hai thanh trên
    yy=h+45
    dimh(ax,xs[0]+d/2,xs[1]-d/2,yy,'',ext=ytop+d/2)
    text(ax,xs[1]+10,h+100,r'$t_o\geq(30,d_{max})$',fs=9,ha='center')
    # t0 >= 50 (cốt thép từ 3 lớp)
    xd2=X0+b+45
    dimv(ax,ybot2,ys[1],xd2,'',ext=X0+b)
    text(ax,xd2+30,(ybot2+ys[1])/2,r'$t_o\geq50$',fs=9)
    # t0 hai lớp dưới
    dimv(ax,ybot1,ybot2,X0-45,'',ext=X0)
    text(ax,X0-60,(ybot1+ybot2)/2,r'$t_o$',fs=9,ha='right')
    # t0>=(25,dmax) đáy
    dimh(ax,xs[1]+d/2,xs[2]-d/2,-45,'',ext=ybot1-d/2)
    text(ax,xs[2]+10,-100,r'$t_o\geq(25,d_{max})$',fs=9,ha='center')
    # b
    dimh(ax,X0,X0+b,-130,'b',ext=0,tpos='below' if False else 'above',fs=11)
    return fig,ax
def beam_detail_right(ax,x0):
    pass
def fig54():
    fig,ax=new(10.5,4.9,(-80,1420),(-170,760))
    b,h=250,700; X0=110
    # --- phần trái
    def part_left(ax):
        poly(ax,[(X0,0),(X0+b,0),(X0+b,h),(X0,h)],lw=1.0)
        c=20; d=22
        stirrup(ax,X0+c,c,X0+b-c,h-c,r=14,lw=1.3)
        xs=np.linspace(X0+c+d/2+8,X0+b-c-d/2-8,5)
        ytop=h-c-10-d/2
        ybot1=c+10+d/2; ybot2=ybot1+d+10
        for x in xs: dot(ax,x,ytop,d); dot(ax,x,ybot1,d); dot(ax,x,ybot2,d)
        ys=[ytop-290, ytop-580]
        for y in ys: dot(ax,xs[0],y,d*0.75); dot(ax,xs[-1],y,d*0.75)
        # đường dẫn cốt cấu tạo
        line(ax,[(xs[0],ys[0]),(X0+b/2,ys[0]+120),(xs[-1],ys[0])],lw=0.6)
        line(ax,[(X0+b/2,ys[0]+120),(X0+b+330,ys[0]+120)],lw=0.6)
        text(ax,X0+b+200,ys[0]+170,'Cốt dọc cấu tạo khi h ≥700',fs=9.5,ha='left')
        text(ax,X0+b+250,ys[0]+75,r'$A_{S\ ct}\geq0.1\%\,(0.5bS)$',fs=9.5,ha='left')
        # h
        dimv_rot(ax,0,h,X0-85,'h',ext=X0,fs=11)
        # S<=400
        dimv(ax,ytop,ys[0],X0-35,'S≤400',ext=X0,side='left',fs=9,toff=14)
        dimv(ax,ys[0],ys[1],X0-35,'S≤400',ext=X0,side='left',fs=9,toff=14)
        # t0 trên
        dimh(ax,xs[0]+d/2+0,xs[1]-d/2,h+40,'',ext=ytop)
        text(ax,xs[1],h+85,r'$t_o\geq(30,\ d_{max})$',fs=9,ha='center')
        # t0>=50
        dimv(ax,ybot2,ys[1],X0+b+35,'',ext=X0+b)
        text(ax,X0+b+55,(ybot2+ys[1])/2,r'$t_o\geq50$',fs=9.5)
        dimv(ax,ybot1,ybot2,X0-35,'',ext=X0)
        text(ax,X0-45,(ybot1+ybot2)/2-0,r'$t_o$',fs=9.5,ha='right')
        dimh(ax,xs[2]+d/2,xs[3]-d/2,-40,'',ext=ybot1)
        text(ax,xs[3]+25,-95,r'$t_o\geq(25,\ d_{max})$',fs=9,ha='center')
        dimh(ax,X0,X0+b,-135,'b',ext=0,fs=11)
    part_left(ax)
    # --- phần phải trên: mặt cắt chữ U (hai lớp thép dưới, hở >=1.5dmax)
    XR=830; wR=250
    ytopR=520; ybotR=280
    line(ax,[(XR,ytopR),(XR,ybotR),(XR+wR,ybotR),(XR+wR,ytopR)],lw=1.0)
    zig_v(ax,XR+20,XR+wR-60,ytopR+3,25) if False else None
    line(ax,[(XR-20,ytopR),(XR+wR/2-40,ytopR)],lw=1.0); line(ax,[(XR+wR/2+40,ytopR),(XR+wR+20,ytopR)],lw=1.0)
    line(ax,[(XR+wR/2-40,ytopR),(XR+wR/2+10,ytopR+20),(XR+wR/2-10,ytopR-25),(XR+wR/2+40,ytopR)],lw=1.0) if False else None
    # dấu gãy xiên
    line(ax,[(XR+85,ytopR+25),(XR+150,ytopR-45),(XR+120,ytopR-10)],lw=0.0)
    line(ax,[(XR+90,ytopR+20),(XR+120,ytopR-10),(XR+105,ytopR-10),(XR+135,ytopR-45)],lw=1.0)
    stirrup(ax,XR+22,ybotR+22,XR+wR-22,ytopR-20,r=14,lw=1.3,hook=False)
    line(ax,[(XR+22,ytopR-20),(XR+22,ybotR+22),(XR+wR-22,ybotR+22),(XR+wR-22,ytopR-20)],lw=1.3)
    d=22
    xs=np.linspace(XR+22+d/2+4,XR+wR-22-d/2-4,5)
    y1=ybotR+22+4+d/2; y2=y1+d
    for x in xs: dot(ax,x,y1,d); dot(ax,x,y2,d)
    yc=ytopR-120
    dot(ax,xs[0],yc+60,d); dot(ax,xs[-1],yc+60,d)
    dimv(ax,y1,ytopR-20-0,XR+wR+30,'',ext=XR+wR) if False else None
    dimv(ax,ybotR+80,ybotR+330,XR+wR+40,'',ext=XR+wR+0)
    text(ax,XR+wR+65,ybotR+205,r'$t_o\geq50$',fs=9.5)
    dimh(ax,xs[0]-0,xs[1]+0,ybotR-30-0,'',ext=ybotR)
    dimh(ax,XR+wR/2-25,XR+wR/2+25,ybotR-45,'',ext=y1-d/2) if False else None
    text(ax,XR+wR/2,ybotR-115,r'$t_o\geq1.5d_{max}$',fs=9.5,ha='center')
    dimh(ax,xs[2]-d/2-0,xs[3]-d/2+0,ybotR-30,'',ext=y1-d/2) 
    # --- phần phải dưới: lớp bảo vệ C>=(20,dmax)
    XC=830; YC=60
    line(ax,[(XC,YC+210),(XC,YC),(XC+140,YC)] if False else [(XC,YC+210),(XC,YC-20)],lw=1.0)
    line(ax,[(XC-30,YC+210),(XC+60,YC+210)],lw=1.0)
    line(ax,[(XC+60,YC+210),(XC+80,YC+235),(XC+95,YC+195),(XC+125,YC+210)],lw=0.0)
    line(ax,[(XC+60,YC+210),(XC+85,YC+240)],lw=1.0); line(ax,[(XC+85,YC+240),(XC+95,YC+205)],lw=1.0); line(ax,[(XC+95,YC+205),(XC+125,YC+240)],lw=1.0) if False else None
    line(ax,[(XC+110,YC+210),(XC+180,YC+210)],lw=1.0)
    line(ax,[(XC+180,YC+210),(XC+180,YC-20)],lw=1.0)
    # thép + đai góc
    line(ax,rrpath([(XC+25,YC+210),(XC+25,YC+35),(XC+170,YC+35)],18),lw=1.0)
    line(ax,rrpath([(XC+35,YC+210),(XC+35,YC+45),(XC+170,YC+45)],14),lw=1.0)
    dot(ax,XC+65,YC+85,50)
    dimv(ax,YC+35,YC-5+0,XC+230,'',ext=XC+180) if False else None
    dimv(ax,YC+20,YC+75,XC+235,'',ext=XC+180)
    text(ax,XC+255,YC+48,r'$C\geq(20,\ d_{max})$',fs=9.5)
    dimh(ax,XC-0,XC+25,YC-40,'',ext=YC+10) if False else None
    text(ax,XC-10,YC-70,'C',fs=10,ha='center')
    text(ax,XC-20,-148,r'$d_{max}$: đường kính thanh cốt dọc lớn nhất',fs=9.5,family=None) if False else text(ax,XC-20,-148,r'$d_{max}$ : đường kính thanh cốt dọc lớn nhất',fs=9.5)
    return fig
fig=fig54(); save(fig,'/home/claude/redraw/out/h54_beam_section.png')
