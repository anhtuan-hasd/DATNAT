from jt import *
def edge_node(ax,var='a',ox=668,h1=152,off=0,ytop=60,ty=237,by=322,ybot=497,xe=990,sp_up=20,sp_lo=27):
    xr1=ox+h1; xr2=xr1+off
    # bê tông cột
    L(ax,[(ox,ytop+0),(ox,ybot)],lw=LW_CON)
    pts=[(xr1,ytop),(xr1,ty)]+([(xr2,by)] if off else [])+[(xr2,ybot)]
    L(ax,pts,lw=LW_CON)
    L(ax,[(ox-12,ytop),(ox+h1*0.35,ytop),(ox+h1*0.5,ytop-40),(ox+h1*0.6,ytop+0),(xr1+12,ytop)],lw=LW_CON)
    colbreak(ax,ox,max(h1,h1+off),ybot)
    # dầm
    L(ax,[(xr1,ty),(xe,ty)],lw=LW_CON); L(ax,[(xr2,by),(xe,by)],lw=LW_CON)
    beambreak(ax,xe,ty,by)
    # chân đai thẳng đứng + cốt dọc cột
    for x in (ox+8,): L(ax,[(x,ytop+8),(x,ybot-4)],lw=0.9)
    L(ax,[(xr1-8,ytop+8),(xr1-8,ty)],lw=0.9); L(ax,[(xr1-8,ty),(xr2-8,by)] if off else [(xr1-8,ty),(xr1-8,by)],lw=0.9); L(ax,[(xr2-8,by),(xr2-8,ybot-4)],lw=0.9)
    L(ax,[(ox+16,ytop+8),(ox+16,ybot-4)],lw=2.0,z=4)
    if var=='c':
        L(ax,[(xr1-16,ytop+8),(xr1-16,ty+14)],lw=2.0,z=4)
        B(ax,[(xr2-16,ybot-4),(xr2-16,by+30),(xr1-16,ty-6)],r=14,lw=2.0) if False else None
        B(ax,[(xr2-16,ybot-4),(xr2-16,by+18),(xr1-24,ty-4)],r=16,lw=2.0)
    elif off:
        B(ax,[(xr2-16,ybot-4),(xr2-16,by+20),(xr1-16,ty+5),(xr1-16,ytop+8)],r=14,lw=2.0)
    else:
        L(ax,[(xr1-16,ytop+8),(xr1-16,ybot-4)],lw=2.0,z=4)
    # đai trên (dày) và dưới
    y=ytop+38
    while y<ty-8:
        w2=xr1-8
        tie(ax,ox+8,w2,y,thick=((y-ytop)//sp_up%2==0)); y+=sp_up
    y=ty+16
    while y<by-4:
        tie(ax,ox+8,(xr2-8 if y>ty+40 else xr1-8),y,thick=False); y+=26
    y=by+22; i=0
    while y<ybot-10:
        tie(ax,ox+8,xr2-8,y,thick=(i%2==0)); y+=sp_lo; i+=1
    # cốt dầm
    B(ax,[(xe-22,ty+7),(ox+28,ty+7),(ox+28,by+16)],r=20,lw=1.7) if var!='c' else B(ax,[(xe-22,ty+7),(ox+28,ty+7),(ox+28,by+36)],r=20,lw=1.7)
    B(ax,[(xe-22,by-8),(xr2-88,by-8)],lw=2.1)
    return dict(ox=ox,xr1=xr1,xr2=xr2,ty=ty,by=by,xe=xe,ybot=ybot,ytop=ytop)
def deco(ax,g,var):
    ox,xr1,xr2,ty,by,xe,ybot,ytop=[g[k] for k in ('ox','xr1','xr2','ty','by','xe','ybot','ytop')]
    lv_dn(ax,xe-90,ty,'Mặt trên dầm',L_=190,side='r')
    lv_up(ax,xe-80,by,'Mặt dưới dầm',L_=150,side='r')
    bigM(ax,(xe+130,ty-50),(xe+135,by+55),bulge=50)
    # mũi tên cong Lan và Lan
    arrow_path(ax,[(ox+62,ty-18),(ox+6,ty-18),(ox+6,ty+75)],r=30,head1=True)
    lan_v(ax,ox-30,ty-70,ty-8,ext_to=ox-6,xt=ox-34)
    T(ax,ox-48,ty+8,r'$L_{an}$',fs=FS,ha='right',va='center')
    T(ax,ox-48,ty+8,'',ha='right')
    # 15Ø
    py=by+40; end=xr2-90
    ax.annotate('',xy=(end,Y(py)),xytext=(xr2-4,Y(py)),arrowprops=dict(arrowstyle='-|>',lw=0.9,color='k',mutation_scale=8,shrinkA=0,shrinkB=0))
    L(ax,[(end,py-9),(end,py+9)],lw=0.8); T(ax,xr2+6,py,'15Ø',fs=FS-1)
    ldr(ax,ox+170,ty-125,'Cốt đai nằm dưới mặt dưới của sàn',(xr1-10,ty+30))
    # khoảng cách đai
    spacing(ax,ox-505,ty-85,l1='≤ 300',l2='≤ 10Ø',bigbrace=None,dy=26)
    spacing(ax,ox-505,by+110,l1='≤ 500',l2='≤ 15Ø',bigbrace=(ox-80,by+55,ybot-5),dy=26)
    return
def figs():
    # a)
    fig,ax=new(8.9,6.0,(110,1230),(-675,-5)); g=edge_node(ax,'a'); deco(ax,g,'a')
    dh(ax,g['ox'],g['xr1'],g['ybot']+85,'h',ext=g['ybot']+92,off=-4)
    save(fig,'out/h517a.png')
    # b)
    fig,ax=new(10.0,6.6,(110,1560),(-680,40))
    g=edge_node(ax,'b',h1=135,off=14); deco(ax,g,'b')
    ox=g['ox']; 
    dh(ax,ox,g['xr1'],g['ytop']-75,r'$h_1$',ext=g['ytop']-5,off=-4)
    dh(ax,ox,g['xr2'],g['ybot']+85,r'$h_2$',ext=g['ybot']+92,off=-4)
    T(ax,g['xr1']+55,g['ty']+55,r'tg$\beta$≤ 1/6',fs=FS-1,serif=True)
    # sơ đồ phụ
    X0=1290;W1=135;W2=149
    L(ax,[(X0,60),(X0,497)],lw=LW_CON); L(ax,[(X0+W1,60),(X0+W1,237),(X0+W2,322),(X0+W2,497)],lw=LW_CON)
    L(ax,[(X0+W1,237),(X0+W1+130,237)],lw=LW_CON); L(ax,[(X0+W2,322),(X0+W1+130,322)],lw=LW_CON)
    L(ax,[(X0+W1,237),(X0+W2,322)],lw=0.9,ls=(0,(3,2)))
    L(ax,[(X0-12,60),(X0+W1*0.35,60),(X0+W1*0.5,20),(X0+W1*0.6,60),(X0+W1+12,60)],lw=LW_CON)
    colbreak(ax,X0,W2,497)
    T(ax,X0+W1+14,330,r'$\beta$',fs=FS-1)
    dh(ax,X0,X0+W1,-15,r'$h_1$',ext=55,off=-4); dh(ax,X0,X0+W2,582,r'$h_2$',ext=500,off=-4)
    save(fig,'out/h517b.png')
    # c)
    fig,ax=new(8.9,6.4,(110,1230),(-680,40))
    g=edge_node(ax,'c',h1=135,off=28); deco(ax,g,'c')
    ox=g['ox']
    dh(ax,ox,g['xr1'],g['ytop']-75,r'$h_1$',ext=g['ytop']-5,off=-4)
    dh(ax,ox,g['xr2'],g['ybot']+85,r'$h_2$',ext=g['ybot']+92,off=-4)
    T(ax,g['xr1']+55,g['ty']+55,r'tg$\beta$> 1/6',fs=FS-1,serif=True)
    save(fig,'out/h517c.png')
if __name__=='__main__': figs()
