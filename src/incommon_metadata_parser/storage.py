from pymongo import MongoClient


class MetadataStorage(object):
    def __init__(self, host, port, user, password):
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._client = None

    def _get_client(self):
        if self._client is None:
            self._client = MongoClient(
                self._host,
                port=self._port,
                username=self._user,
                password=self._password
            )

        return self._client

    @staticmethod
    def _to_dict(obj, classkey=None):
        if isinstance(obj, dict):
            data = {}
            for (k, v) in obj.items():
                data[k] = MetadataStorage._to_dict(v, classkey)
            return data
        elif hasattr(obj, "_ast"):
            return MetadataStorage._to_dict(obj._ast())
        elif hasattr(obj, "__iter__") and not isinstance(obj, str):
            return [MetadataStorage._to_dict(v, classkey) for v in obj]
        elif hasattr(obj, "__dict__"):
            data = dict([(key, MetadataStorage._to_dict(value, classkey))
                         for key, value in obj.__dict__.items()
                         if not callable(value) and not key.startswith('_')])
            if classkey is not None and hasattr(obj, "__class__"):
                data[classkey] = obj.__class__.__name__
            return data
        else:
            return obj

    def save_service_providers(self, service_providers):
        db = self._get_client().metadata

        for service_provider in service_providers:
            serialized_service_provider = self._to_dict(service_provider)
            db.sps.insert_one(serialized_service_provider)
