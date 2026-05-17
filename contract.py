"""
Flight Delay Insurance - GenLayer Smart Contract
AI-powered smart contract that insures flight delays and auto-pays compensation

How it works on GenLayer:
1. Deploy contract on GenLayer testnet
2. Passengers call buy_insurance() with premium payment
3. After flight, anyone can call check_flight_and_payout()
4. AI validators crawl airline websites and return delay status
5. Payout is automatically sent to passenger wallet
"""

from genlayer import *


class FlightInsurance(Contract):
    """
    Flight Delay Insurance Smart Contract

    This contract:
    - Allows passengers to buy flight delay insurance
    - Uses GenLayer AI Query to check real flight status from airline websites
    - Automatically pays compensation if flight is delayed beyond threshold
    """

    def __init__(self):
        """Initialize contract with default values."""
        self.insurance_payout = 100      # USDC payout amount
        self.premium_cost = 10           # USDC premium cost
        self.min_delay_hours = 2         # Minimum delay for payout
        self.insured_passengers = StorageMap()


    @payable
    def buy_insurance(
        self,
        flight_number: str,
        departure_date: str,
        passenger_wallet: Address
    ) -> str:
        """
        Purchase flight delay insurance.

        Args:
            flight_number: Flight number (e.g., "IR123", "UA456")
            departure_date: Departure date (YYYY-MM-DD format)
            passenger_wallet: Wallet address to receive payout

        Returns:
            Success message with policy details
        """
        # Check that premium is paid exactly
        if msg.value != self.premium_cost:
            raise Error(f"Premium must be exactly {self.premium_cost} USDC")

        # Check if insurance already purchased for this flight
        if self.insured_passengers.contains(flight_number):
            raise Error(f"Insurance already purchased for flight {flight_number}")

        # Store passenger data
        passenger_data = {
            "passenger": str(passenger_wallet),
            "departure_date": departure_date,
            "premium_paid": msg.value,
            "payout_claimed": False,
            "payout_amount": 0,
            "status": "active"
        }

        self.insured_passengers[flight_number] = passenger_data

        # Emit event
        emit InsurancePurchased(
            flight_number=flight_number,
            passenger=str(passenger_wallet),
            premium=msg.value,
            coverage=self.insurance_payout
        )

        return (
            f"Insurance purchased for flight {flight_number}. "
            f"Coverage: {self.insurance_payout} USDC. "
            f"Premium paid: {msg.value} USDC."
        )


    def check_flight_and_payout(self, flight_number: str) -> dict:
        """
        Check flight status using GenLayer AI and process payout if delayed.

        This is the core AI-powered function:
        - GenLayer validators crawl airline websites using AI
        - They determine if the flight was actually delayed
        - If delayed beyond threshold, payout is auto-sent to passenger wallet

        Args:
            flight_number: Flight number to check

        Returns:
            Dictionary with check results and payout status
        """
        # Verify insurance exists for this flight
        if not self.insured_passengers.contains(flight_number):
            raise Error(f"No insurance found for flight {flight_number}")

        passenger_data = self.insured_passengers[flight_number]

        # Prevent double-payout
        if passenger_data["payout_claimed"]:
            raise Error("Payout has already been claimed for this flight")

        # Build AI prompt for GenLayer validators
        prompt = (
            f"You are an AI oracle checking real flight data.\n\n"
            f"Flight: {flight_number}\n"
            f"Scheduled Departure: {passenger_data['departure_date']}\n\n"
            f"Task: Go to the airline website and check if this flight was delayed.\n"
            f"Return:\n"
            f"  - status: 'delayed' or 'on_time'\n"
            f"  - delay_minutes: actual delay in minutes (0 if on time)\n"
            f"  - reason: brief reason for delay (if delayed)\n"
            f"\n"
            f"Be thorough and check official airline sources."
        )

        # ══════════════════════════════════════════════════════════════════════
        # THE AI MAGIC: GenLayer AI Query
        # In production, this calls GenLayer's AI oracle which:
        # 1. Distributes query to 3+ AI validators
        # 2. Each validator crawls airline websites independently
        # 3. Validators reach consensus on flight status
        # 4. Result is returned as JSON matching the schema
        # ══════════════════════════════════════════════════════════════════════
        ai_response = IAgent.query(
            prompt=prompt,
            ABI='''
            {
                "status": "string",
                "delay_minutes": "number",
                "reason": "string"
            }
            ''',
            min_validators=3,
            validation_rules="strict"
        )

        # Update status in storage BEFORE sending funds (re-entrancy protection)
        passenger_data["status"] = ai_response["status"]
        passenger_data["delay_minutes"] = ai_response["delay_minutes"]

        # Check if delay meets threshold
        if ai_response["status"] == "delayed" and ai_response["delay_minutes"] >= self.min_delay_hours * 60:
            # Mark as claimed FIRST to prevent re-entrancy attack
            passenger_data["payout_claimed"] = True
            passenger_data["payout_amount"] = self.insurance_payout
            self.insured_passengers[flight_number] = passenger_data

            # Auto transfer payout to passenger wallet
            send_funds(passenger_data["passenger"], self.insurance_payout)

            # Emit payout event
            emit PayoutProcessed(
                flight_number=flight_number,
                passenger=passenger_data["passenger"],
                amount=self.insurance_payout,
                delay_minutes=ai_response["delay_minutes"],
                reason=ai_response.get("reason", "unknown")
            )

            return {
                "status": "payout_success",
                "flight_number": flight_number,
                "delay_minutes": ai_response["delay_minutes"],
                "payout_amount": self.insurance_payout,
                "message": f"Flight delayed by {ai_response['delay_minutes']} minutes. Payout sent to wallet."
            }

        else:
            # No payout - flight was on time or delay too small
            passenger_data["payout_claimed"] = False
            passenger_data["status"] = "no_delay"
            self.insured_passengers[flight_number] = passenger_data

            return {
                "status": "no_payout",
                "flight_number": flight_number,
                "delay_minutes": ai_response["delay_minutes"],
                "message": f"Flight on time or delay under {self.min_delay_hours} hours threshold."
            }


    def get_passenger_info(self, flight_number: str) -> dict:
        """Get insurance info for a specific flight."""
        if not self.insured_passengers.contains(flight_number):
            raise Error(f"No insurance found for flight {flight_number}")

        return self.insured_passengers[flight_number]


    def get_contract_stats(self) -> dict:
        """Get contract statistics and statistics."""
        total_policies = 0
        payout_count = 0
        total_payouts = 0

        # Iterate through all stored flights
        for flight_key in self.insured_passengers.keys():
            passenger_data = self.insured_passengers[flight_key]
            total_policies += 1

            if passenger_data["payout_claimed"]:
                payout_count += 1
                total_payouts += passenger_data["payout_amount"]

        return {
            "total_policies": total_policies,
            "payout_count": payout_count,
            "total_payouts": total_payouts,
            "premium_cost": self.premium_cost,
            "insurance_payout": self.insurance_payout,
            "min_delay_hours": self.min_delay_hours
        }


# ═══════════════════════════════════════════════════════════════════════════
# Event Definitions
# ═══════════════════════════════════════════════════════════════════════════

class InsurancePurchased(Event):
    flight_number: str
    passenger: str
    premium: int
    coverage: int


class PayoutProcessed(Event):
    flight_number: str
    passenger: str
    amount: int
    delay_minutes: int
    reason: str