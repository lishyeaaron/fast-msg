# -*- coding: utf-8 -*-
import shutil
import os
import time


class Storage:
    """
    封装了操作系统文件、路径相关操作 实现类linux命令
    """

    @staticmethod
    def pwd():
        """
        获取当前路径
        :return:
        """
        return os.getcwd()

    @staticmethod
    def ls(path='.'):
        """
        获取当前目录下的文件
        :param path:
        :return:
        """
        return os.listdir(path)

    @staticmethod
    def has(path, time_out=0, retry=1):
        for i in range(retry):
            if os.path.exists(path):
                return True
            else:
                time.sleep(time_out)
        return False

    @staticmethod
    def isfile(src):
        return os.path.isfile(src)

    @staticmethod
    def copy(src, dst, exist_ignore=True):
        """
        copy file
        :param src:
        :param dst:
        :param exist_ignore
        :return:
        """
        try:
            if os.path.isfile(src):
                shutil.copy(src, dst)
            else:
                shutil.copytree(src, dst)
        except FileExistsError:
            print('文件已经存在')
            if not exist_ignore:
                raise

    @staticmethod
    def move(src, dst):
        """
        move file
        :param src:
        :type src:str
        :param dst:
        :type dst:str
        :return:
        """
        shutil.move(src, dst)

    @staticmethod
    def cd(path):
        """
         cd pah.
         :type path: str
         """
        os.chdir(path)

    @staticmethod
    def rm(path):
        """
         rm pah.
         :type path: str
         :return:list of file content
         """
        try:
            if os.path.isfile(path):
                os.remove(path)
            else:
                shutil.rmtree(path)
        except (Exception,):
            pass

    @staticmethod
    def rm_suffix_recurve(path, suffix):
        """
        递归删除文件下后缀名为suffix的文件
        :param path:
        :param suffix:
        :return:
        """
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(suffix):
                    os.remove(os.path.join(root, file))

    @staticmethod
    def rm_suffix(path):
        """
        删除后缀名为suffix的文件
        :param path:
        :return:
        """
        print(path)
        for f in Storage.ls(path):
            Storage.rm(f)

    @staticmethod
    def mkdir(dir_name):
        """
        make direction
        :param dir_name:
        :type dir_name:str
        :return:
        """
        os.mkdir(dir_name)

    @staticmethod
    def check_or_mkdir(dir_path):
        """
        make direction
        :param dir_path:
        :type dir_path:str
        :return:
        """
        if not Storage.has(dir_path):
            Storage.mkdir(dir_path)

    @staticmethod
    def touch(file_name, mode=0o777):
        """
        make file
        :param file_name:
        :type file_name:str
        :param mode:
        :return:
        """
        with open(file_name, 'w') as f:
            f.write('')
            f.close()
        os.chmod(file_name, mode)

    @staticmethod
    def join_path(path, file_name):
        """
         join_path
         """
        return os.path.join(path, file_name)

    @staticmethod
    def read_file(file_name):
        """
         read file and return list of file content.
         :type file_name: str
         :return:list of file content
         """
        with open(file_name, 'rb') as f:
            file_content = f.readlines()
            f.close()
            return file_content

    @staticmethod
    def write_file(file_name, content):
        """
         write file.
         :type file_name: str
         :type content: str
         """
        with open(file_name, 'w') as f:
            f.write(content)
            f.close()

    @staticmethod
    def safe_write_file(file_name, content, mode='w'):
        """
         安全写入文件，如果遇到文件被占用的情况，会等待一段时间后再次尝试写入write file.
         :type file_name: str
         :type content: str
            :type mode: str
         """
        max_retry = 15
        retry = 0
        while retry < max_retry:
            try:
                with open(file_name, mode, encoding='utf-8') as f:
                    f.write(content)
                    f.close()
                    break
            except (Exception,):
                retry += 1
                time.sleep(1)
                print(f'write file {file_name} failed, retry {retry} times')
                pass
        else:
            raise Exception("文件写入失败,请检查是否被占用: %s" % file_name)

    @staticmethod
    def safe_append_file(file_name, content):
        """
         安全追加写入文件，如果遇到文件被占用的情况，会等待一段时间后再次尝试写入write file.
         :type file_name: str
         :type content: str
         """
        max_retry = 15
        retry = 0
        while retry < max_retry:
            try:
                with open(file_name, 'a') as f:
                    f.write(content)
                    f.close()
                    break
            except (Exception,):
                retry += 1
                time.sleep(1)
                pass
        else:
            raise Exception("write file failed: %s" % file_name)

    @staticmethod
    def append_list_to_file(file_name, write_content):
        """
         append list of str to file.if file not exists,new file then  write.
         :param file_name:str
         :type write_content:list of str
         :return:
         """
        with open(file_name, "a") as f:
            f.writelines(write_content)
            f.close()

    @staticmethod
    def rm_dir(dir_name):
        """
        remove direction
        :param dir_name:
        :type dir_name:str
        :return:
        """
        os.rmdir(dir_name)

    @staticmethod
    def split_path(path):
        """
        split path to two.
        :param path:
        :type path:str
        :return:tuple of (str,str)
        """
        return os.path.split(path)

    @staticmethod
    def rename_file_or_dir(old_name, new_name):
        """
        rename file or dir.
        :param old_name:
        :type old_name:str
        :param new_name:
        :type new_name:str
        :return:
        """
        os.rename(old_name, new_name)

    @staticmethod
    def remove_file(file_name):
        """
        remove file
        :param file_name:
        :type file_name:str
        :return:
        """
        os.remove(file_name)

    @staticmethod
    def rm_path(path):
        """
        递归删除文件夹、文件
        """
        if os.path.isdir(path):
            for i in os.listdir(path):
                Storage.rm_path(os.path.join(path, i))
            os.rmdir(path)
        else:
            os.remove(path)

    @staticmethod
    def get_files_by_suffix(suffix, path='', recursive=False):
        """
        获取指定目录下指定后缀的文件
        :param path:
        :param suffix:
        :param recursive:
        :return:
        """
        file_list = []
        if recursive:
            for root, dirs, files in os.walk(path):
                for file in files:
                    if os.path.splitext(file)[1] == suffix:
                        file_list.append(os.path.join(root, file))
            return file_list
        else:
            return [file for file in os.listdir(path) if file.endswith(suffix)]

    @staticmethod
    def get_file_by_suffix(suffix, path='', recursive=False):
        """
        获取指定目录下指定后缀的文件
        :param path:
        :param suffix:
        :param recursive:
        :return:
        """
        if path == '':
            path = Storage.pwd()
        files = Storage.get_files_by_suffix(suffix, path, recursive)
        if not files:
            raise FileNotFoundError('未找到{}文件'.format(suffix))
        else:
            return files[0]

    @staticmethod
    def count_file(file_name, word):
        """
        统计文件中某个字符串出现的次数
        :param file_name:
        :param word:
        :return:
        """
        count = 0
        with open(file_name, 'r', encoding='utf-8') as f:
            for line in f:
                line = "".join(line.split())
                if word in line:
                    print(line)
                    count += 1
        return count

    @staticmethod
    def get_file_size(file_name, unit='MB', precision=2):
        """
        获取文件大小
        :param file_name:
        :param unit:
        :param precision:
        :return:
        """
        size = os.path.getsize(file_name)
        if unit == 'B':
            size = size
        elif unit == 'KB':
            size = size / 1024
        elif unit == 'MB':
            size = size / 1024 / 1024
        elif unit == 'GB':
            size = size / 1024 / 1024 / 1024
        else:
            raise Exception('不支持的单位')
        return round(size, precision)

    @staticmethod
    def chmod(path, mode):
        """
        设置window文件夹与文件的权限
        :param path:
        :param mode:
        :return:
        """
        if os.path.exists(path):
            os.chmod(path, mode)
        else:
            raise Exception(f'文件或文件夹{path}不存在')

    @staticmethod
    def get_all_files(path, suffix='', recursive=False):
        """
        获取指定目录下所有文件
        :param path:
        :param suffix:
        :param recursive:
        :return:
        """
        file_list = []
        if recursive:
            for root, dirs, files in os.walk(path):
                for file in files:
                    if os.path.splitext(file)[1] == suffix:
                        file_list.append(os.path.join(root, file))
            return file_list
        else:
            return [file for file in os.listdir(path) if file.endswith(suffix)]

    @staticmethod
    def delete_all_files(path, except_files=None):
        """
        删除除了except_files以外的所有文件
        :param path:
        :param except_files:
        :return:
        """
        if except_files is None:
            except_files = []
        for file in os.listdir(path):
            if file in except_files:
                continue
            file_path = os.path.join(path, file)
            Storage.rm(file_path)
