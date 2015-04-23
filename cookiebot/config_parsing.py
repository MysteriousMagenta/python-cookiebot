from __future__ import print_function, division, with_statement
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

section_start = re.compile("^\[(.*?)\]$")


def parse_line(line, section=None):
    data_dict = {}
    if section is not None:
        data_dict[section] = {}
    for type_, reg in regex.items():
        data = reg.match(line)
        if data:
            if type_.__name__ == "list":
                if section is None:
                    data_dict[data.group(1)] = []
                else:
                    data_dict[section][data.group(1)] = []
                for elem in data.group(2).split(","):
                    elem = elem.strip()
                    if section is  None:
                        data_dict[data.group(1)].append(parse_line("dummy={}".format(elem))["dummy"])
                    else:
                        data_dict[section][data.group(1)].append(parse_line("dummy={}".format(elem))["dummy"])
            elif type_.__name__ == "str":
                if section is None:
                    data_dict[data.group(1)] = str(data.group(2))
                else:
                    data_dict[section][data.group(1)] = str(data.group(2))
            elif type_.__name__ == "int":
                if section is None:
                    data_dict[data.group(1)] = int(data.group(2))
                else:
                    data_dict[section][data.group(1)] = int(data.group(2))
            elif type_.__name__ == "bool":
                if section is None:
                    data_dict[data.group(1)] = data.group(2).lower() == "true"
                else:
                    data_dict[section][data.group(1)] = data.group(2).lower() == "true"
            return data_dict


def parse_file(file_obj):
    file_obj.seek(0)
    section = None
    chosen = {}
    for line in file_obj:
        if line.startswith("#"):
            continue
        sect = section_start.match(line)
        if sect:
            section = sect.group(1)
            chosen[section] = {}
            continue
        if section is None:
            chosen.update(parse_line(line, section))
        else:
            chosen[section].update(parse_line(line, section)[section])
    return chosen

if __name__ == "__main__":
    with open("config.txt") as f:
        print(parse_file(f))