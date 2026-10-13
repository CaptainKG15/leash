# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
import typing


@gl.evm.contract_interface
class Payee:
  class View:
    pass

  class Write:
    pass


class PayTest(gl.Contract):
  owner: Address
  has_owner: bool
  deposited: u256
  paid: u256

  def __init__(self):
    self.owner = gl.message.sender_address
    self.has_owner = False
    self.deposited = u256(0)
    self.paid = u256(0)

  @gl.public.write.payable
  def deposit(self) -> None:
    if not self.has_owner:
      self.owner, self.has_owner = gl.message.sender_address, True
    self.deposited = u256(int(self.deposited) + int(gl.message.value))

  @gl.public.write
  def pay_out(self, to: str, amount: int) -> None:
    if gl.message.sender_address != self.owner:
      raise gl.vm.UserError("[EXPECTED] only the owner can pay out")
    if amount <= 0 or amount > int(self.balance):
      raise gl.vm.UserError("[EXPECTED] bad amount")
    Payee(Address(to)).emit_transfer(value=u256(amount))
    self.paid = u256(int(self.paid) + amount)

  @gl.public.view
  def info(self) -> typing.Any:
    return {"balance": int(self.balance), "deposited": int(self.deposited), "paid": int(self.paid), "owner": self.owner.as_hex}
