# Leash

A testnet vault that reads the payee's page before it pays.

An AI agent (or a person) asks the vault to pay an address and names the payee's own web page. GenLayer validators read that page and check it against the owner's policy, written in plain English. The vault pays only if they agree. Everything that can be enforced by plain code is enforced by plain code, and the model is used only for the judgement that code cannot make.

**Testnet only.** It does not protect real funds. Never use real money.

## How a payment works
1. The owner deposits test GEN and sets a plain-English policy, a per-payment limit, a total budget, and optionally an agent address.
2. The owner or the agent calls `request_payment(recipient, amount, page URL, reason)`.
3. Anyone calls `judge(request id)`. Each validator fetches the page and decides on its own; they must reach the same verdict (`allow`, `deny` or `review`).
4. `allow` queues the payment. `deny` stops it. `review` waits for the owner to approve or decline. An unreadable page voids the request.
5. A queued payment becomes a real transfer only after the transaction is **finalized**. The app says "queued" until the balance actually changes.

## What plain code decides, and what the model decides
| Decided by plain code (tested, not a model's opinion) | Decided by the model |
|---|---|
| Who may ask for a payment (owner or one named agent) | Whether the page shows a real business or person |
| The per-payment limit and the total budget | Whether the page matches the stated reason |
| Never paying more than the vault holds, even with several payments queued | Whether the policy allows paying it |
| Refusing pages that try to give orders ("ignore previous instructions", fake system notices, a planted verdict) before the model is asked | |
| Refusing pages that do not show the recipient's exact address (stops look-alike and poisoned addresses) | |
| Sending a model failure or a garbled answer to human review, never to payment | |
| Withdrawals, cancellation, and one judgement per request | |

The model can be wrong. The red-team set below measures how often, and the result is published whether or not it flatters the project.

## Testing
- `python3 tests/test_leash.py`: 91 off-chain checks of the logic and accounting (a stand-in network records transfers instead of moving money).
- `python3 tests/mutation_test.py`: breaks the contract in 44 small ways (flipped checks, shifted limits, altered amounts, wrong recipients) and confirms the tests fail each time. **44 of 44 killed.** The first run killed 36 of 44; the 8 survivors were real gaps (boundary values and a length limit) and now have tests.
- `redteam/`: 29 fictional payee pages with a recorded expectation each: 5 genuine businesses, 6 scam-like pages, 4 address problems, 8 injection attempts, 4 policy violations, 2 unreadable pages. Eight of them (the address problems and the pattern-detectable injections) are refused by plain code, and that is checked off-chain. The other 19 reach the model, and the app's **Red team** tab runs them against real validators and records the result.

## Network status
See `RESULTS.md` for the evidence and what is still open.
- **Studio:** the payout path is verified by balances (the vault dropped and the recipient received the exact amount).
- **Bradbury:** deposits work. Whether a queued payout executes there was still being checked when this was written. Nothing in this project claims it until it has been seen.

## Honest limits
- The judgement is a model's reading of a page at one moment. Pages can look different to validators than to a person, and a convincing scam can still pass. The red-team table shows what happened in testing.
- An address on a page proves only that the page claims it, not that the payee owns it.
- The policy is natural language, so it can be ambiguous.
- A single model call per validator means the judgement is correlated, not independent.
- Pages are read as text; the model sees the first 6,000 characters, though the address and injection checks run on the whole page.
- Anyone can deposit; only the owner can withdraw or change the rules. There is no rate limit on requests.
- The owner is trusted. There is no multi-signature, no audit, and no recovery if the owner key is lost.
- Payments are not instant: money moves after finalization, which can take minutes.

## Run it
1. Host the folder on GitHub Pages, then open `app/index.html`.
2. Press **Deploy my own vault**, then **Deposit** and **Save settings**.
3. Use a preset or fill in the agent desk, then **Ask the vault to pay**.
4. For the red team: open the **Red team** tab, press **1. Apply red-team settings and fund the vault**, then **2. Run**. Studio first; it takes a minute or two per case.

`build_app.py` rebuilds `app/index.html` from `app/index.src.html` with the contract embedded.

## Files
- `contracts/leash.py`: the contract, 8,826 bytes, SHA-256 `3b636803db87b0b1e970bf999a64b8b82ed72a97736329564e07ebc64c460ae6`
- `app/`: the page
- `redteam/`: the cases, the generator and the manifest
- `tests/`: the tests and the mutation test
