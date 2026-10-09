from jt import *
HC=117; HD=52
def vstir(ax,x0,x1,ty,by,step=22,lw=0.9):
    x=x0
    while x<x1: L(ax,[(x,ty+7),(x,by-7)],lw=lw); x+=step
def corner_core(ax,ox=640,ty=140,hc=HC,hd=HD,xr=890,ybot=345,sp=25,bottom_end=None,n_top_dn=44,tie_from=None,
                bar_B=True,vst=False,top_ext=0,top_bar=True):
    xc=ox+hc; by=ty+hd
    L(ax,[(ox,ybot),(ox,ty),(xr,ty)],lw=LW_CON); L(ax,[(xc,ybot),(xc,by),(xr,by)],lw=LW_CON)
    beambreak(ax,xr,ty,by); colbreak(ax,ox,hc,ybot)
    for x in (ox+7,xc-7): L(ax,[(x,ty+7),(x,ybot-4)],lw=0.9)
    L(ax,[(ox+7,ty+7),(xr-8,ty+7)],lw=0.9)
    L(ax,[(xc-15,ty+30),(xc-15,ybot-4)],lw=2.1,z=4)
    y=tie_from if tie_from is not None else by+sp; i=0
    while y<ybot-12:
        tie(ax,ox+7,xc-7,y,thick=(i%3==0)); y+=sp; i+=1
    if bar_B: B(ax,[(ox+16,ybot-4),(ox+16,ty+16),(ox+16+(xc-ox)*0.75,ty+16)],r=14)
    if top_bar: B(ax,[(xr-22,ty+8),(ox+8,ty+8),(ox+8,ty+8+n_top_dn)],r=20,lw=1.6)
    be=bottom_end if bottom_end is not None else ox+hc*0.35
    if be is not False: B(ax,[(xr-22,by-8),(be,by-8)],lw=2.1)
    return dict(ox=ox,xc=xc,ty=ty,by=by,xr=xr,ybot=ybot,hc=hc,hd=hd)
def common(ax,g,mx=150):
    ox,xc,ty,by,xr,ybot=g['ox'],g['xc'],g['ty'],g['by'],g['xr'],g['ybot']
    lv_dn(ax,xr-120,ty,'Mặt trên dầm mái',L_=200,side='r')
    lv_up(ax,xr-95,by,'Mặt dưới dầm',L_=170,side='r',dxt=0)
    bigM(ax,(xr+mx-15,ty-45),(xr+mx,by+70),bulge=55)
    dh(ax,ox,xc,ybot+85,g.get('hlab','h'),ext=ybot+93,off=-4)
def d15(ax,g,end,py):
    xc=g['xc']
    ax.annotate('',xy=(end,Y(py)),xytext=(xc-4,Y(py)),arrowprops=dict(arrowstyle='-|>',lw=0.9,color='k',mutation_scale=8,shrinkA=0,shrinkB=0))
    L(ax,[(xc-4,py-9),(xc-4,py+9)],lw=0.8); T(ax,xc+4,py,'15Ø',fs=FS-1)
def newfig(w=8.4,h=5.2,xl=(200,1190),yl=(-440,-5)): return new(w,h,xl,yl)
def panel_a():
    fig,ax=newfig(); g=corner_core(ax,bottom_end=640+HC-70); common(ax,g)
    ox,xc,ty,by=g['ox'],g['xc'],g['ty'],g['by']
    ldr(ax,370,80,'Cốt đai nằm dưới mặt dưới của sàn',(ox+75,ty+6))
    lan_v(ax,595,ty-3,by,ext_to=ox-10,xt=592); d15(ax,g,xc-72,by+47)
    spacing(ax,240,225,bigbrace=(None,170,305)); save(fig,'out/h513a.png')
def panel_b():
    fig,ax=newfig(yl=(-480,-5)); g=corner_core(ax,bottom_end=False,ybot=370); common(ax,g)
    ox,xc,ty,by=g['ox'],g['xc'],g['ty'],g['by']
    B(ax,[(g['xr']-22,by-8),(ox+30,by-8),(ox+30,by+62)],r=12)
    B(ax,[(xc-72,by+8),(xc-72,by+8)],lw=0) if False else None
    ldr(ax,370,80,'Cốt đai nằm dưới mặt dưới của sàn',(ox+75,ty+6))
    lan_v(ax,595,ty-3,by,ext_to=ox-10,xt=592); lan_v(ax,595,by,by+55,ext_to=ox-10,xt=592)
    d15(ax,g,xc-72,by+42)
    spacing(ax,240,225,bigbrace=(None,170,320))
    ldr(ax,260,435,'Thép dầm kéo xuống quá đáy dầm ít nhất hai thanh',(ox+30,by+60),ha='left')
    save(fig,'out/h513b.png')
def panel_c():
    fig,ax=newfig(yl=(-460,-5)); g=corner_core(ax,bottom_end=640+HC-70,ybot=355,n_top_dn=44+95); common(ax,g)
    ox,xc,ty,by=g['ox'],g['xc'],g['ty'],g['by']
    ldr(ax,370,80,'Cốt đai nằm dưới mặt dưới của sàn',(ox+75,ty+6))
    lan_v(ax,595,by,by+48,ext_to=ox-10,xt=592); lan_v(ax,595,by+48,by+96,ext_to=ox-10,xt=592)
    d15(ax,g,xc-72,by+47)
    spacing(ax,240,225,bigbrace=(None,175,330))
    ldr(ax,370,405,'Ít nhất hai thanh',(ox+10,by+96))
    save(fig,'out/h513c.png')
def panel_d():
    fig,ax=newfig(10.6,5.8,(40,1260),(-520,-5)); g=corner_core(ax,hd=62,xr=980,ybot=400,bottom_end=False,tie_from=None,n_top_dn=50,sp=22)
    ox,xc,ty,by,xr,ybot=g['ox'],g['xc'],g['ty'],g['by'],g['xr'],g['ybot']
    # đai nghiêng gia cường trong vùng đầu dầm
    x=ox+75
    while x<xc+190:
        L(ax,[(x,ty+8),(x+40,by+8)],lw=0.9,z=3); x+=26
    vstir(ax,xc+215,xr-10,ty,by,step=22)
    # cốt dưới dầm và 20% cốt dọc đầu dầm uốn xiên
    B(ax,[(xr-22,by-10),(xc+130,by-10)],lw=1.0)
    B(ax,[(xr-22,by-10),(xc+120,by-10),(xc-35,by+60)],lw=2.1)
    common(ax,g,mx=170)
    ldr(ax,420,60,'Cốt đai gia cường',(ox+225,ty+30),fs=FS)
    lan_v(ax,590,ty-3,by,ext_to=ox-10,xt=588); lan_v(ax,590,by+22,by+72,ext_to=ox-10,xt=588)
    dv(ax,ty,by,xr+30,r'$h_d$',ext=xr-5,xt=xr+22) if False else None
    dh(ax,xc,xc+120,by+98,'0.1L',ext=by+90,off=-4)
    dv(ax,by,by+0.4*62,xc+160,'',ext=None) if False else None
    ldr(ax,xc+190,by+120,'20% cốt dọc đầu dầm',(xc+125,by-8),ha='left')
    spacing(ax,100,by+85,bigbrace=(None,by+25,ybot-20)) if False else spacing(ax,60,by+110,bigbrace=(None,by+60,ybot-10))
    ldr(ax,230,ybot+40,'Ít nhất hai thanh',(ox+10,by+105))
    save(fig,'out/h513d.png')
def panel_e():
    fig,ax=newfig(8.6,5.2,(180,1160),(-430,-5))
    ox,ty,hc=470,120,117; hd=172; by=ty+hd; xc=ox+hc; xr=760; ybot=by+110
    L(ax,[(ox,ybot),(ox,ty),(xr,ty)],lw=LW_CON); L(ax,[(xc,ybot),(xc,by),(xr,by)],lw=LW_CON)
    beambreak(ax,xr,ty,by); colbreak(ax,ox,hc,ybot)
    for x in (ox+7,xc-7): L(ax,[(x,ty+7),(x,ybot-4)],lw=0.9)
    L(ax,[(ox+7,ty+7),(xr-8,ty+7)],lw=0.9); L(ax,[(ox+7,by-7),(xr-8,by-7)],lw=0.9)
    L(ax,[(xc-15,ty+40),(xc-15,ybot-4)],lw=2.1,z=4)
    # vùng nút mở rộng: đai kín dạng chữ U/kín, nét đứng
    x=ox+30
    while x<xr-12: L(ax,[(x,ty+7),(x,by-7)],lw=0.9); x+=22
    for py,ex in ((ty+78,xc+150),(ty+112,xc+150),(by+6+22,xc-7)):
        tie(ax,ox+7,ex if ex>xc else xc-7,py,thick=True)
    y=by+22+22
    i=0
    while y<ybot-12: tie(ax,ox+7,xc-7,y,thick=(i%3==0)); y+=22; i+=1
    B(ax,[(xr-22,by-10),(ox+60,by-10)],lw=2.1)
    B(ax,[(ox+16,ybot-4),(ox+16,ty+16),(ox+16+(xc-ox)*0.75,ty+16)],r=14)
    B(ax,[(xr-22,ty+8),(ox+8,ty+8),(ox+8,ty+8+50)],r=20,lw=1.6)
    lv_dn(ax,xr-100,ty,'Mặt trên dầm mái',L_=190,side='r')
    lv_up(ax,xr-85,by,'Mặt dưới dầm',L_=170,side='r')
    bigM(ax,(xr+140,ty-40),(xr+150,by-40),bulge=55)
    dv(ax,ty,by,xr+40,r'$h_d$≥1.5$h_c$',ext=xr+10,xt=xr+30) 
    dh(ax,ox,xc,ybot+55,r'$h_c$',ext=ybot+62,off=-4)
    for tx,ty2 in ((ox+30,ty+10),(ox+45,ty+16),(ox+60,ty+30)): pass
    ldr(ax,260,70,'Thép uốn chữ U',(ox+28,ty+20))
    ldr(ax,260,70,'',(ox+42,ty+34)) if False else None
    for tgt in ((ox+40,ty+54),(ox+60,ty+78)): line(ax,[(ox+10,Y(ty-6)),(tgt[0],Y(tgt[1]))],lw=0.8)
    save(fig,'out/h513e.png')
if __name__=='__main__':
    for f in (panel_a,panel_b,panel_c,panel_d,panel_e): f()
