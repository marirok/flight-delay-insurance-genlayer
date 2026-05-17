# ✈️ Flight Delay Insurance - GenLayer Smart Contract

**An AI-powered smart contract that actually does something useful**

When your flight is delayed more than 2 hours, compensation is automatically sent to your wallet.

---

## 🎯 The Problem It Solves

```markdown
❌ Current Problem: Getting flight delay insurance payout is hard
   - Fill out forms
   - Gather documentation
   - Wait weeks for processing
   - High chance of claim rejection

✅ GenLayer Smart Contract Solution:
   - Buy insurance in 1 second
   - AI automatically checks flight status from airline websites
   - Instant payout if delayed
   - No documentation or forms required
```

---

## 🏗️ Architecture

```markdown
┌─────────────────────────────────────────────────────────────────┐
│                      GenLayer Blockchain                         │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              FlightInsurance Contract                     │    │
│  │                                                          │    │
│  │  ┌──────────────────┐   ┌───────────────────────────┐   │    │
│  │  │   buy_insurance  │   │ check_flight_and_payout  │   │    │
│  │  │   (payable)      │   │   (AI-powered)           │   │    │
│  │  └────────┬─────────┘   └───────────┬───────────────┘   │    │
│  │           │                        │                    │    │
│  │           ▼                        ▼                    │    │
│  │  ┌──────────────────┐   ┌───────────────────────────┐   │    │
│  │  │ StorageMap       │   │ IAgent.query()            │   │    │
│  │  │ (passenger data) │   │ (AI Oracle)              │   │    │
│  │  └──────────────────┘   └───────────┬───────────────┘   │    │
│  │                                      │                    │    │
│  │                            ┌──────────┴──────────┐        │    │
│  │                            ▼                     ▼        │    │
│  │                    ┌───────────────┐    ┌────────────┐    │    │
│  │                    │ AI Validators │    │  Airline   │    │    │
│  │                    │ (3+ nodes)    │───▶│  Website   │    │    │
│  │                    └───────────────┘    └────────────┘    │    │
│  │                            │                               │    │
│  │                            ▼                               │    │
│  │                    ┌───────────────┐                       │    │
│  │                    │ send_funds()  │                       │    │
│  │                    │ (auto-payout) │                       │    │
│  │                    └───────────────┘                       │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔑 Key Features

| Feature | Description |
| --- | --- |
| **AI-Powered Oracle** | GenLayer validators crawl airline websites using AI |
| **Consensus** | 3+ validators must agree on flight status |
| **Auto-Payout** | Compensation sent directly to passenger wallet |
| **No Claims Process** | No forms, no documentation, no waiting |
| **Re-entrancy Protection** | Double-payout prevention built-in |

---

## 💰 Economics

```markdown
Premium:      10 USDC  (cost to passenger)
Payout:      100 USDC  (compensation on delay > 2 hours)
Profit:       90 USDC  per policy (before operational costs)
```

---

## 📝 Contract Interface

### Functions

#### `buy_insurance(flight_number, departure_date, passenger_wallet)`

Purchase flight delay insurance.

```python
# Example
result = contract.buy_insurance(
    flight_number="IR123",
    departure_date="2025-06-01",
    passenger_wallet="0xAliceWallet123"
)
# Returns: "Insurance purchased for flight IR123. Coverage: 100 USDC."
```

#### `check_flight_and_payout(flight_number)`

Check flight status using AI and auto-pay if delayed.

```python
# Example
result = contract.check_flight_and_payout("IR123")

# Returns:
# {
#     "status": "payout_success",
#     "delay_minutes": 180,
#     "payout_amount": 100,
#     "message": "Flight delayed by 180 minutes. Payout sent to wallet."
# }
```

#### `get_contract_stats()`

Get contract statistics.

```python
stats = contract.get_contract_stats()
# Returns: {total_policies, payout_count, total_payouts, ...}
```

---

## 🚀 Deployment

### 1. Install GenLayer SDK

```bash
pip install genlayer
```

### 2. Deploy Contract

```python
from genlayer import Contract

# Deploy
contract = FlightInsurance.deploy()

# Or load existing
contract = FlightInsurance.at("0xContractAddress")
```

### 3. Usage Flow

```python
# 1. Passenger buys insurance (pays 10 USDC)
contract.buy_insurance(
    flight_number="UA456",
    departure_date="2025-07-15",
    passenger_wallet="0xPassengerWallet",
    value=10  # USDC
)

# 2. After flight departure, anyone triggers the check
# (typically done via automated oracle or frontend button)
result = contract.check_flight_and_payout("UA456")

# 3. If delayed > 2 hours:
#    - 100 USDC auto-sent to passenger wallet
#    - Event emitted for transparency
```

---

## 🎭 Events

| Event | Trigger | Data |
| --- | --- | --- |
| `InsurancePurchased` | `buy_insurance()` called | flight_number, passenger, premium, coverage |
| `PayoutProcessed` | Delay confirmed, payout sent | flight_number, passenger, amount, delay_minutes, reason |

---

## 🔒 Security Features

1. **Exact Premium**: Must pay exactly 10 USDC (no more, no less)
2. **One Policy Per Flight**: Cannot double-insure same flight
3. **Payout Claimed Flag**: Prevents double-payout (checked BEFORE sending funds)
4. **AI Consensus**: 3+ validators must agree on flight status
5. **Strict Validation**: AI response must match expected schema

---

## 📊 Test Results

```markdown
## 📊 Simulator Test Results

```text
======================================================================
✈️  Flight Delay Insurance Smart Contract - GenLayer Demo
======================================================================
📋 Config:   insurance_payout = 100 USDC   premium_cost = 10 USDC   min_delay_hours = 2
----------------------------------------------------------------------
🎫 Scenario 1: Purchase Insurance
----------------------------------------------------------------------
✅ Insurance purchased:   flight_number: IR123   passenger: 0xAliceWallet123   premium: 10 USDC   coverage: 100 USDC
----------------------------------------------------------------------
🔍 Scenario 2: Check Flight Status (Delayed - 3 hours)
----------------------------------------------------------------------
🔮 [GenLayer AI Query]   prompt: Check flight IR123 status...   min_validators: 3   validation_rules: strict   ✓ AI Response: delayed (180 min delay)
💸 [PAYMENT] 100 USDC → 0xAliceWallet123
📊 Result:   status: payout_success   message: Flight delayed by 180 minutes. Payout sent.   💰 payout: 100 USDC   ⏱️  delay: 180 minutes
----------------------------------------------------------------------
🔍 Scenario 3: Purchase & Check On-Time Flight
----------------------------------------------------------------------
🔮 [GenLayer AI Query]   prompt: Check flight IR789 status...   min_validators: 3   validation_rules: strict   ✓ AI Response: on_time (0 min delay)
📊 Result:   status: no_payout   message: Flight on time or delay under 2 hours threshold.   delay: 0 minutes
----------------------------------------------------------------------
🚫 Scenario 4: Prevent Double Payout (should reject)
----------------------------------------------------------------------
✅ Double payout prevented:   message: Payout has already been claimed for this flight
======================================================================
📊 Test Summary
======================================================================
✅ Tests: 4/4 passed
📈 Contract Stats:   Total policies: 2   Payouts processed: 1   Total USDC paid out: 100
📢 Events Emitted:   Event(InsurancePurchased, {'flight_number': 'IR123', 'passenger': '0xAliceWallet123'})   Event(PayoutProcessed, {'flight_number': 'IR123', 'amount': 100})   Event(InsurancePurchased, {'flight_number': 'IR789', 'passenger': '0xBobWallet456'})
======================================================================
🎉 All GenLayer smart contract tests completed successfully!
======================================================================
```

---

## 🔮 The AI Magic (How IAgent.query Works)

```python
# This is the core of the contract - the AI oracle call:
ai_response = IAgent.query(
    prompt="""
    Flight: IR123
    Departure: 2025-06-01
    
    Go to airline website and check if this flight was delayed.
    Return: status (delayed/on_time), delay_minutes, reason
    """,
    ABI='{"status": "string", "delay_minutes": "number", "reason": "string"}',
    min_validators=3,        # 3+ AI validators must agree
    validation_rules="strict"  # Response must match schema
)
```

GenLayer's AI validators:

1. Receive the query
2. Each independently crawls airline websites
3. Reach consensus on flight status
4. Return structured data to the contract

This is what makes GenLayer special - **the contract can fetch real-world data using AI**.

---

## 📁 Project Structure

```markdown
flight-delay-insurance-genlayer/
├── README.md       # This file
├── contract.py     # Main smart contract (GenLayer)
└── demo.py         # Local testing with mock
```

---

## 📜 License

MIT License - Use freely for educational and commercial purposes.
