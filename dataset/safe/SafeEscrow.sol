// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe escrow contract implementing proper state transitions.
contract SafeEscrow {
    address public buyer;
    address public seller;
    address public arbiter;
    uint256 public amount;
    
    enum State { AWAITING_PAYMENT, AWAITING_DELIVERY, COMPLETE, REFUNDED }
    State public currentState;

    constructor(address _seller, address _arbiter) {
        seller = _seller;
        arbiter = _arbiter;
        currentState = State.AWAITING_PAYMENT;
    }

    function deposit() external payable {
        require(currentState == State.AWAITING_PAYMENT, "Already paid");
        buyer = msg.sender;
        amount = msg.value;
        currentState = State.AWAITING_DELIVERY;
    }

    function confirmDelivery() external {
        require(msg.sender == buyer, "Only buyer can confirm");
        require(currentState == State.AWAITING_DELIVERY, "Cannot confirm delivery");
        
        currentState = State.COMPLETE;
        
        (bool success, ) = seller.call{value: amount}("");
        require(success, "Transfer failed");
    }

    function refund() external {
        require(msg.sender == arbiter, "Only arbiter can refund");
        require(currentState == State.AWAITING_DELIVERY, "Cannot refund");
        
        currentState = State.REFUNDED;
        
        (bool success, ) = buyer.call{value: amount}("");
        require(success, "Transfer failed");
    }
}