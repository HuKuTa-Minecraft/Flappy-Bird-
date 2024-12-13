import os.path

from settings import *

resource_debug = False
resources_dir = 'resources'
sprites_dir_name = 'sprites'

class Fonts:
    font16 = None
    font20 = None
    font22 = None
    font32 = None
    font64 = None

    @staticmethod
    def init():
        Fonts.font16 = pg.font.SysFont(None, 16)
        Fonts.font20 = pg.font.SysFont(None, 20)
        Fonts.font22 = pg.font.SysFont(None, 22)
        Fonts.font32 = pg.font.SysFont(None, 32)
        Fonts.font64 = pg.font.SysFont(None, 64)

class Saves:
    from typing import TextIO

    __data_save_file = 'data'

    save_file_path = '.'
    save_file_name = 'scores.sv'

    # __byte_len = 4
    key = 0xDD # 1101 1101

    # FIXME Limit on scores - 255

    @staticmethod
    def save_scores(scores: int):
        if not os.path.exists(Saves.__data_save_file):
            os.mkdir(Saves.__data_save_file)
        save_file = Saves.open_save_file('wb')
        save_file.write(Saves.pack_data(scores))
        if resource_debug:
            print('Saved scores.sv: ' + str(scores))
        save_file.close()
    @staticmethod
    def read_scores() -> int:
        if os.path.exists(Saves.get_save_file_path()) and os.path.isfile(Saves.get_save_file_path()):
            save_file = Saves.open_save_file('rb')
            scores = Saves.unpack_data(save_file.read())
            save_file.close()
            if resource_debug:
                print('Loaded scores.sv: ' + str(scores))
            return scores
        return 0

    @staticmethod
    def open_save_file(mode) -> TextIO:
        return open(Saves.get_save_file_path(), mode)

    @staticmethod
    def get_save_file_path() -> str:
        return f"{Saves.__data_save_file}/{Saves.save_file_path}/{Saves.save_file_name}"

    @staticmethod
    def pack_data(data: int) -> bytes:
        return int.to_bytes(data ^ Saves.key)
    @staticmethod
    def unpack_data(data: bytes) -> int:
        return int.from_bytes(data) ^ Saves.key

class Images:
    from typing import Dict, List

    sprites_dir = resources_dir + os.sep + sprites_dir_name

    images: Dict[str, pg.Surface] = dict()

    @staticmethod
    def load_sync():
        filenames = Images.__find_files(Images.sprites_dir, '.bmp')
        for filename in filenames:
            # print(Images.__image_file + os.sep + filename)
            image_name_entry = filename.split(os.sep)
            image_name = image_name_entry[len(image_name_entry) - 1][:-4]
            if resource_debug:
                print('Loaded sprite from: ' +
                    os.sep.join([image_name_entry[i] for i in range(2, len(image_name_entry))]) +
                    ", with Id: " + image_name
                )
            Images.images[image_name] = pg.image.load(filename).convert_alpha()

    @staticmethod
    def __find_files(path: str, extension: str = '') -> List[str]:
        file_paths = []
        if os.path.isfile(path):
            file_paths.append(path)
        else:
            for file in os.listdir(path):
                if not os.path.isfile(file):
                    file_paths.extend(Images.__find_files(path + os.sep + file, extension))
                elif extension and file.endswith(extension) or not extension:
                    file_paths.append(file)
        return file_paths

    @staticmethod
    def get_images(width: int = 0, height: int = 0, *names):
        return_images = []
        for name in names:
            image = Images.images[name]
            if width and height:
                image = pg.transform.scale(image, (width, height))
            return_images.append(image)
        return return_images