import pypartpicker

pcpp = pypartpicker.Client()

result = pcpp.get_parts(pypartpicker.PRODUCT_CPU_PATH)

print(result.__dict__)
