import file_write

explanation = file_write.make_file()

def get_processor(log_file):
    with open(log_file, 'r') as file:
        lines = file.readlines()
    res = []
    ind = 0
    for line in lines:   
        if "OSPLATFORM_TYPE:" in line:
            res.append(line)
        if "[CPU Information]" in line:
          ind = 1
          res.append(line)
        elif ind == 1 and  'MSR8B' not in line:
            res.append(line)  
        elif ind == 1 and 'MSR8B' in line:
            res.append(line)
            break
        else:
            continue
    return res

print(explanation.get_processor())
para = get_processor(log_file = 'my_logfile.txt')

for i in para:
    print(i, end="")

