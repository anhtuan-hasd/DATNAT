import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
plt.rcParams['font.family']='DejaVu Sans'
fig,ax=plt.subplots(figsize=(8,6.2)); ax.set_aspect('equal'); ax.axis('off')
hc=600; hb=450  # column in-plane depth, beam depth (schematic)
# column from y=-1500 to 0 ; joint y 0..hb ; beam to the right
ax.plot([0,0,hc,hc],[-1500,hb,hb,hb],'k',lw=1.6) # left edge, top edge
ax.plot([hc,hc],[-1500,0],'k',lw=1.6)
ax.plot([hc,2600],[0,0],'k',lw=1.6); ax.plot([hc,2600],[hb,hb],'k',lw=1.6)
ax.plot([0,hc],[hb,hb],'k',lw=1.6)
ax.plot([2600,2600],[0,hb],'k',lw=1.0,ls='--')
c=40
# beam top bars: run along top, over the column to the outside face, then bend down L_an
Lan=450
ax.plot([2500,c,c],[hb-c,hb-c,hb-c-Lan-0],color='#C00000',lw=3)
ax.plot([2500,c+45,c+45],[hb-c-35,hb-c-35,hb-c-Lan-120],color='#C00000',lw=2)
ax.text(2450,hb+70,'thép trên dầm 2Ø16: uốn xuống cột ≥ L_an = 450',color='#C00000',fontsize=8,ha='right')
ax.annotate('',xy=(c-85,hb-c-Lan),xytext=(c-85,hb-c),arrowprops=dict(arrowstyle='<->',lw=0.9))
ax.text(c-110,hb-c-Lan/2,'L_an\n≥450',fontsize=8,ha='right',va='center')
# column bars: outer bar goes to top of beam
ax.plot([c+110,c+110],[-1500,hb-c-90],color='#1F4E79',lw=3)
ax.plot([hc-c,hc-c],[-1500,0-40],color='#1F4E79',lw=3)
ax.plot([hc-c,hc-c+0],[0-40,hb-c-90],color='#1F4E79',lw=1.5,ls=':')
ax.text(hc+30,-700,'thép cột:\nthanh phía ngoài kéo\nlên sát mép trên dầm',color='#1F4E79',fontsize=8)
# bottom beam bars anchored in column
ax.plot([2500,hc-c-60,hc-c-60],[c,c,c+260],color='#1F4E79',lw=2)
ax.text(2450,-150,'thép dưới dầm neo vào cột (bẻ lên ≥ L_an hoặc theo mục 9.5)',fontsize=8,color='#1F4E79',ha='right')
# stirrups
for y in range(-1400,-100,150): ax.plot([c-20,hc-c+20],[y,y],color='#548235',lw=1)
for y in (-80,-10): pass
for x in range(120,520,100): ax.plot([x,x],[c-15,hb-c+15],color='#548235',lw=1)
ax.text(-80,-900,'đai cột đặt\nđến sát\nđáy dầm',fontsize=8,ha='right',color='#548235')
ax.annotate('đai phụ (a ≤ 100)\ntại chỗ uốn',xy=(c+15,hb-120),xytext=(-650,hb+150),fontsize=8,color='#548235',arrowprops=dict(arrowstyle='->',color='#548235'))
ax.set_xlim(-800,2700); ax.set_ylim(-1550,hb+450)
ax.set_title('Nút góc mái, e0/h > 0,5 (cột 17 – dầm 50): sơ đồ nguyên tắc cốt thép\n(minh hoạ, không theo tỉ lệ; chi tiết số lượng thép lấy theo bảng thống kê)',fontsize=9)
fig.savefig('/home/claude/build/figs/joint_corner_roof.png',dpi=190,bbox_inches='tight')
