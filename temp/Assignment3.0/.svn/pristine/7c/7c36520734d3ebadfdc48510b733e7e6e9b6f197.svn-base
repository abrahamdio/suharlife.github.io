import json


class log_entry(object):

    def __init__(self, dict, path, file_log):
        """
        :param dict: file/dir information based on XML
        :type dict: dict
        :param path: path to file/dir
        :type path: string
        :param file_log: dictionary passed from log_entry.py
        :type file_log: fill out a file_log dict
        """
        self._revision = int(dict["revision"])
        self._author = dict["author"]
        dict_date = dict["date"].split("T")
        date_ = dict_date[0]
        time_ = dict_date[1].split(".")[0]
        date = "{} ({})".format(date_, time_)
        self._date = date
        self._message = dict["msg"]
        self._paths = []

        out = json.loads(json.dumps(path['path']))

        # two cases: out is a list (two or paths) , or out is dict(only one path)
        if isinstance(out, list):
            for key in out:
                kind = key["@kind"]
                action = key["@action"]
                url = key["#text"]
                url = url.split("/")
                sep = "/"
                url_univ = sep.join(url[2:])
                self._paths.append( (kind, action, url_univ) )
                file_log[url_univ].add(int(self._revision))
        else:
            kind = out["@kind"]
            action = out["@action"]
            url = out["#text"]
            url = url.split("/")
            sep = "/"
            url_univ = sep.join(url[2:])
            self._paths.append((kind, action, url_univ))
            file_log[url_univ].add(int(self._revision))

    def get_revision(self):
        return self._revision