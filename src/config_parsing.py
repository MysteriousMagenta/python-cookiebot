import re
# Basic Regex
regex = {
    str: "^([^=]+)=['\"]([^'\"]*)['\"]$",
    int: "^([^=]+)=(\d+)$",
    list: "^([^=])=\[(.*?)\]$"
}
for i in regex:
    regex[i] = re.compile(regex[i])


def parse_line(line):
    for type_,reg in regex.items():
        data = reg.match(line)
        data_dict = {}
        if data:
            if type_.__name__ == "list":
                data_dict[data.group(1)] = []
                for i in data.group(2).split(","):
                    i = i.strip()
                    data_dict[data.group(1)].append(parse_line("dummy={}".format(i))["dummy"])
            elif type_.__name__ == "str":
                data_dict[data.group(1)] = str(data.group(2))
            elif type_.__name__ == "int":
                data_dict[data.group(1)] = int(data.group(2))
            return data_dict

