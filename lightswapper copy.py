import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaUI as OpenMayaUI
import maya.mel as mel
import os
import sys
import json

def getCurrentRenderer():
    currentRenderer = cmds.getAttr('defaultRenderGlobals.currentRenderer')
    return currentRenderer

def checkCurrentRenderer(currentRenderer):
    with open('/transfer/s5512613_SP/Masters_Project/Render_Scene_Swapper/Dictionary/lights.json','r') as file :
        lightsData=json.load(file)
    for rendererInfo in lightsData["Lights"]["renderer"]:
        if currentRenderer in rendererInfo:
            return ("Renderer Supported")

def assignNumber(currentRenderer):
    if currentRenderer == "arnold" :
        return 0
    elif currentRenderer == "renderman" :
        return 1
    elif currentRenderer == "vray" :
        return 2
    else:
        return False 

def createLightComponentMap(components_light_map,lightsData,light_type,number):
    for light in lightsData["Lights"]:
        if light != "renderer":
            for key,value in lightsData["Lights"][light_type].items():
                if key in ["attribute_intensity","attribute_color","attribute_exposure"]:
                    components_light_map[key]=value[number]

def copyLightAttributes(light,lightsData,light_type,number,convNumber):
    convLight=lightsData["Lights"][light_type]["name"][convNumber]
    print(convLight)
    convLight=cmds.shadingNode(f"{convLight}",asLight=True,name=f"{light}_conv")
    
    components_light_map={}
    createLightComponentMap(components_light_map,lightsData,light_type,number)
    print(components_light_map)

    components_convLight_map={}
    createLightComponentMap(components_convLight_map,lightsData,light_type,convNumber)
    print(components_convLight_map)

    for attr,convAttr in zip(components_light_map.values(),components_convLight_map.values()):
        try:
            value=cmds.getAttr(light+'.'+attr)
            print(value)
            file_node=cmds.connectionInfo(light + '.'+ attr, sourceFromDestination=True)
            print(file_node)
            file_node=''.join(file_node)
            try:
                print("inside file node")
                if convNumber==1:
                    if number==0:
                        print("Coming in arnold to renderman_file_node")
                        file_path=cmds.listConnections(light + '.'+ attr,type='file')
                        file_path=''.join(file_path)
                        file_path=cmds.getAttr("%s.fileTextureName" % file_path)
                        print(file_path)
                        cmds.setAttr(convLight+'.'+convAttr,file_path,type='string')
                    else:
                        print("Coming in vray to renderman_file_node")
                        file_path=cmds.listConnections(light + '.'+ attr,type='file')
                        file_path=''.join(file_path)
                        file_path=cmds.getAttr("%s.fileTextureName" % file_path)
                        print(file_path)
                        cmds.setAttr(convLight+'.'+convAttr,file_path,type='string')

                if convNumber==2:
                    if number == 0:
                        print("Coming in arnold to vray_file_node")
                        file_path=cmds.listConnections(light + '.'+ attr,type='file')
                        file_path=''.join(file_path)
                        print(file_path)
                        cmds.setAttr(convLight+'.useDomeTex',1)
                        cmds.connectAttr(file_path+'.outColor',convLight+'.'+convAttr)
                    else:
                        print("Coming in renderman to vray_file_node")
                        cmds.setAttr(convLight+'.useDomeTex',1)
                        new_file_node=cmds.shadingNode('file',asTexture=True)
                        cmds.setAttr(new_file_node+'.fileTextureName',value,type='string')
                        cmds.connectAttr(new_file_node+'.outColor',convLight+'.'+convAttr)     

                if convNumber==0:
                    print("To arnold")
                    if number == 2:
                        print("Coming in vray to arnold")
                        file_path=cmds.listConnections(light + '.'+ attr,type='file')
                        file_path=''.join(file_path)
                        cmds.connectAttr(file_path+'.outColor',convLight+'.'+convAttr)
                    else:
                        print("Coming in renderman to arnold")
                        new_file_node=cmds.shadingNode('file',asTexture=True)
                        print("created new node")
                        cmds.setAttr(new_file_node+'.fileTextureName',value,type='string')
                        cmds.connectAttr(new_file_node+'.outColor',convLight+'.'+convAttr)     
            
            except:
                try:
                    try:
                        cmds.setAttr(convLight+'.'+convAttr,value)
                    except:
                        cmds.setAttr(convLight+'.'+convAttr,value[0][0],value[0][1],value[0][2],type='double3')
                    finally:
                        pass
                except:            
                    if '' in attr.lower():
                        continue
        
        except:
            if '' in attr.lower():
                continue
        
        
    
    lightTransform=cmds.listRelatives(light,parent=True,shapes=True,fullPath=True)
    cmds.matchTransform(f"{convLight}", lightTransform)
    lightSet=cmds.listRelatives(lightTransform,parent=True,fullPath=True)
    if lightSet:
        cmds.parent(f"{convLight}", lightSet)    

def lightsConversion(convNumber):
    with open('/transfer/s5512613_SP/Masters_Project/Render_Scene_Swapper/Dictionary/lights.json','r') as file :
        lightsData=json.load(file)
    currentRenderer=getCurrentRenderer()    
    number=assignNumber(currentRenderer)
    sel = cmds.ls(sl=True)
    if not sel :
        cmds.confirmDialog(title='Error', message='Please select an object', button=['OK'], defaultButton='OK')
        cmds.warning("Error : Please select an object")
        return

    light_conversion_map = {
        lightsData["Lights"]["area_light"]["name"][number]: "area_light",
        lightsData["Lights"]["point_light"]["name"][number]: "point_light",
        lightsData["Lights"]["directional_light"]["name"][number]: "directional_light",
        lightsData["Lights"]["spot_light"]["name"][number]: "spot_light",
        lightsData["Lights"]["skyDome_light"]["name"][number]: "skyDome_light",
        lightsData["Lights"]["mesh_light"]["name"][number]: "mesh_light"
    }

    for obj in sel:
        lights = cmds.ls(sl=True, dag=True, s=True)
        print(lights)
        for light in lights:
            print(light)
            light_type = cmds.nodeType(light)
            print(light_type)
            if light_type in light_conversion_map:
                light_type = light_conversion_map[light_type]
                print(light_type)
                copyLightAttributes(light, lightsData, light_type, number, convNumber)


def convertLights(convNumber):
    currentRenderer=getCurrentRenderer()
    print(currentRenderer)
    check1=checkCurrentRenderer(currentRenderer)
    if check1== "Renderer Supported":
        lightsConversion(convNumber)
    else:
        print("Renderer not supported for conversion")


def createUI():
    
    # Function to call the selected conversion function
    def convert_selected(conversion_group):
        selected_button = cmds.radioCollection(conversion_group, query=True, select=True)
        selected_button_f = cmds.radioButton(selected_button, query=True, label=True)
        print(f"{selected_button_f=}")
        if selected_button_f == "Arnold to Renderman":
            convNumber=1
            convertLights(convNumber)
        elif selected_button_f == "Renderman to Arnold":
            convNumber=0
            convertLights(convNumber)
        elif selected_button_f == "Arnold to VRay":
            convNumber=2
            convertLights(convNumber)
        elif selected_button_f == "VRay to Arnold":
            convNumber=0
            convertLights(convNumber)
        elif selected_button_f == "Renderman to VRay":
            convNumber=2
            convertLights(convNumber)
        elif selected_button_f == "VRay to Renderman":
            convNumber=1
            convertLights(convNumber)
    
    window_name = "Renderer_Scene_Swapper"
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)
        
    cmds.window(window_name, title="Universal Renderer Scene Swapper : Maya",widthHeight=(500, 300))

    # Creating a radio button group to choose the conversion function
    layout=cmds.columnLayout(adjustableColumn=True)
    cmds.text(label="Please select all the lights and then select the conversion function:")
    conversion_group = cmds.radioCollection()
    arnold_to_renderman_button = cmds.radioButton(label="Arnold to Renderman")
    print(f"{arnold_to_renderman_button=}")
    renderman_to_arnold_button = cmds.radioButton(label="Renderman to Arnold")
    print(f"{renderman_to_arnold_button=}")
    arnold_to_vray_button = cmds.radioButton(label="Arnold to VRay")
    print(f"{arnold_to_vray_button=}")
    vray_to_arnold_button = cmds.radioButton(label="VRay to Arnold")
    print(f"{vray_to_arnold_button=}")
    renderman_to_vray_button = cmds.radioButton(label="Renderman to VRay")
    print(f"{renderman_to_vray_button=}")
    vray_to_renderman_button = cmds.radioButton(label="VRay to Renderman")
    print(f"{vray_to_renderman_button=}")

    # Creating a button to trigger the selected conversion function
    cmds.button(label="Convert", command=lambda *args: convert_selected(conversion_group))
    cmds.showWindow(window_name)

# Calling the createUI function
createUI()