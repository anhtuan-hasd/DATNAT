from dr import *
SER='Liberation Serif'
def sec(ax,x0,Z1v,Z2v,title,tens,comp_label):
    """tiết diện 250x500, khung đai 202x452; hai bên: minh hoạ mặt nén (gạch) và biên kéo"""
    b,h=250,500
    poly(ax,[(x0-b/2,-h/2),(x0+b/2,-h/2),(x0+b/2,h/2),(x0-b/2,h/2)],lw=LW_CON)
    stirrup(ax,x0-101,-226,x0+101,226,r=14,hook=True)
    # thép: đáy 2Ø20, đỉnh 2Ø14, mỗi bên 2Ø14 (giữa chiều cao)
    for x,y,d in ((-101+10+4,-226+10+4,20),(101-10-4,-226+10+4,20),(-101+7+4,226-7-4,14),(101-7-4,226-7-4,14),(-101+7+4,-3,14),(101-7-4,-3,14)):
        pass
    pts=[(-81,-206,20),(81,-206,20),(-90,206,14),(90,206,14),(-93,0,14),(93,0,14)]
    for x,y,d in pts: dot(ax,x0+x,y,d)
    ax.text(x0,-h/2-45,title,fontsize=8.5,ha='center',va='top',family=SER)
def fig():
    f,ax=new(8.2,3.9,(-260,260+720),(-390,300))
    sec(ax,0,202,452,'a) Mặt nén ở cạnh trên (hoặc dưới)\nbiên kéo = cạnh đáy: $Z_1=b$, $Z_2=h$',None,None)
    # đánh dấu vùng nén phía trên bằng nét đứt
    line(ax,[(-125,250),(125,250)],lw=2.2,c='0.5'); ax.text(0,262,'nén',fontsize=8,ha='center',va='bottom',family=SER)
    line(ax,[(-125,-250),(125,-250)],lw=2.2,c='k',ls=(0,(3,2))); ax.text(135,-250,'biên kéo (A$_{s1}$)',fontsize=8,ha='left',va='center',family=SER)
    dimh(ax,-101,101,300,'Z$_1$ = 202',tpos='above',fs=8,s=7)
    dimv(ax,-226,226,-150,'Z$_2$ = 452',side='left',fs=8,s=7)
    sec(ax,560,452,202,'b) Mặt nén ở cạnh bên\nbiên kéo = cạnh bên đối diện: $Z_1=h$, $Z_2=b$',None,None)
    line(ax,[(560-125,-250),(560-125,250)],lw=2.2,c='0.5'); ax.text(560-140,0,'nén',fontsize=8,ha='right',va='center',family=SER,rotation=90)
    line(ax,[(560+125,-250),(560+125,250)],lw=2.2,c='k',ls=(0,(3,2))); ax.text(560+170,180,'biên kéo\n(A$_{s1}$)',fontsize=8,ha='left',va='center',family=SER)
    dimv(ax,-226,226,560+150,'Z$_1$ = 452',side='right',fs=8,s=7)
    dimh(ax,560-101,560+101,300,'Z$_2$ = 202',tpos='above',fs=8,s=7)
    ax.plot([560+125],[0],marker='')
    f.savefig('out/htor.png',dpi=190,bbox_inches='tight',pad_inches=0.04,facecolor='white'); plt.close(f)
fig()
