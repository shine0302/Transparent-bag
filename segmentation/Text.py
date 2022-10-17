import bpy
object =  list(bpy.data.objects)
print(object[1])

object_name = bpy.data.objects.keys()
lens = len(object_name) 
for i in range(0,lens):
    if "bag" in str(object_name[i]):
        obj = bpy.data.objects[object_name[i]]
        obj["category_id"] = 1
        print(obj["category_id"] )
    
    else :
        obj = bpy.data.objects[object_name[i]]
        obj["category_id"] = 0
        print(obj["category_id"] )

