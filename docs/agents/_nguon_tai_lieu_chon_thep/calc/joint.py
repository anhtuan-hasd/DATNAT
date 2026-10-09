"""Kiểm tra hình học nút: thép dầm xuyên qua nút có lọt giữa thép dọc cột không.
Mặt phẳng khung: dầm chạy theo x, bề rộng dầm/cột b theo y. Thép dọc cột ở hai mặt đầu (x=±) có toạ độ y.
Thanh dầm (nằm ngang) cắt đường thẳng đứng của thanh cột => phải lọt khe giữa các thanh cột (theo y)."""
import itertools
def col_bars_y(bc, cover, d_st, dias):
    """dias: danh sách Ø thanh trên một mặt đầu, từ trái qua phải; góc ở hai đầu, các thanh giữa chia đều"""
    n=len(dias); y0=bc/2-cover-d_st-dias[0]/2
    ys=[-y0+i*(2*y0)/(n-1) for i in range(n)] if n>1 else [0]
    return list(zip(ys,dias))
def gaps(bars):
    g=[]
    for (y1,d1),(y2,d2) in zip(bars,bars[1:]):
        g.append(((y1+y2)/2, (y2-y1)-(d1+d2)/2))
    return g
def check(bc,dias_col,beam_layer_dias,cover=20,d_st=8,tol=10):
    cb=col_bars_y(bc,cover,d_st,dias_col); gp=gaps(cb)
    # xếp thanh dầm (một lớp) vào khe: mỗi khe lọt tối đa 1 thanh nếu khe >= d+2*tol
    need=sorted(beam_layer_dias,reverse=True); free=sorted([g for g in gp],key=lambda t:-t[1])
    ok=0; used=[]
    for d in need:
        for k,(yc,w) in enumerate(free):
            if w>=d+2*tol and k not in used: used.append(k); ok+=1; break
    return cb,gp,ok,len(need)
print('Cột 250x600, mỗi mặt 2Ø25+1Ø22 (Ø25,Ø22,Ø25):')
cb,gp,ok,n=check(250,[25,22,25],[25,22,25]); print(' thanh cột y:',[(round(y,1),d) for y,d in cb]); print(' khe:',[(round(y,1),round(w,1)) for y,w in gp]); print(' lọt',ok,'/',n,'thanh hàng ngoài dầm (3Ø: 25,22,25)')
print('  hàng trong 2Ø22:', check(250,[25,22,25],[22,22])[2],'/2')
for bc,dias in ((250,[25,22,25]),(300,[22,22,22,22]),(300,[25,22,22,25]),(350,[25,22,22,25]),(250,[28,28])):
    cb,gp,ok,n=check(bc,dias,[25,22,25]); print('bc',bc,dias,'khe',[round(w,1) for _,w in gp],'→ lọt',ok,'/3')
# tiết diện cột thép
import math
A=lambda d:math.pi*d*d/4
print('4Ø22 =',round(4*A(22)),' 2Ø25+2Ø22=',round(2*A(25)+2*A(22)),' 2Ø28=',round(2*A(28)))
