# -*- coding: utf-8 -*- 

import os
import os.path
import csv
import re

#打开文件
#filePath = 'D:\LCP_WORK_FILES\ddr3_io_csv2xdc\z045_ddr3_pinlist.csv'
filePath = input('请输入原始CSV文件全路径：\n')

netPortMap = [
('DDR3_DIMM1_CAS_N' , 'ddr3_cas_n'),         #0
('DDR3_DIMM1_CK0_N', 'ddr3_ck_n[0]'),       #1
('DDR3_DIMM1_CK0_P', 'ddr3_ck_p[0]'),       #2
('DDR3_DIMM1_CKE0', 'ddr3_cke[0]'),           #3
('DDR3_DIMM1_CS0_N', 'ddr3_cs_n[0]'),       #4
('DDR3_DIMM1_ODT0_N', 'ddr3_odt[0]'),       #5
('DDR3_DIMM1_RAS_N', 'ddr3_ras_n'),          #6
('DDR3_DIMM1_WE_N', 'ddr3_we_n'),              #7
('DDR3_DIMM1_RESET_N', 'ddr3_reset_n'),    #8

('DDR3_DIMM1_DM', 'ddr3_dm'),                     #9
('DDR3_DIMM1_DQ', 'ddr3_dq'),                     #10
('DDR3_DIMM1_A', 'ddr3_addr'),                   #11
('DDR3_DIMM1_BA', 'ddr3_ba'),                     #12

('DDR3_DIMM1_DQS', 'ddr3_dqs'),                  #13

('FPGA_Name', 'U1'),                                     #14

]
#统计约束数量
xdcDict={
0:0, 
1:0, 
2:0, 
3:0, 
4:0, 
5:0, 
6:0, 
7:0, 
8:0, 
9:0, 
10:0, 
11:0, 
12:0, 
13:0, 

}
#fun defs
#匹配网络名称    
def findNetNameInMap(row):
    for index in range(0,  14):
        answer = 'err'
        netName = row[0]
        if netName.find(netPortMap[index][0]) != -1:
            if netName.find(netPortMap[13][0]) != -1: #对DQS进行第二次判断
                answer = (row[0],  netPortMap[13][0],  netPortMap[13][1], 13)
            else:
                answer = (row[0],  netPortMap[index][0],  netPortMap[index][1], index)
            return answer
    return answer
#生成XDC约束
def genXDCLine(netName,  netNameNoIndex,  portName,  number, originString):
    originStringSplit = originString.split(' ')
    for item in originStringSplit:         #获取FPGA引脚位置
            if item.find(netPortMap[14][1]+'.') != -1:
                pinLOC = item[len(netPortMap[14][1]+'.'):]      
                
    if number <= 8: #固定名称的引脚                
        xdcLine = 'set_property PACKAGE_PIN '+pinLOC+' [get_ports {'+portName+'}]'
        #print(xdcLine)
    if 9 <= number <= 12: #DM，DQ，ADDR， BA单端信号
        portNameIndex = netName[len(netNameNoIndex):]
        xdcLine = 'set_property PACKAGE_PIN '+pinLOC+' [get_ports {'+portName+'['+portNameIndex+']}]'
        #print(xdcLine)    
    if number == 13:  #DQS，差分信号
        portNameRes = netName[len(netNameNoIndex):]
        #print(portNameRes)
        portNameIndex = re.sub("\D", "", portNameRes)  #去掉非数字字符，得到索引
        portNamePolarity = re.sub("[^a-zA-Z]", "", portNameRes) #去掉非字母字符，得到极性
        portNamePolarity = portNamePolarity.lower()
        #print(portNameIndex,  portNamePolarity)
        xdcLine = 'set_property PACKAGE_PIN '+pinLOC+' [get_ports {'+portName+'_'+portNamePolarity+'['+portNameIndex+']}]'
        #print(xdcLine)
    return xdcLine
#process start            
xdcFilePath=filePath.replace('.csv', '.xdc')
xdcfile = open(xdcFilePath,  'w')

with open(filePath, 'r', encoding='utf-8') as csvfile:
    fileContent = csv.reader(csvfile,  delimiter=',')
    for row in fileContent:                          #遍历每行  
       # print ("读取的数据为: %s" % (row[0]))
        
        answer = findNetNameInMap(row)
        #print (answer,  row[1])
        if answer != 'err':
            xdcLine = genXDCLine(netName=answer[0], netNameNoIndex = answer[1], portName = answer[2],  number= int(answer[3]), originString=row[1])
            xdcfile.write(xdcLine+'\n')
            #print(answer[3])
            xdcDict[answer[3]] = xdcDict[answer[3]] + 1
        
        
xdcfile.close()
print('============================================')
print('约束文件已生成，并保存为：'+xdcFilePath)
print('约束数量统计==============================')
for key in xdcDict:
    print(netPortMap[key][0] + ':    '+str(xdcDict[key]))

        

