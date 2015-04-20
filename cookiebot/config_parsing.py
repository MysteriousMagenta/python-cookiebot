import re
# Basic Regexes for each type.
regex = {
    str: "^([^=]+)=['\"]([^'\"]*)['\"]$",
    int: "^([^=]+)=(\d+)$",
    list: "^([^=]+)=\[(.*?)\]$",
    bool: "^([^=]+)=([fF][aA][lL][sS][eE]|[tT][rR][uU][eE])"
}
for i in regex:
    regex[i] = re.compile(regex[i])


def parse_line(line, existing=None):
    for type_, reg in regex.items():
        data = reg.match(line)
        data_dict = existing if existing is not None else {}
        if data:
            if type_.__name__ == "list":
                data_dict[data.group(1)] = []
                for elem in data.group(2).split(","):
                    elem = elem.strip()
                    data_dict[data.group(1)].append(parse_line("dummy={}".format(elem))["dummy"])
            elif type_.__name__ == "str":
                data_dict[data.group(1)] = str(data.group(2))
            elif type_.__name__ == "int":
                data_dict[data.group(1)] = int(data.group(2))
            elif type_.__name__ == "bool":
                data_dict[data.group(1)] = data.group(2).lower() == "true"
            return data_dict


def parse_file(file_obj):
    file_obj.seek(0)
    chosen = {}
    for line in file_obj:
        if line.startswith("#"):
            continue
        parse_line(line, chosen)
    return chosen
