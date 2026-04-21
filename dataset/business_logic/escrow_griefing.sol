// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Escrow Griefing via Dust Deposit
 * CATEGORY: Business Logic — Incorrect State Invariant
 *
 * The escrow requires an exact ETH amount from the buyer to confirm.
 * Any party can send 1 wei directly to the contract, making the stored
 * balance != expectedAmount forever, permanently griefing the escrow
 * and locking both parties' funds. Additionally, the seller can confirm
 * their own release if the dispute timer expires.
 */
contract EscrowGriefing {
    enum State { AWAITING_PAYMENT, COMPLETE, DISPUTED }

    address public buyer;
    address public seller;
    uint256 public expectedAmount;
    uint256 public createdAt;
    State   public state;

    constructor(address _seller, uint256 _amount) payable {
        buyer          = msg.sender;
        seller         = _seller;
        expectedAmount = _amount;
        createdAt      = block.timestamp;
    }

    function confirmPayment() external payable {
        require(state == State.AWAITING_PAYMENT, "Wrong state");
        // BUG: anyone can grief by sending dust, making balance != expectedAmount
        require(address(this).balance == expectedAmount, "Incorrect amount");
        state = State.COMPLETE;
        payable(seller).transfer(address(this).balance);
    }

    function raiseDispute() external {
        require(msg.sender == buyer || msg.sender == seller, "Not party");
        state = State.DISPUTED;
    }

    // BUG: seller can call this unilaterally after timeout — no arbitration
    function sellerRelease() external {
        require(msg.sender == seller, "Not seller");
        require(block.timestamp > createdAt + 7 days, "Too early");
        payable(seller).transfer(address(this).balance);
    }

    // Accepting any ETH breaks the exact-balance check above
    receive() external payable {}
}
