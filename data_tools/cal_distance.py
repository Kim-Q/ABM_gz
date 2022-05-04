import numpy as np

# 用于计算地球上两点之间的直线距离
def cal_distance(l1,l2):
    distance=None 
    #椭球体参数，采用NAD83
    a=6378137 #半长轴 
    f=1/298.257222101 #逆扁平率 
    b=abs((f*a)-a) #半短轴 
    lon1,lat1=l1[0],l1[1]
    lon2,lat2=l2[0],l2[1]

    L=np.radians(lon1-lon2) 
    U1=np.arctan((1-f)*np.tan(np.radians(lat1)))
    U2=np.arctan((1-f)*np.tan(np.radians(lat2)))
    sinU1=np.sin(U1) 
    cosU1=np.cos(U1)
    sinU2=np.sin(U2)
    cosU2=np.cos(U2)
    lam=L 
    for i in range(100):
        sinLam=np.sin(lam)
        cosLam=np.cos(lam)     
        sinSigma=np.sqrt((cosU2*sinLam)**2+(cosU1*sinU2-sinU1*cosU2*cosLam)**2)  
        if sinSigma==0:         
            distance=0 #重合点         
            break     
        cosSigma=sinU1*sinU2+cosU1*cosU2*cosLam     
        sigma=np.arctan2(sinSigma,cosSigma)
        sinAlpha=cosU1*cosU2*sinLam/sinSigma    
        cosSqAlpha=1-sinAlpha**2     
        cos2SigmaM=cosSigma-2*sinU1*sinU2/cosSqAlpha    
        if np.isnan(cos2SigmaM):         
            cosSigmaM=0 #赤道线     
        C=f/16*cosSqAlpha*(4+f*(4-3*cosSqAlpha))    
        LP=lam    
        lam=L+(1-C)*f*sinAlpha*(sigma+C*sinSigma*(cos2SigmaM+C*cosSigma*(-1+2*cos2SigmaM*cos2SigmaM)))    
        if not abs(lam-LP) > 1e-12:         
            break 
        uSq=cosSqAlpha*(a**2-b**2)/b**2 
        A=1+uSq/16384*(4096+uSq*(-768+uSq*(320-175*uSq))) 
        B=uSq/1024*(256+uSq*(-128+uSq*(74-47*uSq)))
        deltaSigma=B*sinSigma*(cos2SigmaM+B/4*(cosSigma*(-1+2*cos2SigmaM*cos2SigmaM)-B/6*cos2SigmaM*(-3+4*sinSigma*sinSigma)*(-3+4*cos2SigmaM*cos2SigmaM)))

        s=b*A*(sigma-deltaSigma)
        distance=s
    return distance