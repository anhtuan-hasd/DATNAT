import math
Rb,Rs,Es,Eb=17.,435.,2e5,32500.
b,h,a=250.,600.,40.; h0=h-a
xiR=0.8/(1+(Rs/Es)/0.0035)
N,M=1514.38e3,417.74e6
As=1362.
# actual Is,D,eta
l0=3640.
I=b*h**3/12; Is=2*As*(h/2-a)**2
phiL=1+(18.06+1168.39*0.26)/(417.74+1514.38*0.26)
e0=M/N; de=e0/h; kb=0.15/(phiL*(0.3+de))
D=kb*Eb*I+0.7*Es*Is; Ncr=math.pi**2*D/l0**2; eta=1/(1-N/Ncr)
print("Is",Is,"D",D/1e9,"Ncr",Ncr/1e3,"eta",eta)
e=eta*e0+h/2-a; print("e",e)
x=(N+Rs*As*(1+xiR)/(1-xiR)-Rs*As)/(Rb*b+2*Rs*As/(h0*(1-xiR)))
print("x",x,"xi",x/h0,"xiR",xiR)
sig=Rs*(2*(1-x/h0)/(1-xiR)-1); print("sigma_s",sig)
Ne_cap=Rb*b*x*(h0-x/2)+Rs*As*(h0-a); print("Ne cap",Ne_cap/1e6,"Ne",N*e/1e6,"ratio",N*e/Ne_cap)
print("Mgh at N (M=Ne_cap/eta-style):",(Ne_cap - N*(h/2-a))/1e6, "vs eta*M", eta*M/1e6)
# out of plane
for LoverB in [l0/b]:
    phi=0.90-(LoverB-10)/5*(0.90-0.83); 
    Nu=phi*(Rb*b*h+Rs*2*As)/1e3
    print("L0/b",LoverB,"phi long-term",phi,"Nu",Nu)
# phi_n
sm=N/(b*h); print("sigma_m",sm,"0.25Rb",0.25*Rb,"0.75Rb",0.75*Rb)
print("Qb,min with phin=1.25:",0.5*1.25*1.15*b*h0/1e3)
# lap
for d in (16,18,20,22,25,28):
    L0=37.8*d
    print(d,round(L0),"tension 1.2:",round(1.2*L0),"comp 0.9:",round(0.9*L0),"min tens",round(max(0.4*1.2*L0,20*d,250)),"min comp",round(max(0.4*.9*L0,20*d,250)))
# bar areas
import itertools
print(math.pi*25**2/4, math.pi*22**2/4, math.pi*16**2/4)
mu=As/(b*h0); print("mu",mu*100,"mu_t actual with 2Ø16 constr",(2*As+2*201.06)/(b*h)*100)
# mu min interpolation
lam=l0/h; print("mu_min",0.1+(lam-5)/(25-5)*0.15)
