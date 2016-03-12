import xmltodict
from collections import defaultdict
from log_entry import log_entry


class xml_obj(object):

    def __init__(self, xml_list_file, xml_log_file):
        """
        Constructor for xml_obj
        :param xml_list_file: xml_list_file
        :type xml_list_file: string
        :param xml_log_file: xml_log_file
        :type xml_log_file: string
        """
        # key: path - value: tuple(child path, type of path<dir,file>)
        self._dir = defaultdict(set)
        # key: path to project - value: dict of log info
        self._projects = {}
        # key: rev - value: log_entry object
        self._log = {}
        # key: path value: set of revision numbers
        self._file_log = defaultdict(set)

        with open(xml_list_file) as fd:
            doc = xmltodict.parse(fd.read())

        with open(xml_log_file) as fd:
            log = xmltodict.parse(fd.read())

        # parsing svn_log
        for logentry in log["log"]["logentry"]:
            dict = {}

            dict["revision"] = logentry["@revision"]
            dict["author"] = logentry["author"]
            dict["date"] = logentry["date"]
            dict["msg"] = logentry["msg"]
            entry = log_entry(dict, logentry["paths"], self._file_log)
            self._log[int(logentry["@revision"])] = entry

        # parsing svn_list
        for entry in doc['lists']['list']['entry']:
            if entry["@kind"] == "dir":
                self._dir[entry['name']].add(None)
                full_dir = entry["name"].split('/')
                if len(full_dir) == 1:
                    self._projects[entry["name"]] = self.get_recent_file_log(entry['name'])
                    self._projects[entry["name"]]["revision"] = int(entry["commit"]["@revision"])

                if len(full_dir) > 1:
                    sep = "/"
                    path = sep.join(full_dir[:-1])
                    self._dir[path].add((entry["name"], "dir"))

            if entry["@kind"] == "file":
                full_dir = entry["name"].split('/')
                sep = "/"
                path = sep.join(full_dir[:-1])
                self._dir[path].add((full_dir[len(full_dir)-1], "file", entry["size"], entry["commit"]["@revision"]))

    def get_all_rev(self):
        """
        A helper function to get all revision number along with its useful information
        :return: dict[revision_number] = info
        :rtype: dict
        """
        result = dict()
        for key in self._log:
            log_entry = self._log[key]
            result[key] = {"author": log_entry._author, "date": log_entry._date, "message": log_entry._message}
        return result

    def get_projects(self):
        """
        A getter for projects to be displayed in homepage
        :return: self._projects
        :rtype: dict
        """
        return self._projects

    def get_files(self, key):
        """
        Get all files given the parent directory
        :param key: parent directory
        :type key: string
        :return: dict[path_to_file] = info on file
        :rtype: dict
        """
        result = {}
        for file in self._dir[key]:
            if file is not None and file[1] == "file":
                url = "{}/{}".format(key, file[0])
                get_log = self.get_recent_file_log(url)
                name = file[0]
                author = get_log["author"]
                revision = file[3]
                date = get_log["date"]
                message = get_log["message"]
                size = file[2]
                type = self.get_type(file[0])
                result[file[0]] = {"name": name, "author": author, "revision": revision, "date": date, "message": message, "size": size, "type": type}
        return result

    def get_dirs(self, key):
        """
        Get all directories given the parent directory
        :param key: parent directory
        :type key: string
        :return: dict[path_to_dir] = info on dir
        :rtype: dict
        """
        result = {}
        for dir in self._dir[key]:
            if dir is not None and dir[1] == "dir":
                url = "{}".format(key)
                get_log = self.get_recent_file_log(url)
                name = dir[0].split("/")
                name = name[len(name)-1]
                author = get_log["author"]
                revision = get_log["revision"]
                date = get_log["date"]
                message = get_log["message"]
                result[dir[0]] = {"name": name, "author": author, "revision": revision, "date": date, "message": message}
        return result

    def get_recent_file_log(self, path):
        """
        Get log given path to file
        :param path: path to file
        :type path: string
        :return: dict[info] = value
        :rtype: dict
        """
        rev = max(self._file_log[path], key=lambda x: self._file_log[x])
        result = dict()
        result["author"] = self._log[rev]._author
        result["revision"] = self._log[rev]._revision
        result["date"] = self._log[rev]._date
        result["message"] = self._log[rev]._message
        return result

    def get_log_by_rev(self, rev):
        """
        Get log given revision number
        :param rev: revision number
        :type rev: string
        :return: dict[info] = value
        :rtype: dict
        """
        result = dict()
        result["author"] = self._log[rev]._author
        result["revision"] = self._log[rev]._revision
        result["date"] = self._log[rev]._date
        result["message"] = self._log[rev]._message
        result["paths"] = self._log[rev]._paths
        return result

    def get_rev_history(self, url):
        """
        Getter for all revision history
        :param url: path to file
        :type url: string
        :return: dict
        :rtype: dict
        """
        return self._file_log[url]

    def get_type(self, file):
        """
        Helper function to specify a file 'type'
        :param file: file.something
        :type file: string
        :return: type
        :rtype: string
        """
        doc = ["pdf", "pptx"]
        diff_file = ["txt", "json"]
        code = ["py", "xml", "java", "html", "iml"]
        img = ["png"]
        doxy = ["Doxyfile", "doxyfile"]
        file_ext = file.split(".")
        length = len(file_ext)
        file_ext = file_ext[length - 1]
        if file_ext in doc:
            return "Documentation"
        elif file_ext in diff_file:
            return "Testing"
        elif file_ext in code:
            return "Code"
        elif file_ext in img:
            return "Image"
        elif file in doxy:
            return "Doxygen"
        else:
            return " - "
