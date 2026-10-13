# Leash: payout proof

Before building the real project (a wallet that reads a payee's page and checks it against a plain-English policy before it pays), this proves the one risky thing: **can a contract receive GEN and pay it out to an address, on the network we will use?**

Test GEN only. Never use this with value.

## Why this test exists
- Paying an address with `gl.get_contract_at(address).emit_transfer(...)` is known to pay nobody while the contract still reports "paid". The contract here uses the documented external route instead (`gl.evm.contract_interface`).
- An open issue on GenLayer's repo reports that on the network family Bradbury belongs to, emitted transfers may never execute. It may have been fixed. This test finds out.
- The local test mode cannot move money, so only an on-chain balance check counts. That is what `app/paytest.html` does.

## Run it
**First, host the pages.** Wallets only connect to normal websites, not to files opened from your computer. Host the folder with GitHub Pages, exactly as for Beat the Jury:
1. Create a new public GitHub repo called `leash`.
2. Unzip, then upload everything inside the folder (Add file, Upload files) and commit.
3. Settings, Pages, deploy from branch `main`, root. Wait for the green build in the Actions tab.
4. Your pages are then at `https://<your-username>.github.io/leash/app/deploy_bradbury.html` and `https://<your-username>.github.io/leash/app/paytest.html`.

1. **Studio:** paste `contracts/pay_test.py` into studio.genlayer.com and deploy with no arguments. Open `app/paytest.html` (host it with GitHub Pages if opening the file directly does not work), choose Studio, paste the address.
2. **Step 1, Deposit** 0.01 GEN.
3. **Step 2, Read before:** enter a recipient address you can look at and press the button. This records both the recipient's balance and the vault's balance.
4. **Step 3, Pay out** 0.004.
5. **Wait.** The money only moves once the pay out is **FINALIZED**, which comes after "accepted" and can take minutes. Open the transaction on the explorer and wait for FINALIZED. Judging earlier gives "Not yet", which is not a failure.
6. **Step 4, Read after:** press the button. The verdict comes from both balances:
   - **Received:** the recipient gained the amount. Payouts work here.
   - **Not yet:** neither balance changed. Wait for FINALIZED and judge again. If it stays like this long after FINALIZED, payouts are not executing on this network.
   - **Lost in transit:** the vault gave the money but the recipient got nothing. The payout is going to the wrong place.
   - **Unexpected:** something else moved. Other transactions may have touched the accounts.
7. **Bradbury:** deploy with `app/deploy_bradbury.html` (wallet needed), then repeat steps 2 to 6 with the wallet, using small amounts.

Record every result, including "Not yet" and "received nothing".

## What it does not prove
Anything about the jury, the policy or the page reading. This is only the money path.
