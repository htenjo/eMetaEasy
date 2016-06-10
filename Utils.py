import os


# This functions renames all files inside directory_path with wrong extensions
# to the right form. For example "my_file pdf" -> "my_file.pdf" where
# file_end_with_string = " pdf" and file_default_extension = ".pdf"
def rename_files(directory_path, file_default_extension, file_end_with_string):
    print "-> Listing files..."
    files = []

    for name in os.listdir(directory_path):
        file_path = os.path.join(directory_path, name)
        is_file = os.path.isfile(file_path)
        is_pdf = file_path.endswith(file_end_with_string)

        if is_file and is_pdf:
            last_space_index = file_path.rfind(" ")
            print "File processed: " + file_path
            new_file_path = file_path[:last_space_index] + file_default_extension
            print "File renamed to " + new_file_path
            os.rename(file_path, new_file_path)
    return files