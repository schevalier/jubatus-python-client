import msgpackrpc
from types import *

class TypeMismatch(Exception):
    pass
class UnknownMethod(Exception):
    pass

def translate_error(e):
    if e.message == 1:
        raise UnknownMethod()
    elif e.message == 2:
        # TODO(unno) we cannot get which arugment is illegal
        raise TypeMismatch()
    else:
        raise e

class Client(object):
    def __init__(self, client, name):
        self.client = client
        self.name = name

    def call(self, method, args, ret_type, args_type):
        if len(args) != len(args_type):
            # This error does not occurr if a client code is correctly generated
            message = "\"%s\" takes %d argument, but %d given" \
                % (method, len(args_type), len(args))
            raise TypeError(message)

        values = [self.name]
        for (v, t) in zip(args, args_type):
            values.append(t.to_msgpack(v))

        try:
            ret = self.client.call(method, *values)
        except msgpackrpc.error.RPCError, e:
            translate_error(e)

        if ret_type != None:
            return ret_type.from_msgpack(ret)

class ClientBase(object):
    def __init__(self, host, port, name, timeout=10):
        address = msgpackrpc.Address(host, port)
        self.client = msgpackrpc.Client(address, timeout=timeout)
        self.jubatus_client = Client(self.client, name)

    def get_client(self):
        return self.client

    def save(self, id):
        return self.jubatus_client.call("save", [id], TBool(), [TString()])

    def load(self, id):
      return self.jubatus_client.call("load", [id], TBool(), [TString()])

    def get_config(self):
        return self.jubatus_client.call("get_config", [], TString(), [])

    def get_status(self):
        return self.jubatus_client.call(
            "get_status",
            [],
            TMap(TString(), TMap(TString(), TString())),
            [])