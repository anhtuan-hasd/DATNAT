from dr import *
def fig54():
    fig,ax=new(10.2,6.2,(-260,1330),(-340,880))
    b,h=250,800; X0=40; d=18
    # ---- mặt cắt dầm (trái), vẽ đúng tỉ lệ
    poly(ax,[(X0,0),(X0+b,0),(X0+b,h),(X0,h)],lw=1.0)
    stirrup(ax,X0+20,20,X0+b-20,h-20,r=14,lw=1.4,hk=22)
    xs=np.linspace(X0+20+8+d/2,X0+b-20-8-d/2,5)
    yt=h-20-8-d/2; yb1=20+8+d/2; yb2=yb1+d+25
    for x in xs:
        dot(ax,x,yt,d); dot(ax,x,yb1,d); dot(ax,x,yb2,d)
    s1=yt-300; s2=s1-300
    for y in (s1,s2):
        dot(ax,xs[0],y,d*0.8); dot(ax,xs[-1],y,d*0.8)
    # đường dẫn cốt cấu tạo
    xm=X0+b/2; ya=s1+120
    line(ax,[(xs[0],s1),(xm,ya),(xs[-1],s1)],lw=0.6)
    line(ax,[(xm,ya),(X0+b+300,ya)],lw=0.6)
    text(ax,X0+b+60,ya+55,'Cốt dọc cấu tạo khi h ≥700',fs=9.5)
    text(ax,X0+b+110,ya-50,r'$A_{S\ ct}\ \geq\ 0.1\%\,(0.5bS)$',fs=9.5)
    # h
    dimv_rot(ax,0,h,X0-215,'h',ext=X0,fs=11)
    # S ≤ 400
    dimv(ax,s1,yt,X0-45,'S≤ 400',ext=X0,fs=9.5,toff=10)
    dimv(ax,s2,s1,X0-45,'S≤ 400',ext=X0,fs=9.5,toff=10)
    # t0 ≥ 50 : giữa cốt cạnh bên cuối và lớp dưới
    dimv(ax,yb2,s2,X0+b+55,'',ext=X0+b)
    text(ax,X0+b+75,(yb2+s2)/2,r'$t_o\ \geq\ 50$',fs=9.5)
    # t0 hai lớp dưới
    dimv(ax,yb1,yb2,X0-45,'',ext=X0)
    text(ax,X0-60,(yb1+yb2)/2-6,r'$t_o$',fs=9.5,ha='right')
    # t0 ≥ (30,dmax) trên: khe giữa hai thanh
    dimh(ax,xs[1]+d/2,xs[2]-d/2,h+55,'',ext=yt+d/2)
    text(ax,xs[1]+(xs[2]-xs[1])/2,h+95,r'$t_o\ \geq\ (30,\ d_{max})$',fs=9.5,ha='center')
    # t0 ≥ (25,dmax) đáy
    dimh(ax,xs[1]+d/2,xs[2]-d/2,-55,'',ext=yb1-d/2)
    text(ax,xs[1]+(xs[2]-xs[1])/2+40,-125,r'$t_o\ \geq\ (25,\ d_{max})$',fs=9.5,ha='center')
    # b
    dimh(ax,X0,X0+b,-185,'',ext=0)
    text(ax,xm,-225,'b',fs=11,ha='center')
    # ---- chi tiết phải trên: tiết diện hình U (thép 2 lớp, khe 1.5 dmax)
    XR=640; wR=250
    top=600; bot=330
    line(ax,[(XR,top),(XR,bot),(XR+wR,bot),(XR+wR,top)],lw=1.0)
    line(ax,[(XR-35,top),(XR+78,top)],lw=1.0); line(ax,[(XR+150,top),(XR+wR+35,top)],lw=1.0)
    line(ax,[(XR+78,top),(XR+112,top+30),(XR+105,top-30),(XR+150,top)],lw=1.0) if False else None
    line(ax,[(XR+110,top+32),(XR+128,top+5),(XR+112,top+5),(XR+138,top-30)],lw=1.0)
    line(ax,[(XR+78,top),(XR+110,top+32)],lw=0) 
    # đai (3 cạnh) với bo tròn
    line(ax,rrpath([(XR+20,top-5),(XR+20,bot+20),(XR+wR-20,bot+20),(XR+wR-20,top-5)],12),lw=1.4)
    xr=np.linspace(XR+20+8+d/2,XR+wR-20-8-d/2,5)
    y1=bot+20+8+d/2; y2=y1+d+25
    for x in xr: dot(ax,x,y1,d); dot(ax,x,y2,d)
    ym=top-110
    dot(ax,xr[0],ym,d*0.8); dot(ax,xr[-1],ym,d*0.8)
    dimv(ax,y2,ym,XR+wR+55,'',ext=XR+wR)
    text(ax,XR+wR+75,(y2+ym)/2,r'$t_o\ \geq\ 50$',fs=9.5)
    dimh(ax,xr[2]+d/2,xr[3]-d/2,bot-50,'',ext=y1-d/2)
    text(ax,XR+wR/2+10,bot-110,r'$t_o\ \geq\ 1.5d_{max}$',fs=9.5,ha='center')
    # ---- chi tiết phải dưới: lớp bảo vệ C ở góc đai
    XC=640; YC=-140
    line(ax,[(XC,YC+205),(XC,YC-10)],lw=1.0)
    line(ax,[(XC-35,YC+205),(XC+55,YC+205)],lw=1.0)
    line(ax,[(XC+105,YC+205),(XC+185,YC+205)],lw=1.0)
    line(ax,[(XC+55,YC+205),(XC+90,YC+235),(XC+75,YC+180),(XC+105,YC+205)],lw=0.0)
    line(ax,[(XC+78,YC+232),(XC+96,YC+208),(XC+82,YC+205),(XC+104,YC+180)],lw=1.0)
    line(ax,[(XC+185,YC+205),(XC+185,YC-10)],lw=1.0)
    # đai: góc bo
    line(ax,rrpath([(XC+35,YC+190),(XC+35,YC+35),(XC+185,YC+35)],18),lw=1.4)
    line(ax,[(XC,YC-10),(XC+185,YC-10)],lw=0.0)
    dot(ax,XC+62,YC+62,40)
    dimh(ax,XC,XC+35,YC-30,'',ext=YC+35) if False else None
    dimh(ax,XC,XC+35,YC-5,'',ext=YC+20) if False else None
    line(ax,[(XC,YC-10),(XC+185,YC-10)],lw=1.0)
    dimh(ax,XC,XC+35,YC-45,'',ext=YC+20)
    text(ax,XC+17,YC-90,'C',fs=10,ha='center')
    dimv(ax,YC-10,YC+35,XC+235,'',ext=XC+185)
    dimv(ax,YC+35,YC+0,XC+235,'',ext=XC+185) if False else None
    dimv(ax,YC+35,YC-10,XC+235,'',ext=XC+185) if False else None
    text(ax,XC+255,YC+12,r'$C\ \geq\ (20,\ d_{max})$',fs=9.5)
    text(ax,XC-10,-310,r'$d_{max}$ : đường kính thanh cốt dọc lớn nhất',fs=9.5)
    return fig
save(fig54(),'/home/claude/redraw/out/h54_beam_section.png')
