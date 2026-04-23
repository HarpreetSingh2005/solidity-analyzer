// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe Escrow contract
contract SafeNewEscrow01 {
    address public arbiter;
    mapping(address => uint256) public deposits;
    
    constructor(address _arbiter) { arbiter = _arbiter; }
    
    function deposit() external payable { deposits[msg.sender] += msg.value; }
    
    function resolve(address payee, uint256 amount) external {
        require(msg.sender == arbiter, "Only arbiter");
        require(amount <= address(this).balance, "Insufficient balance");
        (bool success, ) = payee.call{value: amount}("");
        require(success, "Transfer failed");
    }
}