// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe simplified lending pool utilizing strict ratio checks.
contract SafeLending {
    mapping(address => uint256) public deposits;
    mapping(address => uint256) public borrows;
    uint256 public totalLiquidity;

    function deposit() external payable {
        deposits[msg.sender] += msg.value;
        totalLiquidity += msg.value;
    }

    function borrow(uint256 amount) external {
        require(amount <= totalLiquidity, "Not enough liquidity");
        require(deposits[msg.sender] * 2 >= borrows[msg.sender] + amount, "Insufficient collateral");
        
        borrows[msg.sender] += amount;
        totalLiquidity -= amount;
        
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
    }

    function repay() external payable {
        require(borrows[msg.sender] >= msg.value, "Overpayment");
        borrows[msg.sender] -= msg.value;
        totalLiquidity += msg.value;
    }
}