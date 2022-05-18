import numpy as np
import sys
import math as m
import random as ran

y_ax = int(sys.argv[1]) -1
x_ax = int(sys.argv[2]) -1

#Defining function to test the input point
def self_test(self, m_id):
    if self[0] < 0 or self[0] >= y_ax or self[1] < 0 or self[1] >= x_ax:
        return "oob"
    else:
        return m_id[self[0]][self[1]]
#Defining function to test point adjacency, output list element order is L R U D
def adj_test(self, m_id, subject):
    results = []
    #Test left
    if self[1] - 1 < 0:
        results.append("oob")
    elif m_id[self[0]][self[1] - 1] == subject:
         #print m_id[self[0]][self[1] - 1]
         results.append(True)
    else:
        results.append(False)
    #Test right
    if self[1] + 1 >= x_ax:
        results.append("oob")
    elif m_id[self[0]][self[1]+1] == subject:
        results.append(True)
    else:
        results.append(False)
    #Test up
    if self[0] + 1 >= y_ax:
        results.append("oob")
    elif m_id[self[0]+1][self[1]] == subject:
        results.append(True)
    else:
        results.append(False)
    #Test down
    if self[0] - 1 < 0:
        results.append("oob")
    elif m_id[self[0]-1][self[1]] == subject:
        results.append(True)
    else:
        results.append(False)
    return results
#define self_test that tests left, up and diag
def cr_test(self, m_id, subject):
    results = []
    #Test right
    if self[1] + 1 >= x_ax:
        results.append("oob")
    elif m_id[self[0]][self[1]+1] == subject:
        results.append(True)
    else:
        results.append(False)
    #Test up
    if self[0] + 1 >= y_ax:
        results.append("oob")
    elif m_id[self[0]+1][self[1]] == subject:
        results.append(True)
    else:
        results.append(False)
    #Test down
    if self[0] - 1 < 0:
        results.append("oob")
    elif m_id[self[0]+1][self[1]+1] == subject:
        results.append(True)
    else:
        results.append(False)
    return results
#Define function to generate correct reception size
rs = [3,4] #reception size, determined by user
def genrec(region, m_id, size):
    rb = []
    rc = []
    counter = 0
    while counter < 50 :
        chosen_id = region[ran.randint(0,len(region)-1)]
        counter += 1
        if len(rb) >= 12:
            counter += 50
        else:
            for i in range(size[0]):
                if self_test([chosen_id[0] + i,chosen_id[1]], m_id) == "oob":
                    continue
                else:
                    for j in range(size[1]):
                        if self_test([chosen_id[0],chosen_id[1] + j], m_id) == "oob":
                            continue
                        else:
                            m_id[chosen_id[0] + i][chosen_id[1] + j] = "R"
                            rb.append([chosen_id[0] + i, chosen_id[1] + j])
                            if i == 0 and j == 0: 
                                rc.append([chosen_id[0] + i, chosen_id[1] + j])
                            elif i == 0 and j == size[1]-1:
                                rc.append([chosen_id[0] + i, chosen_id[1] + j])
                            elif i == size[0]-1 and j == 0:
                                rc.append([chosen_id[0] + i, chosen_id[1] + j])
                            elif i == size[0]-1 and j == size[1] - 1 :
                                rc.append([chosen_id[0] + i, chosen_id[1] + j])
                            else:
                                continue
    return m_id, rb, rc

#Defining function to test if corridors are connected to a valid space ("0", "1")
def valid_cor(m_id):
    valid = None
    for y in range(len(m_id)):
      for x in range(len(m_id[y])):
        bool_list = adj_test([y,x],m_id,"0") + adj_test([y,x],m_id,"1")
        #print (bool_list)
        if bool_list.count(True) < 2:
          valid = False
          return valid
          break
        else:
          valid = True
          return valid

#Define cluster type 1: double loaded corridor
def conrm1(self, m_id, rotate):
    #create consultation room matrix
    original_mid = m_id #store original matrix ID to revert when required
    counter = 0
    clusterid = []
    clustersize = [6,5]
    cluster1 = [["C","C","1","C","C"],["C","C","1","C","C"],["C","C","1","C","C"],["C","C","1","C","C"],["C","C","1","C","C"],["C","C","1","C","C"]]
    valid = None
    for y in range(clustersize[0]):
        for x in range(clustersize[1]):
            if self_test([self[0]+y,self[1]+x],m_id) != "0":
                valid = False
                break
    if (self[0]+clustersize[0]) > len(m_id) or (self[1]+clustersize[1]) > len(m_id[0]):
        pass
    elif valid is False:
        pass
    else:
        for y in range(clustersize[0]):
            for x in range(clustersize[1]):
                m_id[self[0]+y][self[1]+x] = cluster1[y][x]
                counter += 1
                clusterid.append([(self[0]+y),(self[1]+x)])
        #print(rotate)
        if rotate == 0:
            pass
        else:
            for i in range(rotate):
                #print("rotation" + str(i+1))
                rotation = rotatecluster(self, m_id, clustersize,clusterid)
                clusterid = rotation[1]
                self = rotation[2]
            clusterid = rotation[1]
        valid = True
    if counter < 30:
        pass
    validtest = valid_cor(m_id)
    if validtest == False:
        valid = False
        m_id = original_mid
    return m_id, clusterid, valid

#Define cluster type 2: single loaded corridor
def conrm2(self, m_id, rotate):
    #create consultation room matrix
    original_mid = m_id #store original matrix ID to revert when required
    counter = 0
    clusterid = []
    clustersize = [3,4]
    cluster1 = [["C","C","C","C"],["C","C","C","C"],["1","1","1","1"]]
    valid = None
    for y in range(clustersize[0]):
        for x in range(clustersize[1]):
            if self_test([self[0]+y,self[1]+x],m_id) != "0":
                valid = False
                break
    if (self[0]+clustersize[0]) > len(m_id) or (self[1]+clustersize[1]) > len(m_id[0]):
        pass
    elif valid is False:
        pass
    else:
        for y in range(clustersize[0]):
            for x in range(clustersize[1]):
                m_id[self[0]+y][self[1]+x] = cluster1[y][x]
                counter += 1
                clusterid.append([(self[0]+y),(self[1]+x)])
        #print(rotate)
        if rotate == 0:
            pass
        else:
            for i in range(rotate):
                #print("rotation" + str(i+1))
                rotation = rotatecluster(self, m_id, clustersize,clusterid)
                clusterid = rotation[1]
                self = rotation[2]
            clusterid = rotation[1]
        valid = True
    if counter < 30:
        pass
    validtest = valid_cor(m_id)
    if validtest == False:
        valid = False
        m_id = original_mid
    return m_id, clusterid, valid

#generate type 3: corner
def conrm3(self, m_id, rotate):
    #create consultation room matrix
    original_mid = m_id #store original matrix ID to revert when required
    counter = 0
    clusterid = []
    clustersize = [4,4]
    cluster1 = [["C","C","1","0"],["C","C","1","1"],["0","0","C","C"],["0","0","C","C"]]
    valid = None
    for y in range(clustersize[0]):
        for x in range(clustersize[1]):
            if self_test([self[0]+y,self[1]+x],m_id) != "0":
                valid = False
                break
    if (self[0]+clustersize[0]) > len(m_id) or (self[1]+clustersize[1]) > len(m_id[0]):
        pass
    elif valid is False:
        pass
    else:
        for y in range(clustersize[0]):
            for x in range(clustersize[1]):
                m_id[self[0]+y][self[1]+x] = cluster1[y][x]
                counter += 1
                clusterid.append([(self[0]+y),(self[1]+x)])
        #print(rotate)
        if rotate == 0:
            pass
        else:
            for i in range(rotate):
                #print("rotation" + str(i+1))
                rotation = rotatecluster(self, m_id, clustersize,clusterid)
                clusterid = rotation[1]
                self = rotation[2]
            clusterid = rotation[1]
        valid = True
    if counter < 30:
        pass
    validtest = valid_cor(m_id)
    if validtest == False:
        valid = False
        m_id = original_mid
    return m_id, clusterid, valid

#defines which cluster to instantiate
def clustertype(gen_id,m_id,rotation,type):
  if type == 1:
    return conrm1(gen_id,m_id,rotation)
  elif type == 2:
    return conrm2(gen_id,m_id,rotation)
  elif type == 3:
    return conrm3(gen_id,m_id,rotation)

#generate Toilet: Handicap
def toiletH(self, m_id, rotate):
    #create toilet matrix
    original_mid = m_id #store original matrix ID to revert when required
    counter = 0
    clusterid = []
    clustersize = [3,1]
    cluster1 = [["T"],["T"],["1"]]
    valid = None
    for y in range(clustersize[0]):
        for x in range(clustersize[1]):
            if self_test([self[0]+y,self[1]+x],m_id) != "0":
                valid = False
                break
    if (self[0]+clustersize[0]) > len(m_id) or (self[1]+clustersize[1]) > len(m_id[0]):
        pass
    elif valid is False:
        pass
    else:
        for y in range(clustersize[0]):
            for x in range(clustersize[1]):
                m_id[self[0]+y][self[1]+x] = cluster1[y][x]
                counter += 1
                clusterid.append([(self[0]+y),(self[1]+x)])
        #print(rotate)
        if rotate == 0:
            pass
        else:
            for i in range(rotate):
                #print("rotation" + str(i+1))
                rotation = rotatecluster(self, m_id, clustersize,clusterid)
                clusterid = rotation[1]
                self = rotation[2]
            clusterid = rotation[1]
        valid = True
    if counter < 30:
        pass
    validtest = valid_cor(m_id)
    if validtest == False:
        valid = False
        m_id = original_mid
    #remove "i" from clusterid
    testclusterid = []
    for i in range(len(clusterid)):
        if m_id[clusterid[i][0]][clusterid[i][1]] != "1":
            testclusterid.append(clusterid[i])
    clusterid = testclusterid
    return m_id, clusterid, valid

#generate Toilet:
def toilet(self, m_id, rotate):
    #create toilet matrix
    original_mid = m_id #store original matrix ID to revert when required
    counter = 0
    clusterid = []
    clustersize = [4,3]
    cluster1 = [["T","T","1"],["T","T","1"],["T","T","1"],["T","T","1"]]
    valid = None
    for y in range(clustersize[0]):
        for x in range(clustersize[1]):
            if self[0]+y > y_ax or self[1]+x > x_ax:
              valid = False
              break
            elif self_test([self[0]+y,self[1]+x],m_id) != "0":
                valid = False
                break
    if (self[0]+clustersize[0]) > y_ax or (self[1]+clustersize[1]) > x_ax:
        pass
    elif valid is False:
        pass
    else:
        for y in range(clustersize[0]):
            for x in range(clustersize[1]):
                m_id[self[0]+y][self[1]+x] = cluster1[y][x]
                counter += 1
                clusterid.append([(self[0]+y),(self[1]+x)])
        #print clusterid
        if rotate == 0:
            pass
        else:
            for i in range(rotate):
                #print("rotation" + str(i+1))
                rotation = rotatecluster(self, m_id, clustersize,clusterid)
                clusterid = rotation[1]
                self = rotation[2]
            clusterid = rotation[1]
        #print "toilet cluster id = " + str(clusterid)
        valid = True
    if counter < 30:
        pass
    validtest = valid_cor(m_id)
    if validtest == False:
        valid = False
        m_id = original_mid
    #remove "i" from clusterid
    testclusterid = []
    for i in range(len(clusterid)):
        if m_id[clusterid[i][0]][clusterid[i][1]] != "1":
            testclusterid.append(clusterid[i])
    clusterid = testclusterid
    return m_id, clusterid, valid


#define rotating function to rotate cluster
def rotatecluster(self, m_id, clustersize, clusterid):
    m_size = []
    m_size.append(clustersize[0])
    m_size.append(clustersize[1])
    rm_size = max(m_size)
    can_rotate = None
    #make new max matrix ID
    rotate_matrix = []
    r_clusterid = []
    for y in range(rm_size):
        rotate_matrixX = []
        for x in range(rm_size):
            if self[0] + y > (y_ax-1) or self[1] + x > (x_ax-1):
                can_rotate = False
            else:
                rotate_matrixX.append(m_id[self[0]+y][self[1]+x])
                r_clusterid.append([(self[0]+y),(self[1]+x)])
        rotate_matrix.append(rotate_matrixX)
    #check if grabbed cells are "0"
    countzero = []
    for i in range(len(r_clusterid)):
        countzero.append(self_test(r_clusterid[i],m_id))
    if countzero.count("0") < rm_size:
        can_rotate = False
    #change the m_id if rotate matrix is valid
    if rotate_matrix is None or len(rotate_matrix) < 1:
        nclusterid = clusterid
        pass
    elif can_rotate == False:
        nclusterid = clusterid
        pass
    elif len(rotate_matrix) == 1:
        nclusterid = clusterid
        pass
    else:
        new_matrix = [row[:] for row in rotate_matrix]
        row_count = len(rotate_matrix)
        for x in range(0,row_count):
            for j in range(0,row_count):
                    new_matrix[j][row_count -1 -x] = rotate_matrix[x][j]
        for y in range(rm_size):
            for x in range(rm_size):
                m_id[r_clusterid[(y*rm_size)+x][0]][r_clusterid[(y*rm_size)+x][1]] = new_matrix[y][x]
        #change clusterid to new rotated cluster
        nclusterid = []
        for i in range(len(r_clusterid)):
          if self_test(r_clusterid[i], m_id) != "0":
            nclusterid.append(r_clusterid[i])
        self = nclusterid[0]
    return m_id, nclusterid, self

#define generate cluster near reception
def gencluster(m_id,rec_id,offset, num_cr):#,rotate,rec_id,conrmtype,offset):
    #find region offset from reception that is a viable location for the consultation room cluster
    flatrec_yid = []
    flatrec_xid = []
    genclusterid = []
    num_c = 0
    for i in range(len(rec_id)):
        flatrec_yid.append(rec_id[i][0])
        flatrec_xid.append(rec_id[i][1])
    if (min(flatrec_yid)-6) < 0 and (min(flatrec_xid)-6) < 0:
        btmleft_id = [0,0]
    elif (min(flatrec_yid)-6) < 0:
        btmleft_id = [0, (min(flatrec_xid)-6)]
    elif (min(flatrec_xid)-6) < 0:
        btmleft_id = [(min(flatrec_yid)-6), 0]
    else:
        btmleft_id = [(min(flatrec_yid)-6), (min(flatrec_xid)-6)]
    if (max(flatrec_yid)+2) > y_ax:
        topright_id = [y_ax, (max(flatrec_xid)+2)]
    elif (max(flatrec_xid)+2) > x_ax:
        topright_id = [(max(flatrec_yid)+2), x_ax]
    else:
        topright_id = [(max(flatrec_yid)+2), (max(flatrec_xid)+2)]
    #generate region to check for viability
    gen_region = []
    for y in range((topright_id[0]-btmleft_id[0])+1):
        for x in range((topright_id[1]-btmleft_id[1])+1):
            if m_id[(btmleft_id[0]+y)][(btmleft_id[1]+x)] == "0":
                gen_region.append([(btmleft_id[0]+y),(btmleft_id[1]+x)])
    #call for genconrm function
    counter = 0
    valid = False
    cor_index = []
    while valid == False and not counter >= 10:
        m_id, cluster_id, valid = clustertype(gen_region[ran.randint(0,len(gen_region)-1)],m_id,ran.randint(0,3),ran.randint(1,3))
        counter += 1
        if valid == True:
          genclusterid.append(cluster_id)
    for y in range(y_ax):
        for x in range(x_ax):
            if self_test([y,x],m_id) == "C":
                num_c += 1
            elif self_test([y,x],m_id) == "0":
                cor_index.append([y,x])
    #print cor_index
    if num_c/4 < num_cr:
        counter2 = 0
        num_c1 = 0
        while num_c1/4 < num_cr and not counter2 > 200:
            m_id, cluster_id, valid = clustertype(cor_index[ran.randint(0,len(cor_index)-2)],m_id,ran.randint(0,2),ran.randint(1,3))
            counter2 += 1
            #print (valid)
            if valid == True:
              genclusterid.append(cluster_id)
            num_c1 = 0
            for y in range(y_ax):
                for x in range(x_ax):
                    if self_test([y,x],m_id) == "C":
                        num_c1 += 1
    #print ("Number of consultation room = " + str(num_c1/4))
    return m_id , genclusterid, gen_region

#Generate toilets from the latest m_id
def gentoilet(m_id,h_num,t_num):
  num_t =0
  num_ht = 0
  counter_t = 0
  counter_ht = 0
  cor_index = []
  cor_indexH = []
  gentoiletid = []
  for y in range(y_ax):
        for x in range(x_ax):
            if self_test([y,x],m_id) == "0":
                cor_index.append([y,x])
  while num_t < t_num and not counter_t >100:
    m_id, clusterid, valid = toilet(cor_index[ran.randint(0,len(cor_index)-2)],m_id,0)
    counter_t += 1
    if valid == True:
      num_t += 1
      gentoiletid.append(clusterid)
  #generate handicap toilets
  for y in range(y_ax):
        for x in range(x_ax):
            if self_test([y,x],m_id) == "0":
                cor_indexH.append([y,x])
  while num_ht < h_num and not counter_ht >100:
    m_id, clusterid, valid = toiletH(cor_index[ran.randint(0,len(cor_index)-2)],m_id,0)
    counter_ht += 1
    #print valid
    if valid == True:
      num_ht += 1
      gentoiletid.append(clusterid)
  #print ("Number of Toilets = " + str(num_t))
  #print ("Number of Handicap Toilets = " + str(num_ht))
  return m_id, gentoiletid

#Find bounds of any set of cluster IDs and returns the edits bounds + point distance
def bounds(clusterid,ptd):
    boundset = []
    yid = []
    xid = []
    for i in range(len(clusterid)):
        yid.append(clusterid[i][0])
        xid.append(clusterid[i][1])
    #append to boundset in the order of btm left, btm right, top right, top left
    boundset.append([min(yid),min(xid)])
    boundset.append([min(yid),max(xid)+ptd])
    boundset.append([max(yid)+ptd,max(xid)+ptd])
    boundset.append([max(yid)+ptd,min(xid)])
    return boundset

def Layout():
  #Step 1: create mxn matrix + matrix identity
  m_pt = []
  m_id = []
  for i in range(y_ax):
    x_pt = []
    x_id = []
    for j in range(x_ax):
        x_id.append("0")
    m_pt.append(x_pt)
    m_id.append(x_id)
  a = m_pt
    #Step 2: Find entrance in the matrix
  #Revit twin: use distance to method
  door_dist = [0,10]
  E_yid = door_dist.index(min(door_dist))//y_ax
  E_xid = door_dist.index(min(door_dist)) - (E_yid*y_ax)
  m_id[E_yid][E_xid] = "E"
  b = m_id 

  #Step 3: Identify reception generation boundary based on location of E
  #Finding x and y id of points within generation boundary
  rr = []
  for i in range(E_yid - 4, E_yid + 4):
      if i <= 0 or i >= y_ax:
          pass
      else:
          for j in range (E_xid - 4, E_xid + 4):
              if j <= 0 or j >= x_ax:
                  pass
              else:
                  rr.append([i,j]) 

  #Generating bottom left corner and top right corner of reception boundary
  rb = []
  rs = [3,4] #reception size, determined by user
  m_id, rb, rc = genrec(rr, m_id, rs)
  #Step 4: Generating consultation rooms
  cs = [2,3] #Consultation room size, determined by user
  n_crx = 3 #Number of consultation rooms arrayed continuously, determined by user
  n_cry = 1
  f_cs = [cs[0] * n_cry, cs[1] * n_crx]
  tn_cr = 15 #Total number of consultation rooms

  crr = []
  crr_ids = []
  crr_b = []
  #for i in range(len(ratresult)):
      #if True in i:
          
  #Finding spaces outside of reception and reception region
  for i in range(y_ax):
      for j in range(x_ax):
          if m_id[i][j] == "R" or m_id[i][j] == " ":
              pass
          else:
              crr.append([i,j])

  #Selecting n random points to begin arraying
  for i in range(int(tn_cr / (n_crx * n_cry))):
      crr_ids.append(crr[ran.randint(0,len(crr)-1)])

  for i in range(len(crr_b)):
      m_id[crr_b[i][0]][crr_b[i][1]] = "C" 
      
  m_id, genclusterid, gen_region = gencluster(m_id,rc,2,40)
  m_id, gentoiletid = gentoilet(m_id,5,3)

  #print('GenClusterid:')
  #print (*genclusterid, sep = "\n")
  #print('End')
  #print(gen_region)
  #print (*m_id, sep = "\n")

  #checks if the genclusterid is correct (currently should equal to 6x5x4 = 120)
  check_GC_id = 0
  for i in range(len(genclusterid)):
    if len(genclusterid[i]) != 0:
      for j in range(len(genclusterid[i])):
        if m_id[genclusterid[i][j][0]][genclusterid[i][j][1]] != "0":
          check_GC_id += 1
  #print (check_GC_id)
  #group sets of 4 for consultion rom
  ptd = 1
  cr_m_id = m_id
  cr_set = []

  #Find bounds of reception
  cr_set += (bounds(rc,1))

  #Find bounds of Toilet
  for i in range(len(gentoiletid)):
    cr_set += bounds(gentoiletid[i],1)

  #group sets of 4 for consultion rom
  for y in range(y_ax-1):
    for x in range(x_ax-1):
      if self_test([y,x],cr_m_id) == "C":
        cr_setid = []
        if cr_test([y,x],cr_m_id, "C").count(True) == 3:
          cr_setid = [[y,x],[y,x+1+ptd],[y+1+ptd,x+1+ptd],[y+1+ptd,x]]
          cr_m_id[y+1][x] = "N"
          cr_m_id[y][x+1] = "N"
          cr_m_id[y+1][x+1] = "N"
          cr_set.append([y,x])
          cr_set.append([y,x+1+ptd])
          cr_set.append([y+1+ptd,x+1+ptd])
          cr_set.append([y+1+ptd,x])
  cr_set_str = ""
  for i in range(len(cr_set)):
    if i == (len(cr_set)-1):
        cr_set_str += str(cr_set[i][0])+ "," + str(cr_set[i][1]) 
    elif (i+1)%4 == 0:
        cr_set_str += str(cr_set[i][0]) + "," + str(cr_set[i][1]) + "S" 
    elif (i+1)%4 != 0:
        cr_set_str += str(cr_set[i][0]) + "," + str(cr_set[i][1]) + "A"
  cr_set_tag = ""
  for j in range(int(len(cr_set)/4)):
    if j == 0:
        cr_set_tag += "Reception" + "S"
    elif j == (int((len(cr_set))/4)-1):
        cr_set_tag += "ConsultationRoom"
    elif j < len(gentoiletid)+1:
        cr_set_tag += "Toilet" + "S"
    else:
        cr_set_tag += "ConsultationRoom" + "S"

  return [m_id,genclusterid,gentoiletid,rb,cr_set_str,cr_set_tag]

m_id,genclusterid,gentoiletid,rb,cr_set_str,cr_set_tag=Layout()
print (cr_set_str)
print (cr_set_tag)