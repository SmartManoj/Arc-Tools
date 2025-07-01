def list_strip(list, element):
    list = list.copy()
    while list and list[0] == element:
        list.pop(0)
    while list and list[-1] == element:
        list.pop()
    return list