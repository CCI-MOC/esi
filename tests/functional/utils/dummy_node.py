import os
import tempfile

class DummyNode():
    def __init__(self, node_dir, project_uuid=''):
        if not os.path.exists(node_dir):
            os.mkdir(node_dir)
        elif not os.path.isdir(node_dir):
            raise NotADirectoryError('Invalid value for dummy_node_dir: %s'
                    % node_dir)

        dummy_node_info = [
                '{',
                '   "project_owner_id": "%s",' % project_uuid,
                '   "server_config": {',
                '       "example_attribute": "example server config",',
                '       "cpu_type": "Intel Xeon",',
                '       "cores": 16,',
                '       "ram_gb": 512,',
                '       "storage_type": "Samsung SSD",',
                '       "storage_size_gb": 1024',
                '   }',
                '}']

        node = tempfile.mkstemp(prefix='', dir=node_dir, text=True)
        node_fd = node[0]
        node_path = node[1]
        for line in dummy_node_info:
            os.write(node_fd, ('%s\n' % line).encode())
        os.close(node_fd)

        self.path = node_path
        self.uuid = os.path.basename(node_path)

    def __del__(self):
        os.remove(self.path)
