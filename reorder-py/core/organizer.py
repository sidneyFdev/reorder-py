import os
import glob
import re
import datetime
import shutil

"""_summary_

__init__ declarations for the class FolderInformations:
    _path_ :
        It is the folder declared by user.]
        
    _organize_format_ : 
        The format to organize the files and folders. It will be passed with a bar "/" and the following formats:

            %a	Sun	Weekday as locale’s abbreviated name.
            %A	Sunday	Weekday as locale’s full name.
            %w	0	Weekday as a decimal number, where 0 is Sunday and 6 is Saturday.
            %d	08	Day of the month as a zero-padded decimal number.
            %-d	8	Day of the month as a decimal number. (Platform specific)
            %b	Sep	Month as locale’s abbreviated name.
            %B	September	Month as locale’s full name.
            %m	09	Month as a zero-padded decimal number.
            %-m	9	Month as a decimal number. (Platform specific)
            %y	13	Year without century as a zero-padded decimal number.
            %Y	2013	Year with century as a decimal number.
            
        Examples:
            - 'Y/m/d' -> 2023/10/12
            - 'Y/B' -> 2023/September
            - 'Y' -> 2023
            - 'Y-m-d' -> 2023-10-12
            
        Observation: Which bar "/" will create a subfolder.
        
        font: https://strftime.org/
        
    _remove_empty_folders_ :
        During function _fetch_items_from_folder_ if the folder is empty, it will be removed.
        
    _include_subfolders_files_ :
        If True, it will include the files from subfolders and move it.
        
    _move_folders_ : 
        If True, it will move the folders on root_path to the new path.
        If False, it will only move the files from root_path.
"""

class FolderInformations:
    def __init__(self, path: str, remove_empty_folders = True, include_subfolders_files = True, organize_format = 'Y/m/d', move_folders = False, include_ocult_files = True):
        self.root_path = path
        self.include_subfolders_files = include_subfolders_files
        self.move_folders = move_folders
        self.remove_empty_folders = remove_empty_folders
        self.organize_format = organize_format
        self.include_ocult_files = include_ocult_files
        self.items = []

    def fetch_all_items(self):
        # Check for informations in the function fetch_items_from_folder
        self.items = self.fetch_items_from_folder(self.root_path)
        
    def fetch_items_from_folder(self, path):
        
        current_items = []
        has_items = False
        
        if self.include_ocult_files:
            the_glob = (
                glob.glob(os.path.join(path, "*"), recursive=True) +
                glob.glob(os.path.join(path, ".*"), recursive=True)
            )
        else:
            the_glob = glob.glob(os.path.join(path, "*"))
        
        for item in the_glob:
            if os.path.isfile(item):
                has_items = True
                item_info = self.build_item_info(item, "file")
                # FOR KDE - remove .directory
                if item_info['name'] == '.directory':
                    try:
                        os.remove(item)
                    except Exception as e:
                        print(f"[ERROR] While removing {item}: {e}")
                        pass
                else:
                    current_items.append(item_info)

            elif os.path.islink(item):
                has_items = True
                if os.path.exists(os.path.realpath(item)):
                    current_items.append({
                        "parent_path": os.path.dirname(item),
                        "type":"link",
                        "real_path": os.path.realpath(item),
                        "name": os.path.basename(item),
                        "path": item,
                    })
                os.remove(item)


            elif os.path.isdir(item):
                if self.include_subfolders_files:
                    sub_items = self.fetch_items_from_folder(item)
                    if sub_items:
                        has_items = True
                        current_items.extend(sub_items)
                else:
                    has_items = True
                    current_items.append(self.build_item_info(item, "folder"))
                    

                

        # If there are no files or subfolders with content, remove the folder
        if not has_items and self.remove_empty_folders and path != self.root_path:
            try:
                # print(f"[INFO] Removing empty folder: {path}")
                os.rmdir(path)
            except Exception as e:
                pass
                # print(f"[ERROR] While removing {path}: {e}")
                
        return current_items

    def build_item_info(self, item_path, tipo, real_path=None):
        return {
            "path": item_path,
            "parent_path": os.path.dirname(item_path),
            "real_path": real_path if real_path else item_path,
            "size": os.path.getsize(item_path) if tipo == "file" else 0,
            "name": os.path.basename(item_path),
            "type": tipo,
            "extension": os.path.splitext(item_path)[1] if tipo == "file" else None,
            "creation_timestamp": datetime.datetime.fromtimestamp(os.path.getctime(item_path))
        }
        
    def check_if_folder_name_is_date(self, item):
        if item['type'] != 'folder':
            return False

        try:
            datetime.datetime.strptime(item['name'], self.organize_format)
            return True
        except ValueError:
            return False
    
    def move_items(self):
        self.fetch_all_items()
        for item in self.items:
            if self.check_if_folder_name_is_date(item):
                pass
            else:      
                try:
                    new_path = ( self.root_path + "/" + item['creation_timestamp'].strftime(self.organize_format) + "/" + item['name'] )      
                    
                    # print(f"[INFO] {item['path']} -> {new_path}")
                    os.makedirs(os.path.dirname(new_path), exist_ok=True)
                    if item['type'] == 'file':
                        os.rename(item['path'], new_path)
                    elif item['type'] == 'link':
                        shutil.copy(item['real_path'], new_path)
                except Exception as e:
                    print(f"[INFO] {e}")
            

test = FolderInformations(
    input(str()),
    remove_empty_folders=True,
    include_subfolders_files=True,
    organize_format='%Y/%B-%d'
)

test.move_items()
