import math
A={d:math.pi*d*d/4 for d in (12,14,16,18,20,22,25,28,32)}
print({d:round(v,1) for d,v in A.items()})
combos=[(2,16),(3,16),(2,18),(3,18),(2,20),(3,20),(2,22),(3,22),(2,25),(3,25),(4,25),(2,28),(3,28)]
for n,d in combos: print(f"{n}Ø{d}",round(n*A[d]))
mix=[((2,20),(1,16)),((2,22),(1,20)),((2,25),(1,22)),((2,25),(1,20)),((2,25),(1,18)),((2,22),(1,18)),((2,20),(1,18)),((2,28),(1,25)),((2,28),(1,22))]
for (n1,d1),(n2,d2) in mix: print(f"{n1}Ø{d1}+{n2}Ø{d2}",round(n1*A[d1]+n2*A[d2]))
# b_min for n bars, clear 50, cover 20, stirrup 8
for d in (16,18,20,22,25,28,32):
    print(d,[round(2*(20+8)+n*d+(n-1)*max(50,d)) for n in (2,3,4,5)])
# interaction points
Rb,Rs=17.,435.; b,h,a=250.,600.,40.; h0=h-a; xiR=0.4933920704845815; As=1362.
def sig(x):
    xi=x/h0
    return Rs if xi<=xiR else max(-Rs,min(Rs,Rs*(2*(1-xi)/(1-xiR)-1)))
def pt(x):
    s=sig(x); xe=min(x,h)
    N=Rb*b*xe+Rs*As-s*As
    M=Rb*b*xe*(h/2-xe/2)+Rs*As*(h/2-a)+s*As*(h/2-a)
    return round(x,1),round(s),round(N/1e3,1),round(M/1e6,1)
for x in (2*a,0.5*xiR*h0,xiR*h0,1.3*xiR*h0,1.8*xiR*h0,h0,h):
    print(pt(x))
print("N0",(Rb*(b*h-2*As)+Rs*2*As)/1e3,"B",Rs*As*(h0-a)/1e6)
phi=0.92-(6.07-6)/(10-6)*0.02; print("phiN",phi, phi*(Rb*(b*h-2*As)+Rs*2*As)/1e3)
print("A's pt",(Rb*b*h+(Rs-Rb)*2*As)/1e3)
