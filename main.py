import pandas as pd
import tabloo as tb

def memory(end_add):
    lst = [['.']*17]*end_add
    df = pd.DataFrame(lst, columns = ['Memory','0', '1', '2', '3', '4', '5', '6',
                                      '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F'])
    hx = '0000'
    df.loc[0, 'Memory'] = hx
    hx = hex(int(hx, 16)+16)[2:]
    for i in range(1, end_add):
        if(len(hx)==2):
            hx = '00' + hx
        if(len(hx)==3):
            hx = '0' + hx
        hx = hx.upper()
        df.loc[i, 'Memory'] = hx
        if(hx == str(end_add)):
            break
        hx = hex(int(hx, 16)+16)[2:]
    return df

choose = input("input if the file is SIC or SICXE: ")
choose = choose.upper()

if(choose == 'SIC'): #Absolute
    f1 = open('input.txt', 'r')
    for line in f1.readlines():
        # print(line)
        if(line[0] == 'H'):
            start = hex(int(line[7:13], 16) - int(line[12], 16))
            end = hex(int(start, 16) + int(line[13:19], 16))
            # print(end)
            if(line[18]!='0'):
                end = hex(int(end, 16) + (16 - int(line[18], 16)))
            # print(end)
            start = str(start[2:])
            end = str(end[2:])
            end = (16*16*int(end[0], 16)) + (16*int(end[1], 16)) + (int(end[2], 16)+1)
            # print(start)
            # print(end)
            df = memory(end)
        elif(line[0] == 'T'):
            row_hex = hex(int(line[3:7], 16) - int(line[6], 16))[2:]
            # print(row_hex)
            col = line[6]
            # print(col)
            rng = int(line[7:9], 16)
            # print(rng)
            line2 = line[9:]
            line2 = [line2[i:i+2] for i in range(0, len(line2), 2)]
            line2.pop()
            # print(line2)
            for i in range(0, rng):
                col = col.upper()
                # print(col)
                # print(row_hex)
                row = int((16*16*int(row_hex[0], 16)) + (16*int(row_hex[1], 16)) + (int(row_hex[2], 16)))
                # print(row)
                df.loc[row, col] = line2[i]
                if(col == 'F'):
                    col = '0'
                    row_hex = hex(int(row_hex, 16) + 16)
                    row_hex = row_hex[2:]
                else:
                    col = hex(int(col, 16) + 1)[2:]
        else:
            f1.close()
    tb.show(df)


elif(choose == 'SICXE'): #Linker-Loader
    f1 = open('prog2.txt', 'r')
    ES = open('Ext_Sym_Table.txt', 'w')
    relocation = input('enter the start address: ')
    last = '0000'

    for line in f1.readlines():     #crating ESTAB
        line = line.split()
        # print(line)
        if(line[0]=='H'):
            first = hex(int(line[2], 16) + int(relocation, 16) + int(last, 16))[2:].upper()
            ES.write(line[1] + '\t-\t\t' + first + '\t' + line[3] + '\n')
            last = hex(int(line[3], 16) + int(last, 16))[2:].upper()
        if(line[0]=='D'):
            for i in range(1, len(line), 2):
                ES.write('-\t\t' + line[i] + '\t' + hex(int(line[i+1], 16) + int(first, 16))[2:].upper() + '\n')
    f1.close()
    ES.close()

    #Add the object codes of the T records before any modification
    f1 = open('prog2.txt', 'r')
    with open('Ext_Sym_Table.txt') as inp:
        esp = [line.split() for line in inp]

    last = hex(int(relocation, 16) + int(last, 16))[2:]
    end = (16*16*int(last[0], 16)) + (16*int(last[1], 16)) + (int(last[2], 16)+1)
    df = memory(end)

    for line in f1.readlines():
        line = line.split()
        if(line[0]=='H'):
            for i in range(0, len(esp)):
                if(line[1]==esp[i][0]):
                    add = esp[i][2]
                    break
        print(add)
        # print(line)
        if(line[0] == 'T'):
            row_hex = hex(int(line[1], 16) + int(add, 16) - int(line[1][5], 16))[2:]
            print(row_hex)
            col = hex(int(add[3], 16) + int(line[1][5], 16))[2:].upper()
            rng = int(line[2], 16)
            # print(rng)
            # print(col)
            line2 = line[3]
            for k in range(4, len(line)):
                line2 += line[k]
            # print(line2)
            line2 = [line2[i:i+2] for i in range(0, len(line2), 2)]
            # print(line2)
            for i in range(0, rng):
                col = col.upper()
                # print(col)
                # print(row_hex)
                row = int((16*16*int(row_hex[0], 16)) + (16*int(row_hex[1], 16)) + (int(row_hex[2], 16)))
                # print(row)
                df.loc[row, col] = line2[i]
                if(col == 'F'):
                    col = '0'
                    row_hex = hex(int(row_hex, 16) + 16)
                    row_hex = row_hex[2:]
                else:
                    col = hex(int(col, 16) + 1)[2:]

    f1.close()
    ES.close()

    #The modification operation
    f1 = open('prog2.txt', 'r')
    with open('Ext_Sym_Table.txt') as inp:
        esp = [line.split() for line in inp]
    op='+'
    M_add='0'

    for line in f1.readlines():
        line = line.split()
        #Get the cureent prog's address
        if(line[0]=='H'):
            for i in range(0, len(esp)):
                if(line[1]==esp[i][0]):
                    add = esp[i][2]
                    break

        if(line[0]=='M'):
            # print(line)
            # print(add)

            #Find my start position of row and column
            row_hex = hex(int(line[1], 16) + int(add, 16))[2:].upper()
            col = row_hex[3]
            row_hex = hex(int(row_hex, 16) - int(col, 16))[2:].upper()
            row = int((16*16*int(row_hex[0], 16)) + (16*int(row_hex[1], 16)) + (int(row_hex[2], 16)))

            print(row_hex + '\t' + str(row) + '\t' + col)

            #Extracting the val that need modification from the dataframe
            for i in range(0, 3):
                print(col)
                if(i==0): val = df.loc[row, col]
                else: val = val + df.loc[row, col]
                col = hex(1 + int(col, 16))[2:].upper()
                if(col == '10'):
                    col = '0'
                    row += 1
            # print('val before = ')
            # print(val)

            #Get the address of the desired symble we need to add or subtract
            for i in range(0, len(esp)):
                if(line[3][1:] == esp[i][1]):
                    sb_add = esp[i][2]
                    print(esp[i][1])
                if(line[3][1:] == esp[i][0]):
                    sb_add = esp[i][2]
                    print(esp[i][2])
            # print('sb address = ')
            # print(sb_add)

            #Check if the current address the same as the previous one
            #to keep the op sign from previous iteration or ignore it
            if(line[1][4:] != M_add):
                op='+'
            #Doing the operation + or -
            if(line[3][0]=='+' and op=='+'):
                val = hex(int(val, 16) + int(sb_add, 16)).upper()
            else:
                val = hex(int(val, 16) - int(sb_add, 16)).upper()
            #Check if the result have -ve or +ve sign to act in the next iteration based on it
            # print(val)
            M_add = line[1][4:]
            if(val[0]=='-'):
                op='-'
                val = val[3:]
            else:
                op='+'
                val = val[2:]
            # print('val after = ')
            # print(val)
            # print('sign = ')
            # print(op)

            #Check if the length of the val to obtain the diff to get 6 bits in the end
            if(len(val)>6):
                val = val[1:]
            if(len(val)<6):
                for i in range(6-len(val)):
                    val = "0"+val

            #Devide the val into 2 bits in a list
            val = [val[i:i+2] for i in range(0, len(val), 2)]
            # print('val after list = ')
            # print(val)

            #Find my start position of row and column
            row_hex = hex(int(line[1], 16) + int(add, 16))[2:].upper()
            col = row_hex[3]
            row_hex = hex(int(row_hex, 16) - int(col, 16))[2:].upper()
            row = int((16*16*int(row_hex[0], 16)) + (16*int(row_hex[1], 16)) + (int(row_hex[2], 16)))

            #Add back tha val after modification into the dataframe
            for i in range(0, len(val)):
                # print(col)
                df.loc[row, col] = val[i]
                # print(df.loc[row, col])
                col = hex(1 + int(col, 16))[2:].upper()
                if(col == '10'):
                    col = '0'
                    row += 1
    tb.show(df)


else:
    print('Rerun and enter SIC or SICXE')