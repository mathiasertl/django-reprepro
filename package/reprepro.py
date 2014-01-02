import os

class RepreproConfig(dict):
    def __init__(self, basedir):
        self.basedir = basedir
        self.dist_config = os.path.join(basedir, 'conf', 'distributions')


        dist_content = open(self.dist_config).readlines()

        dist_config = {}

        for line in dist_content:
            line = line.strip()
            if line.startswith('#'):
                continue  # skip empty lines

            if '#' in line:
                line = line.split('#', 1)[0].strip()  # strip comments

            if line:
                field, value = line.split(':', 1)
                field = field.strip()
                value = value.strip()

                dist_config[field] = value
            else:
                self[dist_config['Codename']] = dist_config
                dist_config = {}

    def components(self, dist):
        return self[dist]['Components'].split()
