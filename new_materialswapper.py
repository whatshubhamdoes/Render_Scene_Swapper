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


def createMaterialComponentMap(components_material_map,materialsData,material_type,number):
    for material in materialsData["Materials"]:
        if material != "renderer":
            for key,value in materialsData["Materials"][material_type].items():
                if key in ["attribute_diffuse_color", "attribute_specular_color", "attribute_roughness", "attribute_metalness", "attribute_opacity", "attribute_normal_map", "attribute_displacement", "attribute_emissive_color", "attribute_transparency", "attribute_ambient_occlusion"]:
                    components_material_map[key]= value[number]


def copyMaterialAttributes(material, materialsData, material_type, number, convNumber):
    convMaterial = materialsData["Materials"][material_type]["name"][convNumber]
    print(convMaterial)
    convMaterial = cmds.shadingNode(f"{convMaterial}", asShader=True, name=f"{material}_conv")
    convMaterialShadingGroup = cmds.sets(convMaterial, renderable=True, noSurfaceShader=True, empty=True, name=convMaterial + 'SG')
    cmds.connectAttr(convMaterial + '.outColor', convMaterialShadingGroup + '.surfaceShader', force=True)
    
    components_material_map = {}
    createMaterialComponentMap(components_material_map, materialsData, material_type, number)
    print(components_material_map)
    
    components_convMaterial_map = {}
    createMaterialComponentMap(components_convMaterial_map, materialsData, material_type, convNumber)
    print(components_convMaterial_map)
    
    for attr, convAttr in zip(components_material_map.values(), components_convMaterial_map.values()):
        try:
            material_new = ''.join(material)
            attribute = material_new + '.' + attr
            value = cmds.getAttr(attribute)
            file_node = cmds.connectionInfo(attribute, sourceFromDestination=True)
            
            convMaterial = ''.join(convMaterial)
            convMaterial_new = convMaterial + '.' + convAttr
            if 'met'in attr.lower():
                if convNumber or number == 1:
                    if convNumber == 1:
                        # as explained in this - https://rmanwiki.pixar.com/display/REN24/PxrMetallicWorkflow
                        renderman_shader = ''.join(convMaterial)
                        print(renderman_shader)
                        print(convMaterial)
                        rman_metallic_shader = cmds.shadingNode('PxrMetallicWorkflow', asShader=True)
                        if file_node:
                            try:
                                file_path_bColor = cmds.listConnections(convMaterial + '.baseColor', type='file')
                                file_path_bColor = ''.join(file_path_bColor)
                            except:
                                file_path_bColor = cmds.listConnections(convMaterial + '.diffuseColor', type='file')
                                file_path_bColor = ''.join(file_path_bColor)

                            cmds.connectAttr(file_path_bColor + '.outColor', rman_metallic_shader + '.baseColor')
                            file_path_metallic = cmds.listConnections(material_new + attr, type='file')
                            file_path_metallic = ''.join(file_path_metallic)
                            cmds.connectAttr(file_path_metallic + '.outAlpha', rman_metallic_shader + '.metallic')
                            
                        else:
                            try:
                                file_node_new = cmds.connectionInfo(material_new + '.baseColor', sourceFromDestination=True)
                            except:
                                file_node_new = cmds.connectionInfo(material_new + '.diffuseColor', sourceFromDestination=True)
                            if file_node_new:
                                try:
                                    file_path_bColor = cmds.listConnections(material_new + '.baseColor', type='file')
                                    file_path_bColor = ''.join(file_path_bColor)
                                except:
                                    file_path_bColor = cmds.listConnections(material_new + '.diffuseColor', type='file')
                                    file_path_bColor = ''.join(file_path_bColor)
                                
                                cmds.connectAttr(file_path_bColor + '.outColor', rman_metallic_shader + '.baseColor')
                                metalness = cmds.getAttr(material_new + attr)
                                print(metalness)
                                cmds.setAttr(rman_metallic_shader + '.metallic', metalness)
                            
                            else:
                                try:       
                                    diffuse_color = cmds.getAttr(material_new + '.baseColor')
                                except:
                                    diffuse_color = cmds.getAttr(material_new + '.diffuseColor')
                                
                                cmds.setAttr(rman_metallic_shader + '.baseColor', diffuse_color[0][0], diffuse_color[0][1], diffuse_color[0][2], type='double3')
                                metalness = cmds.getAttr(material_new + attr)
                                print(metalness)
                                cmds.setAttr(rman_metallic_shader + '.metallic', metalness)
                        
                        cmds.connectAttr(rman_metallic_shader + '.resultDiffuseRGB', convMaterial + '.diffuseColor', force=True)
                        cmds.connectAttr(rman_metallic_shader + '.resultSpecularEdgeRGB', convMaterial + '.specularEdgeColor', force=True)
                        cmds.connectAttr(rman_metallic_shader + '.resultSpecularFaceRGB', convMaterial + '.specularFaceColor', force=True)

                    else:
                        print("from renderman metallic")
                        conv_shader=''.join(convMaterial)
                        conv_shader_new=conv_shader+'.'+attr
                        print(conv_shader_new)
                        file_paths=cmds.listConnections(material_new + '.diffuseColor')
                        try:
                            file_paths=''.join(file_paths)
                            file_paths=cmds.getAttr(file_paths+attr)
                            cmds.setAttr(conv_shader_new,file_paths)
                        except:
                            value=cmds.getAttr(attribute)
                            file_node=cmds.connectionInfo(attribute,sourceFromDestination=True)
                            file_paths=''.join(file_paths)
                            if 'met' in file_paths.lower():
                                try:
                                    try:
                                        file_paths = cmds.listConnections(file_paths+'.baseColor')
                                    except:
                                        file_paths = cmds.listConnections(file_paths+'.diffuseColor')
                                    file_paths=''.join(file_paths)
                                    cmds.connectAttr(file_paths + '.outColor', conv_shader_new)
                                except:
                                    print("except")
                                    print(file_paths)
                                    try:
                                        file_paths=cmds.getAttr(file_paths +'.baseColor')
                                    except:
                                        file_paths=cmds.getAttr(file_paths +'.diffuseColor')
                                    cmds.setAttr(conv_shader_new,file_paths)
                            else:
                                cmds.connectAttr(file_paths + '.outColor', conv_shader_new)

                        
                
                else:
                    try:
                        cmds.setAttr(convMaterial_new, value)
                    except:
                        cmds.setAttr(convMaterial_new, value[0][0], value[0][1], value[0][2], type='double3')
                    finally:
                        if file_node:
                            file_path = cmds.listConnections(attribute)
                            file_path = ''.join(file_path)
                            try:
                                cmds.connectAttr(file_path + '.outColor', convMaterial_new)
                            except:
                                cmds.connectAttr(file_path + '.outAlpha', convMaterial_new)
                            finally:
                                cmds.connectAttr(file_path + '.outValue', convMaterial_new)

            else:
                try:
                    cmds.setAttr(convMaterial_new, value)
                except:
                    cmds.setAttr(convMaterial_new, value[0][0], value[0][1], value[0][2], type='double3')
                finally:
                    if file_node:
                        file_path = cmds.listConnections(attribute)
                        file_path = ''.join(file_path)
                        try:
                            cmds.connectAttr(file_path + '.outColor', convMaterial_new)
                        except:
                            cmds.connectAttr(file_path + '.outAlpha', convMaterial_new)
                        finally:
                            cmds.connectAttr(file_path + '.outValue', convMaterial_new)
        except:
            continue
    return convMaterialShadingGroup


def materialsConversion(convNumber):
    with open('/transfer/s5512613_SP/Masters_Project/Render_Scene_Swapper/Dictionary/materials.json','r') as file :
        materialsData=json.load(file)
    currentRenderer=getCurrentRenderer()    
    number=assignNumber(currentRenderer)
    sel = cmds.ls(sl=True)
    if not sel :
        cmds.confirmDialog(title='Error', message='Please select an object', button=['OK'], defaultButton='OK')
        cmds.warning("Error : Please select an object")
        return

    material_conversion_map = {
        materialsData["Materials"]["standard_material"]["name"][number] : "standard_material",
        materialsData["Materials"]["hair_material"]["name"][number] : "hair_material"
    }

    for obj in sel:
        objects=cmds.ls(sl=True,dag=True,s=True)
        print (objects)
        for object in objects:
            print (object)
            shadeEng=cmds.listConnections(object,type='shadingEngine')
            print(shadeEng)
            if shadeEng :
                for sg in shadeEng :
                    print (sg)
                    material=cmds.ls(cmds.listConnections(sg),materials = True)
                    print(material)
                    for mat in material:
                        material_type=cmds.nodeType(mat)
                        print(material_type)
                        if material_type in material_conversion_map :
                            material_type=material_conversion_map[material_type]
                            print(material_type)
                            shading_group= copyMaterialAttributes(material, materialsData, material_type, number, convNumber)
                        cmds.sets(object,edit=True,forceElement=shading_group)



def convertMaterials(fromNumber,convNumber):
    currentRenderer=getCurrentRenderer()
    print(currentRenderer)
    check1=checkCurrentRenderer(currentRenderer)
    if check1== "Renderer Supported":
        materialsConversion(convNumber)
    else:
        print("Renderer not supported for conversion")

def createUI():
    
    # Function to call the selected conversion function
    def convert_selected(*args):
        from_renderer = cmds.optionMenu(from_menu, query=True, value=True)
        to_renderer = cmds.optionMenu(to_menu, query=True, value=True)
        
        conversion_map = {
            "Arnold": 0,
            "Renderman": 1,
            "VRay": 2
        }
        
        if from_renderer and to_renderer:
            from_index = conversion_map.get(from_renderer)
            to_index = conversion_map.get(to_renderer)
            
            if from_index is not None and to_index is not None:
                convertMaterials(from_index, to_index)
    
    window_name = "Renderer_Scene_Swapper"
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)
        
    cmds.window(window_name, title="Universal Renderer Scene Swapper : Maya", widthHeight=(500, 300))

    # Creating two optionMenus to choose the conversion from and to renderers
    layout = cmds.columnLayout(adjustableColumn=True, width=500, columnAlign="center")  # Set width and alignment
    
    cmds.text(label="Please select all the lights and then select the conversion function:", align="center")  # Center align
    
    from_menu = cmds.optionMenu(label="From Renderer:")
    cmds.menuItem(label="Arnold")
    cmds.menuItem(label="Renderman")
    cmds.menuItem(label="VRay")
    
    to_menu = cmds.optionMenu(label="To Renderer:")
    cmds.menuItem(label="Arnold")
    cmds.menuItem(label="Renderman")
    cmds.menuItem(label="VRay")

    # Creating a button to trigger the selected conversion function
    cmds.button(label="Convert", command=convert_selected)
    cmds.showWindow(window_name)

# Calling the createUI function
createUI()
