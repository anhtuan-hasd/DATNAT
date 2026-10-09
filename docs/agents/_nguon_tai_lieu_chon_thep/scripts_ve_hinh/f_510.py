from dr import *
fig,ax=new(9.2,8.0,(0,1310),(-1135,-25))
SW=1.5; C0=17; DD=11
def Y(p): return -p
def sec(x0,ptop,W,H,ys_side,xs_mid=(),mid_stir=(),extra=None):
    """x0: trái, ptop: toạ độ book (từ trên xuống) của mép trên bê tông. ys_side: tỉ lệ (0..1) dot ở hai cạnh bên;
    xs_mid: tỉ lệ x của các dot ở mép trên/dưới (không tính góc)"""
    yt=Y(ptop); yb=Y(ptop+H)
    ax.add_patch(Rectangle((x0,yb),W,H,fc='none',ec='k',lw=LW_CON,zorder=2))
    sx0,sx1=x0+C0,x0+W-C0; sy0,sy1=yb+C0,yt-C0
    stirrup(ax,sx0,sy0,sx1,sy1,r=5,lw=SW,hk=9)
    d=DD/2+1.5
    cx0,cx1,cy0,cy1=sx0+d,sx1-d,sy0+d,sy1-d
    for f in ys_side:
        y=cy0+f*(cy1-cy0); dot(ax,cx0,y,DD); dot(ax,cx1,y,DD)
    for f in xs_mid:
        x=cx0+f*(cx1-cx0); dot(ax,x,cy0,DD); dot(ax,x,cy1,DD)
    return dict(cx0=cx0,cx1=cx1,cy0=cy0,cy1=cy1,sx0=sx0,sx1=sx1,sy0=sy0,sy1=sy1,x0=x0,yb=yb,yt=yt,W=W,H=H)
def vhook(x,y,up,sgn=1,L=8):
    line(ax,[(x,y),(x+sgn*L,y+(L if up else -L))],lw=SW*0.8,z=3)
def vlink(s,xf,top=True,bot=True):
    x=s['cx0']+xf*(s['cx1']-s['cx0'])
    line(ax,[(x,s['sy0']),(x,s['sy1'])],lw=SW,z=3)
    return x
def lab(x,py,s): text(ax,x,Y(py),s,fs=13,ha='left')

# ---------- a)
lab(62,67,'a)'); lab(595,67,'b)')
a=sec(165,142,215,111,[0,1/3,2/3,1],xs_mid=[0.5])
x=a['cx0']+0.5*(a['cx1']-a['cx0']); line(ax,[(x,a['sy0']),(x,a['sy1'])],lw=SW,z=3)
vhook(x,a['sy1'],False,1); vhook(x,a['sy0'],True,1)
dimh(ax,a['sx0']+0,x,Y(297),r'$S_2$',ext=None,arr=True,toff=3)
dimh(ax,x,a['sx1'],Y(297),r'$S_2$≤500',ext=None,arr=True,toff=3)
for xx in (a['sx0'],x,a['sx1']): line(ax,[(xx,a['sy0']),(xx,Y(305))],lw=LW_DIM*0.8)
dimh(ax,165,380,Y(345),'h',ext=None,arr=True,toff=3)
for xx in (165,380): line(ax,[(xx,a['yb']),(xx,Y(352))],lw=LW_DIM*0.8)
# t0>=50
dimv(ax,Y(165),Y(180),130,'',arr=False,s=0)
line(ax,[(122,Y(165)),(158,Y(165))],lw=LW_DIM*.8); line(ax,[(122,Y(180)),(158,Y(180))],lw=LW_DIM*.8)
ax.annotate('',xy=(131,Y(165)),xytext=(131,Y(150)),arrowprops=dict(arrowstyle='-|>',lw=.6,color='k',mutation_scale=6,shrinkA=0,shrinkB=0))
ax.annotate('',xy=(131,Y(180)),xytext=(131,Y(195)),arrowprops=dict(arrowstyle='-|>',lw=.6,color='k',mutation_scale=6,shrinkA=0,shrinkB=0))
text(ax,70,Y(172),r'$t_o$≥50',fs=TXT)
# S1
ys=[a['cy1']-i*(a['cy1']-a['cy0'])/3 for i in range(4)]
xl=420
for i in range(3):
    y1,y2=ys[i],ys[i+1]
    ax.annotate('',xy=(xl,y1),xytext=(xl,y1+0),arrowprops=dict(arrowstyle='-'))
    dimv(ax,y2,y1,xl,'',arr=True,ms=6)
for y in ys: line(ax,[(a['cx1']+8,y),(xl+14,y)],lw=LW_DIM*0.8)
text(ax,xl+16,(ys[0]+ys[1])/2,r'$S_1$',fs=TXT)
text(ax,xl+16,(ys[1]+ys[2])/2,r'$S_1$',fs=TXT)
text(ax,xl+16,(ys[2]+ys[3])/2-4,r'$S_1$ ≤ 400',fs=TXT)

# ---------- b)
b=sec(697,142,163,111,[0,1/3,2/3,1])
dimv_rot(ax,Y(253),Y(142),640,'',arr=True) if False else None
dimv(ax,Y(253),Y(142),614,'',arr=True)
for yy in (142,253): line(ax,[(608,Y(yy)),(697,Y(yy))],lw=LW_DIM*.8)
text(ax,624,Y(197),'b≤ 400',fs=TXT,ha='left')
dimh(ax,697,860,Y(312),'h≤ 500',arr=True,toff=4,tpos='above')
for xx in (697,860): line(ax,[(xx,Y(253)),(xx,Y(318))],lw=LW_DIM*.8)

# ---------- c)
lab(62,422,'c)'); lab(595,422,'d)')
c=sec(166,498,215,110,[0,1/3,2/3,1],xs_mid=[0.5])
x=c['cx0']+0.5*(c['cx1']-c['cx0']); line(ax,[(x,c['sy0']),(x,c['sy1'])],lw=SW,z=3)
vhook(x,c['sy1'],False,1); vhook(x,c['sy0'],True,1)
dimv(ax,Y(608),Y(498),88,'',arr=True)
for yy in (498,608): line(ax,[(82,Y(yy)),(166,Y(yy))],lw=LW_DIM*.8)
text(ax,96,Y(552),'b≤ 400',fs=TXT)
dimh(ax,166,381,Y(668),r'500 ≤h≤ 1000',arr=True,toff=4,tpos='above')
for xx in (166,381): line(ax,[(xx,Y(608)),(xx,Y(675))],lw=LW_DIM*.8)
ax.texts[-1].set_family('Liberation Serif')

# ---------- d)
d=sec(698,470,215,128,[0,0.5,1],xs_mid=[0.5])
xm=d['cx0']+0.5*(d['cx1']-d['cx0']); ym=(d['cy0']+d['cy1'])/2
line(ax,[(xm,d['cy1']),(d['cx0'],ym),(xm,d['cy0']),(d['cx1'],ym),(xm,d['cy1'])],lw=SW,z=3)
vhook(xm,d['cy1']+DD/2,True,-1,L=7)
dimv(ax,Y(598),Y(470),620,'',arr=True)
for yy in (470,598): line(ax,[(612,Y(yy)),(698,Y(yy))],lw=LW_DIM*.8)
text(ax,630,Y(535),'b> 400',fs=TXT)
dimh(ax,d['sx0'],xm,Y(655),r'$S_2$',arr=True,toff=3)
dimh(ax,xm,d['sx1'],Y(655),r'$S_2$≤ 500',arr=True,toff=3)
for xx in (d['sx0'],xm,d['sx1']): line(ax,[(xx,d['sy0']),(xx,Y(662))],lw=LW_DIM*.8)
dimh(ax,698,913,Y(705),'500 ≤h≤ 1000',arr=True,toff=4,tpos='above')
for xx in (698,913): line(ax,[(xx,d['yb']),(xx,Y(712))],lw=LW_DIM*.8)
# chi tiết đai phụ
dp=rrpath([(1012,Y(540)),(1012+4,Y(540)),(1012,Y(540))],0)
pts=[(1012,Y(486)),(1105,Y(540)),(1012,Y(597)),(922,Y(540)),(1012,Y(486))]
p=rrpath(pts,10); ax.plot(p[:,0],p[:,1],color='k',lw=SW)
line(ax,[(1017,Y(486)),(1017,Y(496))],lw=SW) if False else None
line(ax,[(1013,Y(486)),(1013,Y(498))],lw=SW*.8)
text(ax,1012,Y(540),'Đai phụ',fs=TXT+1,ha='center',family='Liberation Serif')

# ---------- e)
lab(62,763,'e)'); lab(595,763,'f)')
e=sec(166,810,308,127,[0,1/3,2/3,1],xs_mid=[0.23,0.77])
x1=e['cx0']+0.23*(e['cx1']-e['cx0']); x2=e['cx0']+0.77*(e['cx1']-e['cx0']); ym=(e['cy0']+e['cy1'])/2
# hai đai phụ dạng '<' và '>' móc vào cốt dọc
line(ax,[(x1,e['cy1']),(e['cx0'],ym+0),(x1,e['cy0'])],lw=SW,z=3)
line(ax,[(x2,e['cy1']),(e['cx1'],ym),(x2,e['cy0'])],lw=SW,z=3)
for xx in (x1,x2):
    vhook(xx,e['cy1']+DD/2-1,True,-1,L=7); vhook(xx,e['cy0']-DD/2+1,False,-1,L=7)
dimv(ax,Y(937),Y(810),95,'',arr=True)
for yy in (810,937): line(ax,[(88,Y(yy)),(166,Y(yy))],lw=LW_DIM*.8)
text(ax,104,Y(878),'b> 400',fs=TXT)
dimh(ax,e['sx0'],x1,Y(992),r'$S_2$',arr=True,toff=3)
dimh(ax,x1,x2,Y(992),r'$S_2$≤ 500',arr=True,toff=3)
dimh(ax,x2,e['sx1'],Y(992),r'$S_2$',arr=True,toff=3)
for xx in (e['sx0'],x1,x2,e['sx1']): line(ax,[(xx,e['sy0']),(xx,Y(999))],lw=LW_DIM*.8)
dimh(ax,166,474,Y(1053),'1000≤h≤ 1500',arr=True,toff=4,tpos='above')
for xx in (166,474): line(ax,[(xx,e['yb']),(xx,Y(1060))],lw=LW_DIM*.8)
# chi tiết đai phụ '<'
p=rrpath([(572,Y(826)),(486,Y(880)),(572,Y(934))],8); ax.plot(p[:,0],p[:,1],color='k',lw=SW)
ax.plot([572,575,575,572],[Y(826),Y(826),Y(822),Y(822)],color='k',lw=0)
line(ax,[(572,Y(826)),(578,Y(832))],lw=SW*.8); line(ax,[(572,Y(934)),(578,Y(928))],lw=SW*.8)
text(ax,517,Y(877),'Đai phụ',fs=TXT+1,family='Liberation Serif')

# ---------- f)
f=sec(698,813,308,202,[0,0.2,0.4,0.6,0.8,1],xs_mid=[0.31,0.69])
xa=f['cx0']+0.31*(f['cx1']-f['cx0']); xb=f['cx0']+0.69*(f['cx1']-f['cx0'])
for xx in (xa,xb):
    line(ax,[(xx,f['sy0']),(xx,f['sy1'])],lw=SW,z=3)
    vhook(xx,f['sy1'],False,1,L=7); vhook(xx,f['sy0'],True,1,L=7)
for fr,lft in ((0.4,False),(0.6,True)):
    y=f['cy0']+fr*(f['cy1']-f['cy0'])
    line(ax,[(f['sx0'],y),(f['sx1'],y)],lw=SW,z=3)
    # móc ở hai đầu
    line(ax,[(f['sx0']+1,y),(f['sx0']+9,y+8)],lw=SW*.8,z=3)
    line(ax,[(f['sx1']-1,y),(f['sx1']-9,y-8)],lw=SW*.8,z=3)
dimv(ax,Y(1015),Y(813),623,'',arr=True)
for yy in (813,1015): line(ax,[(612,Y(yy)),(698,Y(yy))],lw=LW_DIM*.8)
text(ax,634,Y(918),'b> 400',fs=TXT)
dimh(ax,f['sx0'],xa,Y(1043),r'$S_2$',arr=True,toff=3)
dimh(ax,xa,xb,Y(1043),r'$S_2$≤ 500',arr=True,toff=3)
dimh(ax,xb,f['sx1'],Y(1043),r'$S_2$',arr=True,toff=3)
for xx in (f['sx0'],xa,xb,f['sx1']): line(ax,[(xx,f['sy0']),(xx,Y(1050))],lw=LW_DIM*.8)
dimh(ax,698,1006,Y(1090),'1000≤h≤ 1500',arr=True,toff=4,tpos='above')
for xx in (698,1006): line(ax,[(xx,f['yb']),(xx,Y(1097))],lw=LW_DIM*.8)
# chi tiết đai phụ thẳng 2 móc
line(ax,[(1020,Y(883)),(1282,Y(883))],lw=SW); 
p=rrpath([(1014,Y(878)),(1014,Y(883)),(1030,Y(883))],0)
ax.plot([1020,1014,1014,1022],[Y(883),Y(883),Y(878),Y(878)],color='k',lw=SW) if False else None
line(ax,[(1020,Y(883)),(1014,Y(879))],lw=SW); line(ax,[(1282,Y(883)),(1285,Y(879))],lw=SW)
line(ax,[(1060,Y(830)),(1060,Y(1000))],lw=SW)
line(ax,[(1060,Y(830)),(1066,Y(826)),(1066,Y(838))],lw=SW) 
line(ax,[(1060,Y(1000)),(1066,Y(1004)),(1066,Y(992))],lw=SW)
text(ax,1097,Y(910),'Đai phụ',fs=TXT+1,family='Liberation Serif')
save(fig,'out/h510_col_sections.png')
