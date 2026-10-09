from dr import *
import numpy as np
SER='Liberation Serif'
def P(x,y): return np.array([x,y],float)
def seg_pts(th,W,dl):
    """đường biên lệch dl (dương: phía trên/ngoài) của trục chữ V ngược; trả 3 điểm A,apex,B (y-up)"""
    t=np.tan(th); c=np.cos(th); s=np.sin(th)
    A=P(-W,-W*t)+dl*P(-s,c); B=P(W,-W*t)+dl*P(s,c); M=P(0,dl/c)
    return [A,M,B]
def pl(ax,pts,lw=LW_CON,r=0,z=3,c='k',ls='-'):
    p=rrpath(pts,r) if r else np.array(pts); ax.plot(p[:,0],p[:,1],color=c,lw=lw,zorder=z,ls=ls,solid_joinstyle='round')
def zz(ax,p0,p1,amp=9,lw=LW_CON):
    p0=np.array(p0);p1=np.array(p1); d=p1-p0; n=np.array([-d[1],d[0]])/np.linalg.norm(d)
    m=(p0+p1)/2; dd=d/np.linalg.norm(d)
    pts=[p0,m-dd*amp*0.6,m+dd*0.0+n*amp-dd*0.1*amp,m-n*amp+dd*0.1*amp,m+dd*amp*0.6,p1]
    ax.plot([q[0] for q in pts],[q[1] for q in pts],color='k',lw=lw,zorder=3)
def dimp(ax,P0,P1,off,txt,fs=9,ms=7,tdx=0,rot=None,side=1):
    P0=np.array(P0);P1=np.array(P1);off=np.array(off)
    a=P0+off;b=P1+off
    ax.annotate('',xy=a,xytext=b,arrowprops=dict(arrowstyle='<|-|>',lw=0.6,color='k',mutation_scale=ms,shrinkA=0,shrinkB=0),zorder=6)
    for p,q in ((P0,a),(P1,b)):
        e=q+0.12*off if False else q+ (off/np.linalg.norm(off))*8
        ax.plot([p[0],e[0]],[p[1],e[1]],color='k',lw=0.5,zorder=2)
    d=b-a; ang=np.degrees(np.arctan2(d[1],d[0]))
    if ang>90: ang-=180
    if ang<-90: ang+=180
    m=(a+b)/2; n=off/np.linalg.norm(off)
    ax.text(m[0]+n[0]*14+tdx,m[1]+n[1]*14,txt,fontsize=fs,rotation=rot if rot is not None else ang,ha='center',va='center',rotation_mode='anchor',family='Liberation Sans')
def bigM2(ax,p0,p1,bulge,txt,tp):
    p0=np.array(p0);p1=np.array(p1); m=(p0+p1)/2+np.array(bulge)
    t=np.linspace(0,1,40)
    pts=np.array([(1-s)**2*p0+2*(1-s)*s*m+s**2*p1 for s in t])
    ax.plot(pts[:,0],pts[:,1],color='k',lw=0.8)
    d=pts[-1]-pts[-4]; d/=np.linalg.norm(d); n=np.array([-d[1],d[0]])
    ax.add_patch(Polygon([pts[-1],pts[-1]-16*d+6*n,pts[-1]-16*d-6*n],closed=True,fc='white',ec='k',lw=0.8,zorder=6))
    ax.text(tp[0],tp[1],txt,fontsize=11,ha='center',va='center')
def member(ax,th,W,h,c=10,bars=True,stir=True,dense=150,bar_r=40):
    # bê tông + lớp chân đai
    for dl in (h/2,-h/2):
        pl(ax,seg_pts(th,W,dl),lw=LW_CON,z=2)
    for dl in (h/2-5,-(h/2-5)):
        pl(ax,seg_pts(th,W,dl),lw=0.6,z=2)
    t=np.tan(th); s=np.sin(th); co=np.cos(th)
    # break ở hai đầu
    for sg in (-1,1):
        xe=sg*W; ye=-W*t
        n=P(-s*sg*-1*0+(-s if sg<0 else s),co)
        a=P(xe,ye)+(h/2)*n; b=P(xe,ye)-(h/2)*n
        zz(ax,a-(a-b)*0.0,b,amp=h*0.09)
def stirrups(ax,th,W,h,x_list,lw=0.8,dl=None):
    t=np.tan(th); s=np.sin(th); co=np.cos(th); d=(h/2-6) if dl is None else dl
    for x in x_list:
        y=-abs(x)*t
        n=P(-s,co) if x<0 else P(s,co)
        a=P(x,y)+d*n; b=P(x,y)-d*n
        ax.plot([a[0],b[0]],[a[1],b[1]],color='k',lw=lw,zorder=3)
def fig_a():
    th=np.deg2rad(16); W=560; h=100
    fig,ax=new(10,5.2,(-700,900),(-330,300))
    member(ax,th,W,h)
    d=h/2-14
    pl(ax,seg_pts(th,W-8,d),lw=2.2,r=40,z=4); pl(ax,seg_pts(th,W-8,-d),lw=2.2,r=40,z=4)
    xs=list(np.arange(-400,-150,30))+list(np.arange(-150,-12,16)); xs=xs+[-x for x in xs]
    stirrups(ax,th,W,h,xs)
    ap=np.array([0, (h/2)/np.cos(th)]); inn=np.array([0,-(h/2)/np.cos(th)])
    # đường tâm nét đứt
    ax.plot([-80,760],[0,0],color='k',lw=0.7,ls=(0,(14,6)),zorder=2)
    # các tia dưới góc 3/8 alpha
    alpha=np.pi-2*th; a1=3*alpha/8
    for sg in (-1,1):
        end=inn+np.array([sg*np.tan(a1)*(h*1.6),h*1.6])
        ax.plot([inn[0],end[0]],[inn[1],end[1]],color='k',lw=0.5,ls=(0,(10,5)),zorder=2)
    # S
    Sx=(h/2)*np.tan(a1)
    ytop=ap[1]+60
    for sg in (-1,1): ax.plot([sg*Sx,sg*Sx],[ap[1]+4,ytop+30],color='k',lw=0.5)
    ax.annotate('',xy=(-Sx,ytop+15),xytext=(Sx,ytop+15),arrowprops=dict(arrowstyle='<|-|>',lw=0.6,color='k',mutation_scale=7,shrinkA=0,shrinkB=0))
    ax.text(0,ytop+40,r'S= h·tg(3/8$\alpha$)',fontsize=10,ha='center',va='bottom')
    ax.text(95,ap[1]+52,r'$\alpha_1$ = 3/4$\alpha$',fontsize=9.5,ha='left',va='center')
    # α
    arc=np.linspace(np.deg2rad(200),np.deg2rad(340),30)
    ax.plot(inn[0]+34*np.cos(arc),inn[1]+34*np.sin(arc)-6,color='k',lw=0.6)
    ax.text(0,inn[1]-62,r'$\alpha$≥160$^o$',fontsize=10,ha='center',va='center')
    # kích thước h bên phải
    XR=720
    yt=ap[1]; yb=inn[1]
    for y in (yt,0,yb): ax.plot([20,XR+30][:1]+[XR+30],[y,y],color='k',lw=0.5) if False else None
    for y in (yt,yb): ax.plot([200,XR+30],[y,y],color='k',lw=0.5)
    ax.annotate('',xy=(XR,yt),xytext=(XR,yb),arrowprops=dict(arrowstyle='<|-|>',lw=0.6,color='k',mutation_scale=7,shrinkA=0,shrinkB=0))
    ax.annotate('',xy=(XR-50,yt),xytext=(XR-50,0),arrowprops=dict(arrowstyle='<|-|>',lw=0.6,color='k',mutation_scale=7,shrinkA=0,shrinkB=0))
    ax.annotate('',xy=(XR-50,0),xytext=(XR-50,yb),arrowprops=dict(arrowstyle='<|-|>',lw=0.6,color='k',mutation_scale=7,shrinkA=0,shrinkB=0))
    ax.text(XR+16,0,'h',fontsize=10,ha='left',va='center'); ax.text(XR-60,yt/2,'h/2',fontsize=9,ha='right',va='center',rotation=90); ax.text(XR-60,yb/2,'h/2',fontsize=9,ha='right',va='center',rotation=90)
    ax.plot([XR-80,XR+30],[0,0],color='k',lw=0.5)
    # h1, h2 ở hai đầu và M
    t=np.tan(th); s=np.sin(th); co=np.cos(th)
    for sg,lab in ((-1,r'$h_1$'),(1,r'$h_2$')):
        xe=sg*W; ye=-W*t; n=P(-s if sg<0 else s,co)
        a=P(xe,ye)+(h/2)*n; b=P(xe,ye)-(h/2)*n
        off=P(sg*co*0+(-co*sg*0),0)
        o=np.array([ -sg*s*0, 0])
        dd=np.array([sg*co,sg*s*-1]) # hướng dọc trục ra ngoài (xuống)
        dimp(ax,a,b,dd*70*-1*-1 if False else np.array([sg*55*co,-55*s]),lab)
    bigM2(ax,(-560,-232),(-640,-110),(-70,60),'M',(-660,-60))
    bigM2(ax,(560,-232),(640,-110),(60,60),'M',(665,-60))
    # chú thích
    t1=ax.text(10,-250,'Cốt dọc tính toán\nđặt liên tục qua nút',fontsize=10.5,ha='center',va='center',family=SER)
    for sg in (-1,1):
        ax.annotate('',xy=(sg*190,-(190*np.tan(th))-(h/2-14)+2),xytext=(sg*60,-226),arrowprops=dict(arrowstyle='-|>',lw=0.7,color='k',mutation_scale=8,shrinkA=0,shrinkB=0),zorder=6)
    save(fig,'out/h520a.png')
def fig_b():
    th=np.deg2rad(26); W=520; h=100
    fig,ax=new(10,5.4,(-700,900),(-360,320))
    member(ax,th,W,h)
    d=h/2-14
    # cốt trên liên tục
    pl(ax,seg_pts(th,W-8,d),lw=2.2,r=40,z=4)
    # cốt dưới tách rời: mỗi bên kéo qua điểm giao, neo vào vùng nén
    t=np.tan(th); co=np.cos(th); s=np.sin(th)
    for sg in (-1,1):
        n=P(-s*sg*-1*0+(-s if sg<0 else s),co)
        a=P(sg*(W-8),-(W-8)*t)-d*n
        # tới điểm sau apex 1 đoạn Lan rồi bẻ lên
        apex_in=P(0,-d/co)
        far=apex_in+P(-sg*70,70*t*0+0)  # vượt sang phía đối diện theo hướng cũ
        dirv=(apex_in-a)/np.linalg.norm(apex_in-a)
        e=apex_in+dirv*80
        pl(ax,[a,apex_in,e],lw=2.2,z=4)
    # cốt ngang thẳng đứng + đai dày
    ap=np.array([0,(h/2)/co]); inn=np.array([0,-(h/2)/co])
    xs=list(np.arange(-380,-130,28))+list(np.arange(-130,-10,13)); xs=xs+[-x for x in xs]
    stirrups(ax,th,W,h,xs)
    ax.plot([0,0],[ap[1]+60,inn[1]+8],color='k',lw=2.2,zorder=5)
    alpha=np.pi-2*th; a1=3*alpha/8
    ax.plot([-80,760],[0,0],color='k',lw=0.7,ls=(0,(14,6)),zorder=2)
    Sx=(h/2)*np.tan(a1); ytop=ap[1]+75
    for sg in (-1,1):
        end=inn+np.array([sg*np.tan(a1)*(h*1.7),h*1.7]); ax.plot([inn[0],end[0]],[inn[1],end[1]],color='k',lw=0.5,ls=(0,(10,5)),zorder=2)
        ax.plot([sg*Sx,sg*Sx],[ap[1]+4,ytop+30],color='k',lw=0.5)
    ax.annotate('',xy=(-Sx,ytop+15),xytext=(Sx,ytop+15),arrowprops=dict(arrowstyle='<|-|>',lw=0.6,color='k',mutation_scale=7,shrinkA=0,shrinkB=0))
    ax.text(0,ytop+40,r'S= h·tg(3/8$\alpha$)',fontsize=10,ha='center',va='bottom')
    ax.text(95,ap[1]+58,r'$\alpha_1$ = 3/4$\alpha$',fontsize=9.5,ha='left',va='center')
    arc=np.linspace(np.deg2rad(200),np.deg2rad(340),30); ax.plot(0+38*np.cos(arc),inn[1]+38*np.sin(arc)-6,color='k',lw=0.6)
    ax.text(0,inn[1]-58,r'$\alpha$<160$^o$',fontsize=10,ha='center',va='center')
    ax.text(-110,inn[1]-30,r'$L_{an}$',fontsize=10,ha='center',va='center')
    XR=720; yt=ap[1]; yb=inn[1]
    for y in (yt,yb): ax.plot([200,XR+30],[y,y],color='k',lw=0.5)
    ax.plot([XR-80,XR+30],[0,0],color='k',lw=0.5)
    for (a_,b_) in ((yt,yb),):
        ax.annotate('',xy=(XR,yt),xytext=(XR,yb),arrowprops=dict(arrowstyle='<|-|>',lw=0.6,color='k',mutation_scale=7,shrinkA=0,shrinkB=0))
    ax.annotate('',xy=(XR-50,yt),xytext=(XR-50,0),arrowprops=dict(arrowstyle='<|-|>',lw=0.6,color='k',mutation_scale=7,shrinkA=0,shrinkB=0))
    ax.annotate('',xy=(XR-50,0),xytext=(XR-50,yb),arrowprops=dict(arrowstyle='<|-|>',lw=0.6,color='k',mutation_scale=7,shrinkA=0,shrinkB=0))
    ax.text(XR+16,0,'h',fontsize=10,ha='left',va='center'); ax.text(XR-60,yt/2,'h/2',fontsize=9,ha='right',va='center',rotation=90); ax.text(XR-60,yb/2,'h/2',fontsize=9,ha='right',va='center',rotation=90)
    for sg,lab in ((-1,r'$h_1$'),(1,r'$h_2$')):
        xe=sg*W; ye=-W*t; n=P(-s if sg<0 else s,co)
        a=P(xe,ye)+(h/2)*n; b=P(xe,ye)-(h/2)*n
        dimp(ax,a,b,np.array([sg*55*co,-55*s]),lab)
    bigM2(ax,(-520,-290),(-600,-170),(-70,60),'M',(-630,-110))
    bigM2(ax,(520,-290),(600,-170),(60,60),'M',(635,-110))
    ax.text(10,-310,'Cốt dọc tính toán\nphải được neo vào vùng nén',fontsize=10.5,ha='center',va='center',family=SER)
    save(fig,'out/h520b.png')
def fig_c():
    fig,ax=new(10,6.0,(-640,640),(-470,270))
    # khung dạng V ngược góc nhọn: trục lệch 42° so với phương ngang
    th=np.deg2rad(42); W=380; h=130
    t=np.tan(th); s=np.sin(th); co=np.cos(th)
    # biên ngoài + biên trong
    for dl in (h/2,-h/2): pl(ax,seg_pts(th,W,dl),lw=LW_CON,z=2)
    for sg in (-1,1):
        xe=sg*W; ye=-W*t; n=P(-s if sg<0 else s,co)
        zz(ax,P(xe,ye)+(h/2)*n,P(xe,ye)-(h/2)*n,amp=11)
    # cốt dọc tính toán (hai thanh chữ V ngược, đặt sát biên trong)
    d=h/2-12
    pl(ax,seg_pts(th,W-8,-d),lw=2.4,z=4)
    pl(ax,seg_pts(th,W-8,-d+8),lw=1.0,z=4)
    inn=P(0,-(d)/co)
    # thép gia cường ngang (vòng cung hai đầu uốn xuống)
    yc=inn[1]+30
    pl(ax,[(-160,yc-34),(-150,yc+0),(-110,yc+22),(110,yc+22),(150,yc+0),(160,yc-34)],lw=2.0,r=45,z=5) if False else None
    pl(ax,[(-170,yc-50),(-130,yc+6),(0,yc+6),(130,yc+6),(170,yc-50)],lw=2.0,r=55,z=5)
    # vòng khép kín phía trên
    cyl=yc+66; R=42
    tt=np.linspace(0,2*np.pi,80); ax.plot(R*np.cos(tt),cyl+R*np.sin(tt),color='k',lw=2.0,zorder=5)
    # hai nhánh chéo từ vòng xuống điểm giao
    for sg in (-1,1):
        ax.plot([sg*R*0.95,sg*14],[cyl-R*0.3,yc+6],color='k',lw=2.0,zorder=5)
    # Lan
    for sg in (-1,1):
        ax.annotate('',xy=(sg*22,yc+22),xytext=(sg*90,yc+22) ,arrowprops=dict(arrowstyle='-|>',lw=0.6,color='k',mutation_scale=7),zorder=6) if False else None
    ax.text(-70,yc+28,r'$L_{an}$',fontsize=10.5,ha='center',va='center'); ax.text(70,yc+28,r'$L_{an}$',fontsize=10.5,ha='center',va='center')
    # h1/2,h2/2 ở góc ngoài
    for sg,lab in ((-1,r'$h_1$/2'),(1,r'$h_2$/2')):
        ap=P(0,(h/2)/co)
        dirv=P(-sg*co*-1*-1*0+(-co*0+ (co if sg>0 else -co)*-1)*-1,0)
        a=ap+P(sg*0,0)
        # đoạn dọc theo mặt ngoài từ đỉnh xuống h/2
        along=P(sg*co,-s)   # hướng xuống dọc theo biên ngoài
        p0=ap; p1=ap+along*(h/2)
        nrm=P(-s*sg*-1*0+ (s if sg>0 else -s)*-1*-1*0,0)
        outn=P(sg*s*0+(s if sg>0 else -s)*1*0,0)
        n_out=P(-s if sg<0 else s,co)   # pháp tuyến hướng lên-ngoài
        dimp(ax,p0,p1,n_out*55,lab,fs=9.5)
    # thép gia cường chú thích
    ax.annotate('',xy=(185,yc-10),xytext=(330,yc-60),arrowprops=dict(arrowstyle='-|>',lw=0.7,color='k',mutation_scale=8,shrinkA=0,shrinkB=0))
    ax.plot([330,470],[yc-60,yc-60],color='k',lw=0.6); ax.text(340,yc-48,'Thép gia cường',fontsize=10.5,family=SER,ha='left',va='bottom')
    # Cốt dọc tính toán
    ax.text(0,-245,'Cốt dọc tính toán',fontsize=10.5,family=SER,ha='center',va='center')
    ax.plot([-95,95],[-262,-262],color='k',lw=0.6)
    for sg in (-1,1):
        ax.annotate('',xy=(sg*200,-(200*t)-d/co+4),xytext=(sg*100,-250),arrowprops=dict(arrowstyle='-|>',lw=0.7,color='k',mutation_scale=8,shrinkA=0,shrinkB=0),zorder=6)
    for sg,lab in ((-1,r'$h_1$'),(1,r'$h_2$')):
        xe=sg*W; ye=-W*t; n=P(-s if sg<0 else s,co)
        a=P(xe,ye)+(h/2)*n; b=P(xe,ye)-(h/2)*n
        dimp(ax,a,b,np.array([sg*55*co*-1*-1*0+sg*60*s*0+(sg*45*co),-45*s]),lab)
    bigM2(ax,(-470,-390),(-480,-300),(-30,40),'M',(-515,-330))
    bigM2(ax,(470,-390),(480,-300),(30,40),'M',(520,-330))
    save(fig,'out/h520c.png')
if __name__=='__main__': fig_a(); fig_b(); fig_c()
