import math
# Dầm biên 250x500, B30, CB240-T Ø8 (Rsw=170), CB500-V dọc (Rs=435). Số liệu GIẢ ĐỊNH để minh hoạ.
Rb,Rbt,Rs,Rsw=17,1.15,435,170
b,h,cov,dst=250,500,20,8
Asw1=math.pi*8**2/4
# kích thước khung đai (tâm đai)
Zb=b-2*(cov+dst/2); Zh=h-2*(cov+dst/2)
print('Zb,Zh',Zb,Zh,'Asw1',round(Asw1,1))
T=10e6; Q=60e3; M=80e6
# 7.21
print('0.1Rb b^2 h = %.1f kN.m'%(0.1*Rb*b*b*h/1e6))
def Tgh(q,As1,Z1,Z2):
    d=Z1/(2*Z2+Z1); r=q*Z1/(Rs*As1)
    if r<0.5: return q*Z1*Z2*(d+1),r,d,'7.34'
    if r<=1.5: return q*d*Z1*Z2+0.5*Rs*As1*Z2,r,d,'7.33'
    return 0.5*Rs*As1*Z2*(3*d+1),r,d,'7.35'
# thiết kế đai nhỏ nhất (vùng r<=0.5): q = T/(Z1 Z2 (1+δ)) cho mặt nén là cạnh b (Z1=Zb,Z2=Zh)
for nm,(Z1,Z2) in (('nén ở mặt trên/dưới (Z1=b,Z2=h)',(Zb,Zh)),('nén ở mặt bên (Z1=h,Z2=b)',(Zh,Zb))):
    d=Z1/(2*Z2+Z1); q=T/(Z1*Z2*(1+d)); As1min=2*q*Z1/Rs
    print(nm,'δ=%.4f q=%.1f N/mm  s(Ø8)=%.0f  As1>=%.0f'%(d,q,Rsw*Asw1/q,As1min))
# chọn a60
s=60; q=Rsw*Asw1/s; print('q(a60)=%.1f'%q)
# thép dọc: đáy 2Ø20 (628), đỉnh 2Ø14 (308), mỗi bên 2Ø14 (308)
As_bot=2*math.pi*100; As_top=2*math.pi*49; As_side=2*math.pi*49
for nm,(Z1,Z2,As1) in (('nén mặt trên → biên kéo = đáy',(Zb,Zh,As_bot)),('nén mặt dưới → biên kéo = đỉnh',(Zb,Zh,As_top)),('nén mặt bên → biên kéo = cạnh bên đối diện',(Zh,Zb,As_side))):
    t,r,d,f=Tgh(q,As1,Z1,Z2); print(nm,'As1=%.0f r=%.3f δ=%.3f Tgh=%.2f kN.m (%s)'%(As1,r,d,t/1e6,f))
# 7.36 : Mgh
x=Rs*As_bot/(Rb*b); Mgh=Rs*As_bot*(460-x/2); print('x=%.1f Mgh=%.1f kN.m'%(x,Mgh/1e6))
Tg=Tgh(q,As_bot,Zb,Zh)[0]
print('7.36: Tgh*sqrt(1-(M/Mgh)^2)=%.2f'%(Tg/1e6*math.sqrt(1-(M/Mgh)**2)))
# 7.37
h0=460; print('7.37: %.2f'%(0.1*Rb*b*b*h*(1-Q/(0.3*Rb*b*h0))/1e6))
# 7.38
Qgh=(0.5*Rbt*b+Rsw*2*Asw1/s)*h0; print('Qgh=%.1f kN ; 7.38: %.2f'%(Qgh/1e3,Tg/1e6*(1-Q/Qgh)))
# xem a=?? nếu a100
for s2 in (100,80,60):
    q2=Rsw*Asw1/s2; Tg2=Tgh(q2,As_bot,Zb,Zh)[0]; Qg2=(0.5*Rbt*b+Rsw*2*Asw1/s2)*h0
    print('a%d: Tgh=%.2f ; 7.36=%.2f ; 7.38=%.2f'%(s2,Tg2/1e6,Tg2/1e6*math.sqrt(1-(M/Mgh)**2),Tg2/1e6*(1-Q/Qg2)))
