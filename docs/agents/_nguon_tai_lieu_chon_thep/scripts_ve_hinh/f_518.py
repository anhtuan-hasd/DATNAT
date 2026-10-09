from jt import *
def f518():
    fig,ax=new(9.0,6.2,(150,1290),(-770,-95))
    ox,oc=710,850; ytop,ybot=140,685; tT=368; bL=500; bR=447; xl,xr=550,1015
    L(ax,[(ox,ytop),(ox,tT)],lw=LW_CON); L(ax,[(oc,ytop),(oc,tT)],lw=LW_CON)
    L(ax,[(ox,bL),(ox,ybot)],lw=LW_CON); L(ax,[(oc,bR),(oc,ybot)],lw=LW_CON)
    L(ax,[(ox-12,ytop),(ox+50,ytop),(ox+70,ytop-45),(ox+90,ytop),(oc+12,ytop)],lw=LW_CON)
    colbreak(ax,ox,oc-ox,ybot)
    L(ax,[(xl,tT),(ox,tT)],lw=LW_CON); L(ax,[(xl,bL),(ox,bL)],lw=LW_CON)
    L(ax,[(oc,tT),(xr,tT)],lw=LW_CON); L(ax,[(oc,bR),(xr,bR)],lw=LW_CON)
    beambreak_l(ax,xl,tT,bL); beambreak(ax,xr,tT,bR)
    for x in (ox+8,oc-8): L(ax,[(x,ytop+8),(x,tT)],lw=0.9); L(ax,[(x,bR if x>ox+20 else bL),(x,ybot-4)],lw=0.9)
    for x in (ox+16,oc-16): L(ax,[(x,ytop+8),(x,ybot-4)],lw=2.0,z=4)
    y=ytop+55; i=0
    while y<tT-5: tie(ax,ox+8,oc-8,y,thick=(i%2==0)); y+=25; i+=1
    y=tT+12
    while y<bL-5: tie(ax,ox+8,oc-8,y,thick=False); y+=25
    y=bL+22; i=0
    while y<ybot-8: tie(ax,ox+8,oc-8,y,thick=(i%2==0)); y+=21; i+=1
    # thép dầm
    B(ax,[(xl+4,tT+4),(xr-22,tT+4)],lw=2.0)
    B(ax,[(xl+4,bL-4),(oc-20,bL-4)],lw=2.0)
    B(ax,[(xr-22,bR-4),(ox+45,bR-4)],lw=1.4)
    lv_dn(ax,xr-60,tT,'Mặt trên dầm',L_=170,side='r')
    lv_up(ax,xr-50,bR,'Mặt dưới dầm',L_=150,side='r')
    bigM(ax,(xr+170,tT-30),(xr+180,bR+60),bulge=50)
    # M bên trái (hướng ngược lại): vẽ đối xứng
    x0,y0,x1,y1=xl-200,tT-20,xl-175,bL-5
    t=np.linspace(0,1,50); c1=(x0-95,y0+10); c2=(x1-70,y1-70)
    px=(1-t)**3*x0+3*(1-t)**2*t*c1[0]+3*(1-t)*t**2*c2[0]+t**3*x1; py=(1-t)**3*y0+3*(1-t)**2*t*c1[1]+3*(1-t)*t**2*c2[1]+t**3*y1
    ax.plot(px,-py,color='k',lw=0.8)
    d=np.array([px[-1]-px[-4],-(py[-1]-py[-4])]); d/=np.linalg.norm(d); n=np.array([-d[1],d[0]]); tip=np.array([px[-1],-py[-1]])
    ax.add_patch(Polygon([tip,tip-18*d+7*n,tip-18*d-7*n],closed=True,fc='white',ec='k',lw=0.8,zorder=6))
    T(ax,x1-55,y1+22,'M',fs=FS+1)
    # Lan
    lan_v(ax,640,300,tT,ext_to=ox-6,xt=636); L(ax,[(626,300),(700,300)],lw=0.7)
    ax.annotate('',xy=(ox+45,Y(bL-3)),xytext=(oc-3,Y(bL-3)),arrowprops=dict(arrowstyle='-|>',lw=0.9,color='k',mutation_scale=8,shrinkA=0,shrinkB=0))
    T(ax,oc+10,bL-2,r'$L_{an}$',fs=FS,va='center')
    ax.annotate('',xy=(oc-40,Y(bL+55)),xytext=(ox+2,Y(bL+55)),arrowprops=dict(arrowstyle='-|>',lw=0.9,color='k',mutation_scale=8,shrinkA=0,shrinkB=0))
    L(ax,[(oc-40,bL+30),(oc-40,bL+60)],lw=0.8)
    T(ax,ox-8,bL+50,r'$L_{an}$',fs=FS,ha='right',va='center')
    ldr(ax,ox+160,ytop+95,'Cốt đai nằm dưới mặt dưới của sàn',(oc-6,tT-2))
    spacing(ax,235,tT-65,l1='≤ 300',l2='≤ 10Ø',dy=22)
    spacing(ax,235,ybot-90,l1='≤ 500',l2='≤ 15Ø',bigbrace=(None,bL+60,ybot-5),dy=22)
    dh(ax,ox,oc,ybot+78,'h',ext=ybot+86,off=-4)
    save(fig,'out/h518.png')
def f519():
    fig,ax=new(9.4,5.2,(100,1560),(-660,5))
    cx0,cx1=725,865; fx0,fx1=550,1045; ft,fb=248,515
    # móng
    L(ax,[(fx0,ft),(cx0-12,ft)],lw=LW_CON); L(ax,[(cx1+12,ft),(fx1,ft)],lw=LW_CON) if False else None
    L(ax,[(fx0,ft),(fx0,350),(fx0+20,360),(fx0-20,380),(fx0,392),(fx0,fb)],lw=LW_CON) if False else None
    # móng: hai cạnh có ký hiệu gãy
    L(ax,[(fx0,ft),(fx0,345),(fx0+16,358),(fx0-12,372),(fx0,385),(fx0,fb)],lw=LW_CON)
    L(ax,[(fx1,ft),(fx1,345),(fx1-16,358),(fx1+12,372),(fx1,385),(fx1,fb)],lw=LW_CON)
    L(ax,[(fx0,ft),(cx0,ft)],lw=LW_CON); L(ax,[(cx1,ft),(fx1,ft)],lw=LW_CON); L(ax,[(fx0,fb),(fx1,fb)],lw=LW_CON)
    # thân cột
    L(ax,[(cx0,15),(cx0,ft)],lw=LW_CON); L(ax,[(cx1,15),(cx1,ft)],lw=LW_CON)
    L(ax,[(cx0-12,15),(cx0+50,15),(cx0+70,-25),(cx0+90,15),(cx1+12,15)],lw=LW_CON)
    for x in (cx0+8,cx1-8): L(ax,[(x,30),(x,ft+30)],lw=0.9)
    # thép chờ: cột dưới vào móng bẻ L ra ngoài
    B(ax,[(cx0+16,40),(cx0+16,445),(cx0-100,470+0)],r=0,lw=0) if False else None
    B(ax,[(cx0+12,60),(cx0+12,440),(cx0-110,472)],lw=0) if False else None
    B(ax,[(cx0+12,60),(cx0+12,470),(620,470)],r=32,lw=1.8)
    B(ax,[(cx1-12,60),(cx1-12,470),(970,470)],r=32,lw=1.8)
    # đai: dày trên mặt móng
    y=50; i=0
    while y<ft+25: tie(ax,cx0+12,cx1-12,y,thick=(i%2==0)); y+=30; i+=1
    tie(ax,cx0+12,cx1-12,438,thick=True)
    # lưới thép đáy móng (nét đứt + chấm)
    for k,x in enumerate(range(555,1045,48)):
        L(ax,[(x,478),(x+30,478)],lw=1.2); L(ax,[(x,484),(x+30,484)],lw=1.2)
        ax.add_patch(Circle((x+45,Y(476)),4.5,fc='white',ec='k',lw=0.8,zorder=6))
    # thép chờ rời (hình bên trái)
    B(ax,[(237,70),(237,445),(122,470)],r=0,lw=0) if False else None
    B(ax,[(237,70),(237,470),(122,470)],r=30,lw=1.6)
    lv_dn(ax,632,ft,'Mặt trên móng',L_=-160,side='l') if False else None
    h=9
    ax.add_patch(Polygon([(632-h,Y(ft-1.6*h)),(632+h,Y(ft-1.6*h)),(632,Y(ft))],closed=True,fc='white',ec='k',lw=0.8,zorder=6))
    L(ax,[(470,ft-1.6*h),(700,ft-1.6*h)],lw=0.8)
    T(ax,420,ft-1.6*h-12,'Mặt trên móng',serif=True,va='bottom')
    ldr(ax,265,25,'Thép chờ chữ L từ móng',(cx0+12,330))
    # kích thước
    dh(ax,cx1,970,375,'≥ 200',ext=462,off=-5)
    # 100
    dv(ax,ft-2,ft+20,920,'',ext=None)
    L(ax,[(880,ft+20),(930,ft+20)],lw=0.7)
    ax.text(895,Y(ft-12),'100',fontsize=FS-1,rotation=90,ha='center',va='bottom')
    # Lan
    dv(ax,70,ft,998,r'$L_{an}$',ext=890,xt=992)
    L(ax,[(945,ft),(995,ft)],lw=2.4,z=5)
    spacing(ax,1015,150,l1='≤ 300',l2='≤ 10Ø',dy=26)
    save(fig,'out/h519.png')
if __name__=='__main__': f518(); f519()
