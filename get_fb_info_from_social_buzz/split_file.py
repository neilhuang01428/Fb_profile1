FB_NAME_LIST_FILE = "FB_DATA.txt"
LINE_LIMIT = 400
OUTPUT_FILE_TEMPLATE = "./split_name/fb_name_part_%04d.txt"


def write_to_split_file(file_template, input_data, index_number):
    output_file_name = file_template % int(index_number / LINE_LIMIT)

    file_writer = open(output_file_name, "a")
    file_writer.write("%s\n" % input_data)
    file_writer.close()

    write_to_single_file(input_data)

    print(output_file_name)
    print(input_data)


def write_to_single_file(input_data):
    output_file_name = "./split_name/fb_name_all.txt"

    file_writer = open(output_file_name, "a")
    file_writer.write("%s\n" % input_data)
    file_writer.close()


if __name__ == "__main__":
    count = 0
    name_dict = dict()

    file_reader = open(FB_NAME_LIST_FILE, "r")
    for line in file_reader:
        fb_name = line.rstrip("\n").replace("  ", " ")
        if len(fb_name) > 0:
            if fb_name not in name_dict:
                name_dict[fb_name] = 1

            count += 1
    file_reader.close()

    name_count = 0
    for user_name in name_dict:
        name_count += 1
        write_to_split_file(OUTPUT_FILE_TEMPLATE, user_name, name_count)

    print(count)
    print(len(name_dict))
    print(name_count)
