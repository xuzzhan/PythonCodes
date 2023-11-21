
#通过三点直接求面积
def calc_area(p1, p2, p3):
        (x1, y1), (x2, y2), (x3, y3) = p1,p2,p3
        return 0.5 * abs(x2 * y3 + x1 * y2 + x3 * y1 - x3 * y2 - x2 * y1 - x1 * y3)

#通过面积反推求点到线距离
def shortestdis_xy(pointlist, line_point1, line_point2):

    if line_point1==line_point2:
        return np.array([1 if i !=(len(pointlist)//2) else 10 for i in range(len(pointlist)) ]), 1
    else:
        Slist = np.array( [ calc_area(point, line_point1, line_point2) for point in pointlist] )
        l = np.sqrt(np.sum(np.square(   np.array(line_point1)-np.array(line_point2)   )))       
        hlist= 2*Slist/l
        return hlist,l

def digui(seqpoint_np):
    trylist =[]
    if len(seqpoint_np)==2:
        # print(seqpoint_np)
         trylist.append(seqpoint_np)
         return trylist
    elif len(seqpoint_np)>2:
        distancearray,d = shortestdis_xy(seqpoint_np,seqpoint_np[0],seqpoint_np[-1])
        x = distancearray.max()
        xd=x/d
        # print(xd)
        if xd < 0.15 :
            # print(seqpoint_np)
            trylist.append(seqpoint_np)
            return trylist
            
        else:
            index=distancearray.argmax()
            # print(index)
            trylist.extend(digui(seqpoint_np[:(index+1)]))
            trylist.extend(digui(seqpoint_np[index:]))
            return trylist
            # return digui(seqpoint_np[:(index+1)]),digui(seqpoint_np[index:])
    else:
        return 'onlyone'

from shapely.ops import nearest_points
import geopandas as gpd
import numpy as np
from shapely.geometry import LineString


temp = gpd.read_file(r"C:\Users\xuzzh\Desktop\gistemp\road.shp")
geometrylist = np.array(temp['geometry'])

geometrylistnew = []
meanxd=0.015

for j in range(len(geometrylist)):
    seqpoint =geometrylist[j].coords
    seqpoint_np = [seqpoint[i] for i in range(len(seqpoint))]
    linepointlist = digui(seqpoint_np)
    linelist = [LineString([i[0],i[-1]]) for i in linepointlist]
    geometrylistnew.extend(linelist)
    print(len(linelist))

s =gpd.GeoSeries(geometrylistnew)
s.to_file(r"C:\Users\xuzzh\Desktop\gistemp\segment_road.shp") 
