import networkx
import pickle 
def countData(asGraph:networkx.Graph):
    lv1 = 0
    lv2 =0
    lv3 = 0
    for node in asGraph.nodes:
        nodeData = asGraph.nodes.get(node)
        if nodeData['linkLevel'] ==1:
            print(node,nodeData)
            lv1+=1    
        if nodeData['linkLevel'] ==2:
            print(node,nodeData)
            lv2+=1
        if nodeData['linkLevel'] ==3:
            lv3+=1
    print("lv1 ", lv1, "lv2,",lv2, "lv3, ",lv3, "sum ",lv1+lv2+lv3)
    return lv1, lv2, lv3

asGraph = pickle.load( open ('pickles/asGraph-3582.pickle','rb'))
print('hello world')
countData(asGraph)
# for node in asGraph.nodes:
#     data = asGraph[node]
#     print(data)