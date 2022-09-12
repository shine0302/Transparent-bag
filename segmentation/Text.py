import bpy
object =  list(bpy.data.objects)
print(object[1])

for i in range(0,6):
    if str(object[i]) in str('bag'):
        obj = bpy.data.objects[i]
        obj["category_id"] = 1
        print(obj["category_id"] )

