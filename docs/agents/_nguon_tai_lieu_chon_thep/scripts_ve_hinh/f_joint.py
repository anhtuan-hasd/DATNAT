from dr import *
from matplotlib.patches import Rectangle, Circle
SER='Liberation Serif'
def panel(ax,x0,bc,cols,beam,cap,note,hh=300,cover=20,dst=8):
    """nhìn dọc trục dầm: thanh cột = vạch đứng; thanh dầm = vòng tròn. Toạ độ y theo bề rộng."""
    X=lambda y:x0+y
    ax.add_patch(Rectangle((X(-bc/2),-hh/2),bc,hh,fill=False,ec='k',lw=0.9,zorder=2))
    # đai (nét đậm vừa)
    s=bc/2-cover-dst/2
    ax.add_patch(Rectangle((X(-s),-hh/2),2*s,hh,fill=False,ec='k',lw=1.0,zorder=2,ls='-'))
    y0=bc/2-cover-dst-cols[0]/2; n=len(cols)
    ys=[-y0+i*2*y0/(n-1) for i in range(n)]
    for y,d in zip(ys,cols):
        ax.add_patch(Rectangle((X(y)-d/2,-hh/2),d,hh,fc='0.35',ec='k',lw=0.8,zorder=3))
    # khe
    for (ya,da),(yb,db),yy in zip(zip(ys,cols),list(zip(ys,cols))[1:],range(99)):
        pass
    gaps=[((a+b)/2,(b-a)-(da+db)/2) for (a,da),(b,db) in zip(zip(ys,cols),list(zip(ys,cols))[1:])]
    for (yc,w) in gaps:
        dimh(ax,X(yc-w/2),X(yc+w/2),-hh/2-26,'%d'%round(w),tpos='below',fs=7.5,s=7)
    # thanh dầm
    for (yb,d,ok) in beam:
        if ok: ax.add_patch(Circle((X(yb),30),d/2,fc='white',ec='k',lw=1.4,zorder=5))
        else:
            ax.add_patch(Circle((X(yb),30),d/2,fc='none',ec='k',lw=1.0,ls=(0,(2,1.5)),zorder=5))
            ax.plot([X(yb)-d/2*0.7,X(yb)+d/2*0.7],[30-d/2*0.7,30+d/2*0.7],color='k',lw=0.9,zorder=6)
            ax.plot([X(yb)-d/2*0.7,X(yb)+d/2*0.7],[30+d/2*0.7,30-d/2*0.7],color='k',lw=0.9,zorder=6)
    dimh(ax,X(-bc/2),X(bc/2),hh/2+26,'b$_c$ = %d'%bc,tpos='above',fs=8,s=7)
    ax.text(x0,-hh/2-92,cap,fontsize=8.5,ha='center',va='top',family=SER)
    ax.text(x0,-hh/2-150,note,fontsize=8,ha='center',va='top',family=SER,color='k',linespacing=1.25)
def fig():
    f,ax=new(8.6,4.3,(-210,210+480),(-330,262)); 
    # (a) cột 250: 2Ø25+1Ø22; dầm cần 3 thanh hàng ngoài
    panel(ax,0,250,[25,22,25],[(-42.2,25,True),(42.2,25,True),(0,22,False)],
          'a) Cột 250: mỗi mặt 2Ø25+1Ø22','Hàng ngoài dầm cần 3 thanh (Ø25, Ø22, Ø25)\nchỉ có 2 khe: lọt 2 thanh, thanh thứ 3 không lọt')
    # (b) cột 300 / 4Ø22
    panel(ax,480,300,[22,22,22,22],[(-74,25,True),(0,22,True),(74,25,True)],
          'b) Cột 300: mỗi mặt 4Ø22 (1521 mm²)','3 khe rộng 52 mm: lọt cả 3 thanh\n(chừa dung sai ≥10 mm mỗi bên)')
    # chú giải
    ax.add_patch(Rectangle((-205,230),14,14,fc='0.35',ec='k',lw=0.8)); ax.text(-183,237,'thanh dọc cột (vạch đứng)',fontsize=8,va='center',family=SER)
    ax.add_patch(Circle((160,237),8,fc='white',ec='k',lw=1.4)); ax.text(176,237,'thanh trên của dầm (nằm ngang, nhìn đầu thanh)',fontsize=8,va='center',family=SER)
    f.savefig('out/hjoint.png',dpi=190,bbox_inches='tight',pad_inches=0.04,facecolor='white'); plt.close(f)
fig()
