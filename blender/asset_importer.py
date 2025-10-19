"""
Blender Asset Importer with instancing support.
Loads GLTF/GLB/FBX/OBJ models and returns a Blender object.
Implements a simple cache of linked Collections for efficient instancing.
"""
from __future__ import annotations

import bpy
from pathlib import Path
from typing import Optional, Dict, Tuple, List


class AssetImporter:
    """Load models (GLTF/FBX/OBJ) and create instances efficiently.

    Cache strategy:
    - Import a model only once per file path, storing the imported root Collection name.
    - Subsequent calls create a Collection Instance (empty with instance_collection) for lightweight instancing.
    - Optionally allow real duplicates if needed (make_real=True).
    """

    def __init__(self) -> None:
        # key: absolute path string -> (collection_name, objects_names)
        self._cache: Dict[str, Tuple[str, List[str]]] = {}

    def import_model(self, file_path: str, *, link_as_instance: bool = True, make_real: bool = False) -> Optional[bpy.types.Object]:
        """Import a model by file extension and return an instance/root object.

        Args:
            file_path: path to the model file (.gltf, .glb, .fbx, .obj)
            link_as_instance: if True, create a collection instance referencing cached import
            make_real: if True and link_as_instance, convert instance to real objects
        """
        path = str(Path(file_path).resolve())
        ext = Path(path).suffix.lower()

        # If already imported, create an instance
        if path in self._cache and link_as_instance:
            collection_name, _ = self._cache[path]
            return self._create_collection_instance(collection_name, make_real=make_real)

        # Import fresh
        prev_objs = set(bpy.data.objects.keys())
        prev_colls = set(bpy.data.collections.keys())

        if ext in (".gltf", ".glb"):
            bpy.ops.import_scene.gltf(filepath=path)
        elif ext == ".fbx":
            bpy.ops.import_scene.fbx(filepath=path)
        elif ext == ".obj":
            bpy.ops.import_scene.obj(filepath=path)
        else:
            raise ValueError(f"Unsupported model extension: {ext}")

        # Determine imported objects and collection
        new_objs = [bpy.data.objects[name] for name in bpy.data.objects.keys() if name not in prev_objs]
        new_colls = [bpy.data.collections[name] for name in bpy.data.collections.keys() if name not in prev_colls]

        # If the importer created a new collection, prefer that; else create one to group
        root_collection = None
        if new_colls:
            # take the newest collection (often importers create one)
            root_collection = new_colls[-1]
        else:
            # create a collection to hold imported objects
            root_collection = bpy.data.collections.new(Path(path).stem)
            for obj in new_objs:
                # Link to collection if not linked yet
                if not any(link.collection == root_collection for link in obj.users_collection):
                    root_collection.objects.link(obj)
            # Ensure collection is linked to the scene
            if root_collection.name not in bpy.context.scene.collection.children:
                bpy.context.scene.collection.children.link(root_collection)

        # Cache
        objects_names = [obj.name for obj in new_objs]
        self._cache[path] = (root_collection.name, objects_names)

        if link_as_instance:
            # Hide original collection by unlinking from view layer if it was newly created at scene root
            # We rely on instances for placement.
            return self._create_collection_instance(root_collection.name, make_real=make_real)
        else:
            # Return a representative object (first imported) if not instancing
            return new_objs[0] if new_objs else None

    def _create_collection_instance(self, collection_name: str, *, make_real: bool = False) -> bpy.types.Object:
        """Create a collection instance for a cached import."""
        collection = bpy.data.collections.get(collection_name)
        if collection is None:
            raise RuntimeError(f"Cached collection not found: {collection_name}")

        # Create an empty and set as collection instance
        instance = bpy.data.objects.new(name=f"{collection_name}_instance", object_data=None)
        instance.instance_type = 'COLLECTION'
        instance.instance_collection = collection
        bpy.context.scene.collection.objects.link(instance)

        if make_real:
            # Convert instance to real objects
            bpy.context.view_layer.objects.active = instance
            instance.select_set(True)
            bpy.ops.object.duplicates_make_real()
            # After making real, original empty remains selected; return it for convenience

        return instance

    def ensure_on_scene(self, obj: bpy.types.Object) -> None:
        """Ensure object is linked to the active scene collection."""
        if obj.name not in bpy.context.scene.collection.objects:
            bpy.context.scene.collection.objects.link(obj)

    def clear_cache(self) -> None:
        self._cache.clear()
