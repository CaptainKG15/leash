# Mutation test for Leash. Run: python3 tests/mutation_test.py
# Each mutant is a small deliberate bug in contracts/leash.py. The test suite should FAIL for every mutant ("killed").
# A mutant that still passes ("survived") shows something the tests cannot see.
import os, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "contracts", "leash.py")
source = open(SRC).read()

EQUIVALENT = {}  # mutants that cannot change behaviour, reported but not counted

MUTANTS = [
    ("owner check inverted", "if gl.message.sender_address != self.owner:", "if gl.message.sender_address == self.owner:"),
    ("anyone but the owner or agent may request", "if s != self.owner and not (self.has_agent and s == self.agent):", "if s != self.owner or not (self.has_agent and s == self.agent):"),
    ("agent check inverted", "s == self.agent)", "s != self.agent)"),
    ("agent flag inverted", 'self.has_agent = agent != ""', 'self.has_agent = agent == ""'),
    ("per-payment limit off by one", "amount > int(self.max_payment)", "amount >= int(self.max_payment)"),
    ("zero amounts allowed", "amount <= 0 or amount > int(self.max_payment)", "amount < 0 or amount > int(self.max_payment)"),
    ("http pages allowed", 'url.startswith("https://")', 'url.startswith("http")'),
    ("url length limit", "len(url) > 300", "len(url) > 3000"),
    ("reason length limit", "len(reason) > 200", "len(reason) > 2000"),
    ("whitespace in urls allowed", "any(c.isspace() for c in url)", "all(c.isspace() for c in url)"),
    ("policy length limit", "len(policy) > 600", "len(policy) > 6000"),
    ("negative limits allowed", "max_payment < 0 or budget < 0", "max_payment < -9 or budget < -9"),
    ("judge a request twice", 'if r.status != "pending":', 'if r.status == "pending":'),
    ("void treated as denied", '.get(v, "void")', '.get(v, "denied")'),
    ("review treated as denied", '"review": "review"', '"review": "denied"'),
    ("allow check inverted", 'if v == "allow":', 'if v != "allow":'),
    ("pay when only one limit is exceeded", "a > int(self.available) or a > int(self.budget_left)", "a > int(self.available) and a > int(self.budget_left)"),
    ("funds boundary off by one", "a > int(self.available) or", "a >= int(self.available) or"),
    ("budget boundary off by one", "or a > int(self.budget_left)", "or a >= int(self.budget_left)"),
    ("available not reduced", "self.available = u256(int(self.available) - a)", "self.available = u256(int(self.available) + a)"),
    ("budget not reduced", "self.budget_left = u256(int(self.budget_left) - a)", "self.budget_left = u256(int(self.budget_left) + a)"),
    ("injection check inverted", "if INJ.search(page) is not None:", "if INJ.search(page) is None:"),
    ("address check inverted", "to.lower() not in page.lower()", "to.lower() in page.lower()"),
    ("address match case sensitive", "to.lower() not in page.lower()", "to.lower() not in page"),
    ("address rule ignored", "if need_addr and", "if False and"),
    ("unknown reason code accepted", 'c if c in CODES else "unclear"', "c"),
    ("model may answer void", "if v not in VERDICTS:", 'if v not in VERDICTS + ("void",):'),
    ("different verdicts accepted", 'leader["verdict"] == validator["verdict"]', 'leader["verdict"] != validator["verdict"]'),
    ("void not a verdict", 'r.get("verdict") in VERDICTS + ("void",)', 'r.get("verdict") in VERDICTS'),
    ("page cap too small", "full[:6000]", "full[:60]"),
    ("empty pages accepted", "if not full.strip():", "if False:"),
    ("address flag always true", "to.lower() in full.lower())", "True)"),
    ("withdraw boundary off by one", "amount > int(self.available)", "amount >= int(self.available)"),
    ("cancel only pending", 'r.status not in ("pending", "review")', 'r.status not in ("pending",)'),
    ("resolve outside review", 'if r.status != "review":', 'if r.status == "review":'),
    ("address rule setting ignored", "self.policy, self.need_addr = policy, need_addr", "self.policy, self.need_addr = policy, True"),
    ("deposit ignored", "int(self.available) + int(gl.message.value)", "int(self.available) + 0"),
    ("plain fetch status check", "r.status == 200", "r.status != 200"),
    ("browser fallback removed", 'return gl.nondet.web.render(url, mode="text")', 'return ""'),
    ("page text includes scripts", "script|style|noscript|template", "style|noscript|template"),
    ("recipient not lowercased", "to=to.lower()", "to=to"),
    ("withdraw sends to the wrong place", "Payee(self.owner)", "Payee(Address(\"0x\" + \"f\" * 40))"),
    ("payment sent to the wrong place", "Payee(Address(r.to))", "Payee(Address(\"0x\" + \"f\" * 40))"),
    ("pattern: marking a payee as approved", r"\s+as\s+(?:allowed|approved|safe|verified|trusted)", r"\s+asX\s+(?:allowed|approved|safe|verified|trusted)"),
    ("pattern: pre-approval claims", r"\bpre-?\s?(?:approved|authori[sz]ed|verified)", r"\bprX-?\s?(?:approved|authori[sz]ed|verified)"),
    ("pattern: skip the checks", r"\bskip\s+(?:the\s+)?(?:checks?", r"\bskiX\s+(?:the\s+)?(?:checks?"),
    ("pattern: message from the owner", r"\s+from\s+(?:the\s+)?(?:vault\s+)?(?:owner|operator|administrator|admin)\b", r"\s+fromX\s+(?:the\s+)?(?:vault\s+)?(?:owner|operator|administrator|admin)\b"),
    ("pattern: the owner has approved it", r"(?:has\s+)?(?:approved|authori[sz]ed|verified)", r"(?:hasX\s+)?(?:approved|authori[sz]ed|verified)"),
    ("pattern: do not mention the note", r"\bdo\s+not\s+(?:mention|reveal)", r"\bdoX\s+not\s+(?:mention|reveal)"),
    ("pattern: approve this payment", r"\b(?:approve|allow)\s+this\s+(?:payment|payee|transfer)", r"\b(?:approvX|allowX)\s+this\s+(?:payment|payee|transfer)"),
    ("prompt: authority claims are red flags", "red flags of fraud", "red flags"),
    ("payment amount altered", "emit_transfer(value=u256(a))", "emit_transfer(value=u256(a + 1))"),
]

def run(contract_path):
    tmp = tempfile.mkdtemp()
    try:
        os.makedirs(os.path.join(tmp, "contracts")); shutil.copy(contract_path, os.path.join(tmp, "contracts", "leash.py"))
        shutil.copytree(HERE, os.path.join(tmp, "tests"), ignore=shutil.ignore_patterns("__pycache__", "attacks"))
        shutil.copytree(os.path.join(HERE, "..", "redteam"), os.path.join(tmp, "redteam"), ignore=shutil.ignore_patterns("__pycache__"))
        return subprocess.run([sys.executable, os.path.join(tmp, "tests", "test_leash.py")], capture_output=True, text=True, timeout=120).returncode
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def main():
    assert run(SRC) == 0, "the unmodified contract must pass the tests first"
    killed, survived, skipped = [], [], []
    for name, old, new in MUTANTS:
        if name in EQUIVALENT: skipped.append((name, "equivalent: " + EQUIVALENT[name])); continue
        if source.count(old) != 1: skipped.append((name, "pattern found %d times" % source.count(old))); continue
        tmp = tempfile.mkdtemp(); m = os.path.join(tmp, "m.py"); open(m, "w").write(source.replace(old, new, 1))
        if subprocess.run([sys.executable, "-m", "py_compile", m], capture_output=True).returncode != 0: skipped.append((name, "does not compile"))
        elif run(m) != 0: killed.append(name)
        else: survived.append(name)
        shutil.rmtree(tmp, ignore_errors=True)
    print("mutants killed: %d of %d" % (len(killed), len(killed) + len(survived)))
    for n in survived: print("  SURVIVED:", n)
    for n, why in skipped: print("  not counted (%s): %s" % (why, n))
    return 0 if not survived else 1

if __name__ == "__main__":
    sys.exit(main())
