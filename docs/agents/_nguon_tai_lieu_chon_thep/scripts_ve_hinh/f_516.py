from jt import *
def colT(ax,cx0,cx1,pbot,p_beam_bot,leg=7,sp=29,n=5):
    L(ax,[(cx0,p_beam_bot),(cx0,pbot)],lw=LW_CON); L(ax,[(cx1,p_beam_bot),(cx1,pbot)],lw=LW_CON)
    for x in (cx0+8,cx1-8): L(ax,[(x,p_beam_bot-0),(x,pbot-3)],lw=0.9)
def v1(ax,dy=0):
    d=lambda p:p+dy
    x0,x1=470,962; ct,cb=135,222
    L(ax,[(x0,d(ct)),(x1,d(ct))],lw=LW_CON); L(ax,[(x0,d(cb)),(640,d(cb))],lw=LW_CON); L(ax,[(808,d(cb)),(x1,d(cb))],lw=LW_CON)
    beambreak_l(ax,x0,d(ct),d(cb)); beambreak(ax,x1,d(ct),d(cb))
    for x in (640,808): L(ax,[(x,d(cb)),(x,d(400))],lw=LW_CON)
    colbreak(ax,640,168,d(400),amp=14)
    for x in (650,798): L(ax,[(x,d(cb)),(x,d(398))],lw=0.9)
    for x in (668,782): L(ax,[(x,d(cb)),(x,d(398))],lw=1.8,z=4)
    # cốt cột uốn vòm ở đỉnh
    t=np.linspace(np.pi,0,40); arcp=[(725+57*np.cos(a),d(215)-57*np.sin(a)) for a in t]
    p=np.array([(x,Y(y)) for x,y in [(668,d(215))]+arcp+[(782,d(215))]]); ax.plot(p[:,0],p[:,1],color='k',lw=1.8,zorder=4)
    L(ax,[(655,d(157)),(790,d(157))],lw=2.4,z=5)
    y=232
    while y<395: tie(ax,658,792,d(y),thick=True); y+=29
    lv_dn(ax,995,d(135),'Mặt trên sàn mái',L_=100)
    # mũi tên Lan
    arrow_path(ax,[(750,d(115)),(670,d(115))],head0=False,head1=True)
    arrow_path(ax,[(750,d(115)),(820,d(135)),(838,d(215))],r=45,head1=True)
    T(ax,808,d(108),r'$L_{an}$',fs=FS+1,ha='left',va='bottom')
    arrow_path(ax,[(712,d(205)),(690,d(170))],head1=True,lw=0.8); rtxt(ax,708,d(183),'r ≥ 5Ø') if False else None
    T(ax,722,d(190),'r ≥ 5Ø',fs=FS-1,serif=True)
    spacing(ax,130,d(318),bigbrace=(None,d(228),d(392)),dy=34)
def v2(ax,dy=0):
    d=lambda p:p+dy
    x0,x1=470,962; ct,cb=540,625
    L(ax,[(x0,d(ct)),(x1,d(ct))],lw=LW_CON); L(ax,[(x0,d(cb)),(660,d(cb))],lw=LW_CON); L(ax,[(795,d(cb)),(x1,d(cb))],lw=LW_CON)
    beambreak_l(ax,x0,d(ct),d(cb)); beambreak(ax,x1,d(ct),d(cb))
    for x in (655,808): L(ax,[(x,d(cb)),(x,d(800))],lw=LW_CON)
    colbreak(ax,655,153,d(800),amp=14)
    for x in (665,798): L(ax,[(x,d(cb)),(x,d(798))],lw=0.9)
    # cốt cột uốn ra hai bên
    B(ax,[(668,d(800)),(668,d(595)),(655,d(560)),(565,d(558))],r=25,lw=1.8) if False else None
    B(ax,[(676,d(790)),(676,d(565)),(565,d(565))],r=30,lw=1.8)
    B(ax,[(786,d(790)),(786,d(565)),(893,d(565))],r=30,lw=1.8)
    y=632
    while y<795: tie(ax,666,796,d(y),thick=True); y+=29
    lv_dn(ax,995,d(540),'Mặt trên sàn mái',L_=100)
    arrow_path(ax,[(815,d(572)),(885,d(572))],head1=True)
    arrow_path(ax,[(815,d(572)),(815,d(625))],head1=True)
    T(ax,840,d(603),r'$L_{an}$',fs=FS+1,ha='left')
    arrow_path(ax,[(655,d(583)),(640,d(566))],head1=True,lw=0.8)
    T(ax,574,d(583),'r ≥ 5Ø',fs=FS-1,serif=True)
    spacing(ax,130,d(720),bigbrace=(None,d(630),d(795)),dy=34)
fig,ax=new(8.6,8.0,(100,1250),(-880,-95))
v1(ax); v2(ax)
save(fig,'out/h516.png')
