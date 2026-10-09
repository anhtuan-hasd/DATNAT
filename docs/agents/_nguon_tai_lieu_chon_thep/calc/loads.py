import math
# --- 1. sơ bộ
L1,L2=3.45,3.9
print("L2/L1=",L2/L1, " hb=",1.0/40*L1*1000)
for L in (6.9,):
    print("hd range",L/14*1000,L/10*1000)
# cột
S_B=(6.9/2+2.1/2)*3.9; N_B=6*10*S_B; F_B=1.3*N_B/17000
S_A=2.1/2*3.9; N_A=6*10*S_A; F_A=1.3*N_A/17000
print("S_B",S_B,"N_B",N_B,"F_B",F_B,"S_A",S_A,"N_A",N_A,"F_A",F_A)
print("lamb", 0.7*5.2/0.25)
# --- 2. tải đơn vị
def layers(ls):
    tc=sum(t*g for t,g,gf in ls if g); 
tab={
 'san':[(0.008,20,1.1),(0.020,18,1.3),(0.100,25,1.1),(0.020,18,1.3)],
 'wc':[(0.008,20,1.1),(0.040,18,1.3),(0.100,25,1.1),(0.020,18,1.3)],
 'mai':[(0.020,18,1.3),(0.100,25,1.1),(0.020,18,1.3)],
}
for k,v in tab.items():
    tc=sum(t*g for t,g,f in v); tt=sum(t*g*f for t,g,f in v)
    if k=='wc': tc+=0.75; tt+=0.75*1.1
    print(k,round(tc,3),round(tt,3),round(tt/tc,3))
# công xôn : mai + tôn 0.2
tc=0.02*18+2.5+0.02*18+0.2; tt=0.02*18*1.3+2.75+0.02*18*1.3+0.21; print('consol',tc,tt,tt/tc)
# tường
t220=(0.22*18+2*0.015*18, 0.22*18*1.1+2*0.015*18*1.3); print('t220',t220,t220[1]/t220[0])
t110=(0.11*18+2*0.015*18, 0.11*18*1.1+2*0.015*18*1.3); print('t110',t110,t110[1]/t110[0])
# --- 3. tải khung
g=3.38; gw=4.49; gm=3.22; gc=3.42
tri=lambda q,L: q*L/2
print("tầng2 CB: tường",4.5*3.2,"S1 tam giác (1 phía)",tri(g,3.45),"WC chữ nhật",tri(gw,1.95),"BA tam giác 2 phía",g*2.1,"AE tường110",2.52*0.7,"consol",tri(gc,2.1))
print("mái CB: tường+tôn",2.52*0.83+0.2*3.9/math.cos(math.radians(13)),"tam giác Sm1 2 phía",gm*3.45,"BA",2.52*0.3+0.2*3.9/math.cos(math.radians(13)),gm*2.1)
# GC tầng 2
bd=25*0.22*0.3*3.9; tw=4.5*3.6*3.9*0.7
s1=g*((3.9+(3.9-3.45))*(3.45/2))/2/2
wc=4.49*1.95*6.9/2/2
print("GC",bd,tw,s1,wc,bd+tw+s1+wc)
s2=g*((3.9+(3.9-2.1))*(2.1/2))/2
GB=bd+tw+s1+s2+wc; print("S2",s2,"GB",GB)
s4=3.42*((3.9+(3.9-2.1))*(2.1/2))/2/2; lc=2.52*0.9*3.9
print("GA t2",bd+s2+s4+lc, "S4",s4,"lan can",lc, "GA t3-6",bd+s2+lc)
GD=25*0.22*0.3*3.9/2+g*((3.9+(3.9-3.45))*(3.45/2))/2
print("GD",GD)
print("GE",25*0.22*0.3*3.9/2 + s4)
# mái
sen=3.22*0.8*3.9; tsn=25*0.08*0.6*3.9
print("sênô",sen,tsn, "GCm",bd*1.1+gm*((3.9+(3.9-3.45))*(3.45/2))/2+sen+tsn)
print("GCm detail", bd*1.1, gm*((3.9+(3.9-3.45))*(3.45/2))/2)
Sm2=gm*((3.9+(3.9-2.1))*(2.1/2))/2; print("Sm2",Sm2)
# hoạt
def hoat(p,Lx): return p*Lx/2
print("p S1",2*3.45/2,"p wc",2*1.95/2,"p BA",3*2.1,"p mái",0.3*2.1,"p consol",0.3*2.1/2)
print("PC",2*((3.9+(3.9-3.45))*(3.45/2))/2/2, 2*1.95*6.9/2/2)
print("PD",2*((3.9+(3.9-3.45))*(3.45/2))/2)
print("PA(t3,5)",3*((3.9+(3.9-2.1))*(2.1/2))/2, "mái",0.3*((3.9+(3.9-2.1))*(2.1/2))/2)
print("nước sênô",10*0.3*0.72*3.9)
# equivalent
b=lambda B1,L2:B1/(2*L2)
be=3.45/(2*3.9); print("beta",be,"kqd trapezoid",1-2*be**2+be**3)
# --- 4. gió
W0=1.55; aT=0.852; W3=aT*W0; z=25.05; zg=365.76; al=7
k=2.01*(z/zg)**(2/al); print("W3s10",W3,"k",k)
cD,cE,Gf=0.8,-0.59,0.85
WD=W3*k*cD*Gf; WE=W3*k*cE*Gf; print("WkD",WD,"WkE",WE,"qD",WD*3.9,"qE",WE*3.9)
print("T1",0.075*26.35**0.75)
for ce in (1.06,0.92,0.16,0.76):
    print("S ce",ce,W3*k*ce*Gf*1.2*3.9)
print("tt: ×2.1 =",WD*3.9*2.1, WE*3.9*2.1)
