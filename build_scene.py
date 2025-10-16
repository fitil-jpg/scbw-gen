from pxr import Usd, UsdGeom, UsdLux, Gf

stage = Usd.Stage.CreateNew("scene.usda")
world = stage.DefinePrim("/World", "Xform")
stage.SetDefaultPrim(world)

cube = UsdGeom.Cube.Define(stage, "/World/Cube")
UsdGeom.XformCommonAPI(cube).SetTranslate(Gf.Vec3d(0, 0, 0))
cube.CreateSizeAttr(2.0)

light = UsdLux.DistantLight.Define(stage, "/World/Light")
UsdGeom.XformCommonAPI(light).SetRotate(Gf.Vec3f(-45, 45, 0))

cam = UsdGeom.Camera.Define(stage, "/World/Camera")
UsdGeom.XformCommonAPI(cam).SetTranslate(Gf.Vec3d(5, 5, 5))
UsdGeom.XformCommonAPI(cam).SetRotate(Gf.Vec3f(-30, -45, 0))

stage.GetRootLayer().Save()