import sys
from PIL import Image
ims=[Image.open(p) for p in sys.argv[2:]]
W=max(i.width for i in ims); H=sum(i.height for i in ims)
m=Image.new('RGB',(W,H),'white'); y=0
for i in ims: m.paste(i,(0,y)); y+=i.height
m=m.resize((W//2,H//2)); m.save(sys.argv[1]); print(m.size)
