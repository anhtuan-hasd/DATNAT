import math
Rb,Rbt,Rs,Rsc,Rsw,Es=17.0,1.15,435.0,435.0,170.0,2e5
xiR=0.8/(1+(Rs/Es)/0.0035); aR=xiR*(1-0.5*xiR)
print("xiR",xiR,"aR",aR,"mumax%",xiR*Rb/Rs*100)
area=lambda d: math.pi*d*d/4
for d in (8,10,12,14,16,18,20,22,25,28,32): print(d,round(area(d),1),end=' | ')
print()
def flex(M,b,h0,bf=None,hf=None,label=''):
    bb=bf if bf else b
    am=M*1e6/(Rb*bb*h0**2); xi=1-math.sqrt(1-2*am); As=xi*Rb*bb*h0/Rs
    print(label,"M",M,"b",bb,"h0",h0,"am",round(am,4),"xi",round(xi,4),"x",round(xi*h0,1),"As",round(As,1),"mu%",round(As/(b*h0)*100,3))
    return As
# CB support
flex(462.37,250,645,label='CB gối C a=55')
flex(434.67,250,645,label='CB gối B')
# nhịp T
Sf=min((3900-220)/2,6620/6); print("Sf",Sf, 'bf', 250+2*1100)
Mf=Rb*2450*100*(660-50)/1e6; print("Mf",Mf)
flex(315.47,250,660,bf=2450,label='CB nhịp T h0=660')
flex(315.47,250,645,bf=2450,label='CB nhịp T h0=645')
flex(315.47,250,660,label='CB nhịp rect (đối chứng)')
# actual layout capacity CB gối: 2Ø25+1Ø22 top row (y=40.5 /39), 2Ø22 second row
c=20;ds=8
y1=c+ds+25/2; 
# second row: clear 25 under 25mm bars
y2=c+ds+25+25+22/2
A1=2*area(25)+area(22); A2=2*area(22)
a=(A1*y1+A2*y2)/(A1+A2); h0=700-a
print("a",a,"h0",h0,"A",A1+A2)
As=A1+A2; x=Rs*As/(Rb*250); Mu=Rs*As*(h0-x/2)/1e6; print("x",x,"Mu",Mu,"x/h0",x/h0,"xiR",xiR)
# nhịp 3Ø22 one row
As=3*area(22); y=c+ds+11; h0n=700-y; x=Rs*As/(Rb*2450); Mu=Rs*As*(h0n-x/2)/1e6; print("nhịp 3Ø22 h0",h0n,"As",As,"x",x,"Mu",Mu)
# cắt: 2Ø25 only (top, single row)
As2=2*area(25); h02=700-(c+ds+12.5); x=Rs*As2/(Rb*250); Mu2=Rs*As2*(h02-x/2)/1e6; print("2Ø25 top: h0",h02,"x",x,"Mu",Mu2)
# shear CB
def shear(Q,b,h0,Asw,hh,label=''):
    Qmax=0.3*Rb*b*h0; Qbmin=0.5*Rbt*b*h0
    smax=Rbt*b*h0**2/(Q*1e3)
    qsw=(Q*1e3)**2/(4.5*Rbt*b*h0**2); qmin=0.25*Rbt*b
    q=max(qsw,qmin); stt=Rsw*Asw/q
    sct=min(h0/2,300)
    C0=math.sqrt(2*Rbt*b*h0**2/q); C=min(max(C0,h0),2*h0)
    Qu=1.5*Rbt*b*h0**2/C+0.75*q*C
    print(label,"0.3Rbbh0",round(Qmax/1e3,1),"Qbmin",round(Qbmin/1e3,2),"smax",round(smax,1),"qsw",round(qsw,2),"q_min",qmin,"stt",round(stt,1),"sct",sct,"C0",round(C0,0),"C",round(C,0),"Qu",round(Qu/1e3,1))
    return q
shear(240.3,250,645,100.5,700,'CB')
# với s=150 actual
for s in (150,):
    q=Rsw*100.5/s; C=min(2*645,max(645,math.sqrt(2*Rbt*250*645**2/q))); print("actual qsw",q,"Qu",(1.5*Rbt*250*645**2/C+0.75*q*C)/1e3)
shear(117.99,250,360,100.5,400,'BA h0=360')
q=Rsw*100.5/150; C=min(720,max(360,math.sqrt(2*Rbt*250*360**2/q))); print("BA actual qsw",q,"Qu",(1.5*Rbt*250*360**2/C+0.75*q*C)/1e3)
# bf BA
print("BA Sf",min(1840,2100/6)); bf=250+2*350
Mf=Rb*bf*100*(360-50)/1e6; print("Mf BA",Mf)
flex(99.37,250,360,bf=bf,label='BA nhịp T')
flex(106.99,250,360,label='BA gối B')
flex(35.43,250,360,label='console')
print("console Qbmin",0.5*Rbt*250*360/1e3)
# hanger
F=15.9*1.15+7.5*1.3; hs=645-270; Awsw=F*(1-hs/645)*1e3/Rsw; print("F",F,"Asw",Awsw,"zone a",2*hs+220, "n đai",Awsw/100.5)
# W
q=Rsw*100.5/150; print("W",240300/(2*q)+5*22, "20d",20*22)
# anchorage
Rbond=2.5*1.0*Rbt; 
for d,Ascal,Asef in ((16,297,402.1),):
    L0=Rs*area(d)/(Rbond*math.pi*d); print("L0an",L0,"Lan",L0*Ascal/Asef,"15d",15*d)
for d in (16,18,20,22,25,28):
    L0=Rs*area(d)/(Rbond*math.pi*d); print(d,"L0an",round(L0), "λ=L0/d",round(L0/d,1))
