import math
# Dữ liệu dầm CB (Chương 11)
L=6900; col=600; fc=300
MC,MB,QB=-462.37,-434.67,240.3
b,h=250,700
Rs=435
# xấp xỉ tải phân bố đều tương đương từ MC, MB, QB (chỉ dùng cho minh hoạ vị trí cắt)
Lm=L/1000
qL=2*(MB-MC+QB*Lm)/Lm; q=qL/Lm; QC=qL-QB
print('q=%.2f kN/m  QC=%.1f'%(q,QC))
def x_at(M0,Q0,Mt):   # |M|=Mt từ đầu có M0 (âm), Q0 (dốc), tải q
    a=q/2; B=-Q0; C=-(M0+Mt)
    return (-B-math.sqrt(B*B-4*a*C))/(2*a)
xC=x_at(MC,QC,260.2); xB=x_at(MB,QB,260.2)
print('x_th C=%.3f  B=%.3f'%(xC,xB))
qsw=113.9; W=lambda Q,d: Q*1000/(2*qsw)+5*d
print('W22 (Qmax)=',W(240.3,22), ' 20d=',20*22)
for nm,x0 in (('C',xC),('B',xB)):
    print(nm,'cắt cách tim',x0*1000+1165)
# thép
As25,As22=490.9,380.1
print('Lan25 full', 37.8*25, 'x0.919=',37.8*25*1950/2122, 'Lan22', 37.8*22*1950/2122)
# trọng lượng đơn vị
for d in (8,12,14,16,18,22,25): print(d, round(0.00617*d*d,3))
# đai
n1=int((1725-50)//150)+1; print('n1',n1,'last',300+50+(n1-1)*150)
mid=list(range(2250,4800,250)); print('mid',mid,len(mid))
# kiểm tra Mu sau khi cắt 3Ø22 : còn 2Ø25
# cột
print('b0',250-2*20-8,'l_cr',max(600,(5200-700)/6,450))
