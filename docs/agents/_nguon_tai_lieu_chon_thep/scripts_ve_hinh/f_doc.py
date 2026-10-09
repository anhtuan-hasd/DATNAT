from dr import *
import numpy as np
SER='Liberation Serif'
def ldr(ax,xt,yt,s,tgt,ha='left',va='bottom',fs=TXT+0.5,serif=True):
    t=ax.text(xt,yt,s,fontsize=fs,ha=ha,va=va,family=SER if serif else 'Liberation Sans')
    ax.figure.canvas.draw(); bb=t.get_window_extent().transformed(ax.transData.inverted())
    yb=bb.y0-0.12*(bb.y1-bb.y0); line(ax,[(bb.x0,yb),(bb.x1,yb)],lw=LW_DIM)
    sx=bb.x1 if tgt[0]>(bb.x0+bb.x1)/2 else bb.x0
    line(ax,[(sx,yb),tgt],lw=LW_DIM)
# ------------------------------------------------------------------ cột 22
def col22():
    fig,ax=new(4.6,6.2,(-190,560),(-220,720))
    b,h,c,ds,dm,d22,d16=250,600,20,8,25,22,16
    ax.add_patch(Rectangle((0,0),b,h,fc='none',ec='k',lw=LW_CON+0.3,zorder=2))
    stirrup(ax,c+ds/2,c+ds/2,b-c-ds/2,h-c-ds/2,r=14,lw=2.0,hk=26)
    xs=[c+ds+dm/2,b/2,b-c-ds-dm/2]
    for y in (c+ds+dm/2,h-c-ds-dm/2):
        dot(ax,xs[0],y,dm); dot(ax,xs[2],y,dm); dot(ax,xs[1],y,d22)
    xm=[c+ds+d16/2,b-c-ds-d16/2]; ym=h/2
    for x in xm: dot(ax,x,ym,d16)
    # đai phụ nối 2 thanh Ø16, móc 135°
    line(ax,[(xm[0],ym),(xm[1],ym)],lw=2.0,z=3)
    for x,sg in ((xm[0],1),(xm[1],-1)):
        line(ax,[(x,ym),(x+sg*22,ym-22)],lw=2.0,z=3)
        line(ax,[(x,ym),(x+sg*22,ym+22)],lw=2.0,z=3) if False else None
    # kích thước
    dimh(ax,0,b,-75,'250',ext=-5,arr=True,toff=10,fs=9)
    dimv_rot(ax,0,h,-80,'600',ext=-5,arr=True,fs=9,toff=14)
    # khoảng cách giữa các thanh (tim hai hàng, cấu tạo)
    xr=b+95
    dimv_rot(ax,xm[0] and (c+ds+dm/2),ym,xr,'259,5',ext=b+4,arr=True,fs=8.5,toff=-4,side='right') if False else None
    ax.annotate('',xy=(xr,c+ds+dm/2),xytext=(xr,ym),arrowprops=dict(arrowstyle='<|-|>',lw=LW_DIM,color='k',mutation_scale=7,shrinkA=0,shrinkB=0))
    ax.annotate('',xy=(xr,ym),xytext=(xr,h-c-ds-dm/2),arrowprops=dict(arrowstyle='<|-|>',lw=LW_DIM,color='k',mutation_scale=7,shrinkA=0,shrinkB=0))
    for y in (c+ds+dm/2,ym,h-c-ds-dm/2): line(ax,[(b+4,y),(xr+14,y)],lw=LW_DIM*.8)
    ax.text(xr+22,(c+ds+dm/2+ym)/2,'259,5 ≤ 500',fontsize=8.5,rotation=90,ha='left',va='center')
    ax.text(xr+22,(h-c-ds-dm/2+ym)/2,'259,5 ≤ 500',fontsize=8.5,rotation=90,ha='left',va='center')
    # khoảng hở
    yy=h+60
    dimh(ax,xs[0]+dm/2,xs[1]-d22/2,yy,'61 ≥ 50',ext=h-c-ds-dm/2+8,arr=True,toff=8,fs=8.5)
    # lớp bảo vệ
    ldr(ax,-150,-165,'Lớp bảo vệ 20',(c/2,c/2+8),fs=9)
    ldr(ax,-185,h+125,'2Ø25 + 1Ø22 mỗi phía',(xs[0]-8,h-c-ds-dm/2+10),fs=9)
    ldr(ax,300,ym+100,'1Ø16 cấu tạo',(xm[1]+d16/2,ym+6),fs=9) if False else None
    ldr(ax,52,ym+95,'1Ø16 cấu tạo',(xm[1]-2,ym+d16/2+1),fs=9)
    ldr(ax,60,ym-120,'Đai phụ Ø8',(130,ym-3),fs=9)
    ldr(ax,b+20,ym-135,'Đai phụ Ø8',(xm[1]-60,ym-2),fs=9) if False else None
    ldr(ax,330,-168,'Đai chính Ø8',(b-c-ds/2,28),fs=9)
    ldr(ax,-170,300+125,'Đai phụ Ø8',(xm[0]+34,ym+1),fs=9) if False else None
    save(fig,'out/hdoc_col22.png')

# ------------------------------------------------------------------ dầm CB
def bar_ends(ax,x0,x1,y,lw=LW_BAR,tk=0):
    line(ax,[(x0,y),(x1,y)],lw=lw,z=4)
def beam_cb():
    L=6900; H=700; fc=300
    fig=plt.figure(figsize=(9.2,7.2))
    ax=fig.add_axes([0.0,0.40,1,0.6]); ax.axis('off')
    ax.set_xlim(-1150,L+1150); ax.set_ylim(-1050,1800)
    # cột hai đầu (nét mảnh) + ký hiệu gãy
    for xc in (0,L):
        for sg in (-1,1): line(ax,[(xc+sg*fc,-450),(xc+sg*fc,H+450)],lw=LW_CON)
        for yy,dy in ((-450,-1),(H+450,1)):
            zig_v(ax,xc-fc-60,xc+fc+60,yy,45)
    # dầm
    line(ax,[(fc,0),(L-fc,0)],lw=LW_CON+0.2); line(ax,[(fc,H),(L-fc,H)],lw=LW_CON+0.2)
    # đai
    def st(x): line(ax,[(x,24),(x,H-24)],lw=0.8,z=3)
    for x in np.arange(fc+50,fc+1725,150): st(x)
    for x in np.arange(L-fc-50,L-fc-1725,-150): st(x)
    for x in np.linspace(fc+1725+120,L-fc-1725-120,10): st(x)
    # cốt treo tại D (dầm phụ 220x300): đai dày 5 mỗi bên
    xD=L/2
    for k in range(5):
        for sg in (-1,1): line(ax,[(xD+sg*(110+50+75*k),24),(xD+sg*(110+50+75*k),H-24)],lw=1.8,z=3)
    # dầm phụ gạch chéo
    ax.add_patch(Rectangle((xD-110,H-300),220,300,fc='none',ec='k',lw=LW_CON,zorder=3))
    import matplotlib.patches as mp
    ax.add_patch(Rectangle((xD-110,H-300),220,300,fc='none',ec='k',lw=0,hatch='////',zorder=2))
    # thép dọc
    y1=H-40.5; y2=H-89
    bar_ends(ax,-380,L+380,y1,lw=3.2)       # 2Ø25 trên chạy suốt
    bar_ends(ax,-380,2150,y2,lw=2.4); bar_ends(ax,L-2000,L+380,y2,lw=2.4)   # 3Ø22 gia cường, cắt 2150 / 2000
    bar_ends(ax,-150,L+150,40.5,lw=3.0)     # 3Ø22 dưới, neo 450 qua mép cột
    # cốt cạnh bên 2Ø12/bên (đường nét trung bình)
    for yy in (H*0.62,H*0.38): line(ax,[(fc,yy),(L-fc,yy)],lw=1.3,z=3)
    # ký hiệu gãy cho thép đi tiếp
    for xe,sg in ((-380,-1),(L+380,1)):
        pass
    # kích thước đai
    s=0.0045*(L+2300)
    def dim(x1,x2,y,txt,ext=None):
        dimh(ax,x1,x2,y,txt,ext=ext,arr=False,toff=40,s=s,fs=9.5)
    y0=-560
    dim(fc,fc+1725,y0,'Ø8a150  (L/4 = 1725)',ext=-20)
    dim(fc+1725,L-fc-1725,y0,'Ø8a250',ext=-20)
    dim(L-fc-1725,L-fc,y0,'Ø8a150  (L/4)',ext=-20)
    dim(0,L,-800,'L = 6900 (tim cột)',ext=-460)
    # neo thép dưới
    dimh(ax,-100,fc,-210,'400',ext=None,arr=True,toff=-30,fs=9,tpos='below') if False else None
    # chú thích
    ldr(ax,-1100,H+620,'2Ø25 trên chạy suốt (góc đai)',(-250,y1+8),fs=9.5)
    ldr(ax,520,H+560,'3Ø22 gia cường gối, cắt tại 2150 (C), 2000 (B)',(1700,y2+6),fs=9.5)
    
    ldr(ax,3300,H+840,'Dầm phụ D 220×300; cốt treo 5Ø8 mỗi bên (a75)',(xD+110+50+75*3,H-30),fs=9.5)
    ldr(ax,4800,H+560,'Cốt cạnh 2Ø12 mỗi bên (h = 700)',(5200,H*0.62+4),fs=9.5)
    ldr(ax,1150,-240,'3Ø22 dưới chạy suốt, neo 450 qua mép cột',(1000,34),fs=9.5,va='top')
    # ký hiệu mặt cắt 1-1 (gối) và 2-2 (nhịp)
    for xs,lab in ((700,'1'),(2750,'2')):
        ax.annotate('',xy=(xs,H+170),xytext=(xs,H+400),arrowprops=dict(arrowstyle='-|>',lw=0.9,color='k',mutation_scale=9,shrinkA=0,shrinkB=0))
        line(ax,[(xs-60,H+170),(xs+60,H+170)],lw=2.2)
        ax.text(xs-95,H+290,lab,fontsize=11,ha='right',va='center')
    # --- mặt cắt
    def section(axs,tops,bots,sides,title):
        b,h=250,700
        axs.set_aspect('equal'); axs.axis('off'); axs.set_xlim(-190,b+150); axs.set_ylim(-190,h+120)
        axs.add_patch(Rectangle((0,0),b,h,fc='none',ec='k',lw=LW_CON+0.3))
        c=20; ds=8
        x0=c+ds/2; x1=b-c-ds/2; yb=c+ds/2; yt=h-c-ds/2
        # đai
        p=rrpath([(x0,yb),(x1,yb),(x1,yt),(x0,yt),(x0,yb)],12); axs.plot(p[:,0],p[:,1],color='k',lw=2.0)
        axs.plot([x0,x0+26],[yt,yt-26],color='k',lw=2.0)
        for (x,y,d) in tops+bots+sides: axs.add_patch(Circle((x,y),d/2,fc='k',ec='k'))
        axs.set_title(title,fontsize=10,family=SER,pad=2)
        dimh(axs,0,b,-80,'250',ext=-8,arr=True,toff=10,fs=8.5,s=1) if False else None
        axs.annotate('',xy=(0,-70),xytext=(b,-70),arrowprops=dict(arrowstyle='<|-|>',lw=0.6,color='k',mutation_scale=7,shrinkA=0,shrinkB=0))
        axs.text(b/2,-100,'250',fontsize=8.5,ha='center',va='top')
        axs.annotate('',xy=(-60,0),xytext=(-60,h),arrowprops=dict(arrowstyle='<|-|>',lw=0.6,color='k',mutation_scale=7,shrinkA=0,shrinkB=0))
        axs.text(-85,h/2,'700',fontsize=8.5,rotation=90,ha='center',va='center')
    c=28
    xs=[40.5,125,209.5]
    side=[(36,H*0.62,12),(b:=250,0,0)][:1]
    sides=[(36,H*0.62,12),(214,H*0.62,12),(36,H*0.38,12),(214,H*0.38,12)]
    ax2=fig.add_axes([0.04,0.02,0.30,0.38])
    section(ax2,[(xs[0],H-40.5,25),(xs[1],H-39,22),(xs[2],H-40.5,25),(70,H-89,22),(180,H-89,22)],[(xs[0],40.5,22),(xs[1],39,22),(xs[2],40.5,22)],sides,'Mặt cắt 1-1 (gối)')
    ax2.text(262,H-40,'2Ø25+1Ø22',fontsize=8,va='center',family=SER); ax2.text(262,H-89,'2Ø22',fontsize=8,va='center',family=SER)
    ax2.text(262,40,'3Ø22',fontsize=8,va='center',family=SER); ax2.text(262,H*0.5,'2×2Ø12',fontsize=8,va='center',family=SER)
    ax3=fig.add_axes([0.37,0.02,0.30,0.38])
    section(ax3,[(xs[0],H-40.5,25),(xs[2],H-40.5,25)],[(xs[0],40.5,22),(xs[1],39,22),(xs[2],40.5,22)],sides,'Mặt cắt 2-2 (nhịp)')
    ax3.text(262,H-40,'2Ø25',fontsize=8,va='center',family=SER); ax3.text(262,40,'3Ø22',fontsize=8,va='center',family=SER); ax3.text(262,H*0.5,'2×2Ø12',fontsize=8,va='center',family=SER)
    ax4=fig.add_axes([0.70,0.02,0.29,0.38]); ax4.axis('off'); ax4.set_xlim(0,1); ax4.set_ylim(0,1)
    ax4.text(0.0,0.94,'Ghi chú',fontsize=10,va='top',weight='bold')
    ax4.text(0.0,0.84,'• Đai Ø8 (CB240-T), lớp bảo vệ 20 mm\n• Đai đầu tiên cách mép cột 50 mm\n• Khoảng hở hai hàng thép trên 25 mm\n• Mặt cắt 1-1, 2-2 vẽ cùng tỉ lệ; đai có móc 135°\n   ở một góc',fontsize=8.8,va='top',family=SER,linespacing=1.55)
    fig.savefig('out/hdoc_beam.png',dpi=200,bbox_inches='tight',pad_inches=0.04,facecolor='white'); plt.close(fig)
if __name__=='__main__': col22(); beam_cb()
