#coding=utf-8
import json

import fbx
from fbx_function import *

#解析fbx
def FbxParse(fbxPath):
    '''
    '''

    '''
    初始化场景
       使用sdk需要最重要的就是三个东西：SDKManager,FbxScene,FbxNode
       SDKManager:用来对所有的FBX对象进行内在管理，所有使用SDK加载的资源均在此对象的管控之下，最终的资源释放也由其来完成
       FbxScene:相当于一个场景，里面包含了所有的fbx文件信息，一个fbx文件对应一个FbxScene对象
       FbxNode:整个场景会从一个空节点 RootNode开始, 然后root向下会分出多个 FbxNode,每一个FbxNode下面又会有多个FbxNode(多叉数结构),FbxNode就是具体存储fbx文件信息的节点
    '''
    #初始化SDKManager和scene
    sdkManager, scene = InitializeSdkObjects()
    #加载fbx,fbxpath = .fbx路径地址
    content = LoadScene(sdkManager, scene, fbxPath)

    if content == False:

        sdkManager.Destroy()

        print fbxPath + ' 场景加载失败'
        return
        pass

    print str(content) + ' 场景加载成功'



    #因为在建模软件中,没有三角面的概念(一般都是4边面或者5边6边面...),所有我们初始化场景的时候要对.fbx文件进行三角化方便提取unity Mesh中的信息

    # 对场景三角化
    converter = FbxGeometryConverter(sdkManager)
    converter.Triangulate(scene, True)
    axisSystem = FbxAxisSystem.OpenGL
    axisSystem.ConvertScene(scene)

    # 场景中模型的root节点
    rootNode = scene.GetRootNode()

    # 获取以m为单位转化后的缩放系数
    global VERTEX_FACTOR
    VERTEX_FACTOR = scene.GetGlobalSettings().GetSystemUnit().GetConversionFactorTo(FbxSystemUnit.m)

    '''
    在获取信息的时候需要注意的事项：
      1.FbxNode中的layer层，在每一个节点中都可以有多个layer层，uv纹理信息，法线，切线等都是存在layer中，所以每一层layer都会有一套纹理，法线，切线等信息，一般情况我们只需要用到第一个layer层即可, 这里可能遇到uv加载失败的问题（因为unity默认读取的uvIndex是第一层uv，所以如果在有uv但是读取失败的情况，可以查看fbx文件中的默认uv集的uv是否是正确的）
      2.在FbxLayerElement中有两个重要的属性映射模式：EMappingMode和引用模式(读取数据方式):EReferenceMode
    //映射关系(定义了当前类型的元素如何映射到mesh)
    enum EMappingMode
    {
        eBY_CONTROL_POINT,      //对于每一个顶点有且只有一个对应的值（表示每个顶点无论被几个多边形共享，都只有一个normal,uv,tangent）
        eBY_POLYGON_VERTEX,     //对与每一个三角面中的每一个顶点都有一个对应值(表示如果一个顶点被n个多边形共享，那么这个顶点就有n个   normal,uv,tangen与之相对应)
    }

    //引用的类型，读取数据方式（定义了如何访问相关的数据）
    enum EReferenceMode
    {
        eDIRECT,      //对应DirectArray,表示第i个顶点相对的element元素对应DirectArray的第i个位置
        eIndexToDirect, //对应IndexArray,表示第i个顶点所在的indexArray中的索引位置的element元素对应DirectArray的第i个位置
    }
    '''

    if rootNode:
        # 获取模型根节点数量
        childCount = rootNode.GetChildCount()

        # 如果只有一个模型
        if (childCount == 1):
            # 模型的根节点
            parentNode = rootNode.GetChild(0)

            # 获取模型根节点对象
            nodeObject = GetNodeObject(parentNode,True)
            # 递归回去所有的字节点的属性
            GetChildObject(nodeObject,parentNode)
            #response(200, JsonParse(nodeObject));

            '''
            这里拿到的nodeObject的格式就是fbx_function里面的Node类型,
            里面通过GetNodeObject函数已经解析好内容存放在属性里.通过访问可以进行编辑修改
            eg: print nodeObject.vertices
            ['-500.0,500.0,500.0', '500.0,500.0,500.0', '500.0,-500.0,500.0', '-500.0,500.0,500.0',
            '500.0,-500.0,500.0', '-500.0,-500.0,500.0', '-500.0,500.0,500.0', '-500.0,-500.0,500.0',
            '-500.0,500.0,-500.0', '-500.0,-500.0,500.0', '-500.0,-500.0,-500.0', '-500.0,500.0,-500.0',
            '500.0,-500.0,-500.0', '500.0,500.0,-500.0', '-500.0,-500.0,-500.0', '-500.0,-500.0,-500.0',
            '500.0,500.0,-500.0', '-500.0,500.0,-500.0', '500.0,500.0,500.0', '500.0,-500.0,-500.0', '
            500.0,-500.0,500.0', '500.0,-500.0,-500.0', '500.0,500.0,500.0', '500.0,500.0,-500.0',
            '-500.0,500.0,500.0', '-500.0,500.0,-500.0', '500.0,500.0,500.0', '500.0,500.0,500.0',
            '-500.0,500.0,-500.0', '500.0,500.0,-500.0', '500.0,-500.0,500.0', '500.0,-500.0,-500.0',
            '-500.0,-500.0,500.0', '-500.0,-500.0,500.0', '500.0,-500.0,-500.0', '-500.0,-500.0,-500.0,']

            在拿到数据并修改以后,参照fbx_create_cube.py里生成scene的方法把修改后的数据生成新的scene
            '''

            sdkManager.Destroy()
            return
            pass # end if

        elif (childCount > 1): # 多个模型合并成一个
            # 多个模型的根节点
            tempChildrens = []
            for i in range(childCount):
                child = rootNode.GetChild(i)
                tempChildrens.append(child)
                pass # end for

            # 创建一个空的根节点
            newParentNode = fbx.FbxNode.Create(scene, 'root')
            # 创建一个空节点属性
            nodeAttribute = FbxNodeAttribute.Create(sdkManager,"none")
            newParentNode.SetNodeAttribute(nodeAttribute)
            for i in tempChildrens:
                newParentNode.AddChild(i)
                pass # end for

            # 获取模型根节点的属性
            nodeObject = GetNodeObject(newParentNode ,True)
            # 递归回去所有的字节点的属性
            GetChildObject(nodeObject, newParentNode)
            #response(200, JsonParse(nodeObject));
            sdkManager.Destroy()
            return
            pass # end elif
        else:
            pass # end else
        pass # end if
    sdkManager.Destroy()
    print "解析模型失败" + fbxPath
    #response(400, error)
    pass # end FbxParse


FbxParse("./myFbxSaveFile.fbx")