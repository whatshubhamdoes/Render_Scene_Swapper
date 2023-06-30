import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaUI as OpenMayaUI
import maya.mel as mel
import os
import sys

def convert_arnold_to_renderman_lights():
    sel = cmds.ls(sl=True)
    if not sel :
        cmds.confirmDialog(title='Error', message='Please select an object', button=['OK'], defaultButton='OK')
        cmds.warning("Error : Please select an object")
        return
    for obj in sel:    
        lights = cmds.ls(sl = True, dag = True, s = True)
        print(lights)
        for light in lights:
            print(light)  
            light_type = cmds.nodeType(light)
            print(light_type)
            if (light_type =='aiAreaLight') :
                intensity = cmds.getAttr(f"{light}.intensity")
                l_color = cmds.getAttr(f"{light}.color")
                exposure = cmds.getAttr(f"{light}.exposure")
                print(intensity)
                print(l_color)
                print(exposure)
                renderman_light = cmds.createNode("PxrRectLight", name=f"{light}_RM")
                cmds.setAttr(f"{renderman_light}.intensity", intensity)
                cmds.setAttr(f"{renderman_light}.lightColor", l_color[0][0], l_color[0][1], l_color[0][2], type="double3")
                cmds.setAttr(f"{renderman_light}.exposure", exposure)
                cmds.matchTransform(f"{light}_RM",f"{light}")

                shading_group = cmds.listConnections(light, type="shadingEngine")
                print(shading_group)
                if shading_group:
                    cmds.connectAttr(f"{renderman_light}.outLight", f"{shading_group[0]}.surfaceShader", force=True)
                
                print(light)
                light_set=cmds.listSets(object=light)
                print(light_set)
                if light_set:
                    cmds.sets(renderman_light,addElement=light_set[0])

convert_arnold_to_renderman_lights()