import math
import numpy as np
Rb,Rs,Es,Eb=17.0,435.0,200000.,32500.
b,h,a=250.,600.,40.
h0=h-a; 
xiR=0.8/(1+(Rs/Es)/0.0035); aR=xiR*(1-0.5*xiR)
print("xiR,aR",xiR,aR)
M,N=417.74e6,1514.38e3
Mdh,Ndh=18.06e6,1168.39e3
l=5200.; l0=0.7*l
e1=M/N; ea=max(h/30,l/600,10); e0=max(e1,ea)
print("e1,ea,e0",e1,ea,e0,"l0/h",l0/h)
mu_t=0.02
Is=mu_t*b*h0*(0.5*h-a)**2; I=b*h**3/12
ML1=Mdh+Ndh*(0.5*h-a); ML=M+N*(0.5*h-a)
phiL=min(1+ML1/ML,2.0); de=min(max(e0/h,0.15),1.5)
kb=0.15/(phiL*(0.3+de))
D=kb*Eb*I+0.7*Es*Is
Ncr=math.pi**2*D/l0**2
eta=1/(1-N/Ncr)
print("Is",Is,"phiL",phiL,"de",de,"kb",kb,"D kNm2",D/1e9,"Ncr kN",Ncr/1e3,"eta",eta)
e=eta*e0+0.5*h-a
x1=N/(Rb*b); print("x1",x1,"xiR h0",xiR*h0,"e",e)
# A empirical
n=N/(Rb*b*h0); eps=e/h0; ap=a/h0; al=e/h0  # careful
# A: n=N/(Rb b h0); eps=a'/h0 ; a=e0'/h0 ... use A's: "a = e/h0"? try
delta=a/h0
ae=e/h0
x_emp=h0*((1-xiR)*n+2*xiR*(ae*n-0.48))/((1-xiR)+2*(ae*n-0.48)) if False else None
# A formula: x = h0*[(1-xiR) a n + 2 xiR (n-0.48)]/[(1-xiR) a + 2 (n-0.48)] with n=Ne/(Rb b h0^2), a=?? 
n2=N*e/(Rb*b*h0**2)  # 'n' in A seems Ne/(Rb b h0^2)? test
print("n(N/Rbbh0)",n,"Ne/(Rbbh0^2)",n2)
def Aemp(nn,aa): return h0*((1-xiR)*aa*nn+2*xiR*(nn-0.48))/((1-xiR)*aa+2*(nn-0.48))
for (nn,aa) in [(n,e/h0),(n2,n)]: print("try",nn,aa,Aemp(nn,aa))
# D method (6.22) symmetric
alpha_n=n
am1=(N*e - 0)/(Rb*b*h0**2)  # = [M*eta + N/2 (h0-a')]/(Rb b h0^2)
am1b=(eta*e0*N+0.5*N*(h0-a))/(Rb*b*h0**2)
xi1=min((alpha_n+xiR)/2,1)
als=(am1b-xi1*(1-xi1/2))/(1-delta)
xi=(alpha_n*(1-xiR)+2*als*xiR)/(1-xiR+2*als)
x=xi*h0
As=Rb*b*h0/Rs*(am1b-xi*(1-xi/2))/(1-delta)
print("D: am1",am1b,"xi1",xi1,"als",als,"xi",xi,"x",x,"As",As)
# A: As via x=326 
for xx in (326, x):
    print("As from x",xx,(N*e-Rb*b*xx*(h0-0.5*xx))/(Rs*(h0-a)))
# iterate exact: solve x s.t. N = Rb b x + Rsc As' - sigma_s As with As=As' ; M eq via N e
def sig(x,As):
    xi=x/h0
    s=Rs*(2*(xi-xiR)/(1-xiR)-1) if xi>xiR else Rs
    s=max(-Rs,min(Rs,s)) ; return s
import scipy.optimize as so
def Asreq(xsol):
    pass
# exact: unknown As,x : N=Rb b x+Rs As - s As ; Ne = Rb b x (h0-.5x)+Rs As (h0-a)
def f(v):
    x,As=v
    return [Rb*b*x+Rs*As-sig(x,As)*As-N, Rb*b*x*(h0-0.5*x)+Rs*As*(h0-a)-N*e]
sol=so.fsolve(f,[300,1200]); print("exact(x,As)",sol)
