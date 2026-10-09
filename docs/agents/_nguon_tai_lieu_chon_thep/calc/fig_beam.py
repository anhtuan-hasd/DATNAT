import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
plt.rcParams['font.family']='DejaVu Sans'
fig=plt.figure(figsize=(11,7.6))
ax=fig.add_axes([0.02,0.50,0.96,0.5]); ax.set_aspect('equal'); ax.axis('off')
L=6900; H=700
# columns
for x0 in (-300,L-300):
    ax.add_patch(Rectangle((x0,-450),600,H+900,fill=False,lw=1.2,ec='#333'))
ax.add_patch(Rectangle((300,0),L-600,H,fill=False,lw=1.5,ec='k'))
# D point
xD=L/2
ax.plot([xD,xD],[H+80,H+250],'k-',lw=1); ax.text(xD,H+280,'D: dầm phụ 220×300\n+ cốt treo 5Ø8 mỗi bên (a50–80)',ha='center',fontsize=8)
# top bars at supports (schematic lengths)
top_c=2000; top_b=L-2000
y1=H-66; y2=H-120
ax.plot([-250,top_c],[y1,y1],color='#C00000',lw=2.4)      # 2Ø25 + 1Ø22 row 1
ax.plot([-250,top_c*0.55],[y2,y2],color='#C00000',lw=1.6)  # 2Ø22 row2 (cut earlier)
ax.plot([top_b,L+250],[y1,y1],color='#C00000',lw=2.4)
ax.plot([L-top_c*0.55,L+250],[y2,y2],color='#C00000',lw=1.6)
ax.text(300,H+120,'Thép trên gối: 2Ø25+3Ø22 (2 hàng)',color='#C00000',fontsize=8)
ax.text(L-300,H+120,'(gối B tương tự)',color='#C00000',fontsize=8,ha='right')
# bottom bars
yb=62
ax.plot([-250,L+250],[yb,yb],color='#1F4E79',lw=2.4)
ax.text(L/2,-130,'Thép dưới nhịp: 3Ø22 chạy suốt, vào gối ≥ 2 thanh và ≥ A_s/2; neo ≥ L_an',ha='center',color='#1F4E79',fontsize=8)
# top rack bars
ax.plot([top_c*0.55,top_b+ (L-top_b)*0.45],[H-60,H-60],color='#777',lw=1,ls='--')
ax.text(L/2,H-190,'cốt giá 2Ø14 (nét đứt, chạy suốt, nối chồng với thép gối)',ha='center',fontsize=8,color='#555')
# stirrups
import numpy as np
def st(x): ax.plot([x,x],[22,H-22],color='#548235',lw=0.7)
for x in np.arange(350,1725+350,150): st(x)
for x in np.arange(L-350,L-350-1725-1,-150): st(x)
for x in np.arange(2075+250,L-2075,250)[:]: st(x)
# dims
def dim(x1,x2,y,txt):
    ax.annotate('',xy=(x1,y),xytext=(x2,y),arrowprops=dict(arrowstyle='<->',lw=0.8))
    ax.text((x1+x2)/2,y-90,txt,ha='center',fontsize=8)
dim(300,300+1725,-330,'Ø8a150 (L/4 = 1725)')
dim(300+1725,L-300-1725,-330,'Ø8a250')
dim(L-300-1725,L-300,-330,'Ø8a150 (L/4)')
dim(0,L,-560,'L = 6900 (tim trục C–B)')
ax.set_xlim(-450,L+450); ax.set_ylim(-760,H+450)
ax.set_title('Dầm CB 250×700 (phần tử 40–41, tầng 1) – mặt đứng bố trí thép',fontsize=11)
# sections
def section(axs,x0,title,bars_top,bars_bot,sidebars=True):
    b,h=250,700
    axs.add_patch(Rectangle((0,0),b,h,fill=False,lw=1.5))
    axs.add_patch(Rectangle((20,20),b-40,h-40,fill=False,lw=1,ec='#548235'))
    for (x,y,d,col) in bars_top+bars_bot:
        axs.add_patch(Circle((x,y),d*0.8,color=col))
        axs.text(x,y,str(int(d)),fontsize=7,ha='center',va='center',color='w')
    axs.set_xlim(-60,b+60); axs.set_ylim(-60,h+80); axs.set_aspect('equal'); axs.axis('off'); axs.set_title(title,fontsize=9)
red='#C00000'; blue='#1F4E79'; gr='#666'
# support section (a=40.5 row1, 89 row2 from top)
a1=h1=700-40.5; a2=700-89
sup_top=[(40.5,a1,25,red),(125,a1,22,red),(209.5,a1,25,red),(70,a2,22,red),(180,a2,22,red)]
sup_bot=[(40.5,40.5,22,blue),(125,39,22,blue),(209.5,40.5,22,blue)]
side=[(20+8+6,350+90,12,gr),(250-34,350+90,12,gr),(34,350-90,12,gr),(216,350-90,12,gr)]
ax2=fig.add_axes([0.05,0.0,0.28,0.5]); section(ax2,0,'Mặt cắt gối C, B',sup_top,sup_bot+side)
mid_top=[(40.5,700-40.5,14,gr),(209.5,700-40.5,14,gr)]
mid_bot=[(40.5,39,22,blue),(125,39,22,blue),(209.5,39,22,blue)]
ax3=fig.add_axes([0.36,0.0,0.28,0.5]); section(ax3,0,'Mặt cắt nhịp',mid_top,mid_bot+side)
ax4=fig.add_axes([0.68,0.0,0.30,0.5]); ax4.axis('off')
ax4.text(0,0.95,'Chú thích',fontsize=10,weight='bold',va='top')
ax4.text(0,0.82,'● đỏ: thép chịu kéo trên gối\n● xanh: thép chịu kéo dưới nhịp\n● xám: cốt giá và cốt cạnh bên 2Ø12/bên\n   (h = 700 nằm đúng ngưỡng, nên đặt)\n▭ xanh lá: đai Ø8 (CB240-T)\n\nLớp bảo vệ 20 mm (trong nhà,\nđộ ẩm ≤ 75%); khoảng hở hai\nhàng thép trên 25 mm.\n\nSố trên vòng tròn = đường kính (mm).',fontsize=8.5,va='top',linespacing=1.5)
fig.savefig('/home/claude/build/figs/beam_cb_layout.png',dpi=190,bbox_inches='tight')
