import math, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import brentq
Rb,Rs,Es=17.0,435.0,200000.
b,h,a=250.,600.,40.; h0=h-a
xiR=0.8/(1+(Rs/Es)/0.0035)
N,M=1514.38e3,417.74e6
eta=1.045; e0=275.85; e=eta*e0+0.5*h-a
def sig(x):  # tension +, with As=As'
    xi=x/h0
    return Rs if xi<=xiR else max(-Rs,min(Rs,Rs*(2*(1-xi)/(1-xiR)-1)))
# solve x from As s.t. both equations; scan x
def As_from_N(x): # N = Rb b x + Rs As - sig As
    return (N-Rb*b*x)/(Rs-sig(x))
def res(x):
    As=As_from_N(x)
    return Rb*b*x*(h0-0.5*x)+Rs*As*(h0-a)-N*e
xs=np.linspace(60,560,2001); r=[res(x) for x in xs]
for i in range(len(xs)-1):
    if r[i]*r[i+1]<0:
        x=brentq(res,xs[i],xs[i+1]); print("exact x",x,"As",As_from_N(x))
# capacity diagram for As=As'=1362, a=40.
As=1362.
def pt(x):
    s=sig(x) if x<h0 else -Rs
    xe=min(x,h)
    N=min(Rb*b*xe+Rs*As-s*As,(Rb*(b*h-2*As)+Rs*2*As))
    Mc=Rb*b*xe*(h/2-xe/2)+Rs*As*(h/2-a)+s*As*(h/2-a)  # about centroid
    return N/1e3,Mc/1e6
pts=[(0.0,Rs*As*(h0-a)/1e6)]+[pt(x) for x in np.linspace(2*a,1.6*h,300)]+[((Rb*(b*h-2*As)+Rs*2*As)/1e3,0.0)]
# pure bending
def pureM():
    return None,(0.0,Rs*As*(h0-a)/1e6)
print("pure bending",pureM())
xb=xiR*h0; print("balanced",xb,pt(xb))
print("xE=0.2xiR h0",pt(0.2*xiR*h0),"xD=1.3 xiR h0",pt(1.3*xiR*h0))
N0=(Rb*b*h+(Rs-Rb)*2*As)/1e3 if False else (Rb*(b*h-2*As)+Rs*2*As)/1e3
print("N0 axial",N0)
# demand with eta
Md=eta*M/1e6; Nd=N/1e3
Ns=np.array([p[0] for p in pts]); Ms=np.array([p[1] for p in pts])
# capacity moment at N=Nd by interpolation on compression branch
idx=np.argsort(Ns); Mcap=np.interp(Nd,Ns[idx],Ms[idx]); print("Mcap at Nd",Mcap,"demand eta*M",Md,"ratio",Md/Mcap)
Md0=M/1e6; print("w/o eta",Md0/Mcap)
Mmax=Ms.max(); print("Mmax",Mmax, "N at Mmax",Ns[Ms.argmax()])
# plot
fig,ax=plt.subplots(figsize=(6.2,5.4),dpi=200)
ax.plot(Ms,Ns,color="#1f4e79",lw=2,label="Đường khả năng chịu lực (2Ø25+1Ø22 mỗi phía)")
ax.plot([0,0],[N0,N0],"k.")
ax.axhline(0,color="grey",lw=.6)
ax.plot(Md,Nd,"o",color="#c00000",ms=7,label=f"TH12: ηM = {Md:.1f} kNm; N = {Nd:.0f} kN")
ax.plot(M/1e6,Nd,"s",color="#e6a000",ms=6,label=f"TH12 (chưa nhân η): M = {M/1e6:.1f} kNm")
pp={"B":(0.0,Rs*As*(h0-a)/1e6),"E":pt(2*a),"F":pt(0.5*xb),"C":pt(xb),"D":pt(1.3*xb),"G":pt(h0),"A":(N0,0.0)}
for lab,p in pp.items():
    ax.plot(p[1],p[0],"^",color="#2e7d32"); ax.annotate(lab,(p[1],p[0]),textcoords="offset points",xytext=(6,4),fontsize=8)
ax.set_xlabel("M  (kN·m)"); ax.set_ylabel("N  (kN)  – nén dương")
ax.set_xlim(0,650); ax.set_ylim(-200,3800); ax.grid(alpha=.3); ax.legend(fontsize=7.5,loc="upper right")
ax.set_title("Biểu đồ tương tác N–M, cột 22 tầng 1 (250×600, B30, CB500-V)",fontsize=9)
plt.tight_layout(); plt.savefig("/home/claude/build/figs/interaction_c22.png"); print("saved")
