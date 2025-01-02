with open('avito_5k.txt', 'r', encoding='utf-8') as file:
    s = file.readlines()
    result = []
    counter = 0
    for i in s:
        s1 = i[-6:-1]
        if any(j.isdigit() for j in s1):
            comma_index = i.rindex(',')
            result.append(i[:comma_index] + '\n')
            counter += 1
        else:
            result.append(i)
    for i in range(len(result)):
        try:
            comma_index_check = result[i].rindex(',')
            if any(j.isdigit() for j in result[i][comma_index_check:]):
                print(i, result[i])
        except:
            #print(i, result[i])
            continue

# with open('avito_fixed.txt', 'w', encoding='utf-8') as wfile:
#     wfile.writelines(result)
