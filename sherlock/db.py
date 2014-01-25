from pymongo import MongoClient, GEO2D
import cfg

client = MongoClient(cfg.DB_CONF["host"], cfg.DB_CONF["port"]).watson


class DBConnector():
    def __init__(self):
        pass

    def insert_user(self, external_id, session_key):
        return client.users.insert({
            "external_id": external_id,
            "session_key": session_key,
        })

    def delete_user(self, user_id):
        client.users.remove({"_id": user_id})

    def get_user(self, external_id):
        client.users.find({"external_id": external_id})

    def insert_image(self, user_id, filename, coords, external_ref, hash):
        client.images.ensure_index([("geo", GEO2D)])
        id = client.images.insert({
            "user_id": user_id,
            "filename": filename,
            "geo": coords,
            "external_ref": external_ref,
            "hash": hash
        })
        return id

    def get_image(self, user_id=None, hash=None):
        if user_id is None and hash is None:
            raise RuntimeError
        srch = {}
        if user_id is not None:
            srch["_id"] = user_id
        if hash is not None:
            srch["hash"] = hash

        return client.images.find(srch)

    def find_images_neer(self, user_id, coords=[0, 0], distance=0):
        if len(coords) != 2:
            raise RuntimeError
        cur = client.images.find({
            "user_id": user_id,
            "geo": {"$geoWithin": {
                "$centerSphere": [coords, distance]
            }
            }
        })
        return cur


if __name__ == "__main__":
    conn = DBConnector()
    client.images.drop()
    conn.insert_image("xx", "ss", 56.9, 110, "dfsdf", 12323)
    x = conn.find_images_neer("xx", coords=[56.9, 110], distance=10)
    import pdb;

    pdb.set_trace()
