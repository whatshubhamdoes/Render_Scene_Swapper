import unittest
from Renderer_Conversion_Tool import *
import maya.cmds as cmds
import maya.mel as mel
import os
import sys

class TestRendererConversionTool(unittest.TestCase):
    def setUp(self):
        self.selected_objects=cmds.ls(selection=True)

    def test_convert_material(self):
        cmds.polySphere()
        mat = cmds.shadingNode('aiStandardSurface', asShader=True)
        sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=mat+'SG')
        cmds.connectAttr(mat+'.outColor', sg+'.surfaceShader', force=True)
        cmds.select('pSphere1')
        cmds.sets(forceElement=sg)
        cmds.setAttr(mat+'.base',1.0)
        cmds.setAttr(mat+'.baseColor', 1, 0, 0, type='double3')
        cmds.setAttr(mat+'.metalness',1.0)
        cmds.setAttr(mat+'.specular',1.0)
        cmds.setAttr(mat+'.specularColor', 0, 1, 0, type='double3')
        cmds.setAttr(mat+'.specularRoughness', 0.5)
        cmds.setAttr(mat+'.specularIor',1.5)
        cmds.setAttr(mat+'.transmission',1.0)
        cmds.setAttr(mat+'.coat',0.2)
        cmds.setAttr(mat+'.coatColor',0.2,0.1,0.5,type='double3')
        cmds.setAttr(mat+'.coatRoughness',0.5)
        cmds.setAttr(mat+'.sheen',0.5)
        cmds.setAttr(mat+'.sheenColor',0.5,0.5,0.5,type='double3')
        cmds.setAttr(mat+'.sheenRoughness',0.5)
        cmds.setAttr(mat+'.normalCamera', 1, 0, 0, type='double3')

        convertMaterials(fromNumber=0, convNumber=1)

        # Check if the new material was created
        new_mat = cmds.ls(type='PxrDisneyBSDF')
        self.assertTrue(new_mat)
        new_sg=cmds.listConnections(new_mat,type='shadingEngine')
        self.assertTrue(new_sg)

        # Check if the attributes were properly converted
        self.assertAlmostEqual(cmds.getAttr(new_mat + '.baseColor'),[(1,0,0)])
        self.assertAlmostEqual(cmds.getAttr(new_mat + '.metallic'),1.0)
        self.assertAlmostEqual(cmds.getAttr(new_mat + '.specular'),1.0)
        self.assertAlmostEqual(cmds.getAttr(new_mat + '.roughness'),0.5)
        self.assertAlmostEqual(cmds.getAttr(new_mat + '.ior'),1.5)
        self.assertAlmostEqual(cmds.getAttr(new_mat + '.diffTrans'),1.0)
        self.assertAlmostEqual(cmds.getAttr(new_mat + '.clearCoatGloss'),0.2)
        self.assertAlmostEqual(cmds.getAttr(new_mat + '.clearCoat'),0.2)
        self.assertAlmostEqual(cmds.getAttr(new_mat + '.sheenTint'),0.5)
        self.assertAlmostEqual(cmds.getAttr(new_mat + '.sheen'),[(0.5,0.5,0.5)])
        self.assertAlmostEqual(cmds.getAttr(new_mat + '.bumpNormal'),[(1,0,0)])
        

    def test_convert_light(self):
        light=cmds.aiAreaLight()
        cmds.setAttr(light+'.intensity',0.5)
        cmds.setAttr(light+'.color',1,0,0,type='double3')
        cmds.setAttr(light+'.exposure',0.5)

        convertLights(fromNumber=0, convNumber=2)
        new_light=cmds.ls(type="VRayLightRectShape")
        self.assertTrue(new_light)
        self.assertAlmostEqual(cmds.getAttr(new_light+'.intensity'),0.707)
        self.assertAlmostEqual(cmds.getAttr(new_light+'.color'),[(1,0,0)])

    def tearDown(self):
        cmds.select(self.selected_objects,replace=True)

if __name__ == '__main__':
    unittest.main()