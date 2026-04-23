// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe against reentrancy using Checks-Effects-Interactions and a lock.
contract TestSafeReentrancyGuard {
    mapping(address => uint256) public balances;
    uint256 private _status = 1;
    error ReentrantCall();

    modifier nonReentrant() {
        if (_status == 2) revert ReentrantCall();
        _status = 2;
        _;
        _status = 1;
    }

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw(uint256 amount) external nonReentrant {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        // Effect (state changes before external call)
        balances[msg.sender] -= amount;
        
        // Interaction
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
    }
}