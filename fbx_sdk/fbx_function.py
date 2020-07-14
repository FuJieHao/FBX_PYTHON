#coding=utf-8
import FbxCommon
from FbxCommon import *

#模型顶点缩放系数
global VERTEX_FACTOR
VERTEX_FACTOR = 1

#transform
class Transform(object):
    def __init__(self):

        self.name     = ''      #name
        self.position = '0,0,0' #坐标
        self.rotation = '0,0,0' #旋转
        self.scale    = '1,1,1' #缩放

#node
class Node(object):
    def __init__(self, transform):
        self.name       = transform.name
        self.position   = transform.position
        self.rotation   = transform.rotation
        self.scale      = transform.scale

        self.vertices   = None #顶点
        self.triangles  = None #顶点索引
        self.uv         = None #uv
        self.normals    = None #法线
        self.tangents   = None #切线
        self.children   = []   #所有子节点
        self.childrenCount = 0 #子节点个数
        self.hasMesh = False #判断当前层是否含有mesh属性


#获取transform
#p_Node = 当前模型节点
def GetTransform(p_Node,isRoot = False):
    c_trans = Transform()
    if p_Node is None:
        return c_trans
        pass
    c_trans.name = p_Node.GetName()
    #得到当前Node的Geometric矩阵
    geometricMatrix = FbxAMatrix()
    geometricMatrix.SetIdentity()
    if (p_Node.GetNodeAttribute()):
        lT = p_Node.GetGeometricTranslation(FbxNode.eSourcePivot)
        lR = p_Node.GetGeometricRotation(FbxNode.eSourcePivot)
        lS = p_Node.GetGeometricScaling(FbxNode.eSourcePivot)
        geometricMatrix.SetT(lT)
        geometricMatrix.SetR(lR)
        geometricMatrix.SetS(lS)

    globalMatrix = FbxAMatrix()
    globalMatrix.SetIdentity()
    #如果是根节点则取世界矩阵 否则取子集自身的矩阵
    if isRoot:
        globalMatrix = p_Node.EvaluateGlobalTransform();
    else:
        globalMatrix = p_Node.EvaluateLocalTransform();

    globalMatrix *= geometricMatrix
    rPos = globalMatrix.GetT()
    rotation = globalMatrix.GetR()
    rScale = globalMatrix.GetS()
    if isRoot:
        global VERTEX_FACTOR
        # 获取root的缩放因子
        # scale = 1/float(globalMatrix.GetS()[0]);
        #获取顶点的缩放系数
        # VERTEX_FACTOR/=0.01;
        VERTEX_FACTOR = VERTEX_FACTOR/0.01*float(globalMatrix.GetS()[0])*VERTEX_FACTOR
        c_trans.scale = "1" + "," + "1" + "," + "1" + ","
        c_trans.position = "0" + "," + "0"+ "," + "0"+ ","
        c_trans.rotation = "0" + "," + "0"+ "," + "0"+ ","
    else:
        # c_trans.scale = str(rScale[0])+","+str(rScale[1])+","+str(rScale[2])+",";
        c_trans.scale = "1" + "," + "1" + "," + "1" + ",";
        c_trans.position = str(rPos[0]) + "," + str(rPos[1]) + "," + str(rPos[2]) + ","
        c_trans.rotation = str(rotation[0]) + "," + str(rotation[1]) + "," + str(rotation[2]) + ","
    # rQuaternion = globalMatrix.GetQ().DecomposeSphericalXYZ()
    return c_trans
    pass


#获取顶点
def GetVertex(p_ControlPoints,p_orginPolygonIndex, p_Vertexlist):
    '''
    :param p_ControlPoints: 所有顶点
    :param p_orginPolygonIndex: fbx原文件中顶点索引
    :param p_Vertexlist: 新生的顶点数组
    :return:
    '''
    fbxVec4 =  FbxVector4(0,0,0)

    x = p_ControlPoints[p_orginPolygonIndex][0]
    y = p_ControlPoints[p_orginPolygonIndex][1]
    z = p_ControlPoints[p_orginPolygonIndex][2]

    fbxVec4.Set(x,y,z)
    p_Vertexlist.append(fbxVec4)

    pass


#获取uv
def GetUV(p_UV, p_orginPolygonIndex, p_UVIndex, p_UVlist):
    '''
    :param p_UV: 所有uv
    :param p_orginPolygonIndex: fbx源文件中顶点索引
    :param p_UVIndex: uv索引
    :param p_UVlist: 新生成的uv数组
    :return:
    '''
    x, y = 0,0
    fbxVec2 =  FbxVector2(0,0)
    if (p_UV.GetMappingMode() == FbxLayerElement.eByControlPoint):
        if p_UV.GetReferenceMode() == FbxLayerElement.eDirect:
            x = p_UV.GetDirectArray().GetAt(p_orginPolygonIndex)[0]
            y = p_UV.GetDirectArray().GetAt(p_orginPolygonIndex)[1]
            pass #if
        if p_UV.GetReferenceMode() == FbxLayerElement.eIndexToDirect:
            id = p_UV.GetIndexArray().GetAt(p_orginPolygonIndex)
            x = p_UV.GetDirectArray().GetAt(id)[0]
            y = p_UV.GetDirectArray().GetAt(id)[1]
            pass #if
    if (p_UV.GetMappingMode() == FbxLayerElement.eByPolygonVertex):
        if p_UV.GetReferenceMode() == FbxLayerElement.eDirect or p_UV.GetReferenceMode() == FbxLayerElement.eIndexToDirect:
            x = p_UV.GetDirectArray().GetAt(p_UVIndex)[0]
            y = p_UV.GetDirectArray().GetAt(p_UVIndex)[1]
            pass
    #如果使用的是Direct3D11  1-＝y
    # y=1-y;
    fbxVec2.Set(x,y)
    p_UVlist.append(fbxVec2)
    pass  # end func


#获取法线
def GetNormal(p_Normals,p_orginPolygonIndex,p_VertexIndex, p_Normallist):
    '''
    :param p_Normals: 所有的normal法线
    :param p_orginPolygonIndex: fbx源文件中的顶点索引
    :param p_VertexIndex: 当前顶点
    :param p_Normallist: 新生成的normal数组
    :return:
    '''
    fbxVec4 = FbxVector4(0,0,0)
    x,y,z=0,0,0
    if (p_Normals.GetMappingMode() == FbxLayerElement.eByControlPoint):
        if p_Normals.GetReferenceMode() == FbxLayerElement.eDirect:
            x = p_Normals.GetDirectArray().GetAt(p_orginPolygonIndex)[0]
            y = p_Normals.GetDirectArray().GetAt(p_orginPolygonIndex)[1]
            z = p_Normals.GetDirectArray().GetAt(p_orginPolygonIndex)[2]
        if p_Normals.GetReferenceMode() == FbxLayerElement.eIndexToDirect:
            id = p_Normals.GetIndexArray().GetAt(p_orginPolygonIndex)
            x = p_Normals.GetDirectArray().GetAt(id)[0]
            y = p_Normals.GetDirectArray().GetAt(id)[1]
            z = p_Normals.GetDirectArray().GetAt(id)[2]
    if (p_Normals.GetMappingMode() == FbxLayerElement.eByPolygonVertex):
        if p_Normals.GetReferenceMode() == FbxLayerElement.eDirect:
            x = p_Normals.GetDirectArray().GetAt(p_VertexIndex)[0]
            y = p_Normals.GetDirectArray().GetAt(p_VertexIndex)[1]
            z = p_Normals.GetDirectArray().GetAt(p_VertexIndex)[2]
        if p_Normals.GetReferenceMode() == FbxLayerElement.eIndexToDirect:
            id = p_Normals.GetIndexArray().GetAt(p_VertexIndex)
            x = p_Normals.GetDirectArray().GetAt(id)[0]
            y = p_Normals.GetDirectArray().GetAt(id)[1]
            z = p_Normals.GetDirectArray().GetAt(id)[2]
    fbxVec4.Set(x,y,z)
    p_Normallist.append(fbxVec4)
    pass #end

#获取切线
def GetTangent(p_Tangent,p_orginPolygonIndex,p_VertexIndex, p_Tangentlist):
    '''
    :param p_Tangent: 所有的切线
    :param p_orginPolygonIndex: fbx源文件中的顶点索引
    :param p_VertexIndex: 当前顶点
    :param p_Tangentlist: 新生成的切线数组
    :return:
    '''
    fbxVec4 = FbxVector4(0, 0, 0,1);
    x, y, z,w = 0, 0, 0,1
    if (p_Tangent.GetMappingMode() == FbxLayerElement.eByControlPoint):
        if p_Tangent.GetReferenceMode() == FbxLayerElement.eDirect:
            x = p_Tangent.GetDirectArray().GetAt(p_orginPolygonIndex)[0]
            y = p_Tangent.GetDirectArray().GetAt(p_orginPolygonIndex)[1]
            z = p_Tangent.GetDirectArray().GetAt(p_orginPolygonIndex)[2]
            w = p_Tangent.GetDirectArray().GetAt(p_orginPolygonIndex)[3]
        if p_Tangent.GetReferenceMode() == FbxLayerElement.eIndexToDirect:
            id = p_Tangent.GetIndexArray().GetAt(p_orginPolygonIndex)
            x = p_Tangent.GetDirectArray().GetAt(id)[0]
            y = p_Tangent.GetDirectArray().GetAt(id)[1]
            z = p_Tangent.GetDirectArray().GetAt(id)[2]
            w = p_Tangent.GetDirectArray().GetAt(id)[3]
    if (p_Tangent.GetMappingMode() == FbxLayerElement.eByPolygonVertex):
        if p_Tangent.GetReferenceMode() == FbxLayerElement.eDirect:
            x = p_Tangent.GetDirectArray().GetAt(p_VertexIndex)[0]
            y = p_Tangent.GetDirectArray().GetAt(p_VertexIndex)[1]
            z = p_Tangent.GetDirectArray().GetAt(p_VertexIndex)[2]
            w = p_Tangent.GetDirectArray().GetAt(p_VertexIndex)[3]
        if p_Tangent.GetReferenceMode() == FbxLayerElement.eIndexToDirect:
            id = p_Tangent.GetIndexArray().GetAt(p_VertexIndex)
            x = p_Tangent.GetDirectArray().GetAt(id)[0]
            y = p_Tangent.GetDirectArray().GetAt(id)[1]
            z = p_Tangent.GetDirectArray().GetAt(id)[2]
            w = p_Tangent.GetDirectArray().GetAt(id)[3]
    fbxVec4.Set(x, y, z,w)
    p_Tangentlist.append(fbxVec4)
    pass  # end

#获取node对象
def GetNodeObject(p_Node, p_isRoot = False):

    c_NodeObject = Node(GetTransform(p_Node,p_isRoot))
    # 获取节点的类型
    att_type = p_Node.GetNodeAttribute().GetAttributeType()
    # 是否是mesh
    if att_type != FbxCommon.FbxNodeAttribute.eMesh:
        return c_NodeObject
        pass
    else:
        c_NodeObject.hasMesh = True #这一层包含mesh信息

        mesh = p_Node.GetMesh()

        # 获取顶点索引
        polygonVertices = mesh.GetPolygonVertices();

        # 获取mesh的顶点索引个数
        polygonVertexCount = mesh.GetPolygonVertexCount();

        m_vertex = []  # 顶点
        m_uv = []  # uv
        m_normal = []  # 法线
        m_tangent = []  # 切线
        m_triangles = []  # 顶点索引
        vertexCounter = 0

        if(mesh.GetControlPointsCount() < 0):  # 没有顶点
            return c_NodeObject
            pass
        # 所有顶点
        controlPoints = mesh.GetControlPoints()

        # uv数量与uv
        uvCount = mesh.GetElementUVCount()
        uvs = mesh.GetElementUV()

        # 法线数量与法线
        normalCount = mesh.GetElementNormalCount()
        normals = mesh.GetElementNormal()

        # 切线数量与切线
        tangentCount = mesh.GetElementTangentCount()
        tangents = mesh.GetElementTangent(0)

        for i in range(polygonVertexCount / 3):
            for j in range(3):
                ctrlPointIndex = polygonVertices[i * 3 + j]

                # 获取顶点
                GetVertex(controlPoints, ctrlPointIndex, m_vertex);

                # 获取uv
                if uvCount >= 1:
                    c_uvIndex = mesh.GetTextureUVIndex(i, j);
                    GetUV(uvs, ctrlPointIndex, c_uvIndex, m_uv);
                    pass

                # 获取法线
                if normalCount >= 1:
                    GetNormal(normals, ctrlPointIndex, vertexCounter, m_normal);
                    pass

                # 获取切线
                if tangentCount >= 1:
                    GetTangent(tangents, ctrlPointIndex, vertexCounter, m_tangent);
                    pass

                vertexCounter += 1
                pass  # end for
            pass  # end for

        # 重新排序顶点索引0，1，2，3，4，...
        for i in range(len(polygonVertices)):
            m_triangles.append(i)
            pass #end for

        # 顶点索引反转
        for i in range(len(m_triangles) / 3):
            sw = [];
            sw.append(m_triangles[i * 3 + 0])
            sw.append(m_triangles[i * 3 + 2])
            m_triangles[i * 3 + 2] = sw[0]
            m_triangles[i * 3 + 0] = sw[1]
            pass #end for

        #转化成字符数组
        vs = []
        for i in m_vertex:
            ss = ""
            if i is m_vertex[-1]:
                ss = str(-i[0]*VERTEX_FACTOR)+","+ str(i[1]*VERTEX_FACTOR)+","+str(i[2]*VERTEX_FACTOR)+","
            else:
                ss = str(-i[0]*VERTEX_FACTOR)+","+ str(i[1]*VERTEX_FACTOR)+","+str(i[2]*VERTEX_FACTOR)
            vs.append(ss)
            pass #end for

        uv = []
        for i in m_uv:
            ss = ""
            if i is m_uv[-1]:
                ss = str(i[0]) + "," + str(i[1]) + ","
            else:
                ss = str(i[0]) + "," + str(i[1])
            uv.append(ss)
            pass #end for

        ns = []
        for i in m_normal:
            ss = ""
            if i is m_normal[-1]:
                ss = str(-i[0]) + "," + str(i[1]) + "," + str(i[2]) + ","
            else:
                ss = str(-i[0]) + "," + str(i[1]) + "," + str(i[2])
            ns.append(ss)
            pass #end for

        tg = []
        for i in m_tangent:
            ss = ""
            if i is m_tangent[-1]:
                ss = str(-i[0]) + "," + str(i[1]) + "," + str(i[2]) + ","+ str(-i[3]) + ","
            else:
                ss = str(-i[0]) + "," + str(i[1]) + "," + str(i[2]) + ","+ str(-i[3])
            tg.append(ss)
            pass #end for

        c_NodeObject.vertices = vs
        c_NodeObject.uv = uv
        c_NodeObject.triangles = m_triangles
        c_NodeObject.normals = ns
        c_NodeObject.tangents = tg
        pass
    return c_NodeObject
    pass

#遍历子节点属性
def GetChildObject(p_NodeObject,p_ParentNode):
    '''
    :param p_NodeObject: node对象
    :param p_ParentNode: 获取数据的parent节点
    :return:
    '''
    count = p_ParentNode.GetChildCount()
    p_NodeObject.childrenCount = count
    for i in range(count):
        c_NodeObject = GetNodeObject(p_ParentNode.GetChild(i))
        p_NodeObject.children.append(c_NodeObject)
        GetChildObject(c_NodeObject,p_ParentNode.GetChild(i))
        pass
    pass
