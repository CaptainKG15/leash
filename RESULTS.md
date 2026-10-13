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

## 2. Payout path, Bradbury: open
Test contract `0x63d25Adf80AA7D57a47F4375E5A859e86AE1c645`.
- deposit of 0.01 GEN accepted; the vault held 0.01 GEN.
- pay_out of 0.004 GEN accepted at 16:59:46 (explorer clock, 13 Oct) and emitted one message; the explorer's finalization window ended at 17:29:44.
- **Result after finalization: not yet recorded.** If the vault shows 0.006 GEN, payouts execute on Bradbury. If it still shows 0.01 GEN, they do not, and Leash is demonstrated on Studio only. An open issue on GenLayer's repository reports queued transfers not executing on this network family, so this is a genuine question.

## 3. Off-chain
- 91 checks pass. 44 of 44 mutants killed (see README).
- Red-team set: 29 cases built. The 8 cases that plain code must refuse were checked off-chain against the contract's own functions: all 8 refused, and none of the 5 genuine pages was wrongly blocked.

## 4. Red team against real validators: not run yet
The table of results will go here, with the number approved when they should not have been, the number of genuine payees refused, and every surprise.
