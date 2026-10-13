# Results

Only what was observed is listed. Open questions are marked open.

## 1. Payout path, Studio: verified
Test contract `pay_test.py` on Studio `0x0ddb8Ce2b4fb3c8cf139521d7c401D9F2C1bD70E`. Throwaway key as owner.

| Time | Event |
|---|---|
| 11:29:37 | deposit of 0.01 GEN accepted, the vault held 0.01 GEN |
| 11:30:23 | pay_out of 0.004 GEN accepted, the vault still held 0.01 GEN |
| 11:31:55 | the vault held 0.006 GEN |
| 11:32:04 | the recipient's balance rose by exactly 0.004 GEN |

The Studio explorer later showed four transactions on the contract, all FINALIZED: the deploy, the deposit, the pay_out call, and a separate outgoing Send of the payout. The contract balance read 0.006 GEN.

Lessons built into Leash: a payout is queued at approval and executes only after finalization (about a minute and a half on Studio), so the app reports "queued" until the balance changes; and the recipient of a test must not be the account that pays gas.

## 2. Payout path, Bradbury: verified, with one caveat
Test contract `0x63d25Adf80AA7D57a47F4375E5A859e86AE1c645`. The owner and the recipient were the same wallet (see the caveat).

| Time (13 Oct, wallet clock) | Event |
|---|---|
| 16:58:59 | deposit of 0.01 GEN accepted; the vault held 0.01 GEN |
| 16:59:46 | pay_out of 0.004 GEN accepted; one message queued; the vault still held 0.01 GEN |
| 17:00:06 | the vault still held 0.01 GEN (the explorer showed the finalization window ending at 17:29:44) |
| 17:40:44 | the vault held **0.006 GEN** |

The recipient's balance read 99.97668828520420365 GEN at 17:00:05 and 99.98068828520420365 GEN at 17:40:43: a rise of exactly 0.004 GEN. The 0.0001294 GEN fall between the first two readings was the gas for the pay_out transaction.

**Caveat:** the recipient was the wallet that paid gas, so its gain is established by comparing readings, not by a clean before-and-after. The vault's drop of exactly 0.004 GEN is the clean evidence. The test page's own verdict said "unexpected" for this reason, and the page now refuses to use the acting account as the recipient.

**Timing:** the money moved some time between the end of the finalization window (17:29) and 17:40, so at most about 40 minutes after approval. On Bradbury a payment reaches the payee long after it is approved, and the app shows "queued" until the balance changes. An issue reported on GenLayer's repository said queued transfers did not execute on this network family; in this test they did, once the transaction was finalized.

## 3. Off-chain
- 91 checks pass. 44 of 44 mutants killed (see README).
- Red-team set: 29 cases built. The 8 cases that plain code must refuse were checked off-chain against the contract's own functions: all 8 refused, and none of the 5 genuine pages was wrongly blocked.

## 4. Red team against real validators: not run yet
The table of results will go here, with the number approved when they should not have been, the number of genuine payees refused, and every surprise.
