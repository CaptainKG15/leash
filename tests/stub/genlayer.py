# Local stand-in for the genlayer module so the contract can run off-chain in tests. It is NOT the real SDK.
# It records transfers instead of moving money, so tests check the contract's own accounting, not the network.
class Address:
    def __init__(self, h): self._h = h
    @property
    def as_hex(self): return self._h
    def __eq__(self, o): return isinstance(o, Address) and self._h.lower() == o._h.lower()
    def __ne__(self, o): return not self.__eq__(o)
    def __hash__(self): return hash(self._h.lower())
class _TreeMap:
    def __class_getitem__(cls, item): return dict
TreeMap = _TreeMap
u256 = int
def allow_storage(c): return c
class UserError(Exception): pass
sent = []   # every transfer the contract emits: (address, amount)
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
class _Return:
    def __init__(self, calldata): self.calldata = calldata
class _Vm:
    UserError = UserError; Result = object; Return = _Return
    @staticmethod
    def run_nondet_unsafe(leader_fn, validator_fn):
        res = leader_fn()
        if not validator_fn(_Return(res)): raise Exception("consensus not reached")
        return res
class _Web: get = None; render = None
class _Nondet: web = _Web(); exec_prompt = None
class _Msg:
    sender_address = Address("0x" + "a" * 40); value = 0
class _Contract: balance = 0
class _Gl:
    Contract = _Contract; public = _Public; evm = _Evm(); vm = _Vm(); nondet = _Nondet(); message = _Msg()
gl = _Gl()
