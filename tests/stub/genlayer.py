class Address:
    def __init__(self, h): self._h = h
    @property
    def as_hex(self): return self._h
    def __eq__(self, o): return isinstance(o, Address) and self._h.lower() == o._h.lower()
    def __ne__(self, o): return not self.__eq__(o)
    def __hash__(self): return hash(self._h.lower())
u256 = int
class UserError(Exception): pass
sent = []   # every transfer the contract emits, recorded here instead of moving money
class _Evm:
    @staticmethod
    def contract_interface(cls):
        class Proxy:
            def __init__(self, addr): self.addr = addr
            def emit_transfer(self, value): sent.append((self.addr.as_hex, int(value)))
        return Proxy
class _Public:
    @staticmethod
    def view(f): return f
    class write:
        def __new__(cls, f): return f
        @staticmethod
        def payable(f): return f
class _Msg:
    sender_address = Address("0x" + "a" * 40)
    value = 0
class _Vm: UserError = UserError
class _Gl:
    Contract = object
    public = _Public
    evm = _Evm()
    message = _Msg()
    vm = _Vm()
gl = _Gl()
