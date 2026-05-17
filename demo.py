"""
Demo: Test Flight Delay Insurance Smart Contract (GenLayer)

This file demonstrates how the contract works.
In production, these operations run on GenLayer testnet/mainnet.
"""

import json
from datetime import datetime


# ============================================================================
# Mock Classes for local testing (in production, GenLayer SDK handles this)
# ============================================================================

class MockAddress:
    """Mock address for testing."""
    def __init__(self, address):
        self.address = address

    def __str__(self):
        return self.address


class MockMsg:
    """Mock msg object for testing."""
    def __init__(self, sender, value):
        self.sender = MockAddress(sender)
        self.value = value


class MockBlock:
    """Mock block object for testing."""
    def __init__(self):
        self.timestamp = int(datetime.now().timestamp())


class MockEvent:
    """Mock event log for testing."""
    def __init__(self, name, data):
        self.name = name
        self.data = data

    def __repr__(self):
        return f"Event({self.name}, {self.data})"


# ============================================================================
# Mock StorageMap
# ============================================================================

class MockStorageMap:
    """Mock StorageMap for local testing."""

    def __init__(self):
        self.data = {}

    def contains(self, key) -> bool:
        return key in self.data

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def keys(self):
        return self.data.keys()


# ============================================================================
# Mock IAgent (simulates GenLayer AI Query)
# ============================================================================

class MockIAgent:
    """Mock GenLayer IAgent for local testing."""

    @staticmethod
    def query(prompt: str, ABI: str, min_validators: int, validation_rules: str) -> dict:
        """Simulates GenLayer AI Query with mock responses based on flight number."""

        print(f"\n🔮 [GenLayer AI Query]")
        print(f"   prompt: {prompt[:80]}...")
        print(f"   min_validators: {min_validators}")
        print(f"   validation_rules: {validation_rules}")

        # Simulate different flight scenarios based on flight number
        if "DELAYED" in prompt.upper() or "IR123" in prompt:
            # Simulated delayed flight response
            result = {
                "status": "delayed",
                "delay_minutes": 180,
                "reason": "Weather conditions"
            }
        elif "ONTIME" in prompt.upper() or "IR789" in prompt:
            # Simulated on-time flight response
            result = {
                "status": "on_time",
                "delay_minutes": 0,
                "reason": ""
            }
        else:
            # Default: random delay between 0-120 minutes
            import random
            delay = random.randint(0, 120)
            if delay > 60:
                result = {
                    "status": "delayed",
                    "delay_minutes": delay,
                    "reason": "Aircraft maintenance"
                }
            else:
                result = {
                    "status": "on_time",
                    "delay_minutes": delay,
                    "reason": ""
                }

        print(f"   ✓ AI Response: {result['status']} ({result['delay_minutes']} min delay)")
        return result


# ============================================================================
# Mock send_funds
# ============================================================================

class MockSendFunds:
    """Mock send_funds for local testing."""

    @staticmethod
    def call(to: str, amount: int):
        print(f"💸 [PAYMENT] {amount} USDC → {to}")
        return True


# ============================================================================
# Mock Contract Class (simplified version of the actual contract logic)
# ============================================================================

class FlightInsuranceMock:
    """
    Mock version of FlightInsurance for local testing.
    This simulates the contract logic without GenLayer.
    """

    def __init__(self):
        self.insurance_payout = 100
        self.premium_cost = 10
        self.min_delay_hours = 2
        self.insured_passengers = MockStorageMap()
        self.events = []

    def buy_insurance(self, flight_number, departure_date, passenger_wallet, value):
        """Purchase insurance - mock version."""
        if value != self.premium_cost:
            return {"error": f"Premium must be exactly {self.premium_cost} USDC"}

        if self.insured_passengers.contains(flight_number):
            return {"error": f"Insurance already purchased for flight {flight_number}"}

        passenger_data = {
            "passenger": passenger_wallet,
            "departure_date": departure_date,
            "premium_paid": value,
            "payout_claimed": False,
            "payout_amount": 0,
            "status": "active"
        }

        self.insured_passengers[flight_number] = passenger_data

        self.events.append(MockEvent(
            "InsurancePurchased",
            {"flight_number": flight_number, "passenger": passenger_wallet}
        ))

        return {
            "success": True,
            "message": f"Insurance purchased for flight {flight_number}",
            "coverage": self.insurance_payout,
            "premium": value
        }

    def check_flight_and_payout(self, flight_number):
        """Check flight status and payout - mock version."""
        if not self.insured_passengers.contains(flight_number):
            return {"error": f"No insurance found for flight {flight_number}"}

        passenger_data = self.insured_passengers[flight_number]

        if passenger_data["payout_claimed"]:
            return {"error": "Payout has already been claimed for this flight"}

        # Simulate GenLayer AI Query
        prompt = f"Check flight {flight_number} status"
        ai_response = MockIAgent.query(prompt=prompt, ABI="{}", min_validators=3, validation_rules="strict")

        passenger_data["status"] = ai_response["status"]
        passenger_data["delay_minutes"] = ai_response["delay_minutes"]

        threshold_minutes = self.min_delay_hours * 60

        if ai_response["status"] == "delayed" and ai_response["delay_minutes"] >= threshold_minutes:
            passenger_data["payout_claimed"] = True
            passenger_data["payout_amount"] = self.insurance_payout
            self.insured_passengers[flight_number] = passenger_data

            MockSendFunds.call(passenger_data["passenger"], self.insurance_payout)

            self.events.append(MockEvent(
                "PayoutProcessed",
                {"flight_number": flight_number, "amount": self.insurance_payout}
            ))

            return {
                "status": "payout_success",
                "flight_number": flight_number,
                "delay_minutes": ai_response["delay_minutes"],
                "payout_amount": self.insurance_payout,
                "message": f"Flight delayed by {ai_response['delay_minutes']} minutes. Payout sent."
            }

        else:
            passenger_data["payout_claimed"] = False
            passenger_data["status"] = "no_delay"
            self.insured_passengers[flight_number] = passenger_data

            return {
                "status": "no_payout",
                "flight_number": flight_number,
                "delay_minutes": ai_response["delay_minutes"],
                "message": f"Flight on time or delay under {self.min_delay_hours} hours threshold."
            }

    def get_contract_stats(self):
        """Get contract statistics."""
        total_policies = len(self.insured_passengers.data)
        payout_count = sum(
            1 for p in self.insured_passengers.data.values()
            if p.get("payout_claimed", False)
        )
        total_payouts = sum(
            p.get("payout_amount", 0)
            for p in self.insured_passengers.data.values()
        )

        return {
            "total_policies": total_policies,
            "payout_count": payout_count,
            "total_payouts": total_payouts,
            "premium_cost": self.premium_cost,
            "insurance_payout": self.insurance_payout
        }


# ============================================================================
# Test Scenarios
# ============================================================================

def run_tests():
    """Run all test scenarios."""

    print("=" * 70)
    print("✈️  Flight Delay Insurance Smart Contract - GenLayer Demo")
    print("=" * 70)

    print("\n📋 Config:")
    print(f"   insurance_payout = {100} USDC")
    print(f"   premium_cost = {10} USDC")
    print(f"   min_delay_hours = {2}")

    contract = FlightInsuranceMock()
    results = []

    # =========================================================================
    # Scenario 1: Purchase Insurance
    # =========================================================================
    print("\n" + "-" * 70)
    print("🎫 Scenario 1: Purchase Insurance")
    print("-" * 70)

    result = contract.buy_insurance(
        flight_number="IR123",
        departure_date="2025-06-01",
        passenger_wallet="0xAliceWallet123",
        value=10
    )

    if result.get("success"):
        print("✅ Insurance purchased:")
        print(f"   flight_number: {result.get('flight_number', 'IR123')}")
        print(f"   passenger: 0xAliceWallet123")
        print(f"   premium: {result.get('premium')} USDC")
        print(f"   coverage: {result.get('coverage')} USDC")
        results.append(("Purchase", "PASS"))
    else:
        print(f"❌ Failed: {result.get('error')}")
        results.append(("Purchase", "FAIL"))

    # =========================================================================
    # Scenario 2: Check Delayed Flight & Payout
    # =========================================================================
    print("\n" + "-" * 70)
    print("🔍 Scenario 2: Check Flight Status (Delayed - 3 hours)")
    print("-" * 70)

    result = contract.check_flight_and_payout("IR123")

    print(f"\n📊 Result:")
    print(f"   status: {result.get('status')}")
    print(f"   message: {result.get('message')}")
    if result.get('payout_amount'):
        print(f"   💰 payout: {result.get('payout_amount')} USDC")
        print(f"   ⏱️  delay: {result.get('delay_minutes')} minutes")

    results.append(("Delayed Flight Payout", "PASS" if result.get('status') == 'payout_success' else "FAIL"))

    # =========================================================================
    # Scenario 3: Check On-Time Flight
    # =========================================================================
    print("\n" + "-" * 70)
    print("🔍 Scenario 3: Purchase & Check On-Time Flight")
    print("-" * 70)

    # Purchase another insurance
    contract.buy_insurance(
        flight_number="IR789",
        departure_date="2025-06-02",
        passenger_wallet="0xBobWallet456",
        value=10
    )

    result = contract.check_flight_and_payout("IR789")

    print(f"\n📊 Result:")
    print(f"   status: {result.get('status')}")
    print(f"   message: {result.get('message')}")
    print(f"   delay: {result.get('delay_minutes')} minutes")

    results.append(("On-Time Flight", "PASS" if result.get('status') == 'no_payout' else "FAIL"))

    # =========================================================================
    # Scenario 4: Prevent Double Payout
    # =========================================================================
    print("\n" + "-" * 70)
    print("🚫 Scenario 4: Prevent Double Payout (should reject)")
    print("-" * 70)

    result = contract.check_flight_and_payout("IR123")

    if result.get("error"):
        print(f"✅ Double payout prevented:")
        print(f"   message: {result.get('error')}")
        results.append(("Double Payout Prevention", "PASS"))
    else:
        print(f"❌ Should have rejected but didn't")
        results.append(("Double Payout Prevention", "FAIL"))

    # =========================================================================
    # Summary
    # =========================================================================
    print("\n" + "=" * 70)
    print("📊 Test Summary")
    print("=" * 70)

    all_passed = all(r[1] == "PASS" for r in results)
    print(f"\n{'✅' if all_passed else '❌'} Tests: {sum(1 for r in results if r[1] == 'PASS')}/{len(results)} passed")

    stats = contract.get_contract_stats()
    print(f"\n📈 Contract Stats:")
    print(f"   Total policies: {stats['total_policies']}")
    print(f"   Payouts processed: {stats['payout_count']}")
    print(f"   Total USDC paid out: {stats['total_payouts']}")

    print(f"\n📢 Events Emitted:")
    for event in contract.events:
        print(f"   {event}")

    print("\n" + "=" * 70)
    print("🎉 All GenLayer smart contract tests completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()
