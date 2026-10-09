import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch
b,h=250,600
fig,ax=plt.subplots(figsize=(4.2,6.4),dpi=200)
ax.add_patch(Rectangle((0,0),b,h,fc="#f2f2f2",ec="k",lw=1.6))
c=20; st=8
# main stirrup (centerline)
ax.add_patch(Rectangle((c+st/2,c+st/2),b-2*c-st,h-2*c-st,fc="none",ec="#1f4e79",lw=1.8))
# bars: top face and bottom face: 2Ø25 at corners + Ø22 mid
def bar(x,y,d,col): ax.add_patch(Circle((x,y),d/2,fc=col,ec="k",lw=.8))
xs=[c+st+25/2, b/2, b-c-st-25/2]
for y in (c+st+25/2, h-c-st-25/2):
    bar(xs[0],y,25,"#c00000"); bar(xs[2],y,25,"#c00000"); bar(xs[1],y,22,"#e6a000")
# construction bars Ø16 at mid-height on long faces
ym=h/2
bar(c+st+16/2,ym,16,"#2e7d32"); bar(b-c-st-16/2,ym,16,"#2e7d32")
# cross tie (đai phụ) between the two Ø16
ax.plot([c+st+16/2,b-c-st-16/2],[ym,ym],color="#7030a0",lw=1.8,ls="--")
# dims
ax.annotate("",xy=(0,-30),xytext=(b,-30),arrowprops=dict(arrowstyle="<->")); ax.text(b/2,-60,"250",ha="center",fontsize=8)
ax.annotate("",xy=(-30,0),xytext=(-30,h),arrowprops=dict(arrowstyle="<->")); ax.text(-50,h/2,"600",va="center",rotation=90,fontsize=8)
ax.text(b/2,h+25,"3 thanh/phía: 2Ø25 + 1Ø22",ha="center",fontsize=7.5,color="#c00000")
ax.text(b/2,-95,"đai chính Ø8 (xanh dương) + đai phụ Ø8 (tím nét đứt) giữ 2Ø16 cấu tạo",ha="center",fontsize=6.8)
ax.text(b+18,ym,"1Ø16\ncấu tạo\n(mỗi cạnh dài)",fontsize=6.5,va="center",color="#2e7d32")
ax.annotate("",xy=(0,h+8),xytext=(0,h+8))
ax.text(-45,-5,"lớp bảo vệ 20 mm",fontsize=6,rotation=0,alpha=0)
ax.set_xlim(-80,b+110); ax.set_ylim(-120,h+60); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("Mặt cắt cột 22 (250×600) – bố trí thép",fontsize=9)
plt.tight_layout(); plt.savefig("/home/claude/build/figs/col22_section.png"); print("ok")
