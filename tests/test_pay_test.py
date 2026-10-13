import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "stub")); sys.path.insert(0, os.path.join(HERE, "..", "contracts"))
import pay_test as p
from genlayer import gl, Address
OWNER = Address("0x" + "a" * 40); OTHER = Address("0x" + "b" * 40); TO = "0x" + "c" * 40
n = 0
def check(name, cond):
    global n; assert cond, "FAILED: " + name; n += 1; print("PASS", name)
def refused(f, *a):
    try: f(*a)
    except Exception as e: return "[EXPECTED]" in str(e)
    return False
c = p.PayTest.__new__(p.PayTest); gl.message.sender_address = OTHER; c.__init__(); c.balance = 0
gl.message.sender_address = OWNER; gl.message.value = 1000; c.deposit(); c.balance = 1000
check("deposit is recorded", c.info()["deposited"] == 1000)
check("the first depositor becomes the owner, not the deployer", c.info()["owner"].lower() == OWNER.as_hex.lower())
gl.message.sender_address = OTHER; gl.message.value = 5; c.deposit(); c.balance = 1005
check("a later depositor does not take over ownership", c.info()["owner"].lower() == OWNER.as_hex.lower())
c.balance = 1000; gl.message.value = 0
gl.message.sender_address = OTHER
check("a non-owner cannot pay out", refused(c.pay_out, TO, 10))
gl.message.sender_address = OWNER
check("a zero amount is refused", refused(c.pay_out, TO, 0))
check("more than the balance is refused", refused(c.pay_out, TO, 1001))
from genlayer import sent
c.pay_out(TO, 400)
check("a valid payout emits exactly one transfer to the right address", sent == [(TO, 400)])
check("the payout is recorded", c.info()["paid"] == 400)
print("\n%d checks passed (these check control flow only; money movement must be checked on-chain)" % n)
