from f_513 import *
def arc(cx,cy,R,a0,a1,n=40):
    t=np.linspace(np.deg2rad(a0),np.deg2rad(a1),n); return [(cx+R*np.cos(x),cy-R*np.sin(x)) for x in t]   # cy theo px từ trên xuống
def open_joint(ax,diag=False,xr=890,ox=640,ty=140,hc=117,hd=118,ybot=380):
    g=corner_core(ax,ox=ox,ty=ty,hc=hc,hd=hd,xr=xr,ybot=ybot,bottom_end=False,bar_B=False,top_bar=False,sp=27,tie_from=ty+hd+27)
    by=ty+hd; xc=ox+hc; R=hd/2-12; cx=ox+16+R; cy=ty+hd/2
    # cốt dọc cột ngoài bẻ góc nhỏ lên phía mép trên
    B(ax,[(ox+14,ybot-4),(ox+14,ty+14),(ox+14+36,ty+14)],r=10,lw=1.6)
    # đai dầm
    x=xc+55
    while x<xr-12: L(ax,[(x,ty+7),(x,by-7)],lw=1.0); x+=24
    # cốt dọc chữ U: thanh trên -> cung -> thanh dưới
    pts=[(xr-24,ty+12),(cx,ty+12)]+arc(cx,cy,R,90,270)[1:-1]+[(cx,by-12),(xr-24,by-12)]
    p=np.array([(x,Y(y)) for x,y in pts]); ax.plot(p[:,0],p[:,1],color='k',lw=2.1,zorder=4,solid_joinstyle='round')
    # thanh chữ U thứ hai (lớp trong)
    R2=R-9
    pts=[(xr-24,ty+21),(cx,ty+21)]+arc(cx,cy,R2,90,270)[1:-1]+[(cx,by-21),(xr-24,by-21)]
    p=np.array([(x,Y(y)) for x,y in pts]); ax.plot(p[:,0],p[:,1],color='k',lw=1.2,zorder=4)
    if diag:
        B(ax,[(ox+58,by+100),(ox+58,by+58),(xr-30,ty+30),(xr-8,ty+27)],r=45,lw=2.1)
    return g
def pa():
    fig,ax=newfig(8.4,5.4,(200,1190),(-455,-5)); g=open_joint(ax); common(ax,g)
    ox,xc,ty,by=g['ox'],g['xc'],g['ty'],g['by']
    lan_v(ax,595,ty-3,by,ext_to=ox-10,xt=592); lan_v(ax,595,by+3,by+50,ext_to=ox-10,xt=592)
    spacing(ax,240,by+30,bigbrace=(None,by-5,g['ybot']-20))
    ldr(ax,xc+130,by+160,'Thép dọc chữ U',(xc-34,by-27))
    line(ax,[(xc+130,Y(by+167)),(xc-12,Y(by-35))],lw=0.8) if False else None
    save(fig,'out/h515a.png')
def pb():
    fig,ax=newfig(8.4,5.4,(200,1190),(-480,-5)); g=open_joint(ax,diag=True); common(ax,g)
    ox,xc,ty,by=g['ox'],g['xc'],g['ty'],g['by']
    lan_v(ax,595,ty-3,by,ext_to=ox-10,xt=592); lan_v(ax,595,by+3,by+50,ext_to=ox-10,xt=592)
    spacing(ax,240,by+30,bigbrace=(None,by-5,g['ybot']-20))
    ldr(ax,xc+130,by+165,'Thép dọc chữ U',(xc-34,by-27))
    ldr(ax,xc+60,by+210,'Thép chéo gia cường',(ox+58,by+95),ha='left')
    save(fig,'out/h515b.png')
if __name__=='__main__': pa(); pb()
